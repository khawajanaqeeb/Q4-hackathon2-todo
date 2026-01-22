"""Real Router Agent for the Phase 3 Todo AI Chatbot using native OpenAI API."""

import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import native OpenAI client
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from .base import load_conversation_history, extract_user_id_from_jwt, format_messages_for_openai
from .add_task_agent import add_task_agent
from .list_tasks_agent import list_tasks_agent
from .complete_task_agent import complete_task_agent
from .update_task_agent import update_task_agent
from .delete_task_agent import delete_task_agent


class RouterAgentConfig(BaseModel):
    """Configuration for the Router Agent."""
    model: str = "gpt-4o-mini"  # Using native OpenAI model
    temperature: float = 0.1
    max_tokens: int = 1000


class RouterAgent:
    """Real Router Agent that analyzes user intent and routes to appropriate agents."""

    def __init__(self, config: Optional[RouterAgentConfig] = None):
        self.config = config or RouterAgentConfig()

        # Get OpenAI API key from environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is required in .env")

        # Create native OpenAI client
        self.external_client = AsyncOpenAI(
            api_key=openai_api_key,
        )

        # The model will be used directly with the external client
        # OpenAIChatCompletionsModel doesn't exist in the standard OpenAI library
        # We'll use the model name directly in the API calls

        # Define the system prompt as specified
        self.system_prompt = (
            "You are a precise Router Agent for a todo list chatbot.\n"
            "Analyze user message + history.\n"
            "Route only based on clear intent:\n"
            "\n"
            "- add/create/remember/new task → handoff: add_task_agent\n"
            "- list/show/view/tasks (any filter) → handoff: list_tasks_agent\n"
            "- complete/done/finish/mark → handoff: complete_task_agent\n"
            "- delete/remove/cancel → handoff: delete_task_agent\n"
            "- update/change/edit/modify → handoff: update_task_agent\n"
            "- greeting/question/clarification → respond directly\n"
            "\n"
            "Respond naturally. If routing, say briefly: 'Understood, handling your task request...'\n"
            "Never execute any action yourself. Use handoff when appropriate."
        )

        # Define tool schemas for future MCP tools
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
        Run the router agent with user message and conversation history using real OpenAI API.

        Args:
            user_message: The user's message
            user_id: The authenticated user's ID
            history: Previous conversation history

        Returns:
            Dictionary containing the agent's response and routing decision
        """
        if history is None:
            history = []

        # Format messages for the agent
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # Add conversation history
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add the new user message
        messages.append({"role": "user", "content": user_message})

        try:
            # Prepare the agent execution - in a real scenario this would use the actual agent framework
            # For now, we'll make a direct call to the Gemini-compatible endpoint
            response = self.external_client.chat.completions.create(
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

                # If it's the add_task_agent, execute it directly
                if agent_name == "add_task_agent":
                    # Parse the arguments and execute the add_task_agent
                    import json
                    arguments = json.loads(tool_call.function.arguments)

                    # Run the add_task_agent with the parsed arguments
                    # Use the user_id from the current session
                    agent_response = await add_task_agent.run(
                        user_message=user_message,
                        user_id=user_id,
                        history=history
                    )

                    return {
                        "response": agent_response["response"],
                        "routing_decision": agent_name,
                        "tool_arguments": arguments,
                        "handoff": True,
                        "original_response": agent_response["original_response"],
                        "agent_execution_result": agent_response
                    }
                # If it's the list_tasks_agent, execute it directly
                elif agent_name == "list_tasks_agent":
                    # Parse the arguments and execute the list_tasks_agent
                    import json
                    arguments = json.loads(tool_call.function.arguments)

                    # Run the list_tasks_agent with the parsed arguments
                    # Use the user_id from the current session
                    agent_response = await list_tasks_agent.run(
                        user_message=user_message,
                        user_id=user_id,
                        history=history
                    )

                    return {
                        "response": agent_response["response"],
                        "routing_decision": agent_name,
                        "tool_arguments": arguments,
                        "handoff": True,
                        "original_response": agent_response["original_response"],
                        "agent_execution_result": agent_response
                    }
                # If it's the complete_task_agent, execute it directly
                elif agent_name == "complete_task_agent":
                    # Parse the arguments and execute the complete_task_agent
                    import json
                    arguments = json.loads(tool_call.function.arguments)

                    # Run the complete_task_agent with the parsed arguments
                    # Use the user_id from the current session
                    agent_response = await complete_task_agent.run(
                        user_message=user_message,
                        user_id=user_id,
                        history=history
                    )

                    return {
                        "response": agent_response["response"],
                        "routing_decision": agent_name,
                        "tool_arguments": arguments,
                        "handoff": True,
                        "original_response": agent_response["original_response"],
                        "agent_execution_result": agent_response
                    }
                # If it's the update_task_agent, execute it directly
                elif agent_name == "update_task_agent":
                    # Parse the arguments and execute the update_task_agent
                    import json
                    arguments = json.loads(tool_call.function.arguments)

                    # Run the update_task_agent with the parsed arguments
                    # Use the user_id from the current session
                    agent_response = await update_task_agent.run(
                        user_message=user_message,
                        user_id=user_id,
                        history=history
                    )

                    return {
                        "response": agent_response["response"],
                        "routing_decision": agent_name,
                        "tool_arguments": arguments,
                        "handoff": True,
                        "original_response": agent_response["original_response"],
                        "agent_execution_result": agent_response
                    }
                # If it's the delete_task_agent, execute it directly
                elif agent_name == "delete_task_agent":
                    # Parse the arguments and execute the delete_task_agent
                    import json
                    arguments = json.loads(tool_call.function.arguments)

                    # Run the delete_task_agent with the parsed arguments
                    # Use the user_id from the current session
                    agent_response = await delete_task_agent.run(
                        user_message=user_message,
                        user_id=user_id,
                        history=history
                    )

                    return {
                        "response": agent_response["response"],
                        "routing_decision": agent_name,
                        "tool_arguments": arguments,
                        "handoff": True,
                        "original_response": agent_response["original_response"],
                        "agent_execution_result": agent_response
                    }
                else:
                    # For other agents, return handoff information
                    return {
                        "response": f"Understood, handling your task request...",
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
            raise e


# Global instance of the router agent
router_agent = RouterAgent()