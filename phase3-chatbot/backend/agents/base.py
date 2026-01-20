"""Real base utilities for the Phase 3 Todo AI Chatbot agents."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlmodel import create_engine, Session, select
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# Import the existing models from the Phase II backend
import sys
from pathlib import Path

# Add the project root to the path so we can import from phase2-fullstack
project_root = Path(__file__).parent.parent.parent.parent
phase2_backend = project_root / "phase2-fullstack" / "backend"

# Add to sys.path if not already there
if str(phase2_backend) not in sys.path:
    sys.path.insert(0, str(phase2_backend))

# Add the phase3 backend to the path to get the models
phase3_backend = Path(__file__).parent.parent
if str(phase3_backend) not in sys.path:
    sys.path.insert(0, str(phase3_backend))

# Also add the app directory to the path to allow direct imports
app_dir = phase3_backend / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Try importing from the local directory structure
try:
    # Import directly using the relative path approach
    from app.models.user import User
    from app.models.todo import Todo
    from app.database import get_session
    from app.models.conversation import Conversation
    from app.models.message import Message, MessageRole
except ImportError as e:
    print(f"Error importing from Phase II/III backend: {e}")
    raise


class ConversationMessage(BaseModel):
    """Message model for conversation history."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = datetime.now()


class ConversationHistory(BaseModel):
    """Conversation history model."""
    conversation_id: str
    messages: List[ConversationMessage] = []


async def load_conversation_history(user_id: int) -> List[Dict[str, str]]:
    """
    Load conversation history from the database.
    This is a placeholder implementation since we don't have a conversation/messages table yet.
    In a real implementation, this would query a Conversation/Messages table.

    Args:
        user_id: The authenticated user's ID

    Returns:
        List of message dictionaries with 'role' and 'content' keys
    """
    # Import database dependencies
    from sqlmodel import create_engine, Session, select
    from ..app.config import settings

    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL)

    with Session(engine) as session:
        # Get recent conversations for the user
        # Join with messages to get conversation history
        messages_result = session.execute(
            select(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(20)  # Limit to last 20 messages
        )

        db_messages = messages_result.scalars().all()

        # Format messages for the AI
        formatted_messages = []
        for msg in reversed(db_messages):  # Reverse to get chronological order
            formatted_messages.append({
                "role": msg.role.value if hasattr(msg.role, 'value') else msg.role,
                "content": msg.content
            })

        return formatted_messages


def extract_user_id_from_jwt(token_payload: Optional[dict]) -> Optional[int]:
    """
    Extract user_id from JWT token payload.

    Args:
        token_payload: The decoded token payload (dictionary) from JWT

    Returns:
        User ID if available, None otherwise
    """
    if token_payload is None:
        return None

    # In the Phase II system, the user ID is stored in the 'sub' field
    user_id = token_payload.get("sub")
    if user_id is not None:
        return int(user_id) if isinstance(user_id, (int, str)) else None

    return None


def format_messages_for_openai(history: List[Dict[str, str]], new_message: str) -> List[Dict[str, str]]:
    """
    Format messages for OpenAI API consumption.

    Args:
        history: List of previous messages
        new_message: The new user message

    Returns:
        Formatted list of messages for OpenAI
    """
    # Combine history with the new message
    all_messages = history.copy()
    all_messages.append({"role": "user", "content": new_message})

    return all_messages