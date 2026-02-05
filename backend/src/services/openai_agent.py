"""OpenAI Agent configuration for the Phase 3 chatbot system."""
from typing import Dict, Any, List, Optional
from openai import OpenAI
from sqlmodel import Session
import os
from ..tools.todo_tools import TodoTools
from ..models.user import User


class OpenAIAgent:
    """OpenAI Agent configuration for handling chatbot conversations."""

    def __init__(self, db_session: Session, current_user: User):
        """
        Initialize the OpenAI Agent with necessary dependencies.

        Args:
            db_session: Database session for data access
            current_user: Currently authenticated user
        """
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)

        # Store dependencies
        self.db_session = db_session
        self.current_user = current_user

        # Initialize tools
        self.todo_tools = TodoTools(db_session, current_user)

        # Create the agent
        self.agent = self._create_agent()

    def _create_agent(self):
        """
        Create the OpenAI Assistant agent with the appropriate configuration.

        Returns:
            OpenAI Assistant object
        """
        # Create an assistant with the todo tools
        assistant = self.client.beta.assistants.create(
            name="Todo Assistant",
            description="An AI assistant that helps users manage their todos through natural language",
            model="gpt-4-turbo-preview",  # Using a capable model for tool use
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "create_todo",
                        "description": "Create a new todo item for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Title of the new todo item"},
                                "description": {"type": "string", "description": "Optional description of the todo"},
                                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority level, defaults to 'medium'"},
                                "due_date": {"type": "string", "description": "Optional due date in YYYY-MM-DD format"}
                            },
                            "required": ["title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_todos",
                        "description": "Retrieve the user's todo items with optional filters",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string", "enum": ["active", "completed", "all"], "description": "Filter by status, defaults to 'active'"},
                                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Filter by priority"},
                                "limit": {"type": "integer", "description": "Maximum number of todos to return"},
                                "offset": {"type": "integer", "description": "Offset for pagination"}
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_todo",
                        "description": "Update an existing todo item",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "todo_id": {"type": "string", "description": "ID of the todo to update"},
                                "title": {"type": "string", "description": "New title for the todo"},
                                "description": {"type": "string", "description": "New description for the todo"},
                                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority for the todo"},
                                "status": {"type": "string", "enum": ["active", "completed"], "description": "New status for the todo"},
                                "due_date": {"type": "string", "description": "New due date in YYYY-MM-DD format"}
                            },
                            "required": ["todo_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_todo",
                        "description": "Delete a specific todo item",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "todo_id": {"type": "string", "description": "ID of the todo to delete"}
                            },
                            "required": ["todo_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_todo",
                        "description": "Mark a specific todo item as complete or incomplete",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "todo_id": {"type": "string", "description": "ID of the todo to update"},
                                "completed": {"type": "boolean", "description": "Whether to mark as completed (true) or active (false)"}
                            },
                            "required": ["todo_id", "completed"]
                        }
                    }
                }
            ]
        )

        return assistant

    def process_message(self, user_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message using the OpenAI Agent.

        Args:
            user_message: The message from the user
            conversation_id: Optional conversation ID for thread continuation

        Returns:
            Dictionary containing the agent's response and any tool call results
        """
        try:
            # Create or retrieve thread
            if conversation_id:
                # In a real implementation, we would retrieve the existing thread
                # For now, we'll create a new thread but associate it with the conversation
                thread = self.client.beta.threads.retrieve(conversation_id)
            else:
                # Create a new thread
                thread = self.client.beta.threads.create()

            # Add user message to the thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )

            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.agent.id
            )

            # Wait for the run to complete
            import time
            while run.status in ["queued", "in_progress"]:
                time.sleep(0.5)
                run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # Handle the result based on run status
            if run.status == "completed":
                # Retrieve the messages from the thread
                messages = self.client.beta.threads.messages.list(thread_id=thread.id, order="asc")

                # Get the latest assistant message
                assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
                if assistant_messages:
                    latest_message = assistant_messages[-1]

                    # Extract content from the message
                    content_blocks = latest_message.content
                    full_response = ""
                    for block in content_blocks:
                        if block.type == "text":
                            full_response += block.text.value

                    return {
                        "conversation_id": thread.id,
                        "response": full_response,
                        "status": "completed"
                    }
                else:
                    return {
                        "conversation_id": thread.id,
                        "response": "I processed your request but didn't generate a response.",
                        "status": "completed_no_response"
                    }

            elif run.status == "requires_action":
                # Handle tool calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = eval(tool_call.function.arguments)

                    # Execute the appropriate tool based on function name
                    if function_name == "create_todo":
                        result = self.todo_tools.create_todo(**function_args)
                    elif function_name == "list_todos":
                        result = self.todo_tools.list_todos(**function_args)
                    elif function_name == "update_todo":
                        result = self.todo_tools.update_todo(**function_args)
                    elif function_name == "delete_todo":
                        result = self.todo_tools.delete_todo(**function_args)
                    elif function_name == "complete_todo":
                        result = self.todo_tools.complete_todo(**function_args)
                    else:
                        result = {"error": f"Unknown function: {function_name}"}

                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": str(result)
                    })

                # Submit tool outputs back to the assistant
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

                # Wait for the run to complete after tool execution
                while run.status in ["queued", "in_progress"]:
                    time.sleep(0.5)
                    run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

                # Get the final response after tool execution
                if run.status == "completed":
                    messages = self.client.beta.threads.messages.list(thread_id=thread.id, order="asc")
                    assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
                    if assistant_messages:
                        latest_message = assistant_messages[-1]

                        content_blocks = latest_message.content
                        full_response = ""
                        for block in content_blocks:
                            if block.type == "text":
                                full_response += block.text.value

                        return {
                            "conversation_id": thread.id,
                            "response": full_response,
                            "status": "completed",
                            "tool_calls_executed": [tc.function.name for tc in tool_calls]
                        }

            # If we reach here, something went wrong
            return {
                "conversation_id": thread.id,
                "response": "I'm sorry, I encountered an issue processing your request.",
                "status": "error",
                "error": f"Unexpected run status: {run.status}"
            }

        except Exception as e:
            return {
                "conversation_id": conversation_id or "unknown",
                "response": "I'm sorry, I encountered an error processing your request.",
                "status": "error",
                "error": str(e)
            }

    def cleanup_thread(self, thread_id: str) -> bool:
        """
        Clean up a thread if needed.

        Args:
            thread_id: ID of the thread to clean up

        Returns:
            True if cleanup was successful, False otherwise
        """
        try:
            # In OpenAI's API, threads can't be deleted directly
            # We just return True to indicate that cleanup is not needed
            # In a real implementation, you might want to archive conversation data
            return True
        except Exception:
            return False

    def __del__(self):
        """
        Cleanup method to ensure proper cleanup of resources.
        """
        # In a real implementation, you might want to clean up resources here
        pass