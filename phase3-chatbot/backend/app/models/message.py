"""Message model for AI chatbot conversation history.

This module defines the Message SQLModel entity that represents
individual messages within a conversation session.
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from typing import TYPE_CHECKING
from datetime import datetime
import uuid
from enum import Enum


if TYPE_CHECKING:
    from .conversation import Conversation  # type: ignore # noqa: F401


class MessageRole(str, Enum):
    """Enumeration for message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageStatus(str, Enum):
    """Enumeration for message processing status."""
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"


class MessageBase(SQLModel):
    """Base model for message with common fields."""
    conversation_id: int = Field(foreign_key="conversations.id", index=True, description="Conversation this message belongs to")
    role: MessageRole = Field(sa_column_kwargs={"name": "role"}, description="Role of the message sender")
    content: str = Field(sa_column_kwargs={"server_default": ""}, description="Message content")
    status: MessageStatus = Field(default=MessageStatus.PROCESSED, description="Processing status of the message")

    # Optional fields for tool interactions
    tool_name: str | None = Field(default=None, max_length=100, description="Name of the tool called (if any)")
    tool_input: dict | None = Field(default=None, sa_column=Column(JSON), description="Input parameters for the tool")
    tool_output: dict | None = Field(default=None, sa_column=Column(JSON), description="Output from the tool execution")


class Message(MessageBase, table=True):
    """SQLModel for Message entity."""
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="UUID primary key")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of message creation"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of last update",
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    # Relationship to conversation
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageRead(MessageBase):
    """Response model for reading messages."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    processing_time_ms: int | None = None


class MessageCreate(MessageBase):
    """Request model for creating messages."""
    role: MessageRole
    content: str


class MessageUpdate(SQLModel):
    """Request model for updating messages."""
    content: str | None = Field(default=None)
    status: MessageStatus | None = Field(default=None)
    tool_output: dict | None = Field(default=None)