from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from .conversation import MessageRole


if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """Message model for storing individual chat messages."""

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: MessageRole = Field(sa_column_kwargs={"default": "user"})
    content: str = Field(min_length=1, max_length=10000)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_metadata: Optional[str] = Field(default=None)  # Renamed from metadata to avoid conflict

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    # user: Optional["User"] = Relationship(back_populates="messages")  # Make user relationship optional