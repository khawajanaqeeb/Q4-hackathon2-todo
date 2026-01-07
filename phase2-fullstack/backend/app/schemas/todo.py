"""Todo request and response schemas.

This module defines Pydantic schemas for todo CRUD operations
including creation, updates, and responses.

Spec Reference: specs/001-fullstack-web-app/contracts/todos.yaml
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class TodoCreate(BaseModel):
    """Schema for creating a new todo.

    Used in POST /todos endpoint.
    User ID will be automatically set from authenticated user.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task title (trimmed, non-empty)",
        json_schema_extra={"example": "Buy groceries"}
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional detailed description",
        json_schema_extra={"example": "Milk, eggs, bread, cheese"}
    )
    priority: str = Field(
        default="medium",
        description="Task priority level",
        pattern="^(low|medium|high)$",
        json_schema_extra={"example": "high"}
    )
    tags: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Array of string tags (max 10, each max 50 chars)",
        json_schema_extra={"example": ["shopping", "urgent", "weekly"]}
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Validate title is not empty after trimming."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags_constraints(cls, v: List[str]) -> List[str]:
        """Validate tags array constraints."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed per todo")

        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 character limit")

        # Deduplicate tags while preserving order
        seen = set()
        unique_tags = []
        for tag in v:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, cheese",
                "priority": "high",
                "tags": ["shopping", "urgent"]
            }
        }


class TodoUpdate(BaseModel):
    """Schema for updating an existing todo.

    Used in PUT /todos/{id} endpoint.
    All fields are optional (partial update).
    """
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Updated task title",
        json_schema_extra={"example": "Buy groceries and cook dinner"}
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Updated description",
        json_schema_extra={"example": "Milk, eggs, bread, cheese, pasta"}
    )
    priority: Optional[str] = Field(
        default=None,
        pattern="^(low|medium|high)$",
        description="Updated priority level",
        json_schema_extra={"example": "high"}
    )
    tags: Optional[List[str]] = Field(
        default=None,
        max_length=10,
        description="Updated tags array",
        json_schema_extra={"example": ["shopping", "urgent"]}
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Updated completion status",
        json_schema_extra={"example": True}
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty after trimming."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip() if v else None

    @field_validator("tags")
    @classmethod
    def validate_tags_constraints(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags array constraints."""
        if v is None:
            return None

        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed per todo")

        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 character limit")

        # Deduplicate tags while preserving order
        seen = set()
        unique_tags = []
        for tag in v:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and cook dinner",
                "priority": "high",
                "completed": False
            }
        }


class TodoResponse(BaseModel):
    """Schema for todo in responses.

    Used in all todo endpoints that return todo data.
    Includes all fields including auto-generated ones.
    """
    id: int = Field(..., description="Todo unique identifier")
    user_id: int = Field(..., description="Owner user ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description (can be null)")
    completed: bool = Field(..., description="Completion status")
    priority: str = Field(..., description="Priority level")
    tags: List[str] = Field(..., description="Array of tags")
    created_at: datetime = Field(..., description="UTC timestamp of creation")
    updated_at: datetime = Field(..., description="UTC timestamp of last update")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "high",
                "tags": ["shopping", "urgent"],
                "created_at": "2026-01-02T12:00:00Z",
                "updated_at": "2026-01-02T12:00:00Z"
            }
        }
