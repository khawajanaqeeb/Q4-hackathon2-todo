from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional
import uuid
from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User  # Assuming User model exists from phase 2
from ..services.chat_service import ChatService
from ..services.agent_runner import AgentRunner
from ..services.mcp_integration import McpIntegrationService
from pydantic import BaseModel
from ..models.conversation import Conversation  # Import the Conversation model


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None  # UUID as string


class ChatMessageResponse(BaseModel):
    message: str
    conversation_id: str  # UUID as string
    timestamp: str
    action_taken: str
    confirmation_message: str


class ConversationSummary(BaseModel):
    id: str  # UUID as string
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
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    # Initialize services
    chat_service = ChatService(session)
    agent_runner = AgentRunner()
    mcp_service = McpIntegrationService(session)

    try:
        # Convert conversation_id to UUID if provided
        conversation_id = None
        if request.conversation_id:
            try:
                conversation_id = uuid.UUID(request.conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation_id format"
                )

        # Process the user message through the chat service
        # First, process with agent runner to understand the intent
        conversation_uuid = uuid.UUID(user_id)

        # Get conversation messages for context
        if conversation_id:
            conversation = session.get(chat_service.Conversation, conversation_id)
            if not conversation or conversation.user_id != conversation_uuid:
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
            params = agent_result["intent_result"]["parsed_command"]["parameters"] if "intent_result" in agent_result and "parsed_command" in agent_result["intent_result"] else {}

            mcp_result = await mcp_service.invoke_tool(
                tool_name=tool_name,
                parameters=params,
                user_id=conversation_uuid
            )

            if not mcp_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"MCP operation failed: {mcp_result.get('error', 'Unknown error')}"
                )

        # Process the message using the chat service
        result = chat_service.process_user_message(
            user_id=conversation_uuid,
            message_content=request.message,
            conversation_id=conversation_id
        )

        return ChatMessageResponse(
            message=result["message"],
            conversation_id=str(result["conversation_id"]),
            timestamp=result["timestamp"].isoformat(),
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
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    try:
        user_uuid = uuid.UUID(user_id)
        chat_service = ChatService(session)

        # Get user conversations
        conversations = chat_service.get_user_conversations(user_uuid)

        # Apply pagination
        paginated_conversations = conversations[offset:offset + limit]

        # Format the response
        formatted_conversations = [
            ConversationSummary(
                id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat()
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
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    try:
        user_uuid = uuid.UUID(user_id)
        conv_uuid = uuid.UUID(conversation_id)
        chat_service = ChatService(session)

        # Get the conversation to verify it belongs to the user
        conversation = session.get(chat_service.Conversation, conv_uuid)
        if not conversation or conversation.user_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conversation does not belong to user"
            )

        # Get messages for the conversation
        messages = chat_service.get_conversation_messages(conv_uuid)

        # Format the response
        formatted_messages = [
            {
                "id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
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
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    try:
        user_uuid = uuid.UUID(user_id)
        conv_uuid = uuid.UUID(conversation_id)
        chat_service = ChatService(session)

        # Attempt to delete the conversation
        success = chat_service.delete_conversation(conv_uuid, user_uuid)

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