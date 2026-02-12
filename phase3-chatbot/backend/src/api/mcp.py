from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlmodel import Session
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from ..services.mcp_integration import McpIntegrationService
from ..services.api_key_manager import ApiKeyManager
from ..services.audit_service import AuditService
from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..models.audit_log import AuditLog


router = APIRouter()


class InvokeToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    provider: Optional[str] = None


class InvokeToolResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    tool_name: str
    provider: str


class GetAuditLogsRequest(BaseModel):
    action_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50
    offset: int = 0


class GetAuditLogsResponse(BaseModel):
    logs: list[AuditLog]
    total_count: int
    limit: int
    offset: int


@router.post("/mcp/tools/invoke", response_model=InvokeToolResponse)
async def invoke_mcp_tool(
    request: InvokeToolRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Invoke a registered MCP tool.

    Args:
        request: Contains tool name and parameters
        current_user: Authenticated user
        session: Database session

    Returns:
        Result of tool invocation
    """
    # Initialize services
    api_key_manager = ApiKeyManager()
    audit_service = AuditService(session)
    mcp_service = McpIntegrationService(session, api_key_manager, audit_service)

    try:
        # Invoke the tool
        result = await mcp_service.invoke_tool(
            tool_name=request.tool_name,
            parameters=request.parameters,
            user_id=current_user.id,
            provider=request.provider
        )

        return InvokeToolResponse(
            success=result["success"],
            result=result.get("result"),
            error=result.get("error"),
            tool_name=result.get("tool_name", request.tool_name),
            provider=result.get("provider", request.provider or "unknown")
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error invoking MCP tool: {str(e)}"
        )


@router.get("/mcp/tools/available")
async def get_available_tools(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get list of available MCP tools for the user.

    Args:
        current_user: Authenticated user
        session: Database session

    Returns:
        List of available tools
    """
    # Initialize services
    api_key_manager = ApiKeyManager()
    audit_service = AuditService(session)
    mcp_service = McpIntegrationService(session, api_key_manager, audit_service)

    try:
        available_tools = mcp_service.get_available_tools(user_id=current_user.id)
        return {"tools": available_tools}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving available tools: {str(e)}"
        )


@router.get("/mcp/providers/available")
async def get_available_providers(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get list of supported providers.

    Args:
        current_user: Authenticated user
        session: Database session

    Returns:
        List of supported providers
    """
    # Initialize services
    api_key_manager = ApiKeyManager()
    audit_service = AuditService(session)
    mcp_service = McpIntegrationService(session, api_key_manager, audit_service)

    try:
        providers = mcp_service.get_available_providers()
        return {"providers": providers}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving available providers: {str(e)}"
        )


@router.get("/mcp/tools/schema/{tool_name}")
async def get_tool_schema(
    tool_name: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the schema for a specific tool.

    Args:
        tool_name: Name of the tool
        current_user: Authenticated user
        session: Database session

    Returns:
        Schema for the specified tool
    """
    # This would typically fetch from the database or a predefined schema
    # For now, we'll return a generic response
    # In a real implementation, this would fetch from McpTool.model.tool_schema
    from sqlmodel import select
    from ..models.mcp_tool import McpTool

    tool = session.exec(
        select(McpTool).where(
            McpTool.name == tool_name,
            McpTool.is_active == True
        )
    ).first()

    if not tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found"
        )

    # Verify user has access to this tool
    api_key_manager = ApiKeyManager()
    has_access = api_key_manager.retrieve_key(
        session=session,
        user_id=current_user.id,
        provider=tool.provider
    ) is not None

    if not has_access:
        raise HTTPException(
            status_code=403,
            detail=f"You don't have access to provider '{tool.provider}' required for tool '{tool_name}'"
        )

    return {
        "name": tool.name,
        "description": tool.description,
        "provider": tool.provider,
        "tool_schema": tool.tool_schema
    }


@router.get("/audit/logs", response_model=GetAuditLogsResponse)
async def get_audit_logs(
    request: GetAuditLogsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve audit logs for the user.

    Args:
        request: Filtering parameters
        current_user: Authenticated user (admin users can see all logs)
        session: Database session

    Returns:
        List of audit logs matching the criteria
    """
    # Initialize audit service
    audit_service = AuditService(session)

    try:
        # Determine user_id to filter by
        # Regular users can only see their own logs
        # Admin users can see all logs (would need admin check in real implementation)
        user_id = current_user.id

        # Generate the report using audit service
        logs = await audit_service.generate_report(
            session=session,
            user_id=user_id,
            start_date=request.start_date,
            end_date=request.end_date,
            action_types=[request.action_type] if request.action_type else None
        )

        # Apply pagination
        start_idx = request.offset
        end_idx = start_idx + request.limit
        paginated_logs = logs[start_idx:end_idx]

        return GetAuditLogsResponse(
            logs=paginated_logs,
            total_count=len(logs),
            limit=request.limit,
            offset=request.offset
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving audit logs: {str(e)}"
        )


@router.get("/mcp/user/activity")
async def get_user_activity(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user activity summary.

    Args:
        days: Number of days to look back (default 30)
        current_user: Authenticated user
        session: Database session

    Returns:
        User activity summary
    """
    # Initialize audit service
    audit_service = AuditService(session)

    try:
        activity_summary = await audit_service.get_user_activity(
            session=session,
            user_id=current_user.id,
            days=days
        )

        return activity_summary

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user activity: {str(e)}"
        )


@router.post("/mcp/tools/register")
async def register_tool(
    tool_name: str,
    provider: str,
    description: str,
    schema_json: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Register a new tool (admin functionality).

    Args:
        tool_name: Name of the tool
        provider: Provider associated with the tool
        description: Description of the tool
        schema_json: JSON schema for the tool parameters
        current_user: Authenticated user (must be admin)
        session: Database session

    Returns:
        Confirmation of tool registration
    """
    # For security, only allow this for admin users in a real implementation
    # For this example, we'll allow it for any user for testing purposes
    # In production, add admin check: if not current_user.is_admin:

    from ..services.tool_registration_service import ToolRegistrationService

    try:
        tool_registration_service = ToolRegistrationService(session)

        # In a real implementation, we'd need a handler function
        # For now, we'll create a dummy handler that just echoes back the parameters
        async def dummy_handler(params, api_key, user_id):
            return {
                "message": f"Tool {tool_name} executed with parameters",
                "params": params,
                "provider": provider
            }

        registered_tool = await tool_registration_service.register_tool(
            name=tool_name,
            provider=provider,
            handler=dummy_handler,
            description=description,
            schema_json=schema_json,
            user_id=current_user.id
        )

        return {
            "success": True,
            "message": f"Tool '{tool_name}' registered successfully",
            "tool_id": str(registered_tool.id)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error registering tool: {str(e)}"
        )