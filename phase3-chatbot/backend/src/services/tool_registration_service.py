import asyncio
from typing import Dict, Any, List, Optional, Callable
from sqlmodel import Session, select
from datetime import datetime
from ..models.mcp_tool import McpTool
from ..models.audit_log import AuditLog


class ToolRegistrationService:
    """Dynamic tool registration for MCP integration."""

    def __init__(self, session: Session):
        """
        Initialize Tool Registration Service.

        Args:
            session: Database session
        """
        self.session = session
        self.tools_registry: Dict[str, Dict[str, Any]] = {}

    async def register_tool(
        self,
        name: str,
        provider: str,
        handler: Callable,
        description: str = "",
        schema_json: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> McpTool:
        """
        Register an MCP tool dynamically.

        Args:
            name: Unique name for the tool
            provider: Provider associated with the tool
            handler: Callable that handles the tool execution
            description: Description of the tool
            schema_json: JSON schema for the tool parameters
            user_id: Optional user ID (for user-specific tools)

        Returns:
            Created McpTool object
        """
        # Check if tool already exists
        existing_tool = self.session.exec(
            select(McpTool).where(McpTool.name == name)
        ).first()

        if existing_tool:
            # Update existing tool
            existing_tool.provider = provider
            existing_tool.description = description
            existing_tool.tool_schema = schema_json or {}
            existing_tool.user_id = user_id
            existing_tool.is_active = True
            existing_tool.updated_at = datetime.utcnow()

            self.session.add(existing_tool)
            self.session.commit()
            self.session.refresh(existing_tool)

            # Update in-memory registry
            self.tools_registry[name] = {
                'handler': handler,
                'description': description,
                'provider': provider,
                'tool_schema': schema_json or {},
                'user_id': user_id
            }

            return existing_tool
        else:
            # Create new tool
            tool = McpTool(
                name=name,
                provider=provider,
                description=description,
                tool_schema=schema_json or {},
                user_id=user_id,
                is_active=True
            )

            self.session.add(tool)
            self.session.commit()
            self.session.refresh(tool)

            # Add to in-memory registry
            self.tools_registry[name] = {
                'handler': handler,
                'description': description,
                'provider': provider,
                'tool_schema': schema_json or {},
                'user_id': user_id
            }

            return tool

    async def unregister_tool(self, name: str) -> bool:
        """
        Unregister an MCP tool.

        Args:
            name: Name of the tool to unregister

        Returns:
            True if successful, False otherwise
        """
        if name in self.tools_registry:
            del self.tools_registry[name]

        # Mark as inactive in database
        tool = self.session.exec(
            select(McpTool).where(McpTool.name == name)
        ).first()

        if tool:
            tool.is_active = False
            tool.updated_at = datetime.utcnow()
            self.session.add(tool)
            self.session.commit()
            return True

        return False

    async def get_registered_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a registered tool by name.

        Args:
            name: Name of the tool

        Returns:
            Tool information or None if not found
        """
        if name in self.tools_registry:
            return self.tools_registry[name]

        # Check database
        db_tool = self.session.exec(
            select(McpTool).where(
                McpTool.name == name,
                McpTool.is_active == True
            )
        ).first()

        if db_tool:
            return {
                'handler': None,  # Handler is only in memory
                'description': db_tool.description,
                'provider': db_tool.provider,
                'tool_schema': db_tool.tool_schema,
                'user_id': db_tool.user_id
            }

        return None

    async def list_registered_tools(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered tools.

        Args:
            user_id: Optional user ID to filter tools for specific user

        Returns:
            List of registered tools
        """
        query = select(McpTool).where(McpTool.is_active == True)

        if user_id:
            query = query.where((McpTool.user_id == user_id) | (McpTool.user_id.is_(None)))
        else:
            query = query.where(McpTool.user_id.is_(None))  # Only system-wide tools

        db_tools = self.session.exec(query).all()

        tools_list = []
        for db_tool in db_tools:
            tools_list.append({
                'name': db_tool.name,
                'description': db_tool.description,
                'provider': db_tool.provider,
                'tool_schema': db_tool.tool_schema,
                'user_id': db_tool.user_id,
                'is_active': db_tool.is_active
            })

        return tools_list


class ToolDiscoveryService:
    """Tool discovery mechanism for MCP integration."""

    def __init__(self, session: Session):
        """
        Initialize Tool Discovery Service.

        Args:
            session: Database session
        """
        self.session = session

    async def discover_tools_by_provider(self, provider: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover tools by provider.

        Args:
            provider: Provider name
            user_id: Optional user ID to filter tools for specific user

        Returns:
            List of tools for the specified provider
        """
        query = select(McpTool).where(
            McpTool.provider == provider,
            McpTool.is_active == True
        )

        if user_id:
            query = query.where((McpTool.user_id == user_id) | (McpTool.user_id.is_(None)))

        db_tools = self.session.exec(query).all()

        tools_list = []
        for db_tool in db_tools:
            tools_list.append({
                'name': db_tool.name,
                'description': db_tool.description,
                'provider': db_tool.provider,
                'tool_schema': db_tool.tool_schema,
                'user_id': db_tool.user_id
            })

        return tools_list

    async def discover_tools_by_capability(self, capability: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover tools by capability/keyword.

        Args:
            capability: Capability or keyword to search for
            user_id: Optional user ID to filter tools for specific user

        Returns:
            List of tools matching the capability
        """
        # Search in name and description for the capability
        query = select(McpTool).where(
            McpTool.is_active == True,
            (
                McpTool.name.contains(capability) |
                McpTool.description.contains(capability)
            )
        )

        if user_id:
            query = query.where((McpTool.user_id == user_id) | (McpTool.user_id.is_(None)))

        db_tools = self.session.exec(query).all()

        tools_list = []
        for db_tool in db_tools:
            tools_list.append({
                'name': db_tool.name,
                'description': db_tool.description,
                'provider': db_tool.provider,
                'tool_schema': db_tool.tool_schema,
                'user_id': db_tool.user_id
            })

        return tools_list

    async def discover_all_tools(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover all available tools.

        Args:
            user_id: Optional user ID to filter tools for specific user

        Returns:
            List of all available tools
        """
        query = select(McpTool).where(McpTool.is_active == True)

        if user_id:
            query = query.where((McpTool.user_id == user_id) | (McpTool.user_id.is_(None)))

        db_tools = self.session.exec(query).all()

        tools_list = []
        for db_tool in db_tools:
            tools_list.append({
                'name': db_tool.name,
                'description': db_tool.description,
                'provider': db_tool.provider,
                'tool_schema': db_tool.tool_schema,
                'user_id': db_tool.user_id
            })

        return tools_list


class ToolValidationService:
    """Tool validation framework for MCP integration."""

    def __init__(self, session: Session):
        """
        Initialize Tool Validation Service.

        Args:
            session: Database session
        """
        self.session = session

    async def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool parameters against schema.

        Args:
            tool_name: Name of the tool
            parameters: Parameters to validate

        Returns:
            Validation result with success flag and errors if any
        """
        # Get the tool from database
        db_tool = self.session.exec(
            select(McpTool).where(
                McpTool.name == tool_name,
                McpTool.is_active == True
            )
        ).first()

        if not db_tool:
            return {
                "success": False,
                "errors": [f"Tool '{tool_name}' not found"]
            }

        # Validate against schema if available
        schema = db_tool.tool_schema
        if not schema:
            return {
                "success": True,
                "errors": [],
                "warnings": [f"No schema defined for tool '{tool_name}', skipping validation"]
            }

        # Simple validation based on schema definition
        errors = []
        schema_properties = schema.get("properties", {})

        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in parameters:
                errors.append(f"Required field '{field}' is missing")

        # Validate field types if specified
        for param_name, param_value in parameters.items():
            if param_name in schema_properties:
                expected_type = schema_properties[param_name].get("type")

                if expected_type == "string" and not isinstance(param_value, str):
                    errors.append(f"Field '{param_name}' should be a string, got {type(param_value).__name__}")
                elif expected_type == "number" and not isinstance(param_value, (int, float)):
                    errors.append(f"Field '{param_name}' should be a number, got {type(param_value).__name__}")
                elif expected_type == "integer" and not isinstance(param_value, int):
                    errors.append(f"Field '{param_name}' should be an integer, got {type(param_value).__name__}")
                elif expected_type == "boolean" and not isinstance(param_value, bool):
                    errors.append(f"Field '{param_name}' should be a boolean, got {type(param_value).__name__}")

        return {
            "success": len(errors) == 0,
            "errors": errors,
            "warnings": []
        }

    async def validate_tool_access(self, tool_name: str, user_id: str) -> Dict[str, Any]:
        """
        Validate if a user has access to a specific tool.

        Args:
            tool_name: Name of the tool
            user_id: User ID

        Returns:
            Validation result with access information
        """
        # Get the tool from database
        db_tool = self.session.exec(
            select(McpTool).where(
                McpTool.name == tool_name,
                McpTool.is_active == True
            )
        ).first()

        if not db_tool:
            return {
                "success": False,
                "has_access": False,
                "error": f"Tool '{tool_name}' not found"
            }

        # Check if tool is user-specific
        if db_tool.user_id is not None and db_tool.user_id != user_id:
            return {
                "success": True,
                "has_access": False,
                "error": f"User does not have access to tool '{tool_name}'"
            }

        return {
            "success": True,
            "has_access": True,
            "error": None
        }

    async def validate_tool_compatibility(self, tool_name: str, provider: str) -> Dict[str, Any]:
        """
        Validate if a tool is compatible with a specific provider.

        Args:
            tool_name: Name of the tool
            provider: Provider name

        Returns:
            Validation result with compatibility information
        """
        # Get the tool from database
        db_tool = self.session.exec(
            select(McpTool).where(
                McpTool.name == tool_name,
                McpTool.is_active == True
            )
        ).first()

        if not db_tool:
            return {
                "success": False,
                "is_compatible": False,
                "error": f"Tool '{tool_name}' not found"
            }

        # Check provider compatibility
        is_compatible = db_tool.provider == provider

        return {
            "success": True,
            "is_compatible": is_compatible,
            "error": None if is_compatible else f"Tool '{tool_name}' is not compatible with provider '{provider}', expected '{db_tool.provider}'"
        }