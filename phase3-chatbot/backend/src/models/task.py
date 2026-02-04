from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from enum import Enum


if TYPE_CHECKING:
    from .user import User


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(SQLModel, table=True):
    """Extended Task model with chat-related fields."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")  # Use the default table name
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    due_date: Optional[datetime] = Field(default=None)
    completed: bool = Field(default=False)
    tags: Optional[str] = Field(default=None)  # Store as JSON string instead of array
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow())

    # Relationship to user
    user: "User" = Relationship(back_populates="tasks")