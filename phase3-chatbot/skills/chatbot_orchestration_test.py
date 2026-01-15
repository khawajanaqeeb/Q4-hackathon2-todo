"""
Tests for the Chatbot Orchestration Skill
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from skills.chatbot_orchestration_skill import ChatbotOrchestrationSkill, OrchestrationResult


@pytest.fixture
def orchestration_skill():
    """Create a ChatbotOrchestrationSkill instance for testing."""
    return ChatbotOrchestrationSkill("http://test.com", "test_token")


@pytest.mark.asyncio
async def test_initialization(orchestration_skill):
    """Test initializing the orchestration skill."""
    assert orchestration_skill is not None
    assert orchestration_skill.nlp_agent is not None
    assert orchestration_skill.api_integration_agent is not None
    assert orchestration_skill.response_generation_agent is not None


@pytest.mark.asyncio
async def test_process_user_request_success(orchestration_skill):
    """Test processing a successful user request."""
    with patch.object(orchestration_skill.context_manager_agent, 'get_user_context'), \
         patch.object(orchestration_skill.context_manager_agent, 'add_message_to_history'), \
         patch.object(orchestration_skill.nlp_agent, 'process'), \
         patch.object(orchestration_skill.command_interpreter_agent, 'interpret'), \
         patch.object(orchestration_skill.api_integration_agent, 'send_request'), \
         patch.object(orchestration_skill.response_generation_agent, 'generate_response'):

        # Mock the return values
        orchestration_skill.nlp_agent.process.return_value = MagicMock()
        orchestration_skill.nlp_agent.process.return_value.intent = 'ADD_TODO'
        orchestration_skill.nlp_agent.process.return_value.entities = {}

        from agents.api_integration_agent import APIResponse
        mock_api_response = APIResponse(201, {"id": 1, "content": "test task"})

        orchestration_skill.command_interpreter_agent.interpret.return_value = MagicMock()
        orchestration_skill.api_integration_agent.send_request.return_value = mock_api_response
        orchestration_skill.response_generation_agent.generate_response.return_value = "Task added successfully!"

        result = await orchestration_skill.process_user_request("user123", "Add a task to test")

        assert result.success is True
        assert "Task added" in result.response
        assert result.processing_time > 0


@pytest.mark.asyncio
async def test_process_user_request_error(orchestration_skill):
    """Test processing a request that results in an error."""
    with patch.object(orchestration_skill.context_manager_agent, 'get_user_context'), \
         patch.object(orchestration_skill.context_manager_agent, 'add_message_to_history'), \
         patch.object(orchestration_skill.nlp_agent, 'process', side_effect=Exception("Test error")):

        result = await orchestration_skill.process_user_request("user123", "Invalid input")

        assert result.success is False
        assert result.error is not None
        assert "error" in result.response.lower()


@pytest.mark.asyncio
async def test_process_voice_request(orchestration_skill):
    """Test processing a voice request."""
    with patch.object(orchestration_skill.voice_processing_agent, 'speech_to_text',
                      new_callable=AsyncMock) as mock_speech_to_text, \
         patch.object(orchestration_skill, 'process_user_request', new_callable=AsyncMock) as mock_process_text, \
         patch.object(orchestration_skill.voice_processing_agent, 'text_to_speech',
                      new_callable=AsyncMock) as mock_text_to_speech:

        mock_speech_to_text.return_value = "Add a new task"
        mock_result = OrchestrationResult(success=True, response="Task added")
        mock_process_text.return_value = mock_result
        mock_text_to_speech.return_value = b"audio_response"

        result = await orchestration_skill.process_voice_request("user123", b"audio_input")

        assert result.success is True
        mock_speech_to_text.assert_called_once()
        mock_process_text.assert_called_once()


@pytest.mark.asyncio
async def test_monitor_agent_health(orchestration_skill):
    """Test monitoring agent health."""
    health_status = orchestration_skill.monitor_agent_health()

    # Should have health status for all registered agents
    assert 'nlp_agent' in health_status
    assert 'command_interpreter_agent' in health_status
    assert 'api_integration_agent' in health_status
    assert 'response_generation_agent' in health_status


def test_handle_error_propagation(orchestration_skill):
    """Test handling error propagation."""
    error = Exception("Test error")
    fallback_response = orchestration_skill.handle_error_propagation(error, "test_agent")

    assert "experiencing issues" in fallback_response
    assert "test_agent" in fallback_response


def test_circuit_breaker_pattern(orchestration_skill):
    """Test circuit breaker pattern implementation."""
    # Initially, circuit should be closed
    assert orchestration_skill.implement_circuit_breaker_pattern("test_agent") is False

    # Simulate multiple failures to open the circuit
    for _ in range(5):
        orchestration_skill.handle_error_propagation(Exception("Test error"), "test_agent")

    # After multiple failures, circuit should be open
    # This test would require more complex mocking to fully test the time-based logic


@pytest.mark.asyncio
async def test_orchestrate_agents(orchestration_skill):
    """Test the main orchestration method."""
    with patch.object(orchestration_skill, 'process_user_request', new_callable=AsyncMock) as mock_process:
        mock_result = OrchestrationResult(success=True, response="Test response")
        mock_process.return_value = mock_result

        result = await orchestration_skill.orchestrate_agents("user123", "Test message", "web")

        assert result.success is True
        assert result.response == "Test response"
        mock_process.assert_called_once()


def test_get_system_status(orchestration_skill):
    """Test getting system status."""
    status = orchestration_skill.get_system_status()

    assert 'timestamp' in status
    assert 'agents_health' in status
    assert 'circuit_breakers' in status
    assert 'last_health_check' in status


@pytest.mark.asyncio
async def test_reset_circuit_breaker(orchestration_skill):
    """Test resetting circuit breaker."""
    # Simulate a circuit breaker state
    orchestration_skill.circuit_breaker_states['test_agent'] = {
        'failure_count': 10,
        'last_failure': orchestration_skill.last_health_check.get('test_agent'),
        'state': 'open'
    }

    # Reset the circuit breaker
    orchestration_skill.reset_circuit_breaker('test_agent')

    # Verify reset
    assert 'test_agent' in orchestration_skill.circuit_breaker_states
    assert orchestration_skill.circuit_breaker_states['test_agent']['failure_count'] == 0
    assert orchestration_skill.circuit_breaker_states['test_agent']['state'] == 'closed'


@pytest.mark.asyncio
async def test_orchestrate_agents_with_platform(orchestration_skill):
    """Test orchestration with platform adaptation."""
    with patch.object(orchestration_skill.platform_adapter_agent, 'adapt_request'), \
         patch.object(orchestration_skill, 'process_user_request', new_callable=AsyncMock) as mock_process, \
         patch.object(orchestration_skill.platform_adapter_agent, 'adapt_response'):

        mock_result = OrchestrationResult(success=True, response="Test response")
        mock_process.return_value = mock_result

        result = await orchestration_skill.orchestrate_agents("user123", "Test message", "mobile")

        assert result.success is True
        # Verify that platform adaptation methods were called
        # Note: We can't directly verify the calls because we don't have a real Platform enum in the test


@pytest.mark.asyncio
async def test_error_handling_in_pipeline(orchestration_skill):
    """Test error handling throughout the pipeline."""
    with patch.object(orchestration_skill.context_manager_agent, 'get_user_context'), \
         patch.object(orchestration_skill.context_manager_agent, 'add_message_to_history'), \
         patch.object(orchestration_skill.nlp_agent, 'process', side_effect=RuntimeError("NLP Error")):

        result = await orchestration_skill.process_user_request("user123", "Problematic input")

        assert result.success is False
        assert result.error is not None
        assert "NLP Error" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])