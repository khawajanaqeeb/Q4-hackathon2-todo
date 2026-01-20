"""List Tasks Agent for the Phase 3 Todo AI Chatbot using native OpenAI API."""
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


class ListTasksAgentConfig(BaseModel):
    """Configuration for the List Tasks Agent."""
    model: str = "gpt-4o-mini"  # Using native OpenAI model
    temperature: float = 0.1
    max_tokens: int = 1000


class ListTasksAgent:
    """List Tasks Agent that retrieves and displays user's todo items."""

    def __init__(self, config: Optional[ListTasksAgentConfig] = None):
        self.config = config or ListTasksAgentConfig()

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
            "You are the List Tasks Agent.\n"
            "Your only job is to show the user's current tasks.\n"
            "Determine filter from message: all / pending / completed (default: all)\n"
            "Call the list_tasks MCP tool with correct user_id and status.\n"
            "Format a natural, readable list in the response.\n"
            "If no tasks: say 'You have no tasks yet. Want to add one?'"
        )

        # Define tool schema for list_tasks only
        self.tool_schemas = [
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Handles listing tasks from the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer", "description": "The ID of the authenticated user"},
                            "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter by task status"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "all"], "description": "Filter by priority"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                            "limit": {"type": "integer", "description": "Maximum number of tasks to return"}
                        },
                        "required": ["user_id"]
                    }
                }
            }
        ]

    async def run(self, user_message: str, user_id: int, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Run the list tasks agent with user message and user_id using real Google Gemini API.

        Args:
            user_message: The user's message requesting to list tasks
            user_id: The authenticated user's ID
            history: Previous conversation history

        Returns:
            Dictionary containing the agent's response and tool call results
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

        # Set up run configuration for the agent
        config = RunConfig(
            model=self.model,
            model_provider=self.external_client,
            tracing_disabled=True  # optional, keeps things simple
        )

        # Run the agent using the configured model
        try:
            # Make a direct call to the Gemini-compatible endpoint
            response = self.external_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=self.tool_schemas,
                tool_choice="required",  # Force the model to use the tool
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            # Extract the response
            choice = response.choices[0]
            message = choice.message

            # Check if the tool was called
            if message.tool_calls:
                # Process the tool call
                tool_call = message.tool_calls[0]

                # Parse the tool arguments and ensure user_id is correct
                import json
                arguments = json.loads(tool_call.function.arguments)
                # Override user_id to ensure security - user can't override this
                arguments["user_id"] = user_id

                # Determine status from user message if not provided
                if "status" not in arguments:
                    user_msg_lower = user_message.lower()
                    if "pending" in user_msg_lower or "incomplete" in user_msg_lower or "not done" in user_msg_lower:
                        arguments["status"] = "pending"
                    elif "completed" in user_msg_lower or "done" in user_msg_lower or "finished" in user_msg_lower:
                        arguments["status"] = "completed"
                    else:
                        arguments["status"] = "all"

                # Call the list_tasks function (in a real system, this would be the MCP tool)
                # For now, we'll simulate the tool call result
                # In a real implementation, this would connect to the MCP server
                tool_result = {
                    "success": True,
                    "tasks": [],  # This would be populated with actual tasks
                    "total_count": 0
                }

                # Create a follow-up request to get the final response
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call.id,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": json.dumps(arguments)
                        },
                        "type": "function"
                    }]
                })

                messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_result),
                    "tool_call_id": tool_call.id
                })

                # Get the final response from the model incorporating the tool result
                final_response = self.external_client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )

                final_content = final_response.choices[0].message.content

                # Format response based on whether tasks were found
                if tool_result.get("total_count", 0) == 0:
                    response_text = "You have no tasks yet. Want to add one?"
                else:
                    response_text = final_content or f"I found {tool_result.get('total_count', 0)} tasks for you."

                return {
                    "response": response_text,
                    "tool_call": {
                        "name": tool_call.function.name,
                        "arguments": arguments,
                        "result": tool_result
                    },
                    "original_response": final_content or response_text,
                    "success": True
                }
            else:
                # If no tool call was made, return a default response
                content = message.content or "You have no tasks yet. Want to add one?"
                return {
                    "response": content,
                    "tool_call": None,
                    "original_response": content,
                    "success": True
                }

        except Exception as e:
            raise e


# Global instance of the list tasks agent
list_tasks_agent = ListTasksAgent()