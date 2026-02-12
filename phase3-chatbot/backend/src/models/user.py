from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class User(SQLModel, table=True):
    """User model for authentication and authorization."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(String(36), primary_key=True),
    )
    username: str = Field(unique=True, min_length=3, max_length=50)
    email: str = Field(unique=True, min_length=5, max_length=100)
    hashed_password: str = Field(min_length=8)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")
    # messages: List["Message"] = Relationship(back_populates="user")  # Temporarily commented out to avoid conflicts
    api_keys: List["ApiKey"] = Relationship(back_populates="user")