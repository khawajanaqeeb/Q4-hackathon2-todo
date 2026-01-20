"""Update Task Agent for the Phase 3 Todo AI Chatbot using native OpenAI API."""
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


class UpdateTaskAgentConfig(BaseModel):
    """Configuration for the Update Task Agent."""
    model: str = "gpt-4o-mini"  # Using native OpenAI model
    temperature: float = 0.1
    max_tokens: int = 1000


class UpdateTaskAgent:
    """Update Task Agent that modifies user's todo items."""

    def __init__(self, config: Optional[UpdateTaskAgentConfig] = None):
        self.config = config or UpdateTaskAgentConfig()

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
            "You are the Update Task Agent.\n"
            "Your only job is to modify an existing task's title or description.\n"
            "Identify task ID from message (e.g. 'change task 3 to ...', 'update #5 title to ...').\n"
            "Extract new title and/or description.\n"
            "If unclear, ask for clarification: 'Can you give the task number? Or say \"show my tasks\" first.'\n"
            "Call the update_task MCP tool with user_id, task_id, and changes.\n"
            "Respond naturally, e.g. 'Updated task 3: new title ...'\n"
            "Be polite and helpful in all interactions."
        )

        # Define tool schema for update_task only
        self.tool_schemas = [
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Handles updating tasks in the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer", "description": "The ID of the authenticated user"},
                            "task_id": {"type": "integer", "description": "ID of the task to update"},
                            "title": {"type": "string", "description": "New title for the task"},
                            "description": {"type": "string", "description": "New description for the task"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority for the task"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags for the task"},
                            "completed": {"type": "boolean", "description": "Whether the task is completed"}
                        },
                        "required": ["user_id", "task_id"]
                    }
                }
            }
        ]

    async def run(self, user_message: str, user_id: int, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Run the update task agent with user message and user_id using real Google Gemini API.

        Args:
            user_message: The user's message requesting to update a task
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

        # Run the agent using the configured model
        try:
            # Make a direct call to the OpenAI API
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

                # Extract task_id from the user message if not provided
                if "task_id" not in arguments or arguments["task_id"] is None:
                    # Try to extract task ID from user message
                    import re
                    # Look for patterns like "#123", "task 123", "number 123", etc.
                    task_id_match = re.search(r'(?:#|task |number |item )(\d+)', user_message.lower())
                    if task_id_match:
                        arguments["task_id"] = int(task_id_match.group(1))

                # If task_id is still missing, ask for clarification
                if "task_id" not in arguments or arguments["task_id"] is None:
                    return {
                        "response": "Could you please specify which task you want to update? Please provide the task number.",
                        "tool_call": None,
                        "original_response": "Could you please specify which task you want to update? Please provide the task number.",
                        "success": False
                    }

                # Call the update_task function (in a real system, this would be the MCP tool)
                # For now, we'll simulate the tool call result
                # In a real implementation, this would connect to the MCP server
                tool_result = {
                    "success": True,
                    "task_id": arguments["task_id"],
                    "message": f"Task {arguments['task_id']} updated successfully"
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

                # Format response based on the result
                if tool_result.get("success"):
                    # Extract the changes that were made
                    changes = []
                    if "title" in arguments:
                        changes.append(f"title to '{arguments['title']}'")
                    if "description" in arguments:
                        changes.append(f"description to '{arguments['description']}'")
                    if "priority" in arguments:
                        changes.append(f"priority to '{arguments['priority']}'")

                    changes_str = ", ".join(changes) if changes else "properties"
                    response_text = final_content or f"Updated task {arguments['task_id']}: {changes_str}"
                else:
                    response_text = final_content or f"Sorry, I couldn't update task {arguments.get('task_id')}."

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
                content = message.content or "Could you please specify which task you want to update? Please provide the task number and what changes to make."
                return {
                    "response": content,
                    "tool_call": None,
                    "original_response": content,
                    "success": True
                }

        except Exception as e:
            raise e


# Global instance of the update task agent
update_task_agent = UpdateTaskAgent()