"""
Integration Tests for Full System

End-to-end testing of the complete Todo AI Chatbot system.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from skills.chatbot_orchestration_skill import ChatbotOrchestrationSkill
from agents.nlp_agent import NLPAgent
from agents.todo_command_interpreter_agent import TodoCommandInterpreterAgent
from agents.api_integration_agent import APIIntegrationAgent, APIResponse
from agents.response_generation_agent import ResponseGenerationAgent


@pytest.mark.asyncio
async def test_full_end_to_end_workflow():
    """Test complete end-to-end workflow from user input to API response."""
    # Initialize orchestration skill with test credentials
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent to avoid actual API calls
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        # Mock API response for successful todo creation
        mock_api_response = APIResponse(201, {
            "id": 123,
            "content": "buy groceries",
            "priority": "high",
            "completed": False,
            "due_date": "tomorrow"
        })
        mock_api_request.return_value = mock_api_response

        # Process a user request through the full pipeline
        result = await orchestration_skill.orchestrate_agents(
            user_id="test_user_123",
            input_message="Add a new task to buy groceries tomorrow with high priority",
            platform="web"
        )

        # Verify the result
        assert result.success is True
        assert result.response is not None
        assert "buy groceries" in result.response.lower()
        assert result.processing_time > 0
        assert result.agent_responses is not None


@pytest.mark.asyncio
async def test_full_end_to_end_workflow_list_todos():
    """Test complete end-to-end workflow for listing todos."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        # Mock API response for listing todos
        mock_api_response = APIResponse(200, {
            "items": [
                {"id": 1, "content": "buy groceries", "completed": False, "priority": "high"},
                {"id": 2, "content": "walk the dog", "completed": True, "priority": "medium"}
            ]
        })
        mock_api_request.return_value = mock_api_response

        # Process a user request to list todos
        result = await orchestration_skill.orchestrate_agents(
            user_id="test_user_123",
            input_message="Show me my todos",
            platform="web"
        )

        # Verify the result
        assert result.success is True
        assert result.response is not None
        assert "groceries" in result.response.lower() or "dog" in result.response.lower()
        assert "2" in result.response  # Should mention the count


@pytest.mark.asyncio
async def test_full_end_to_end_workflow_error_handling():
    """Test complete end-to-end workflow with error handling."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent to return an error
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        # Mock API error response
        mock_api_response = APIResponse(404, error="Task not found")
        mock_api_request.return_value = mock_api_response

        # Process a user request that will result in an error
        result = await orchestration_skill.orchestrate_agents(
            user_id="test_user_123",
            input_message="Complete the task that doesn't exist",
            platform="web"
        )

        # Verify the result handles the error gracefully
        assert result.success is True  # Operation completed, even if with error
        assert result.response is not None
        # Response should contain error information but in user-friendly format


@pytest.mark.asyncio
async def test_full_end_to_end_workflow_complete_todo():
    """Test complete end-to-end workflow for completing a todo."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        # Mock API response for completing a todo
        mock_api_response = APIResponse(200, {
            "id": 123,
            "content": "buy groceries",
            "completed": True
        })
        mock_api_request.return_value = mock_api_response

        # Process a user request to complete a todo
        result = await orchestration_skill.orchestrate_agents(
            user_id="test_user_123",
            input_message="Mark the buy groceries task as completed",
            platform="web"
        )

        # Verify the result
        assert result.success is True
        assert result.response is not None
        assert "completed" in result.response.lower() or "marked" in result.response.lower()


