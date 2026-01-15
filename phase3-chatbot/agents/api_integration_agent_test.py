"""
Tests for the API Integration Agent
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
from agents.api_integration_agent import APIIntegrationAgent, APICommand, APIResponse


def test_initialization():
    """Test initializing the API Integration Agent."""
    agent = APIIntegrationAgent(
        base_url="http://test.com",
        jwt_token="test_token"
    )

    assert agent.base_url == "http://test.com"
    assert agent.jwt_token == "test_token"
    assert agent.auth_headers == {
        'Authorization': 'Bearer test_token',
        'Content-Type': 'application/json'
    }


def test_set_auth_headers():
    """Test setting authentication headers."""
    agent = APIIntegrationAgent(base_url="http://test.com")
    agent._set_auth_headers("new_token")

    assert agent.auth_headers == {
        'Authorization': 'Bearer new_token',
        'Content-Type': 'application/json'
    }


def test_authenticate():
    """Test authentication."""
    agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    assert agent.authenticate() is True

    # Test with no token
    agent_no_token = APIIntegrationAgent(base_url="http://test.com")
    assert agent_no_token.authenticate() is False


@patch('agents.api_integration_agent.requests.request')
def test_send_request_success(mock_request):
    """Test sending a successful request."""
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}
    mock_response.content = '{"result": "success"}'
    mock_request.return_value = mock_response

    agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")
    command = APICommand('GET', '/api/test')

    response = agent.send_request(command)

    assert response.is_success() is True
    assert response.status_code == 200
    assert response.data == {"result": "success"}
    mock_request.assert_called_once()


@patch('agents.api_integration_agent.requests.request')
def test_send_request_failure(mock_request):
    """Test sending a request that fails."""
    # Mock a RequestException that occurs on all attempts
    mock_request.side_effect = requests.exceptions.RequestException("Connection failed")

    agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token", max_retries=1)  # Reduce retries for test
    command = APICommand('GET', '/api/test')

    response = agent.send_request(command)

    assert response.is_error() is True
    assert response.status_code == 500
    assert "Request failed after" in response.error


def test_format_response_single_todo():
    """Test formatting a single todo response."""
    agent = APIIntegrationAgent(base_url="http://test.com")

    data = {
        "content": "Buy groceries",
        "priority": "high",
        "completed": False
    }

    formatted = agent.format_response(data)
    assert "Buy groceries" in formatted
    assert "high priority" in formatted
    assert "Status: pending" in formatted


def test_format_response_multiple_todos():
    """Test formatting a response with multiple todos."""
    agent = APIIntegrationAgent(base_url="http://test.com")

    data = {
        "items": [
            {"content": "Buy groceries", "priority": "high"},
            {"content": "Walk the dog", "priority": "medium"}
        ]
    }

    formatted = agent.format_response(data)
    assert "Buy groceries" in formatted
    assert "Walk the dog" in formatted


def test_format_response_generic():
    """Test formatting a generic response."""
    agent = APIIntegrationAgent(base_url="http://test.com")

    data = {"message": "Hello", "code": 200}

    formatted = agent.format_response(data)
    assert "Hello" in formatted or "200" in formatted


def test_handle_error():
    """Test handling different types of errors."""
    agent = APIIntegrationAgent(base_url="http://test.com")

    error_messages = {
        "401 Unauthorized": "Authentication failed",
        "403 Forbidden": "Access denied",
        "404 Not Found": "Item not found",
        "500 Server Error": "Server error occurred",
        "Timeout": "Request timed out"
    }

    for error, expected in error_messages.items():
        result = agent.handle_error(error)
        assert expected in result


def test_validate_response_success():
    """Test validating a successful response."""
    agent = APIIntegrationAgent(base_url="http://test.com")

    # Valid success response
    response = APIResponse(200, {"data": "value"})
    assert agent.validate_response(response) is True

    # Valid success response with list
    response = APIResponse(200, [{"item": "value"}])
    assert agent.validate_response(response) is True


def test_validate_response_error():
    """Test validating an error response."""
    agent = APIIntegrationAgent(base_url="http://test.com")

    # Valid error response with error message
    response = APIResponse(500, error="Something went wrong")
    # Note: Our validation logic doesn't validate error responses that have an error field
    # So this will return True as long as the structure is valid
    assert agent.validate_response(response) is True


def test_apply_authentication():
    """Test applying authentication to a request."""
    agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    command = APICommand('GET', '/api/test')
    authenticated_command = agent.apply_authentication(command)

    assert 'Authorization' in authenticated_command.headers
    assert 'Bearer test_token' in authenticated_command.headers['Authorization']


def test_transform_request_data():
    """Test transforming request data."""
    agent = APIIntegrationAgent(base_url="http://test.com")

    original_data = {
        "content": "Test task",
        "priority": "HIGH",
        "completed": "false",
        "due_date": "2023-12-25"
    }

    transformed = agent.transform_request_data(original_data)

    assert transformed["content"] == "Test task"
    assert transformed["priority"] == "high"  # Lowercased
    assert transformed["completed"] is False  # Boolean converted


def test_get_todo():
    """Test getting a specific todo."""
    agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    with patch.object(agent, 'send_request') as mock_send:
        mock_response = APIResponse(200, {"id": 1, "content": "Test"})
        mock_send.return_value = mock_response

        response = agent.get_todo(1)

        assert response.status_code == 200
        assert response.data == {"id": 1, "content": "Test"}

        # Check that the correct command was sent
        called_command = mock_send.call_args[0][0]
        assert called_command.method == 'GET'
        assert called_command.endpoint == '/api/todos/1'


def test_create_todo():
    """Test creating a todo."""
    agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    with patch.object(agent, 'send_request') as mock_send:
        mock_response = APIResponse(201, {"id": 1, "content": "Buy groceries", "priority": "high"})
        mock_send.return_value = mock_response

        response = agent.create_todo(content="Buy groceries", priority="high")

        assert response.status_code == 201
        assert response.data["content"] == "Buy groceries"

        # Check that the correct command was sent
        called_command = mock_send.call_args[0][0]
        assert called_command.method == 'POST'
        assert called_command.endpoint == '/api/todos'
        assert called_command.data["content"] == "Buy groceries"
        assert called_command.data["priority"] == "high"


def test_update_todo():
    """Test updating a todo."""
    agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    with patch.object(agent, 'send_request') as mock_send:
        mock_response = APIResponse(200, {"id": 1, "completed": True})
        mock_send.return_value = mock_response

        response = agent.update_todo(1, completed=True)

        assert response.status_code == 200
        assert response.data["completed"] is True

        # Check that the correct command was sent
        called_command = mock_send.call_args[0][0]
        assert called_command.method == 'PUT'
        assert called_command.endpoint == '/api/todos/1'
        assert called_command.data["completed"] is True


def test_delete_todo():
    """Test deleting a todo."""
    agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    with patch.object(agent, 'send_request') as mock_send:
        mock_response = APIResponse(204, {})
        mock_send.return_value = mock_response

        response = agent.delete_todo(1)

        assert response.status_code == 204

        # Check that the correct command was sent
        called_command = mock_send.call_args[0][0]
        assert called_command.method == 'DELETE'
        assert called_command.endpoint == '/api/todos/1'


if __name__ == "__main__":
    pytest.main([__file__])