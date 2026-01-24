from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from enum import Enum

if TYPE_CHECKING:
    from .message import Message
    from .user import User  # Assuming User model exists from phase 2


class Conversation(SQLModel, table=True):
    """Conversation model for storing chat conversation data."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: Optional[str] = Field(max_length=255, nullable=True)  # Auto-generated from first message
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow())
    is_active: bool = Field(default=True)

    # Relationship to messages
    messages: list["Message"] = Relationship(back_populates="conversation", cascade_delete=True)


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """Message model for storing individual chat messages."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    role: MessageRole = Field(sa_column_kwargs={"default": "user"})
    content: str = Field(min_length=1, max_length=10000)
    timestamp: datetime = Field(default=datetime.utcnow())
    metadata: Optional[dict] = Field(default=None, sa_column_type="JSONB")  # For tokens used, AI response details

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")