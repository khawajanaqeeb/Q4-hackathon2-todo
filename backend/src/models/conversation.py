from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class ConversationBase(SQLModel):
    title: str
    user_id: int

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, ForeignKey

class ConversationBase(SQLModel):
    title: str
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("user.id")))

class Conversation(ConversationBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

class ConversationRead(ConversationBase):
    id: str
    created_at: datetime
    updated_at: datetime

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(SQLModel):
    title: Optional[str] = None