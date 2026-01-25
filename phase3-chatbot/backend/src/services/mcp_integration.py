import asyncio
from typing import Dict, Any, Optional, List
from sqlmodel import Session
from ..models.mcp_tool import McpTool
from ..models.audit_log import AuditLog
from .audit_service import AuditService
from .api_key_manager import ApiKeyManager
import uuid
import time


class ProviderAdapter:
    """Abstract base class for provider adapters."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    async def execute_request(self, endpoint: str, payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """
        Execute a request to the provider API.

        Args:
            endpoint: API endpoint to call
            payload: Request payload
            api_key: API key for authentication

        Returns:
            Response from the provider API
        """
        raise NotImplementedError("Subclasses must implement execute_request")


class OpenAIProviderAdapter(ProviderAdapter):
    """Provider adapter for OpenAI API."""

    def __init__(self):
        super().__init__("openai")
        self.base_url = "https://api.openai.com/v1"

    async def execute_request(self, endpoint: str, payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """
        Execute a request to the OpenAI API.

        Args:
            endpoint: API endpoint to call
            payload: Request payload
            api_key: API key for authentication

        Returns:
            Response from the OpenAI API
        """
        import aiohttp

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()

                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"OpenAI API error: {result.get('error', {}).get('message', 'Unknown error')}",
                        "status_code": response.status,
                        "result": result
                    }

                return {
                    "success": True,
                    "result": result,
                    "status_code": response.status
                }


class AnthropicProviderAdapter(ProviderAdapter):
    """Provider adapter for Anthropic API."""

    def __init__(self):
        super().__init__("anthropic")
        self.base_url = "https://api.anthropic.com/v1"

    async def execute_request(self, endpoint: str, payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """
        Execute a request to the Anthropic API.

        Args:
            endpoint: API endpoint to call
            payload: Request payload
            api_key: API key for authentication

        Returns:
            Response from the Anthropic API
        """
        import aiohttp

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"  # Use latest version
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()

                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"Anthropic API error: {result.get('error', {}).get('message', 'Unknown error')}",
                        "status_code": response.status,
                        "result": result
                    }

                return {
                    "success": True,
                    "result": result,
                    "status_code": response.status
                }


class McpIntegrationService:
    """Core service for MCP protocol communication and tool management."""

    def __init__(
        self,
        session: Session,
        api_key_manager: ApiKeyManager,
        audit_service: AuditService
    ):
        """
        Initialize MCP Integration Service.

        Args:
            session: Database session
            api_key_manager: Service for managing API keys
            audit_service: Service for audit logging
        """
        self.session = session
        self.api_key_manager = api_key_manager
        self.audit_service = audit_service
        self.tools_registry: Dict[str, Dict[str, Any]] = {}

        # Initialize provider adapters
        self.provider_adapters = {
            "openai": OpenAIProviderAdapter(),
            "anthropic": AnthropicProviderAdapter()
        }

    def register_tool(self, name: str, handler: callable, description: str = "", provider: str = ""):
        """
        Register an MCP tool with the service.

        Args:
            name: Unique name for the tool
            handler: Callable that handles the tool execution
            description: Description of the tool
            provider: Provider associated with the tool
        """
        self.tools_registry[name] = {
            'handler': handler,
            'description': description,
            'provider': provider
        }

    def register_tools(self, tools: List[Dict[str, Any]]):
        """
        Register multiple tools at once.

        Args:
            tools: List of dictionaries containing tool information
        """
        for tool in tools:
            self.register_tool(
                name=tool['name'],
                handler=tool['handler'],
                description=tool.get('description', ''),
                provider=tool.get('provider', '')
            )

    async def enhance_mcp_integration_service(self):
        """
        Enhance MCP integration service to support multiple providers.
        This method can be called to ensure the service is properly configured for multi-provider support.
        """
        # Already implemented in the constructor
        pass

    async def invoke_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: uuid.UUID,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool with proper authentication and validation.

        Args:
            tool_name: Name of the tool to invoke
            parameters: Parameters for the tool
            user_id: User ID making the request
            provider: Optional provider to use

        Returns:
            Dictionary with result of tool execution
        """
        start_time = time.time()

        # Check if tool exists
        if tool_name not in self.tools_registry:
            # Log the failure
            await self.audit_service.log_operation(
                session=self.session,
                user_id=user_id,
                action_type="TOOL_INVOCATION_FAILED",
                resource_type="MCP_TOOL",
                resource_id=None,
                metadata={
                    "tool_name": tool_name,
                    "reason": "Tool not found",
                    "parameters": parameters
                },
                success=False
            )

            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "result": None
            }

        tool_info = self.tools_registry[tool_name]

        try:
            # Determine provider - use specified provider or tool's default
            effective_provider = provider or tool_info['provider']

            # Validate provider if specified
            if effective_provider != tool_info['provider']:
                # Log the failure
                await self.audit_service.log_operation(
                    session=self.session,
                    user_id=user_id,
                    action_type="TOOL_INVOCATION_FAILED",
                    resource_type="MCP_TOOL",
                    resource_id=None,
                    metadata={
                        "tool_name": tool_name,
                        "requested_provider": effective_provider,
                        "expected_provider": tool_info['provider'],
                        "reason": "Provider mismatch"
                    },
                    success=False
                )

                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' is not available for provider '{effective_provider}'",
                    "result": None
                }

            # Get the API key for the provider
            api_key = self.api_key_manager.retrieve_key(
                session=self.session,
                user_id=user_id,
                provider=effective_provider
            )

            if not api_key:
                # Log the failure
                await self.audit_service.log_operation(
                    session=self.session,
                    user_id=user_id,
                    action_type="TOOL_INVOCATION_FAILED",
                    resource_type="MCP_TOOL",
                    resource_id=None,
                    metadata={
                        "tool_name": tool_name,
                        "provider": effective_provider,
                        "reason": "API key not found"
                    },
                    success=False
                )

                return {
                    "success": False,
                    "error": f"No API key found for provider '{effective_provider}'",
                    "result": None
                }

            # Execute the tool handler
            handler = tool_info['handler']
            result = await handler(parameters, api_key, user_id)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Log successful execution
            await self.audit_service.log_operation(
                session=self.session,
                user_id=user_id,
                action_type="TOOL_INVOCATION_SUCCESS",
                resource_type="MCP_TOOL",
                resource_id=None,  # Could be the tool ID if available
                metadata={
                    "tool_name": tool_name,
                    "provider": effective_provider,
                    "parameters": parameters,
                    "result_summary": str(result)[:200] if result else None
                },
                success=True,
                response_time_ms=response_time_ms
            )

            return {
                "success": True,
                "result": result,
                "tool_name": tool_name,
                "provider": effective_provider
            }

        except Exception as e:
            # Calculate response time even for failures
            response_time_ms = int((time.time() - start_time) * 1000)

            # Log the failure
            await self.audit_service.log_operation(
                session=self.session,
                user_id=user_id,
                action_type="TOOL_INVOCATION_FAILED",
                resource_type="MCP_TOOL",
                resource_id=None,
                metadata={
                    "tool_name": tool_name,
                    "provider": tool_info['provider'],
                    "parameters": parameters,
                    "error": str(e)
                },
                success=False,
                response_time_ms=response_time_ms,
                error_message=str(e)
            )

            return {
                "success": False,
                "error": f"Error executing tool '{tool_name}': {str(e)}",
                "result": None
            }

    async def handle_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate tool responses.

        Args:
            response: Raw response from tool execution

        Returns:
            Processed and validated response
        """
        # Validate response structure
        if not isinstance(response, dict):
            return {
                "success": False,
                "error": "Invalid response format",
                "result": None
            }

        # Ensure required fields are present
        if "success" not in response:
            response["success"] = response.get("result") is not None

        # Validate result if present
        if "result" in response and response["result"] is not None:
            # Perform any necessary result validation or transformation
            pass

        return response

    def get_available_tools(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Get list of available tools for a specific user.

        Args:
            user_id: User ID

        Returns:
            List of available tools with their metadata
        """
        available_tools = []

        for name, info in self.tools_registry.items():
            # Check if user has API key for this tool's provider
            has_access = self.api_key_manager.retrieve_key(
                session=self.session,
                user_id=user_id,
                provider=info['provider']
            ) is not None

            available_tools.append({
                "name": name,
                "description": info['description'],
                "provider": info['provider'],
                "has_access": has_access
            })

        return available_tools

    def get_available_providers(self) -> List[str]:
        """
        Get list of supported providers.

        Returns:
            List of supported provider names
        """
        return list(self.provider_adapters.keys())

    async def switch_provider(self, user_id: uuid.UUID, current_provider: str, new_provider: str) -> bool:
        """
        Switch between different AI providers.

        Args:
            user_id: User ID
            current_provider: Current provider
            new_provider: New provider to switch to

        Returns:
            True if switch was successful, False otherwise
        """
        # Verify user has API key for new provider
        new_api_key = self.api_key_manager.retrieve_key(
            session=self.session,
            user_id=user_id,
            provider=new_provider
        )

        if not new_api_key:
            return False

        # In a real implementation, this would update user's preferred provider
        # For now, we just verify that the user has access to the new provider
        return True