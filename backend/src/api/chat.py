from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session
from typing import List

from ..models.user import User
from ..services.chat import ChatService
from ..database import get_session
from ..services.auth import get_current_user

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/messages", response_model=None)
@limiter.limit("30 per minute")
def chat_messages(
    request: Request,
    message: str,
    conversation_id: str = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Send a message to the chatbot and receive a response."""
    chat_service = ChatService(session)

    try:
        result = chat_service.process_message(
            user_id=current_user.id,
            message_content=message,
            conversation_id=conversation_id
        )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.get("/conversations", response_model=None)
@limiter.limit("20 per minute")
def get_user_conversations(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all conversations for the current user."""
    chat_service = ChatService(session)

    try:
        conversations = chat_service.get_conversations(current_user.id)
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )