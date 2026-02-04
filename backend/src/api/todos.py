from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session
from typing import List
from datetime import datetime

from ..models.todo import Todo, TodoCreate, TodoUpdate, TodoRead
from ..models.user import User
from ..services.todo import (
    create_todo, get_todos, get_todo, update_todo, delete_todo, complete_todo
)
from ..database import get_session
from ..services.auth import get_current_user

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("/", response_model=None)
@limiter.limit("20 per minute")
def read_todos(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get todos for the current user."""
    todos = get_todos(session, current_user.id, skip=skip, limit=limit)
    return todos


@router.post("/", response_model=None)
@limiter.limit("10 per minute")
def create_todo_item(
    request: Request,
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new todo for the current user."""
    db_todo = create_todo(session, todo, current_user.id)
    return db_todo


@router.get("/{todo_id}", response_model=None)
@limiter.limit("20 per minute")
def read_todo(
    request: Request,
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific todo by ID for the current user."""
    db_todo = get_todo(session, todo_id, current_user.id)

    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return db_todo


@router.put("/{todo_id}", response_model=None)
@limiter.limit("10 per minute")
def update_todo_item(
    request: Request,
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a specific todo for the current user."""
    db_todo = update_todo(session, todo_id, todo_update, current_user.id)

    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return db_todo


@router.patch("/{todo_id}/complete", response_model=None)
@limiter.limit("10 per minute")
def complete_todo_item(
    request: Request,
    todo_id: int,
    completed: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Mark a specific todo as completed/uncompleted for the current user."""
    db_todo = complete_todo(session, todo_id, current_user.id, completed)

    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return {"id": db_todo.id, "completed": db_todo.completed}


@router.delete("/{todo_id}", response_model=None)
@limiter.limit("10 per minute")
def delete_todo_item(
    request: Request,
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific todo for the current user."""
    success = delete_todo(session, todo_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return {"message": "Todo deleted successfully"}