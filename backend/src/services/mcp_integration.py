"""MCP server integration service for the Phase 3 chatbot system."""
import asyncio
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from uuid import uuid4
import json
from datetime import datetime

from ..models.user import User
from ..dependencies.auth import get_current_user
from ..database import get_session
from ..tools.todo_tools import TodoTools
from ..services.conversation_service import ConversationService
from ..services.openai_agent import OpenAIAgent


class McpIntegrationService:
    """Service for integrating with the MCP server and managing tool execution."""

    def __init__(self, db_session: Session, current_user: User):
        self.db_session = db_session
        self.current_user = current_user
        self.todo_tools = TodoTools(db_session, current_user)
        self.conversation_service = ConversationService(db_session)
        self.openai_agent = OpenAIAgent(db_session, current_user)

    async def execute_todo_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a todo-related tool via the MCP integration.

        Args:
            tool_name: Name of the tool to execute (e.g., 'create_todo', 'list_todos', etc.)
            parameters: Parameters for the tool execution

        Returns:
            Result of the tool execution
        """
        try:
            if tool_name == "create_todo":
                return self.todo_tools.create_todo(**parameters)
            elif tool_name == "list_todos":
                return self.todo_tools.list_todos(**parameters)
            elif tool_name == "update_todo":
                return self.todo_tools.update_todo(**parameters)
            elif tool_name == "delete_todo":
                return self.todo_tools.delete_todo(**parameters)
            elif tool_name == "complete_todo":
                return self.todo_tools.complete_todo(**parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except Exception as e:
            # Log the error
            print(f"Error executing tool {tool_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error executing tool {tool_name}: {str(e)}"
            )

    def validate_user_access(self, user_id: int) -> bool:
        """
        Validate that the user has access to the resources.

        Args:
            user_id: ID of the user to validate

        Returns:
            True if user has access, False otherwise
        """
        return self.current_user.id == user_id

    async def process_conversation_request(
        self,
        user_input: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a conversation request and return the response.

        Args:
            user_input: Input from the user
            conversation_id: Optional conversation ID, creates new if not provided

        Returns:
            Response to the user input
        """
        # Create or retrieve conversation
        if not conversation_id:
            # Create a new conversation
            title = user_input[:50] if len(user_input) > 50 else user_input
            conversation = self.conversation_service.create_conversation(
                user_id=self.current_user.id,
                title=title
            )
            conversation_id = str(conversation.id)
        else:
            # Retrieve existing conversation
            conversation = self.conversation_service.get_conversation_by_id(conversation_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            if conversation.user_id != self.current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this conversation"
                )

        # Add user message to conversation
        user_message = self.conversation_service.add_message_to_conversation(
            conversation_id=conversation_id,
            role="user",
            content=user_input
        )

        # Process the input using the OpenAI agent
        agent_response = self.openai_agent.process_message(user_input, conversation_id)

        # Extract the response content
        response_content = agent_response.get("response", "I'm sorry, I couldn't process your request.")

        # Add assistant response to conversation
        assistant_message = self.conversation_service.add_message_to_conversation(
            conversation_id=conversation_id,
            role="assistant",
            content=response_content
        )

        result = {
            "conversation_id": conversation_id,
            "user_message": {
                "id": str(user_message.id),
                "content": user_message.content,
                "timestamp": user_message.timestamp.isoformat()
            },
            "assistant_response": {
                "id": str(assistant_message.id),
                "content": response_content,
                "timestamp": assistant_message.timestamp.isoformat() if hasattr(assistant_message, 'timestamp') and assistant_message.timestamp else ""
            },
            "status": agent_response.get("status", "success")
        }

        # Include tool call information if available
        if "tool_calls_executed" in agent_response:
            result["tool_calls_executed"] = agent_response["tool_calls_executed"]

        # Include error information if there was an error
        if "error" in agent_response:
            result["error"] = agent_response["error"]

        return result

    def get_user_conversations(self) -> Dict[str, Any]:
        """
        Get all conversations for the current user.

        Returns:
            Dictionary with user's conversations
        """
        conversations = self.conversation_service.get_user_conversations(self.current_user.id)
        return {
            "conversations": [
                {
                    "id": str(conv.id),
                    "title": conv.title,
                    "status": conv.status,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                    "message_count": len(self.conversation_service.get_conversation_messages(str(conv.id)))
                }
                for conv in conversations
            ],
            "count": len(conversations)
        }

    def log_tool_execution(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> str:
        """
        Log the execution of an MCP tool for audit purposes.

        Args:
            tool_name: Name of the tool executed
            parameters: Parameters used for the execution
            result: Result of the execution

        Returns:
            Log entry ID
        """
        log_id = str(uuid4())
        log_entry = {
            "id": log_id,
            "timestamp": str(datetime.utcnow()),
            "user_id": self.current_user.id,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result
        }

        # In a real implementation, this would save to a log database or file
        # For now, we just print for demonstration
        print(f"MCP Tool Execution Log: {json.dumps(log_entry, indent=2)}")

        return log_id


# Helper function to get MCP service instance with dependencies
async def get_mcp_service(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
) -> McpIntegrationService:
    """
    Dependency to get an MCP service instance with current user and db session.

    Args:
        current_user: Currently authenticated user
        db_session: Database session

    Returns:
        Configured MCP integration service instance
    """
    return McpIntegrationService(db_session=db_session, current_user=current_user)


