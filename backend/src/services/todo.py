from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from ..models.todo import Todo, TodoCreate, TodoUpdate, TodoRead
from ..models.user import User


def create_todo(session: Session, todo: TodoCreate, user_id: int) -> Todo:
    """Create a new todo for a user."""
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        priority=todo.priority,
        due_date=todo.due_date,
        tags=todo.tags,
        user_id=user_id
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


def get_todos(session: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Todo]:
    """Get todos for a specific user."""
    statement = select(Todo).where(Todo.user_id == user_id).offset(skip).limit(limit)
    todos = session.exec(statement).all()
    return todos


def get_todo(session: Session, todo_id: int, user_id: int) -> Optional[Todo]:
    """Get a specific todo by ID for a specific user."""
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    return session.exec(statement).first()


def update_todo(session: Session, todo_id: int, todo_update: TodoUpdate, user_id: int) -> Optional[Todo]:
    """Update a specific todo for a specific user."""
    db_todo = get_todo(session, todo_id, user_id)

    if not db_todo:
        return None

    todo_data = todo_update.dict(exclude_unset=True)
    for key, value in todo_data.items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


def delete_todo(session: Session, todo_id: int, user_id: int) -> bool:
    """Delete a specific todo for a specific user."""
    db_todo = get_todo(session, todo_id, user_id)

    if not db_todo:
        return False

    session.delete(db_todo)
    session.commit()

    return True


def complete_todo(session: Session, todo_id: int, user_id: int, completed: bool) -> Optional[Todo]:
    """Mark a specific todo as completed/uncompleted for a specific user."""
    db_todo = get_todo(session, todo_id, user_id)

    if not db_todo:
        return None

    db_todo.completed = completed
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo