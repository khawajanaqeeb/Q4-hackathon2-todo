"""User model for authentication and ownership.

This module defines the User SQLModel entity with auto-increment ID,
email authentication, and one-to-many relationship with Todo items.

Spec Reference: specs/001-fullstack-web-app/data-model.md §Entity 1: User
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class User(SQLModel, table=True):
    """User model for authentication and ownership.

    Represents an authenticated user with personal todo list isolation.
    Uses auto-increment integer primary key as per PostgreSQL best practices.

    Relationships:
        - One-to-many with Todo (cascade delete on user removal)

    Security:
        - Passwords stored as bcrypt hashes (60 chars)
        - Email uniqueness enforced at database level
        - User isolation via user_id foreign key in todos
    """
    __tablename__ = "users"

    # Primary key (auto-increment)
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-increment primary key"
    )

    # Authentication fields
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="Unique email address (login identifier)"
    )
    hashed_password: str = Field(
        max_length=60,
        description="Bcrypt hash of user password (always 60 chars)"
    )

    # User profile
    name: str = Field(
        max_length=255,
        description="User's display name"
    )

    # Status flags
    is_active: bool = Field(
        default=True,
        description="Account active status (soft delete mechanism)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of account creation"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of last profile update"
    )

    # Relationships (optional - for ORM convenience)
    # Uncomment if you need to navigate from User to todos in code
    # todos: List["Todo"] = Relationship(back_populates="user")

    class Config:
        """Pydantic configuration for JSON schema examples."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
            }
        }