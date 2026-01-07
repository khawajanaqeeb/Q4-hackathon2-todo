from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from ..database import get_session
from ..models.todo import Todo, Priority
from ..schemas.todo import TodoCreate, TodoUpdate, TodoResponse as TodoRead
from ..models.user import User
from ..dependencies.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TodoRead])
def get_todos(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    completed: Optional[bool] = Query(None),
    priority: Optional[Priority] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    Get todos for the current user with optional filtering and pagination.
    """
    query = select(Todo).where(Todo.user_id == current_user.id)

    # Apply filters
    if completed is not None:
        query = query.where(Todo.completed == completed)

    if priority is not None:
        query = query.where(Todo.priority == priority)

    if search:
        query = query.where(
            Todo.title.contains(search) | Todo.description.contains(search)
        )

    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Todo.created_at.desc())

    todos = session.exec(query).all()
    return todos

@router.post("/", response_model=TodoRead)
def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new todo for the current user.
    """
    db_todo = Todo(**todo.model_dump(), user_id=current_user.id)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@router.put("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific todo for the current user.
    """
    db_todo = session.get(Todo, todo_id)

    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    if db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this todo"
        )

    # Update the todo with provided values
    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific todo for the current user.
    """
    db_todo = session.get(Todo, todo_id)

    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    if db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this todo"
        )

    session.delete(db_todo)
    session.commit()
    return {"message": "Todo deleted successfully"}

@router.patch("/{todo_id}/toggle", response_model=TodoRead)
def toggle_todo_completion(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a specific todo for the current user.
    """
    db_todo = session.get(Todo, todo_id)

    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    if db_todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to toggle this todo"
        )

    # Toggle the completion status
    db_todo.completed = not db_todo.completed
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo