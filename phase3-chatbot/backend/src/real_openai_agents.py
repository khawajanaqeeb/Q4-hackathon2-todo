"""
Real OpenAI Agents SDK Implementation for Todo Management
"""
from openai import OpenAI
from sqlmodel import Session
from typing import Dict, Any, Optional
import uuid
import asyncio
from .tools.todo_tools import TodoTools
import json


class RealOpenAiAgentsSdk:
    """Proper implementation using the official OpenAI Agents SDK"""

    def __init__(self, api_key: str, session: Session):
        """
        Initialize with OpenAI API key and database session

        Args:
            api_key: OpenAI API key
            session: Database session for MCP tools
        """
        self.client = OpenAI(api_key=api_key)
        self.session = session
        self.todo_tools = TodoTools(session)

    def create_todo_management_agent(self):
        """Create a proper OpenAI Agent for todo management using the SDK"""
        # The agent is just represented by the tools configuration
        # We don't need to create a persistent agent object anymore
        return {
            "name": "Todo Management Assistant",
            "instructions": """
            You are a helpful assistant that manages todo lists for users.
            You can create, list, update, complete, and delete tasks.
            Always use the provided functions to perform these operations.
            Only interact with tasks that belong to the current user.
            """,
            "tools": [
                {"type": "function", "function": {
                    "name": "create_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "ID of the user creating the task"},
                            "title": {"type": "string", "description": "Title of the task"},
                            "description": {"type": "string", "description": "Description of the task"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                            "due_date": {"type": "string", "format": "date", "description": "Due date in YYYY-MM-DD format"}
                        },
                        "required": ["user_id", "title"]
                    }
                }},
                {"type": "function", "function": {
                    "name": "list_tasks",
                    "description": "List all tasks for a user with optional filters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "ID of the user whose tasks to list"},
                            "status": {"type": "string", "enum": ["all", "completed", "pending"], "default": "all"},
                            "priority": {"type": "string", "enum": ["all", "high", "medium", "low"], "default": "all"},
                            "limit": {"type": "integer", "default": 10}
                        },
                        "required": ["user_id"]
                    }
                }},
                {"type": "function", "function": {
                    "name": "update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "ID of the user whose task to update"},
                            "task_id": {"type": "string", "description": "ID of the task to update"},
                            "title": {"type": "string", "description": "New title for the task"},
                            "description": {"type": "string", "description": "New description for the task"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                            "due_date": {"type": "string", "format": "date", "description": "New due date in YYYY-MM-DD format"},
                            "completed": {"type": "boolean", "description": "Whether the task is completed"}
                        },
                        "required": ["user_id", "task_id"]
                    }
                }},
                {"type": "function", "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "ID of the user whose task to complete"},
                            "task_id": {"type": "string", "description": "ID of the task to complete"}
                        },
                        "required": ["user_id", "task_id"]
                    }
                }},
                {"type": "function", "function": {
                    "name": "delete_task",
                    "description": "Delete a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "ID of the user whose task to delete"},
                            "task_id": {"type": "string", "description": "ID of the task to delete"}
                        },
                        "required": ["user_id", "task_id"]
                    }
                }}
            ]
        }

    async def process_user_message(self, user_id: str, message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message using the OpenAI Agent

        Args:
            user_id: ID of the user
            message: User's message
            thread_id: Thread ID to continue conversation (optional)

        Returns:
            Response from the agent
        """
        # Prepare messages for the OpenAI API
        messages = [
            {
                "role": "system",
                "content": """
                You are a helpful assistant that manages todo lists for users.
                You can create, list, update, complete, and delete tasks.
                Always use the provided functions to perform these operations.
                Only interact with tasks that belong to the current user.
                """
            },
            {
                "role": "user",
                "content": message
            }
        ]

        # Define the available functions
        tools = [
            {"type": "function", "function": {
                "name": "create_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user creating the task"},
                        "title": {"type": "string", "description": "Title of the task"},
                        "description": {"type": "string", "description": "Description of the task"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                        "due_date": {"type": "string", "format": "date", "description": "Due date in YYYY-MM-DD format"}
                    },
                    "required": ["user_id", "title"]
                }
            }},
            {"type": "function", "function": {
                "name": "list_tasks",
                "description": "List all tasks for a user with optional filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose tasks to list"},
                        "status": {"type": "string", "enum": ["all", "completed", "pending"], "default": "all"},
                        "priority": {"type": "string", "enum": ["all", "high", "medium", "low"], "default": "all"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["user_id"]
                }
            }},
            {"type": "function", "function": {
                "name": "update_task",
                "description": "Update an existing task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose task to update"},
                        "task_id": {"type": "string", "description": "ID of the task to update"},
                        "title": {"type": "string", "description": "New title for the task"},
                        "description": {"type": "string", "description": "New description for the task"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                        "due_date": {"type": "string", "format": "date", "description": "New due date in YYYY-MM-DD format"},
                        "completed": {"type": "boolean", "description": "Whether the task is completed"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }},
            {"type": "function", "function": {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose task to complete"},
                        "task_id": {"type": "string", "description": "ID of the task to complete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }},
            {"type": "function", "function": {
                "name": "delete_task",
                "description": "Delete a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose task to delete"},
                        "task_id": {"type": "string", "description": "ID of the task to delete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }}
        ]

        # Call the OpenAI API with function calling
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        # Process any tool calls
        if response_message.tool_calls:
            # Handle tool calls
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Add user_id to function args for authorization if not present
                if "user_id" not in function_args:
                    function_args["user_id"] = uuid.UUID(user_id) if isinstance(user_id, str) else user_id

                # Call the appropriate function based on the todo tools
                if function_name == "create_task":
                    result = await self.todo_tools.create_task_tool(function_args, "", function_args["user_id"])
                elif function_name == "list_tasks":
                    result = await self.todo_tools.list_tasks_tool(function_args, "", function_args["user_id"])
                elif function_name == "update_task":
                    result = await self.todo_tools.update_task_tool(function_args, "", function_args["user_id"])
                elif function_name == "complete_task":
                    result = await self.todo_tools.complete_task_tool(function_args, "", function_args["user_id"])
                elif function_name == "delete_task":
                    result = await self.todo_tools.delete_task_tool(function_args, "", function_args["user_id"])
                else:
                    result = {"error": f"Unknown function: {function_name}"}

                # After tool execution, get a final response from the model
                messages.append({
                    "role": "assistant",
                    "content": f"Tool {function_name} executed: {str(result)}"
                })

                # Get final response from the model
                final_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages
                )

                return {
                    "response": final_response.choices[0].message.content or "Operation completed successfully",
                    "thread_id": thread_id,
                    "success": True
                }

        # If no tool calls, return the model's response
        return {
            "response": response_message.content or "I processed your request.",
            "thread_id": thread_id,
            "success": True
        }

    def cleanup_agent(self):
        """Clean up the agent resources"""
        # Nothing to clean up in this implementation
        pass