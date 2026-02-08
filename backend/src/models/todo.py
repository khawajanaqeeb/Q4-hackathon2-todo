from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class TodoBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(default="medium", max_length=20)  # low, medium, high
    due_date: Optional[datetime] = None
    tags: Optional[str] = None  # JSON string of tags array

class Todo(TodoBase, table=True):
    __tablename__ = "todos"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key
    user_id: int = Field(foreign_key="users.id")

    # Relationships
    user: "User" = Relationship(back_populates="todos")

class TodoRead(TodoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class TodoCreate(TodoBase):
    pass

class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None  # low, medium, high
    due_date: Optional[datetime] = None
    tags: Optional[str] = None