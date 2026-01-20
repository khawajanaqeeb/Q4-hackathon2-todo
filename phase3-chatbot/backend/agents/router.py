"""Router Agent for the Phase 3 Todo AI Chatbot."""

import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import os

# Try importing OpenAI SDK
try:
    from openai import OpenAI
except ImportError:
    # Fallback for alternative import structure
    print("OpenAI SDK not found. Please install: pip install openai")
    # Define a mock client for development
    class MockClient:
        def __init__(self, api_key=None):
            pass

        def chat(self):
            return self

        def completions(self):
            return self

        def create(self, *args, **kwargs):
            # Mock response for development
            class MockResponse:
                def __init__(self):
                    class Choice:
                        def __init__(self):
                            class Message:
                                def __init__(self):
                                    self.content = "Mock response for development"
                                    self.tool_calls = None
                            self.message = Message()

                    self.choices = [Choice()]
                    self.usage = None

            return MockResponse()

    OpenAI = MockClient

from .base import load_conversation_history, extract_user_id_from_jwt, format_messages_for_openai


class RouterAgentConfig(BaseModel):
    """Configuration for the Router Agent."""
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 1000


class RouterAgent:
    """Router Agent that analyzes user intent and routes to appropriate agents."""

    def __init__(self, config: Optional[RouterAgentConfig] = None):
        self.config = config or RouterAgentConfig()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define the system prompt as specified
        self.system_prompt = (
            "You are the Router Agent for a simple todo list chatbot.\n"
            "Your ONLY job is to quickly analyze the user's latest message + conversation history,\n"
            "understand the main intent, and decide what to do next.\n"
            "\n"
            "Possible actions:\n"
            "- ADD / CREATE / REMEMBER a new task → handoff to 'add_task_agent'\n"
            "- LIST / SHOW / VIEW tasks (all, pending, completed) → handoff to 'list_tasks_agent'\n"
            "- COMPLETE / MARK DONE / FINISH a task → handoff to 'complete_task_agent'\n"
            "- DELETE / REMOVE a task → handoff to 'delete_task_agent'\n"
            "- UPDATE / CHANGE / EDIT a task → handoff to 'update_task_agent'\n"
            "- Greeting, thanks, question about the bot, or unclear → respond directly, no handoff\n"
            "\n"
            "Rules:\n"
            "- Be concise and fast.\n"
            "- Always respond in natural, helpful tone.\n"
            "- If handing off, say: 'Got it! Handling that for you...' before handoff.\n"
            "- If unclear, ask politely for clarification.\n"
            "- Never perform any CRUD yourself — only route."
        )

        # Placeholder tool schemas for future MCP tools
        self.tool_schemas = [
            {
                "type": "function",
                "function": {
                    "name": "add_task_agent",
                    "description": "Handles adding new tasks to the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The task title"},
                            "description": {"type": "string", "description": "Detailed description of the task"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority level"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the task"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks_agent",
                    "description": "Handles listing tasks from the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter by task status"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Filter by priority"},
                            "limit": {"type": "integer", "description": "Maximum number of tasks to return"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task_agent",
                    "description": "Handles marking tasks as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "ID of the task to complete"},
                            "task_title": {"type": "string", "description": "Title of the task to complete (alternative to ID)"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task_agent",
                    "description": "Handles deleting tasks from the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "ID of the task to delete"},
                            "task_title": {"type": "string", "description": "Title of the task to delete (alternative to ID)"}
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task_agent",
                    "description": "Handles updating tasks in the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "ID of the task to update"},
                            "title": {"type": "string", "description": "New title for the task"},
                            "description": {"type": "string", "description": "New description for the task"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority for the task"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags for the task"},
                            "completed": {"type": "boolean", "description": "Whether the task is completed"}
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    async def run(self, user_message: str, user_id: int, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Run the router agent with user message and conversation history.

        Args:
            user_message: The user's message
            user_id: The authenticated user's ID
            history: Previous conversation history

        Returns:
            Dictionary containing the agent's response and routing decision
        """
        if history is None:
            history = []

        # Format messages for OpenAI
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # Add conversation history
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add the new user message
        messages.append({"role": "user", "content": user_message})

        try:
            # Call OpenAI API with tools
            # Check if we're using the mock client
            if isinstance(self.client, MockClient):
                # Return a mock response for development
                return {
                    "response": "Router Agent mock response: Got it! I'm ready to help with your todo list.",
                    "routing_decision": None,
                    "handoff": False,
                    "original_response": "Router Agent mock response: Got it! I'm ready to help with your todo list."
                }
            else:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    tools=self.tool_schemas,
                    tool_choice="auto",
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )

                # Extract the response
                choice = response.choices[0]
                message = choice.message

                # Check if a tool was called
                if message.tool_calls:
                    # This is a handoff to another agent
                    tool_call = message.tool_calls[0]
                    agent_name = tool_call.function.name

                    return {
                        "response": f"Got it! Handling that for you...",
                        "routing_decision": agent_name,
                        "tool_arguments": tool_call.function.arguments,
                        "handoff": True,
                        "original_response": message.content or ""
                    }
                else:
                    # This is a direct response
                    return {
                        "response": message.content or "I'm here to help with your todo list!",
                        "routing_decision": None,
                        "handoff": False,
                        "original_response": message.content or ""
                    }

        except Exception as e:
            # Handle any errors gracefully
            return {
                "response": f"I encountered an issue: {str(e)}. Could you please rephrase?",
                "routing_decision": None,
                "handoff": False,
                "error": str(e)
            }


# Global instance of the router agent
router_agent = RouterAgent()