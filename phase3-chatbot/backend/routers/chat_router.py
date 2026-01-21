"""Real chat router for the Phase 3 Todo AI Chatbot using FastAPI."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio

# Import the router agent
import sys
from pathlib import Path

# Add the backend directory to the path to allow imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.router_agent import router_agent
from agents.base import load_conversation_history, extract_user_id_from_jwt, format_messages_for_openai

# Add the project root to the path so we can import from phase2-fullstack
project_root = Path(__file__).parent.parent.parent.parent
phase2_backend = project_root / "phase2-fullstack" / "backend"

# Add to sys.path if not already there
if str(phase2_backend) not in sys.path:
    sys.path.insert(0, str(phase2_backend))

# Add the app directory to the path to allow direct imports
app_dir = backend_dir / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Temporarily patch the settings to avoid validation errors during import
import os
import sys
from unittest.mock import Mock

# Create a mock settings object that mimics Phase 2 settings but avoids validation
mock_settings = Mock()
mock_settings.DATABASE_URL = os.getenv("DATABASE_URL")
mock_settings.SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
mock_settings.ALGORITHM = os.getenv("ALGORITHM", "HS256")
mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
mock_settings.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
mock_settings.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
mock_settings.LOGIN_RATE_LIMIT = int(os.getenv("LOGIN_RATE_LIMIT", "5"))

# Temporarily replace the app.config module in sys.modules with our mock
original_config_module = sys.modules.get('app.config')
sys.modules['app.config'] = mock_settings

try:
    from app.dependencies.auth import get_current_user
    from app.models.user import User
except ImportError as e:
    print(f"Error importing auth dependencies: {e}")
    raise
finally:
    # Restore the original config module if it existed
    if original_config_module:
        sys.modules['app.config'] = original_config_module
    else:
        if 'app.config' in sys.modules:
            del sys.modules['app.config']


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    routing_decision: Optional[str] = None
    handoff: bool = False
    timestamp: datetime = datetime.now()


router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Real chat endpoint that processes user messages through the Router Agent.
    Makes real API calls to Google Gemini via OpenAI-compatible endpoint.

    Args:
        user_id: The ID of the user (should match authenticated user)
        request: The chat request containing the user's message
        current_user: The currently authenticated user

    Returns:
        ChatResponse containing the agent's response and routing information
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User ID mismatch"
        )

    try:
        # Load conversation history from DB
        history = await load_conversation_history(user_id)

        # Run the router agent with the user message
        result = await router_agent.run(
            user_message=request.message,
            user_id=user_id,
            history=history
        )

        # Import database models and session for storing messages
        from sqlmodel import Session, create_engine, select
        from ..config import settings  # Use Phase 3 settings instead of Phase 2
        from ..app.models.message import Message, MessageRole, MessageStatus
        from ..app.models.conversation import Conversation

        # Create database engine and session
        engine = create_engine(settings.DATABASE_URL)

        with Session(engine) as session:
            # Get or create a conversation for this user
            # In a real implementation, you might have conversation management logic
            result_conv = session.execute(
                select(Conversation).where(Conversation.user_id == user_id).limit(1)
            )
            conversation = result_conv.scalar_one_or_none()

            if not conversation:
                # Create a new conversation if none exists
                conversation = Conversation(
                    title="Default Conversation",
                    user_id=user_id,
                    is_active=True
                )
                session.add(conversation)
                session.commit()
                session.refresh(conversation)

            # Store the user message in the database
            user_message_db = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=request.message,
                status=MessageStatus.PROCESSED
            )

            # Store the assistant response in the database
            assistant_message_db = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=result["response"],
                status=MessageStatus.PROCESSED
            )

            session.add(user_message_db)
            session.add(assistant_message_db)
            session.commit()

        # Return the response
        return ChatResponse(
            response=result["response"],
            routing_decision=result.get("routing_decision"),
            handoff=result.get("handoff", False)
        )
    except Exception as e:
        # Log the error for debugging (but don't expose internal details to user)
        print(f"Error processing chat request: {str(e)}")

        # Return a friendly error message
        return ChatResponse(
            response="Sorry, I couldn't process that request. Please try again.",
            routing_decision=None,
            handoff=False
        )



# Additional endpoint to get conversation history (real implementation would query DB)
@router.get("/{user_id}/conversations")
async def get_conversations(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history for the user.
    In a real implementation, this would query a Conversation/Messages table.

    Args:
        user_id: The ID of the user (should match authenticated user)
        current_user: The currently authenticated user

    Returns:
        List of conversations for the user
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User ID mismatch"
        )

    # For now, return an empty list since we don't have a conversation table yet
    # In a full implementation, this would query a Conversation/Messages table
    return []