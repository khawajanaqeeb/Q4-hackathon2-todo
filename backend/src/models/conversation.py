from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class ConversationBase(SQLModel):
    title: str
    user_id: int

class Conversation(ConversationBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship()
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

class ConversationRead(ConversationBase):
    id: str
    created_at: datetime
    updated_at: datetime

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(SQLModel):
    title: Optional[str] = None