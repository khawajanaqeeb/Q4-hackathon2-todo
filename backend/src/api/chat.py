"""Chat API endpoint for the Phase 3 chatbot system."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session
from typing import Dict, Any, Optional
import json
import asyncio

from ..models.user import User
from ..services.auth import get_current_user
from ..database import get_session
from ..services.conversation_service import ConversationService
from ..services.mcp_integration import McpIntegrationService
from ..tools.todo_tools import TodoTools


# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Create router for chat endpoints
router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/messages", response_model=None)
@limiter.limit("30 per minute")
async def process_chat_message(
    request: Request,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Process a chat message and return AI response using conversation context and MCP tools.

    This endpoint handles chat messages from users and orchestrates with the OpenAI Agent
    and MCP tools to provide appropriate responses and perform todo operations.
    """
    try:
        # Parse the request body
        body = await request.json()
        user_message = body.get("message", "")
        conversation_id = body.get("conversation_id", None)

        if not user_message or len(user_message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message content is required"
            )

        # Create MCP service instance
        mcp_service = McpIntegrationService(
            db_session=db_session,
            current_user=current_user
        )

        # Process the conversation request
        response = await mcp_service.process_conversation_request(
            user_input=user_message,
            conversation_id=conversation_id
        )

        # Format response to match frontend expectations
        formatted_response = {
            "message": response.get("assistant_response", {}).get("content", ""),
            "confirmation_message": response.get("assistant_response", {}).get("content", ""),
            "conversation_id": response.get("conversation_id"),
            "timestamp": response.get("assistant_response", {}).get("timestamp", ""),
            "action_taken": "processed",
            "status": response.get("status", "success")
        }

        # Include any tool calls executed if present
        if "tool_calls_executed" in response:
            formatted_response["tool_calls_executed"] = response["tool_calls_executed"]

        # Include error information if there was an error
        if "error" in response:
            formatted_response["error"] = response["error"]

        return formatted_response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error (in a real system you'd use proper logging)
        print(f"Error processing chat message: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.get("/stream", response_model=None)
@limiter.limit("30 per minute")
async def stream_chat_response(
    request: Request,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Stream chat responses using Server-Sent Events (SSE).

    This endpoint provides real-time streaming responses for chat interactions,
    ideal for creating interactive chat experiences.
    """
    from fastapi.responses import StreamingResponse

    async def event_generator():
        try:
            # Get query parameters for the streaming request
            user_message = request.query_params.get("message", "")
            conversation_id = request.query_params.get("conversation_id", None)

            if not user_message or len(user_message.strip()) == 0:
                yield f"data: {json.dumps({'error': 'Message content is required'})}\n\n"
                return

            # Create MCP service instance
            mcp_service = McpIntegrationService(
                db_session=db_session,
                current_user=current_user
            )

            # Process the conversation request
            response = await mcp_service.process_conversation_request(
                user_input=user_message,
                conversation_id=conversation_id
            )

            # Yield the response in chunks to simulate streaming
            response_text = response.get("assistant_response", {}).get("content", "")

            # Simulate streaming by yielding parts of the response
            words = response_text.split()
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'content': word + (' ' if i < len(words) - 1 else ''), 'done': i == len(words) - 1})}\n\n"
                await asyncio.sleep(0.05)  # Small delay to simulate real streaming

            # Signal completion
            yield f"data: {json.dumps({'done': True, 'conversation_id': response.get('conversation_id')})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/conversations", response_model=None)
@limiter.limit("20 per minute")
def list_user_conversations(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    List all conversations for the authenticated user.

    Returns a list of the user's conversations with basic metadata.
    """
    try:
        # Create conversation service instance
        conversation_service = ConversationService(db_session)

        # Get user's conversations
        conversations = conversation_service.get_user_conversations(current_user.id)

        # Format response
        result = []
        for conv in conversations:
            # Count messages in conversation
            messages = conversation_service.get_conversation_messages(str(conv.id))

            result.append({
                "id": str(conv.id),
                "title": conv.title,
                "status": conv.status,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "message_count": len(messages),
                "last_message_preview": messages[-1].content[:100] + "..." if messages else None
            })

        return {
            "conversations": result,
            "count": len(result)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=None)
@limiter.limit("20 per minute")
def get_conversation_details(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Get details for a specific conversation including all messages.

    Args:
        conversation_id: The ID of the conversation to retrieve

    Returns:
        Conversation details with all messages
    """
    try:
        # Create conversation service instance
        conversation_service = ConversationService(db_session)

        # Get conversation
        conversation = conversation_service.get_conversation_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Verify user owns this conversation
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )

        # Get messages
        messages = conversation_service.get_conversation_messages(conversation_id)

        # Get todo operation logs
        todo_logs = conversation_service.get_conversation_todo_operations(conversation_id)

        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "status": conversation.status,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                }
                for msg in messages
            ],
            "todo_operation_logs": [
                {
                    "id": str(log.id),
                    "message_id": log.message_id,
                    "operation": log.operation,
                    "todo_id": log.todo_id,
                    "previous_state": json.loads(log.previous_state) if log.previous_state else None,
                    "new_state": json.loads(log.new_state) if log.new_state else None,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
                for log in todo_logs
            ],
            "message_count": len(messages)
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation details: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}", response_model=None)
@limiter.limit("10 per minute")
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Delete a specific conversation.

    Args:
        conversation_id: The ID of the conversation to delete

    Returns:
        Success confirmation
    """
    try:
        # Create conversation service instance
        conversation_service = ConversationService(db_session)

        # Get conversation to verify it exists and belongs to user
        conversation = conversation_service.get_conversation_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Verify user owns this conversation
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )

        # Delete the conversation
        success = conversation_service.delete_conversation(conversation_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )

        return {
            "status": "success",
            "message": f"Conversation {conversation_id} deleted successfully"
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/archive", response_model=None)
@limiter.limit("10 per minute")
def archive_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session)
):
    """
    Archive a specific conversation.

    Args:
        conversation_id: The ID of the conversation to archive

    Returns:
        Success confirmation
    """
    try:
        # Create conversation service instance
        conversation_service = ConversationService(db_session)

        # Get conversation to verify it exists and belongs to user
        conversation = conversation_service.get_conversation_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Verify user owns this conversation
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )

        # Archive the conversation
        success = conversation_service.archive_conversation(conversation_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to archive conversation"
            )

        return {
            "status": "success",
            "message": f"Conversation {conversation_id} archived successfully"
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error archiving conversation: {str(e)}"
        )