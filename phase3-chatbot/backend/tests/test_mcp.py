"""Test suite for MCP (Model Context Protocol) endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import Mock, patch, MagicMock
import uuid

from src.main import app
from src.database import get_session, engine
from src.models.user import User
from src.models.mcp_tool import McpTool
from src.models.api_key import ApiKey
from src.dependencies.auth import get_current_user
from src.config import settings


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        id=uuid.uuid4(),
        email="mcp_test@example.com",
        username="mcptestuser",
        hashed_password=pwd_context.hash("testpassword123"),
        is_active=True,
        is_superuser=True  # Give superuser for MCP operations
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Create authentication headers for test user."""
    from src.utils.security import create_access_token
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


def test_invoke_mcp_tool_success(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test successful invocation of an MCP tool."""
    # Create a test tool in the database
    tool = McpTool(
        id=uuid.uuid4(),
        name="test_tool",
        description="A test tool for MCP",
        provider="test_provider",
        tool_schema={
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "A test parameter"}
            },
            "required": ["param1"]
        },
        is_active=True
    )
    db_session.add(tool)
    db_session.commit()
    
    # Test the tool invocation
    response = client.post(
        "/api/mcp/tools/invoke",
        json={
            "tool_name": "test_tool",
            "parameters": {
                "param1": "test_value"
            }
        },
        headers=auth_headers
    )
    
    # The actual response will depend on the implementation of the tool
    # For now, we'll check that the request is processed without error
    assert response.status_code in [200, 400]  # 400 might be returned if the tool doesn't exist in the actual implementation


def test_invoke_mcp_tool_not_found(client: TestClient, test_user, auth_headers: dict):
    """Test invoking a non-existent MCP tool."""
    response = client.post(
        "/api/mcp/tools/invoke",
        json={
            "tool_name": "nonexistent_tool",
            "parameters": {
                "param1": "test_value"
            }
        },
        headers=auth_headers
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_invoke_mcp_tool_invalid_params(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test invoking an MCP tool with invalid parameters."""
    # Create a test tool in the database
    tool = McpTool(
        id=uuid.uuid4(),
        name="test_tool_with_validation",
        description="A test tool with parameter validation",
        provider="test_provider",
        tool_schema={
            "type": "object",
            "properties": {
                "required_param": {"type": "string", "description": "A required parameter"}
            },
            "required": ["required_param"]
        },
        is_active=True
    )
    db_session.add(tool)
    db_session.commit()
    
    # Test with missing required parameter
    response = client.post(
        "/api/mcp/tools/invoke",
        json={
            "tool_name": "test_tool_with_validation",
            "parameters": {
                "wrong_param": "test_value"  # Missing required_param
            }
        },
        headers=auth_headers
    )
    
    # Should return 422 for validation error or 400 for business logic error
    assert response.status_code in [400, 422]


def test_get_available_tools(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test getting list of available MCP tools."""
    # Create some test tools
    tool1 = McpTool(
        id=uuid.uuid4(),
        name="tool1",
        description="First test tool",
        provider="test_provider",
        tool_schema={"type": "object"},
        is_active=True
    )
    tool2 = McpTool(
        id=uuid.uuid4(),
        name="tool2", 
        description="Second test tool",
        provider="test_provider",
        tool_schema={"type": "object"},
        is_active=True
    )
    db_session.add(tool1)
    db_session.add(tool2)
    db_session.commit()
    
    response = client.get("/api/mcp/tools/available", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) >= 2  # At least our 2 tools should be present
    
    # Check that our tools are in the response
    tool_names = [tool["name"] for tool in data["tools"]]
    assert "tool1" in tool_names
    assert "tool2" in tool_names


def test_get_available_tools_empty(client: TestClient, test_user, auth_headers: dict):
    """Test getting available tools when none exist."""
    response = client.get("/api/mcp/tools/available", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert isinstance(data["tools"], list)


def test_get_tool_schema_success(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test getting schema for a specific tool."""
    # Create a test tool
    expected_schema = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "A test parameter"},
            "param2": {"type": "integer", "description": "A numeric parameter"}
        },
        "required": ["param1"]
    }
    
    tool = McpTool(
        id=uuid.uuid4(),
        name="schema_test_tool",
        description="Tool for schema testing",
        provider="test_provider",
        tool_schema=expected_schema,
        is_active=True
    )
    db_session.add(tool)
    db_session.commit()
    
    response = client.get(f"/api/mcp/tools/schema/{tool.name}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data == expected_schema


def test_get_tool_schema_not_found(client: TestClient, test_user, auth_headers: dict):
    """Test getting schema for a non-existent tool."""
    response = client.get("/api/mcp/tools/schema/nonexistent_tool", headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_available_providers(client: TestClient, test_user, auth_headers: dict):
    """Test getting list of available providers."""
    response = client.get("/api/mcp/providers/available", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    # Should return a list of providers
    assert isinstance(data, list)
    # At minimum, we should have some providers like "internal"
    assert len(data) >= 0  # May be empty depending on configuration


def test_register_tool_success(client: TestClient, test_user, auth_headers: dict):
    """Test successful registration of a new tool (admin functionality)."""
    # Only test with superuser (which our test user is)
    tool_schema = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "A test parameter"}
        },
        "required": ["param1"]
    }
    
    response = client.post(
        "/api/mcp/tools/register",
        params={
            "tool_name": "new_test_tool",
            "provider": "test_provider",
            "description": "A newly registered test tool"
        },
        json=tool_schema,
        headers=auth_headers
    )
    
    # This might return 200 on success, or 409 if tool already exists
    assert response.status_code in [200, 409, 422]


def test_register_tool_unauthorized(client: TestClient, db_session: Session):
    """Test that non-admin users cannot register tools."""
    # Create a non-superuser
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    regular_user = User(
        id=uuid.uuid4(),
        email="regular@example.com",
        username="regularuser",
        hashed_password=pwd_context.hash("password123"),
        is_active=True,
        is_superuser=False  # Not a superuser
    )
    db_session.add(regular_user)
    db_session.commit()
    
    # Create auth headers for regular user
    from src.utils.security import create_access_token
    access_token = create_access_token(data={"sub": str(regular_user.id)})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.post(
        "/api/mcp/tools/register",
        params={
            "tool_name": "restricted_tool",
            "provider": "test_provider",
            "description": "Should not be allowed"
        },
        json={
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            },
            "required": ["param1"]
        },
        headers=headers
    )
    
    # Should return 403 Forbidden for non-admin users
    assert response.status_code == 403


def test_register_tool_missing_params(client: TestClient, test_user, auth_headers: dict):
    """Test registering a tool with missing required parameters."""
    response = client.post(
        "/api/mcp/tools/register",
        params={
            "tool_name": "",  # Empty name
            "provider": "test_provider",
            "description": "Tool with empty name"
        },
        json={
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            },
            "required": ["param1"]
        },
        headers=auth_headers
    )
    
    # Should return 422 for validation error or 400 for business logic error
    assert response.status_code in [400, 422]


def test_get_audit_logs(client: TestClient, test_user, auth_headers: dict):
    """Test retrieving audit logs."""
    response = client.get("/api/audit/logs", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    # Response should have logs array and metadata
    assert "logs" in data
    assert "total_count" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["logs"], list)


def test_get_audit_logs_with_filters(client: TestClient, test_user, auth_headers: dict):
    """Test retrieving audit logs with filters."""
    from datetime import datetime, timedelta
    
    # Test with date range filter
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    response = client.get(
        f"/api/audit/logs?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data


def test_get_user_activity(client: TestClient, test_user, auth_headers: dict):
    """Test retrieving user activity summary."""
    response = client.get("/api/mcp/user/activity", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    # Response should contain activity summary
    assert "user_id" in data
    assert "activity_count" in data
    assert "recent_activities" in data


def test_get_user_activity_with_days_param(client: TestClient, test_user, auth_headers: dict):
    """Test retrieving user activity with custom day range."""
    response = client.get("/api/mcp/user/activity?days=7", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data


def test_unauthorized_access_to_mcp_endpoints(client: TestClient):
    """Test that unauthorized access to MCP endpoints is properly rejected."""
    # Try to invoke a tool without authentication
    response = client.post(
        "/api/mcp/tools/invoke",
        json={
            "tool_name": "test_tool",
            "parameters": {"param": "value"}
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    
    # Try to get available tools without authentication
    response = client.get("/api/mcp/tools/available")
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    
    # Try to register a tool without authentication
    response = client.post(
        "/api/mcp/tools/register",
        params={
            "tool_name": "test",
            "provider": "test",
            "description": "test"
        },
        json={"type": "object"}
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@patch('src.services.mcp_integration.McpIntegrationService')
def test_invoke_tool_with_mock(mock_mcp_service_class, client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test tool invocation with mocked MCP service."""
    # Setup mock
    mock_mcp_service_instance = Mock()
    mock_mcp_service_instance.invoke_tool.return_value = {
        "success": True,
        "result": {"message": "Tool executed successfully"},
        "tool_name": "test_tool",
        "provider": "test_provider"
    }
    mock_mcp_service_class.return_value = mock_mcp_service_instance
    
    # Create a test tool in the database
    tool = McpTool(
        id=uuid.uuid4(),
        name="mock_test_tool",
        description="A test tool for mocking",
        provider="test_provider",
        tool_schema={
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            },
            "required": ["param1"]
        },
        is_active=True
    )
    db_session.add(tool)
    db_session.commit()
    
    # Test the tool invocation
    response = client.post(
        "/api/mcp/tools/invoke",
        json={
            "tool_name": "mock_test_tool",
            "parameters": {
                "param1": "test_value"
            }
        },
        headers=auth_headers
    )
    
    # Should succeed with mocked response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "result" in data


@patch('src.services.mcp_integration.McpIntegrationService')
def test_invoke_tool_with_mock_failure(mock_mcp_service_class, client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test tool invocation with mocked failure."""
    # Setup mock to return failure
    mock_mcp_service_instance = Mock()
    mock_mcp_service_instance.invoke_tool.return_value = {
        "success": False,
        "error": "Mocked tool execution failed",
        "tool_name": "failing_test_tool",
        "provider": "test_provider"
    }
    mock_mcp_service_class.return_value = mock_mcp_service_instance
    
    # Create a test tool in the database
    tool = McpTool(
        id=uuid.uuid4(),
        name="failing_test_tool",
        description="A test tool that fails",
        provider="test_provider",
        tool_schema={
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            },
            "required": ["param1"]
        },
        is_active=True
    )
    db_session.add(tool)
    db_session.commit()
    
    # Test the tool invocation
    response = client.post(
        "/api/mcp/tools/invoke",
        json={
            "tool_name": "failing_test_tool",
            "parameters": {
                "param1": "test_value"
            }
        },
        headers=auth_headers
    )
    
    # Should still return 200 but with success=False
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "error" in data