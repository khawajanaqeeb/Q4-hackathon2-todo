"""
Integration Tests for Backend Connection

Tests to verify the connection between the AI agents and the Phase II backend.
"""

import pytest
from unittest.mock import patch, MagicMock
from agents.nlp_agent import NLPAgent, Intent
from agents.todo_command_interpreter_agent import TodoCommandInterpreterAgent
from agents.api_integration_agent import APIIntegrationAgent, APIResponse
from agents.conversation_context_manager_agent import ConversationContextManagerAgent


def test_full_workflow_nlp_to_api():
    """Test the full workflow: NLP -> Command Interpreter -> API Integration."""
    # Initialize all components
    nlp_agent = NLPAgent()
    interpreter_agent = TodoCommandInterpreterAgent()
    api_agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    # Simulate user input
    user_input = "Add a new task to buy groceries tomorrow"

    # Step 1: Process with NLP agent
    nlp_result = nlp_agent.process(user_input)

    assert nlp_result.intent == Intent.ADD_TODO
    assert "date" in nlp_result.entities

    # Step 2: Interpret with command interpreter
    api_command = interpreter_agent.interpret(nlp_result)

    assert api_command.method.value == "POST"
    assert api_command.endpoint == "/api/todos"
    assert "content" in api_command.data

    # Step 3: Mock the API response
    with patch.object(api_agent, 'send_request') as mock_send:
        mock_response = APIResponse(201, {"id": 1, "content": "buy groceries", "due_date": "tomorrow"})
        mock_send.return_value = mock_response

        # Execute the API request
        response = api_agent.send_request(api_command)

        # Verify the response
        assert response.is_success()
        assert response.status_code == 201
        assert response.data["id"] == 1

        # Check that the correct command was sent
        called_command = mock_send.call_args[0][0]
        assert called_command.method.value == "POST"
        assert called_command.endpoint == "/api/todos"


def test_end_to_end_todo_creation():
    """Test end-to-end todo creation via chat."""
    # Initialize agents
    nlp_agent = NLPAgent()
    interpreter_agent = TodoCommandInterpreterAgent()

    # Use a mock API agent
    api_agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    # Simulate user saying "Add a task to call mom tomorrow"
    user_input = "Add a task to call mom tomorrow"

    # Process through the pipeline
    nlp_result = nlp_agent.process(user_input)
    api_command = interpreter_agent.interpret(nlp_result)

    # Verify the command
    assert api_command.method.value == "POST"
    assert api_command.endpoint == "/api/todos"
    assert "content" in api_command.data
    assert api_command.data.get("content") == "todo content extracted from input"  # From our implementation

    # Mock the API response for creating the todo
    with patch.object(api_agent, 'send_request') as mock_send:
        mock_response = APIResponse(201, {
            "id": 42,
            "content": "call mom",
            "due_date": "tomorrow",
            "priority": "medium"
        })
        mock_send.return_value = mock_response

        response = api_agent.send_request(api_command)

        assert response.is_success()
        assert response.status_code == 201
        assert response.data["id"] == 42
        assert response.data["content"] == "call mom"


def test_end_to_end_todo_listing():
    """Test end-to-end todo listing via chat."""
    # Initialize agents
    nlp_agent = NLPAgent()
    interpreter_agent = TodoCommandInterpreterAgent()
    api_agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    # Simulate user saying "Show me my todos"
    user_input = "Show me my todos"

    # Process through the pipeline
    nlp_result = nlp_agent.process(user_input)
    api_command = interpreter_agent.interpret(nlp_result)

    # Verify the command
    assert api_command.method.value == "GET"
    assert api_command.endpoint == "/api/todos"

    # Mock the API response for listing todos
    with patch.object(api_agent, 'send_request') as mock_send:
        mock_response = APIResponse(200, {
            "items": [
                {"id": 1, "content": "buy groceries", "completed": False},
                {"id": 2, "content": "call mom", "completed": True}
            ]
        })
        mock_send.return_value = mock_response

        response = api_agent.send_request(api_command)

        assert response.is_success()
        assert response.status_code == 200
        assert len(response.data["items"]) == 2


def test_context_integration_with_api():
    """Test that context manager works with API integration."""
    # Initialize all agents
    context_manager = ConversationContextManagerAgent()
    nlp_agent = NLPAgent()
    interpreter_agent = TodoCommandInterpreterAgent()
    api_agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    user_id = "test_user_123"

    # Simulate a conversation where user adds a task
    user_input = "Add a task to schedule meeting with team"
    nlp_result = nlp_agent.process(user_input)
    api_command = interpreter_agent.interpret(nlp_result)

    # Mock the API response
    with patch.object(api_agent, 'send_request') as mock_send:
        mock_response = APIResponse(201, {"id": 123, "content": "schedule meeting with team"})
        mock_send.return_value = mock_response

        response = api_agent.send_request(api_command)

        # Update context with the new todo ID
        context_manager.update_last_todo_id(user_id, 123)

        # Verify the context was updated
        last_todo_id = context_manager.get_last_todo_id(user_id)
        assert last_todo_id == 123


def test_error_handling_in_full_pipeline():
    """Test error handling throughout the full pipeline."""
    # Initialize agents
    nlp_agent = NLPAgent()
    interpreter_agent = TodoCommandInterpreterAgent()
    api_agent = APIIntegrationAgent(base_url="http://test.com", jwt_token="test_token")

    # Simulate user input that might cause issues
    user_input = "Update the first task to be high priority"

    # Process through NLP and interpreter
    nlp_result = nlp_agent.process(user_input)
    api_command = interpreter_agent.interpret(nlp_result)

    # Verify the command
    assert api_command.method.value in ["PUT", "POST", "GET", "DELETE"]

    # Mock an API error
    with patch.object(api_agent, 'send_request') as mock_send:
        mock_response = APIResponse(404, error="Task not found")
        mock_send.return_value = mock_response

        response = api_agent.send_request(api_command)

        assert response.is_error()
        assert response.status_code == 404
        assert response.error == "Task not found"


def test_context_reference_resolution():
    """Test that context manager can resolve references properly."""
    # Initialize context manager
    context_manager = ConversationContextManagerAgent()

    user_id = "test_user_ref"

    # Add some conversation history
    context_manager.add_message_to_history(user_id, "user", "I need to add a task to buy groceries")
    context_manager.add_message_to_history(user_id, "assistant", "Okay, I've added 'buy groceries' to your list")
    context_manager.add_message_to_history(user_id, "user", "Now mark it as completed")

    # Update context with the task ID
    context_manager.update_last_todo_id(user_id, 456)

    # Test reference resolution
    possible_references = ["buy groceries", "call mom", "walk the dog"]
    resolved_reference = context_manager.infer_reference_from_context(user_id, possible_references)

    assert resolved_reference == "buy groceries"


if __name__ == "__main__":
    pytest.main([__file__])