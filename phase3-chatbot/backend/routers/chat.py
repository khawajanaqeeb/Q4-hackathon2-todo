"""Chat router for the Phase 3 Todo AI Chatbot."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Import the router agent
from ..agents.router import router_agent, RouterAgent
from ..agents.base import load_conversation_history, extract_user_id_from_jwt

# Import the existing auth dependencies from Phase II backend
# We'll use the same approach as in base.py for consistency
import sys
from pathlib import Path

# Add the project root to the path so we can import from phase2-fullstack
project_root = Path(__file__).parent.parent.parent.parent
phase2_backend = project_root / "phase2-fullstack" / "backend"

# Add to sys.path if not already there
if str(phase2_backend) not in sys.path:
    sys.path.insert(0, str(phase2_backend))

try:
    from app.dependencies.auth import get_current_user
    from app.models.user import User
except ImportError as e:
    print(f"Warning: Could not import auth dependencies: {e}")
    # Define minimal stubs for development
    class User:
        id: int
        email: str
        is_active: bool


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
    Chat endpoint that processes user messages through the Router Agent.

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
        # Load conversation history from DB (currently returns empty)
        history = await load_conversation_history(user_id)

        # Run the router agent with the user message
        result = await router_agent.run(
            user_message=request.message,
            user_id=user_id,
            history=history
        )

        # Return the response
        return ChatResponse(
            response=result["response"],
            routing_decision=result.get("routing_decision"),
            handoff=result.get("handoff", False)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


# Additional endpoint to get conversation history (if needed)
@router.get("/{user_id}/conversations")
async def get_conversations(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history for the user.

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