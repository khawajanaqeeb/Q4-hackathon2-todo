from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class UserBase(SQLModel):
    username: str = Field(unique=True, nullable=False)
    email: str = Field(unique=True, nullable=False)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    todos: List["Todo"] = Relationship(back_populates="user", cascade_delete=True)

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None