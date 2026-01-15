"""
Chatbot Orchestration Skill

Coordinates the interaction between all Todo AI Chatbot agents, ensuring smooth communication and proper error handling between components.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import logging

from agents.nlp_agent import NLPAgent
from agents.todo_command_interpreter_agent import TodoCommandInterpreterAgent
from agents.conversation_context_manager_agent import ConversationContextManagerAgent
from agents.api_integration_agent import APIIntegrationAgent
from agents.response_generation_agent import ResponseGenerationAgent
from agents.voice_processing_agent import VoiceProcessingAgent
from agents.multi_platform_adapter_agent import MultiPlatformAdapterAgent


class AgentStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class OrchestrationResult:
    """Represents the result of an orchestration operation."""
    success: bool
    response: str
    error: Optional[str] = None
    processing_time: float = 0.0
    agent_responses: Optional[Dict[str, Any]] = None


class ChatbotOrchestrationSkill:
    """
    Coordinates the interaction between all Todo AI Chatbot agents, ensuring smooth communication and proper error handling.
    """

    def __init__(self, api_base_url: str, jwt_token: str):
        # Initialize all agents
        self.nlp_agent = NLPAgent()
        self.command_interpreter_agent = TodoCommandInterpreterAgent()
        self.context_manager_agent = ConversationContextManagerAgent()
        self.api_integration_agent = APIIntegrationAgent(
            base_url=api_base_url,
            jwt_token=jwt_token
        )
        self.response_generation_agent = ResponseGenerationAgent()
        self.voice_processing_agent = VoiceProcessingAgent()
        self.platform_adapter_agent = MultiPlatformAdapterAgent()

        # Agent registry for health monitoring
        self.agent_registry = {
            'nlp_agent': self.nlp_agent,
            'command_interpreter_agent': self.command_interpreter_agent,
            'context_manager_agent': self.context_manager_agent,
            'api_integration_agent': self.api_integration_agent,
            'response_generation_agent': self.response_generation_agent,
            'voice_processing_agent': self.voice_processing_agent,
            'platform_adapter_agent': self.platform_adapter_agent
        }

        # Health check settings
        self.health_check_interval = 30  # seconds
        self.last_health_check = {}
        self.circuit_breaker_states = {}

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    async def process_user_request(self, user_id: str, input_text: str,
                                   platform: Optional[str] = None) -> OrchestrationResult:
        """
        Process a user request through the full agent pipeline.
        """
        start_time = time.time()
        agent_responses = {}

        try:
            self.logger.info(f"Processing request for user {user_id} on platform {platform}")

            # 1. Adapt request for platform if needed
            if platform:
                from agents.multi_platform_adapter_agent import Platform
                platform_enum = getattr(Platform, platform.upper(), Platform.WEB)
                adapted_request = self.platform_adapter_agent.adapt_request(platform_enum, {
                    'user_id': user_id,
                    'message': input_text
                })
                input_text = adapted_request.get('message', input_text)

            # 2. Get user context
            user_context = self.context_manager_agent.get_user_context(user_id)

            # 3. Add user message to history
            self.context_manager_agent.add_message_to_history(user_id, "user", input_text)

            # 4. Process with NLP agent
            nlp_result = self.nlp_agent.process(input_text)
            agent_responses['nlp_agent'] = nlp_result
            self.logger.debug(f"NLP result: intent={nlp_result.intent}, entities={nlp_result.entities}")

            # 5. Interpret with command interpreter
            api_command = self.command_interpreter_agent.interpret(nlp_result)
            agent_responses['command_interpreter_agent'] = api_command
            self.logger.debug(f"API command: {api_command.method} {api_command.endpoint}")

            # 6. Execute API command
            api_response = self.api_integration_agent.send_request(api_command)
            agent_responses['api_integration_agent'] = api_response
            self.logger.debug(f"API response: status={api_response.status_code}")

            # 7. Generate response
            response_data = {
                'status_code': api_response.status_code,
                'data': api_response.data if api_response.is_success() else {},
                'error': api_response.error if api_response.is_error() else None
            }
            generated_response = self.response_generation_agent.generate_response(
                response_data,
                self.context_manager_agent.get_active_context(user_id)
            )
            agent_responses['response_generation_agent'] = generated_response
            self.logger.debug(f"Generated response: {generated_response}")

            # 8. Add response to history
            self.context_manager_agent.add_message_to_history(user_id, "assistant", generated_response)

            # 9. Adapt response for platform if needed
            if platform:
                platform_enum = getattr(Platform, platform.upper(), Platform.WEB)
                adapted_response = self.platform_adapter_agent.adapt_response(platform_enum, {
                    'message': generated_response
                })
                final_response = adapted_response.get('message', generated_response)
            else:
                final_response = generated_response

            processing_time = time.time() - start_time

            return OrchestrationResult(
                success=True,
                response=final_response,
                processing_time=processing_time,
                agent_responses=agent_responses
            )

        except Exception as e:
            self.logger.error(f"Error in orchestration pipeline: {str(e)}", exc_info=True)
            processing_time = time.time() - start_time

            # Generate error response
            error_response = self.response_generation_agent.format_error_response(str(e),
                                                                                  "I'm sorry, but I encountered an error processing your request.")

            return OrchestrationResult(
                success=False,
                response=error_response,
                error=str(e),
                processing_time=processing_time,
                agent_responses=agent_responses
            )

    async def process_voice_request(self, user_id: str, audio_input: bytes) -> OrchestrationResult:
        """
        Process a voice request through the full pipeline.
        """
        start_time = time.time()
        agent_responses = {}

        try:
            self.logger.info(f"Processing voice request for user {user_id}")

            # 1. Convert speech to text
            text_command = await self.voice_processing_agent.speech_to_text(audio_input)
            agent_responses['voice_processing_agent'] = text_command
            self.logger.debug(f"Transcribed text: {text_command}")

            # 2. Continue with text processing pipeline
            result = await self.process_user_request(user_id, text_command)

            # Merge agent responses - handle the case where result.agent_responses might be None
            if result.agent_responses is not None:
                merged_agent_responses = {**result.agent_responses, **agent_responses}
            else:
                merged_agent_responses = agent_responses

            result.processing_time = time.time() - start_time
            result.agent_responses = merged_agent_responses

            # 3. If needed, convert response back to speech
            if result.success:
                audio_response = await self.voice_processing_agent.text_to_speech(result.response)
                result.response = audio_response  # Return audio response instead of text

            return result

        except Exception as e:
            self.logger.error(f"Error in voice orchestration pipeline: {str(e)}", exc_info=True)
            processing_time = time.time() - start_time

            error_response = self.response_generation_agent.format_error_response(
                str(e),
                "I'm sorry, but I encountered an error processing your voice request."
            )

            return OrchestrationResult(
                success=False,
                response=error_response,
                error=str(e),
                processing_time=processing_time,
                agent_responses=agent_responses
            )

    def monitor_agent_health(self) -> Dict[str, AgentStatus]:
        """
        Monitor health of all agents.
        """
        health_status = {}

        for agent_name, agent in self.agent_registry.items():
            try:
                # Simple health check - try to call a basic method
                if hasattr(agent, 'health_check'):
                    status = agent.health_check()
                    health_status[agent_name] = AgentStatus.HEALTHY if status else AgentStatus.UNHEALTHY
                else:
                    # Default healthy status for agents without explicit health check
                    health_status[agent_name] = AgentStatus.HEALTHY

                self.last_health_check[agent_name] = datetime.now()
            except Exception as e:
                self.logger.error(f"Health check failed for {agent_name}: {str(e)}")
                health_status[agent_name] = AgentStatus.UNHEALTHY
                self.last_health_check[agent_name] = datetime.now()

        return health_status

    def handle_error_propagation(self, error: Exception, agent_name: str) -> str:
        """
        Handle error propagation and recovery.
        """
        self.logger.error(f"Error from {agent_name}: {str(error)}")

        # Circuit breaker logic
        if agent_name not in self.circuit_breaker_states:
            self.circuit_breaker_states[agent_name] = {
                'failure_count': 0,
                'last_failure': datetime.now(),
                'state': 'closed'  # closed, open, half_open
            }

        # Increment failure count
        self.circuit_breaker_states[agent_name]['failure_count'] += 1
        self.circuit_breaker_states[agent_name]['last_failure'] = datetime.now()

        # If too many failures, open the circuit
        if self.circuit_breaker_states[agent_name]['failure_count'] >= 5:
            self.circuit_breaker_states[agent_name]['state'] = 'open'
            self.logger.warning(f"Circuit breaker opened for {agent_name}")

        # Return fallback response
        return f"I'm experiencing issues with the {agent_name}. Please try again later."

    def implement_circuit_breaker_pattern(self, agent_name: str) -> bool:
        """
        Implements circuit breaker pattern for agent calls.
        """
        if agent_name not in self.circuit_breaker_states:
            return False  # Circuit is closed, allow call

        state_info = self.circuit_breaker_states[agent_name]

        if state_info['state'] == 'open':
            # Check if enough time has passed to try again (half-open state)
            time_since_failure = datetime.now() - state_info['last_failure']
            if time_since_failure.total_seconds() > 60:  # 1 minute timeout
                state_info['state'] = 'half_open'
                self.logger.info(f"Circuit breaker for {agent_name} transitioning to half-open")
                return False  # Allow one trial call
            else:
                # Still in open state, block the call
                return True

        elif state_info['state'] == 'half_open':
            # If we're in half-open state and there's a failure, go back to open
            # If there's success, close the circuit
            return False  # Allow the trial call to proceed

        return False  # Circuit is closed, allow call

    async def orchestrate_agents(self, user_id: str, input_message: str,
                                 platform: Optional[str] = None) -> OrchestrationResult:
        """
        Main orchestration method that coordinates all agents.
        """
        # Check circuit breakers before proceeding
        for agent_name in self.agent_registry.keys():
            if self.implement_circuit_breaker_pattern(agent_name):
                error_msg = f"Service temporarily unavailable due to issues with {agent_name}"
                return OrchestrationResult(
                    success=False,
                    response=error_msg,
                    error=error_msg,
                    processing_time=0.0
                )

        # Process the request through the pipeline
        return await self.process_user_request(user_id, input_message, platform)

    def reset_circuit_breaker(self, agent_name: str):
        """
        Reset a circuit breaker for a specific agent.
        """
        if agent_name in self.circuit_breaker_states:
            self.circuit_breaker_states[agent_name] = {
                'failure_count': 0,
                'last_failure': datetime.now(),
                'state': 'closed'
            }
            self.logger.info(f"Circuit breaker reset for {agent_name}")

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status.
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'agents_health': self.monitor_agent_health(),
            'circuit_breakers': self.circuit_breaker_states,
            'last_health_check': self.last_health_check
        }


# Example usage
if __name__ == "__main__":
    import asyncio

    # Initialize the orchestration skill
    # Note: In a real implementation, you'd get these from environment/config
    api_url = "http://localhost:8000"
    jwt_token = "your-jwt-token-here"

    orchestration_skill = ChatbotOrchestrationSkill(api_url, jwt_token)

    async def example():
        # Example text request
        result = await orchestration_skill.orchestrate_agents(
            user_id="user123",
            input_message="Add a new task to buy groceries tomorrow",
            platform="web"
        )

        print(f"Success: {result.success}")
        print(f"Response: {result.response}")
        print(f"Processing time: {result.processing_time:.2f}s")

        # Check system status
        status = orchestration_skill.get_system_status()
        print(f"System status: {status}")

    # Run the example
    asyncio.run(example())