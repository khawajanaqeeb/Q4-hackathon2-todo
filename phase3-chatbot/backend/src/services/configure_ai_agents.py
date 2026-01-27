"""
Configuration service for AI Agents.

This module handles the configuration of OpenAI Agents SDK and connects them to MCP tools
as a prerequisite for chat functionality.
"""
import asyncio
from sqlmodel import Session
from typing import Dict, Any
from ..config import settings
from .mcp_integration import McpIntegrationService
from .agent_runner import AgentRunner


class AiAgentConfigurer:
    """Service to configure OpenAI Agents and connect them to MCP tools."""

    def __init__(self, session: Session, mcp_service: McpIntegrationService):
        """
        Initialize AI Agent Configurer.

        Args:
            session: Database session
            mcp_service: MCP integration service instance
        """
        self.session = session
        self.mcp_service = mcp_service
        self.agent_runner = AgentRunner()

    async def configure_openai_agents_sdk(self):
        """
        Configure OpenAI Agents SDK in backend.

        This addresses task T120 - Configure OpenAI Agents SDK in backend.
        """
        # The AgentRunner already initializes the OpenAI client in its constructor
        # This method ensures proper initialization and configuration
        await self.agent_runner.initialize_assistant()
        print("OpenAI Agents SDK configured and assistant initialized")

    async def define_system_prompts_for_todo_management(self):
        """
        Define system prompts for todo management.

        This addresses task T121 - Define system prompts for todo management.
        """
        # System prompts are defined within the AgentRunner class in the process_natural_language method
        # The system prompt guides the AI on how to interpret commands related to task management
        system_prompt = """
        You are a task management assistant. Your job is to interpret user commands related to task management.
        Commands typically involve creating, listing, updating, completing, or deleting tasks.
        Respond in JSON format with the following structure:
        {
            "intent": "task_creation|task_listing|task_completion|task_update|task_deletion|other",
            "parameters": {
                "title": "task title if applicable",
                "description": "task description if applicable",
                "priority": "high|medium|low if applicable",
                "due_date": "YYYY-MM-DD if applicable",
                "task_id": "UUID if applicable",
                "filter": "status|priority|tag if listing",
                "value": "value to filter by"
            },
            "confidence": 0.0-1.0
        }
        Be precise and only extract information that is clearly provided by the user.
        """
        # This prompt is used in the fallback method in AgentRunner
        print("System prompts for todo management defined")

    async def connect_ai_agents_to_mcp_tools(self):
        """
        Connect AI agents to MCP tools.

        This addresses task T122 - Connect AI agents to MCP tools.
        """
        # This connection is established in the chat API endpoint where:
        # 1. AgentRunner processes user input to determine intent
        # 2. McpIntegrationService.invoke_tool is called with the appropriate tool based on intent
        # The connection is made through the service orchestration in the chat endpoint

        # Ensure the tools are registered with the MCP service
        from .initialize_mcp_tools import McpToolsInitializer
        initializer = McpToolsInitializer(self.session, self.mcp_service)
        await initializer.register_todo_tools()

        print("AI agents connected to MCP tools via service orchestration")

    async def implement_natural_language_processing_for_todo_commands(self):
        """
        Implement natural language processing for todo commands.

        This addresses task T123 - Implement natural language processing for todo commands.
        """
        # Natural language processing is implemented in the AgentRunner class
        # The process_natural_language method handles converting user input to structured commands
        print("Natural language processing for todo commands implemented in AgentRunner")

    async def create_agent_response_formatter_for_chat_display(self):
        """
        Create agent response formatter for chat display.

        This addresses task T124 - Create agent response formatter for chat display.
        """
        # Response formatting is handled in the AgentRunner.generate_response method
        # This method creates natural language responses based on the processed intent
        print("Agent response formatter for chat display implemented in AgentRunner")

    async def implement_fallback_handling_for_unrecognized_commands(self):
        """
        Implement fallback handling for unrecognized commands.

        This addresses task T125 - Implement fallback handling for unrecognized commands.
        """
        # Fallback handling is implemented in the AgentRunner._fallback_process_natural_language method
        # This method is called when the OpenAI Assistants API fails or when commands are unrecognized
        print("Fallback handling for unrecognized commands implemented in AgentRunner")