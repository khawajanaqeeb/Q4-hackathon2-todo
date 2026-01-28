from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class MessageBase(SQLModel):
    conversation_id: str
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str

class Message(MessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

class MessageRead(MessageBase):
    id: int
    timestamp: datetime

class MessageCreate(MessageBase):
    pass

class MessageUpdate(SQLModel):
    content: Optional[str] = None