"""Todo API endpoints for Phase 3 backend that map to Task model.

This module provides API endpoints that maintain compatibility with the
existing frontend expecting /api/todos endpoints, but uses the Phase 3
Task model instead of the legacy Todo model.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid
import json

from ..database import get_session
from ..models.task import Task, PriorityLevel
from ..models.user import User
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/todos")

# Schemas for API compatibility
from pydantic import BaseModel, field_validator

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"  # low, medium, high
    tags: Optional[List[str]] = None
    due_date: Optional[str] = None

class TodoCreate(TodoBase):
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        if isinstance(v, str):
            try:
                # If it's a string representation of an array, parse it
                if v.startswith('[') and v.endswith(']'):
                    return json.loads(v)
                else:
                    # If it's a single tag as string, convert to array
                    return [v] if v else None
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, return as single item array
                return [v] if v else None
        return v

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[str] = None

    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags_update(cls, v):
        if isinstance(v, str):
            try:
                # If it's a string representation of an array, parse it
                if v.startswith('[') and v.endswith(']'):
                    return json.loads(v)
                else:
                    # If it's a single tag as string, convert to array
                    return [v] if v else None
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, return as single item array
                return [v] if v else None
        return v

class TodoResponse(TodoBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


def priority_level_to_string(priority: PriorityLevel) -> str:
    """Convert PriorityLevel enum to string."""
    mapping = {
        PriorityLevel.LOW: "low",
        PriorityLevel.MEDIUM: "medium",
        PriorityLevel.HIGH: "high"
    }
    return mapping.get(priority, "medium")


def string_to_priority_level(priority_str: str) -> PriorityLevel:
    """Convert string priority to PriorityLevel enum."""
    mapping = {
        "low": PriorityLevel.LOW,
        "medium": PriorityLevel.MEDIUM,
        "high": PriorityLevel.HIGH
    }
    return mapping.get(priority_str, PriorityLevel.MEDIUM)


def task_to_todo_response(task: Task) -> TodoResponse:
    """Convert Task model to TodoResponse for API compatibility."""
    # Convert tags from JSON string back to array for frontend compatibility
    # The frontend expects tags as an array to call .join(',')
    tags_value = task.tags
    if task.tags and isinstance(task.tags, str):
        try:
            # If tags is a JSON string (like "[\"urgent\", \"work\"]"), parse it to an array
            if task.tags.startswith('"[') and task.tags.endswith(']"'):
                # This handles cases where the JSON string is double-encoded like "[\"urgent\"]"
                cleaned_string = task.tags[1:-1]  # Remove outer quotes
                tags_value = json.loads(cleaned_string)
            elif task.tags.startswith('[') and task.tags.endswith(']'):
                tags_value = json.loads(task.tags)
            else:
                # If it's not a JSON array, treat as a single tag or leave as is
                tags_value = [task.tags] if task.tags else None
        except (json.JSONDecodeError, TypeError):
            # If parsing fails, treat as a single tag in an array
            tags_value = [task.tags] if task.tags else None
    elif task.tags is None:
        tags_value = None

    return TodoResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=priority_level_to_string(task.priority),
        tags=tags_value,  # Array if it was a JSON string, otherwise as a single-item array
        due_date=task.due_date.isoformat() if task.due_date else None,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat()
    )


@router.get("/", response_model=List[TodoResponse])
def get_todos(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    completed: Optional[bool] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    Get tasks for the current user with optional filtering and pagination.
    Maps to the Task model for Phase 3 compatibility.
    """
    query = select(Task).where(Task.user_id == current_user.id)

    # Apply filters
    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority is not None:
        priority_enum = string_to_priority_level(priority)
        query = query.where(Task.priority == priority_enum)

    if search:
        query = query.where(
            Task.title.contains(search) | Task.description.contains(search)
        )

    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())

    tasks = session.exec(query).all()
    return [task_to_todo_response(task) for task in tasks]


@router.post("/", response_model=TodoResponse)
def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the current user.
    Maps to the Task model for Phase 3 compatibility.
    """
    # Convert tags from array to JSON string for storage
    tags_string = None
    if todo.tags is not None:
        try:
            tags_string = json.dumps(todo.tags)
        except (TypeError, ValueError):
            # If conversion fails, store as is
            tags_string = todo.tags

    # Convert todo to task
    task = Task(
        user_id=current_user.id,
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        priority=string_to_priority_level(todo.priority),
        tags=tags_string,
        due_date=datetime.fromisoformat(todo.due_date) if todo.due_date else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    session.commit()
    session.refresh(task)
    return task_to_todo_response(task)


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task for the current user.
    Maps to the Task model for Phase 3 compatibility.
    """
    try:
        task_id = uuid.UUID(todo_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )

    db_task = session.get(Task, task_id)

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Update the task with provided values
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "priority" and value:
                setattr(db_task, field, string_to_priority_level(value))
            elif field == "due_date" and value:
                setattr(db_task, field, datetime.fromisoformat(value))
            elif field == "tags":
                # Convert tags from array to JSON string for storage
                try:
                    tags_string = json.dumps(value) if value is not None else None
                    setattr(db_task, field, tags_string)
                except (TypeError, ValueError):
                    # If conversion fails, set as is
                    setattr(db_task, field, value)
            else:
                setattr(db_task, field, value)

    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return task_to_todo_response(db_task)


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task for the current user.
    Maps to the Task model for Phase 3 compatibility.
    """
    try:
        task_id = uuid.UUID(todo_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )

    db_task = session.get(Task, task_id)

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted successfully"}


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo_completion(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a specific task for the current user.
    Maps to the Task model for Phase 3 compatibility.
    """
    try:
        task_id = uuid.UUID(todo_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )

    db_task = session.get(Task, task_id)

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to toggle this task"
        )

    # Toggle the completion status
    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return task_to_todo_response(db_task)