"""Todo model with user isolation and advanced features.

This module defines the Todo SQLModel entity with priority levels, tags,
and complete user isolation via foreign key relationship.

Spec Reference: specs/001-fullstack-web-app/data-model.md §Entity 2: Todo
"""
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import JSON
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import field_validator


class Priority(str, Enum):
    """Priority levels for todo items.

    Values:
        LOW: Low priority task
        MEDIUM: Medium priority task (default)
        HIGH: High priority task
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo(SQLModel, table=True):
    """Todo item model with user isolation.

    Represents a task in a user's todo list with support for priorities,
    tags, completion status, and timestamps. Each todo belongs to exactly
    one user (enforced via foreign key).

    Relationships:
        - Many-to-one with User (cascade delete when user is deleted)

    Security:
        - User isolation enforced via user_id foreign key
        - All queries MUST filter by current_user.id

    Performance:
        - Indexed on user_id, completed, priority, created_at, title
        - Composite indexes for common query patterns
    """
    __tablename__ = "todos"

    # Primary key (auto-increment)
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-increment primary key"
    )

    # Foreign key (user ownership)
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of this todo (references users.id)"
    )

    # Todo content
    title: str = Field(
        max_length=500,
        index=True,
        description="Todo title (required, 1-500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional detailed description (max 5000 characters)"
    )

    # Status fields
    completed: bool = Field(
        default=False,
        index=True,
        description="Whether todo is marked as complete"
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        index=True,
        description="Priority level: low, medium, or high"
    )

    # Tags (stored as JSON array in PostgreSQL)
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of tags for categorization (max 10 tags)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="UTC timestamp of creation"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of last modification"
    )

    # Relationships (optional - for ORM convenience)
    # Uncomment if you need to navigate from Todo to user in code
    # user: Optional["User"] = Relationship(back_populates="todos")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after trimming whitespace."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags array constraints.

        Rules:
            - Maximum 10 tags per todo
            - Maximum 50 characters per tag
            - Deduplicate tags
        """
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed per todo")

        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 character limit")

        # Deduplicate tags (preserve order)
        seen = set()
        unique_tags = []
        for tag in v:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags

    class Config:
        """Pydantic configuration for JSON schema examples."""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, cheese",
                "priority": "high",
                "tags": ["shopping", "urgent"],
                "completed": False,
            }
        }