@pytest.mark.asyncio
async def test_full_end_to_end_workflow_delete_todo():
    """Test complete end-to-end workflow for deleting a todo."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        # Mock API response for deleting a todo (typically returns 204 No Content)
        mock_api_response = APIResponse(204, {})
        mock_api_request.return_value = mock_api_response

        # Process a user request to delete a todo
        result = await orchestration_skill.orchestrate_agents(
            user_id="test_user_123",
            input_message="Delete the task to call mom",
            platform="web"
        )

        # Verify the result
        assert result.success is True
        assert result.response is not None
        assert "delete" in result.response.lower() or "removed" in result.response.lower()


@pytest.mark.asyncio
async def test_context_preservation_across_requests():
    """Test that context is preserved across multiple requests."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    user_id = "context_test_user"

    # First request - add a task
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        mock_api_request.return_value = APIResponse(201, {"id": 456, "content": "call mom", "completed": False})

        result1 = await orchestration_skill.orchestrate_agents(
            user_id=user_id,
            input_message="Add a task to call mom tomorrow",
            platform="web"
        )

        assert result1.success is True
        assert "call mom" in result1.response.lower()

    # Second request - reference the previous task using context
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        mock_api_request.return_value = APIResponse(200, {"id": 456, "content": "call mom", "completed": True})

        result2 = await orchestration_skill.orchestrate_agents(
            user_id=user_id,
            input_message="Mark it as completed",  # "it" should refer to the previous task
            platform="web"
        )

        # Verify the context was used properly
        assert result2.success is True
        assert "completed" in result2.response.lower()


@pytest.mark.asyncio
async def test_multi_platform_adaptation():
    """Test that responses are adapted for different platforms."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request, \
         patch.object(orchestration_skill.platform_adapter_agent, 'adapt_request') as mock_adapt_req, \
         patch.object(orchestration_skill.platform_adapter_agent, 'adapt_response') as mock_adapt_resp:

        mock_api_request.return_value = APIResponse(201, {"id": 789, "content": "test task", "completed": False})
        mock_adapt_req.return_value = {"user_id": "test_user", "message": "test task"}
        mock_adapt_resp.return_value = {"message": "Adapted response for platform"}

        # Test with mobile platform
        result = await orchestration_skill.orchestrate_agents(
            user_id="test_user_123",
            input_message="Add a test task",
            platform="mobile"
        )

        assert result.success is True
        # Verify that platform adaptation methods were called
        mock_adapt_req.assert_called()
        mock_adapt_resp.assert_called()


@pytest.mark.asyncio
async def test_voice_processing_integration():
    """Test voice processing integration in the full pipeline."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the voice processing agent and API integration
    with patch.object(orchestration_skill.voice_processing_agent, 'speech_to_text', new_callable=AsyncMock) as mock_stt, \
         patch.object(orchestration_skill.voice_processing_agent, 'text_to_speech', new_callable=AsyncMock) as mock_tts, \
         patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:

        # Mock voice processing
        mock_stt.return_value = "Add a new task to buy groceries"
        mock_tts.return_value = b"audio_response_bytes"
        mock_api_request.return_value = APIResponse(201, {"id": 101, "content": "buy groceries", "completed": False})

        # Process voice request
        result = await orchestration_skill.process_voice_request("voice_user_456", b"audio_input_bytes")

        assert result.success is True
        # Result response might be audio bytes or adapted text depending on implementation
        assert result.response is not None


@pytest.mark.asyncio
async def test_error_recovery_and_degradation():
    """Test system degradation and recovery when components fail."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent to occasionally fail
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        # First call succeeds
        mock_api_request.return_value = APIResponse(201, {"id": 202, "content": "test task", "completed": False})

        result1 = await orchestration_skill.orchestrate_agents(
            user_id="test_user_789",
            input_message="Add a task that works",
            platform="web"
        )

        assert result1.success is True

        # Simulate API failure
        failing_response = APIResponse(500, error="Server error")
        mock_api_request.return_value = failing_response

        result2 = await orchestration_skill.orchestrate_agents(
            user_id="test_user_789",
            input_message="Add a task that fails",
            platform="web"
        )

        # Even with API failure, the orchestration should handle it gracefully
        assert result2.success is True  # Process completed, even if with error
        assert result2.response is not None


@pytest.mark.asyncio
async def test_performance_under_load():
    """Test system performance with multiple concurrent requests."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    async def make_request(user_id, message):
        with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
            mock_api_request.return_value = APIResponse(201, {"id": user_id, "content": message, "completed": False})
            return await orchestration_skill.orchestrate_agents(user_id, message, "web")

    # Simulate multiple concurrent requests
    tasks = [
        make_request(f"user_{i}", f"Task {i} content")
        for i in range(5)
    ]

    results = await asyncio.gather(*tasks)

    # Verify all requests completed successfully
    for result in results:
        assert result.success is True
        assert result.response is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])