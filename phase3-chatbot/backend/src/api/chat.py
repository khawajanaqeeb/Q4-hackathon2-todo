from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional
from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..models.conversation import Conversation
from ..services.chat_service import ChatService
from ..services.agent_runner import AgentRunner
from ..services.mcp_integration import McpIntegrationService
from pydantic import BaseModel
from typing import List
from ..services.api_key_manager import ApiKeyManager
from ..services.audit_service import AuditService


router = APIRouter(tags=["Chat"])


class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None  # integer ID as string


class ChatMessageResponse(BaseModel):
    message: str
    conversation_id: str  # integer ID as string
    timestamp: str
    action_taken: str
    confirmation_message: str


class ConversationSummary(BaseModel):
    id: str  # integer ID as string
    title: Optional[str]
    created_at: str
    updated_at: str


class GetConversationsResponse(BaseModel):
    conversations: list[ConversationSummary]
    total_count: int
    limit: int
    offset: int


@router.post("/{user_id}", response_model=ChatMessageResponse)
async def send_message(
    user_id: str,
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send a message to the chatbot.
    Process a user message through the AI chatbot and return a response.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    # Initialize services
    chat_service = ChatService(session)
    agent_runner = AgentRunner()
    api_key_manager = ApiKeyManager()
    audit_service = AuditService(session)
    mcp_service = McpIntegrationService(session, api_key_manager, audit_service)

    try:
        # Convert conversation_id to int if provided
        conversation_id = None
        if request.conversation_id:
            try:
                conversation_id = int(request.conversation_id)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation_id format"
                )

        # Get conversation messages for context
        if conversation_id:
            conversation = session.get(Conversation, conversation_id)
            if not conversation or str(conversation.user_id) != str(user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Conversation does not belong to user"
                )

            # Get recent messages for context
            recent_messages = chat_service.get_conversation_messages(conversation_id)
            context = [{"role": msg.role.value, "content": msg.content} for msg in recent_messages[-5:]]  # Last 5 messages
        else:
            context = []

        # Process with agent runner to understand the intent
        agent_result = await agent_runner.run_agent(request.message, context)

        if not agent_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing message: {agent_result.get('error', 'Unknown error')}"
            )

        # If the agent identified a task operation, process it via MCP
        intent = agent_result["action_taken"]
        mcp_result = None

        if intent in ["task_creation", "task_listing", "task_update", "task_deletion", "task_completion"]:
            # Map the intent to an appropriate MCP tool
            tool_mapping = {
                "task_creation": "create_task",
                "task_listing": "list_tasks",
                "task_update": "update_task",
                "task_deletion": "delete_task",
                "task_completion": "complete_task"
            }

            tool_name = tool_mapping.get(intent, "todo_operation")
            params = {}
            if "intent_result" in agent_result and "parsed_command" in agent_result["intent_result"]:
                params = agent_result["intent_result"]["parsed_command"].get("parameters", {})

            mcp_result = await mcp_service.invoke_tool(
                tool_name=tool_name,
                parameters=params,
                user_id=user_id
            )

            # Check both outer success (tool invocation) and inner success (operation result)
            inner_result = mcp_result.get("result", {}) if mcp_result else {}
            inner_success = inner_result.get("success", False) if isinstance(inner_result, dict) else False

            if not mcp_result.get("success"):
                # Tool invocation failed entirely
                error_msg = mcp_result.get("error", "Unknown error")
                agent_result["response"] = f"Sorry, I couldn't complete the operation: {error_msg}"
            elif not inner_success:
                # Tool was invoked but the operation failed (e.g., task_id missing, task not found)
                error_msg = inner_result.get("error", "Unknown error") if isinstance(inner_result, dict) else "Unknown error"
                agent_result["response"] = f"Sorry, I couldn't complete the operation: {error_msg}"
            else:
                # Regenerate response with MCP results included
                agent_result["response"] = await agent_runner.generate_response_with_mcp(
                    request.message,
                    agent_result["intent_result"],
                    mcp_result
                )

        # Process the message using the chat service, passing the agent's AI response
        result = chat_service.process_user_message(
            user_id=user_id,
            message_content=request.message,
            conversation_id=conversation_id,
            agent_response=agent_result.get("response"),
            action_taken=agent_result.get("action_taken")
        )

        # Ensure timestamp is marked as UTC (DB stores UTC without timezone info)
        ts = result["timestamp"]
        ts_iso = ts.isoformat() + ("Z" if not ts.tzinfo else "")

        return ChatMessageResponse(
            message=result["message"],
            conversation_id=str(result["conversation_id"]),
            timestamp=ts_iso,
            action_taken=result["action_taken"],
            confirmation_message=result["confirmation_message"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def get_user_conversations(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user's conversations.
    Retrieve a list of conversation summaries for the user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    try:

        chat_service = ChatService(session)

        # Get user conversations
        conversations = chat_service.get_user_conversations(user_id)

        # Apply pagination
        paginated_conversations = conversations[offset:offset + limit]

        # Format the response (append Z to mark UTC for naive datetimes)
        formatted_conversations = [
            ConversationSummary(
                id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at.isoformat() + ("Z" if not conv.created_at.tzinfo else ""),
                updated_at=conv.updated_at.isoformat() + ("Z" if not conv.updated_at.tzinfo else "")
            )
            for conv in paginated_conversations
        ]

        return GetConversationsResponse(
            conversations=formatted_conversations,
            total_count=len(conversations),
            limit=limit,
            offset=offset
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{user_id}/conversations/{conversation_id}")
async def get_conversation_messages(
    user_id: str,
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get conversation messages.
    Retrieve all messages in a specific conversation.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    try:

        conv_id_int = int(conversation_id)
        chat_service = ChatService(session)

        # Get the conversation to verify it belongs to the user
        conversation = session.get(Conversation, conv_id_int)
        if not conversation or str(conversation.user_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conversation does not belong to user"
            )

        # Get messages for the conversation
        messages = chat_service.get_conversation_messages(conv_id_int)

        # Format the response (append Z to mark UTC for naive datetimes)
        formatted_messages = [
            {
                "id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() + ("Z" if not msg.timestamp.tzinfo else ""),
                "message_metadata": msg.message_metadata
            }
            for msg in messages
        ]

        return {
            "conversation_id": str(conversation.id),
            "title": conversation.title,
            "messages": formatted_messages
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id or conversation_id format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{user_id}/conversations/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a conversation.
    Permanently delete a conversation and all its messages.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    try:

        conv_id_int = int(conversation_id)
        chat_service = ChatService(session)

        # Attempt to delete the conversation
        success = chat_service.delete_conversation(conv_id_int, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or does not belong to user"
            )

        return {"message": "Conversation deleted successfully"}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id or conversation_id format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


