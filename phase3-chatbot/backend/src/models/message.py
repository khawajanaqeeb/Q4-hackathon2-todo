from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from enum import Enum


if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """Message model for storing individual chat messages."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")  # Use the default table name
    # Temporarily remove user_id to avoid database schema conflicts
    # user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")  # Make optional
    role: MessageRole = Field(sa_column_kwargs={"default": "user"})
    content: str = Field(min_length=1, max_length=10000)
    timestamp: datetime = Field(default=datetime.utcnow())
    message_metadata: Optional[str] = Field(default=None)  # Renamed from metadata to avoid conflict

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    # user: Optional["User"] = Relationship(back_populates="messages")  # Make user relationship optional