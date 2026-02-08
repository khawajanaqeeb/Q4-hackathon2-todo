from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey

class ConversationBase(SQLModel):
    title: str
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id")))
    status: str = Field(default="active")  # active, archived, deleted

class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata_json: Optional[str] = Field(default=None)  # JSON string for additional context

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

class ConversationRead(ConversationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    metadata_json: Optional[str]

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(SQLModel):
    title: Optional[str] = None
    status: Optional[str] = None
    metadata_json: Optional[str] = None

# TodoOperationLog model as specified in task T015
class TodoOperationLogBase(SQLModel):
    conversation_id: str = Field(sa_column=Column(String, ForeignKey("conversations.id")))
    message_id: str  # Reference to message that triggered the operation
    operation: str = Field(max_length=20)  # create, update, delete, complete
    todo_id: str  # ID of the affected todo item
    previous_state: Optional[str] = Field(default=None)  # JSON string of state before operation
    new_state: Optional[str] = Field(default=None)  # JSON string of state after operation

class TodoOperationLog(TodoOperationLogBase, table=True):
    __tablename__ = "todo_operation_logs"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="todo_operation_logs")

class TodoOperationLogRead(TodoOperationLogBase):
    id: str
    timestamp: datetime

class TodoOperationLogCreate(TodoOperationLogBase):
    pass

class TodoOperationLogUpdate(SQLModel):
    previous_state: Optional[str] = None
    new_state: Optional[str] = None