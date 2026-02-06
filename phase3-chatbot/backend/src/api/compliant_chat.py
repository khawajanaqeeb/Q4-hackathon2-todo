"""ChatKit-compatible chat endpoints with OpenAI-compatible additions.

This module provides API endpoints that maintain compatibility with ChatKit
while also supporting OpenAI-compatible payloads.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, Dict, Any, List
import uuid
from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..services.chat_service import ChatService
from ..models.conversation import Conversation
from pydantic import BaseModel
import json


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatKitMessage(BaseModel):
    id: Optional[str] = None
    role: str  # "user", "assistant", "system"
    content: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatKitConversation(BaseModel):
    id: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatKitRequest(BaseModel):
    messages: List[ChatKitMessage]
    conversation: Optional[ChatKitConversation] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatKitResponse(BaseModel):
    messages: List[ChatKitMessage]
    conversation: ChatKitConversation
    metadata: Optional[Dict[str, Any]] = None


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


@router.post("/{user_id}", response_model=ChatKitResponse)
async def chatkit_send_message(
    user_id: str,
    request: ChatKitRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    ChatKit-compatible chat endpoint.
    Stateless endpoint that processes user message through real OpenAI Agents SDK connected to MCP tools.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User trying to access another user's data"
        )

    try:
        # Initialize chat service
        chat_service = ChatService(session)

        # Get the last user message to process
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user message found in request"
            )

        last_user_message = user_messages[-1]

        # Convert conversation_id if provided
        conversation_id = None
        if request.conversation and request.conversation.id:
            try:
                conversation_id = uuid.UUID(request.conversation.id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation_id format"
                )

        # Initialize the real OpenAI Agents SDK with a fresh session to avoid transaction conflicts
        from ..config import settings
        from ..real_openai_agents import RealOpenAiAgentsSdk
        from ..database import get_session

        # Create a separate session for the OpenAI agent to avoid transaction conflicts
        fresh_session_gen = get_session()
        fresh_session = next(fresh_session_gen)
        
        try:
            real_agent_sdk = RealOpenAiAgentsSdk(
                api_key=settings.OPENAI_API_KEY,
                session=fresh_session
            )

            # Create the agent
            agent = real_agent_sdk.create_todo_management_agent()

            # Process the user message through the real OpenAI Agent
            result = await real_agent_sdk.process_user_message(
                user_id=user_id,
                message=last_user_message.content
            )
        except Exception as e:
            # If OpenAI processing fails, still return a response
            result = {
                "response": f"I received your message: '{last_user_message.content}'. Due to a service issue, I cannot process it fully right now.",
                "success": True
            }
        finally:
            # Close the fresh session
            try:
                next(fresh_session_gen)
            except StopIteration:
                pass

        # Process the message using the chat service to persist in DB
        chat_result = chat_service.process_user_message(
            user_id=uuid.UUID(user_id),
            message_content=last_user_message.content,
            conversation_id=conversation_id
        )

        # Create assistant message
        assistant_message = ChatKitMessage(
            id=f"msg_{uuid.uuid4()}",
            role="assistant",
            content=result["response"],
            createdAt=chat_result["timestamp"].isoformat()
        )

        # Create or update conversation
        if chat_result["conversation_id"]:
            conversation = ChatKitConversation(
                id=str(chat_result["conversation_id"]),
                createdAt=chat_result["timestamp"].isoformat(),
                updatedAt=chat_result["timestamp"].isoformat()
            )
        else:
            conversation = ChatKitConversation(
                id=str(uuid.uuid4()),
                createdAt=chat_result["timestamp"].isoformat(),
                updatedAt=chat_result["timestamp"].isoformat()
            )

        # Clean up the agent resources
        real_agent_sdk.cleanup_agent()

        return ChatKitResponse(
            messages=[assistant_message],
            conversation=conversation
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


# Add OpenAI-compatible chat completions endpoint
from typing import List as TypingList  # Avoid conflict with class name


class Message(BaseModel):
    role: str  # "system", "user", or "assistant"
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4"  # Default model
    messages: TypingList[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: TypingList[Choice]
    usage: Usage


@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    OpenAI-compatible chat completions endpoint.
    Process chat messages through the AI system and return a completion response.
    """
    try:
        import time
        import uuid as uuid_lib

        # Initialize services
        chat_service = ChatService(session)
        agent_runner = AgentRunner()

        # Get the last user message to process
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user message found in request"
            )

        last_user_message = user_messages[-1]

        # Process the user message through the chat service
        result = chat_service.process_user_message(
            user_id=current_user.id,
            message_content=last_user_message.content,
            conversation_id=None  # Create new conversation or use default
        )

        # Create the response in OpenAI format
        response_id = f"chatcmpl-{uuid_lib.uuid4()}"
        created_time = int(time.time())

        # Create the assistant message
        assistant_message = Message(
            role="assistant",
            content=result["message"]
        )

        choice = Choice(
            index=0,
            message=assistant_message,
            finish_reason="stop"
        )

        # Calculate approximate token usage
        prompt_tokens = len(last_user_message.content)
        completion_tokens = len(result["message"])
        total_tokens = prompt_tokens + completion_tokens

        usage = Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )

        response = ChatCompletionResponse(
            id=response_id,
            created=created_time,
            model=request.model,
            choices=[choice],
            usage=usage
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )