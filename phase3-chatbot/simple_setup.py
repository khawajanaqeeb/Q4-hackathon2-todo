"""Simple setup script for Phase 3 database tables."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the phase2 backend to the path to get the config and models
phase2_backend_path = Path(__file__).parent.parent / "phase2-fullstack" / "backend"
sys.path.insert(0, str(phase2_backend_path))

# Import settings from Phase II
from app.config import settings

# Import SQLModel and create engine
from sqlmodel import SQLModel, create_engine, Field, Relationship
from typing import List, Optional
from datetime import datetime
import uuid
from enum import Enum
from sqlalchemy import Column, JSON

# Import the existing User model to satisfy foreign key constraints
from app.models.user import User  # noqa: F401

# Define the Conversation model
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(default="New Conversation", max_length=200)
    user_id: int = Field(foreign_key="users.id", index=True)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                 sa_column_kwargs={"onupdate": datetime.utcnow})

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column_kwargs={"name": "role"})
    content: str = Field(sa_column_kwargs={"server_default": ""})
    status: MessageStatus = Field(default=MessageStatus.PROCESSED)

    tool_name: Optional[str] = Field(default=None, max_length=100)
    tool_input: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tool_output: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                 sa_column_kwargs={"onupdate": datetime.utcnow})

def setup_database():
    """Create the database tables."""
    print("Setting up Phase 3 database tables...")

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)

    # Create all tables
    SQLModel.metadata.create_all(engine)

    print("Database tables created successfully!")
    print("- Conversation table created")
    print("- Message table created")
    print("Migration completed!")

if __name__ == "__main__":
    setup_database()