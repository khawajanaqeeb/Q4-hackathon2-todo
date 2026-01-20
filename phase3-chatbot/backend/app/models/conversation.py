"""Conversation model for AI chatbot conversations.

This module defines the Conversation SQLModel entity that represents
a conversation session between a user and the AI chatbot.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .message import Message  # type: ignore # noqa: F401
    from .user import User  # type: ignore # noqa: F401


class ConversationBase(SQLModel):
    """Base model for conversation with common fields."""
    title: str = Field(default="New Conversation", max_length=200, description="Conversation title")
    user_id: int = Field(foreign_key="users.id", index=True, description="Owner of this conversation")
    is_active: bool = Field(default=True, description="Whether conversation is active")


class Conversation(ConversationBase, table=True):
    """SQLModel for Conversation entity."""
    __tablename__ = "conversations"

    id: int = Field(default=None, primary_key=True, description="Auto-increment primary key")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of conversation creation"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of last update",
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationRead(ConversationBase):
    """Response model for reading conversations."""
    id: int
    created_at: datetime
    updated_at: datetime
    message_count: int


class ConversationCreate(ConversationBase):
    """Request model for creating conversations."""
    title: str = Field(default="New Conversation", max_length=200)


class ConversationUpdate(SQLModel):
    """Request model for updating conversations."""
    title: str | None = Field(default=None, max_length=200)
    is_active: bool | None = Field(default=None)