"""Initialize database models for Phase 3 AI Chatbot.

This script ensures that the Conversation and Message tables are created
in the database according to the SQLModel definitions.
"""
from sqlmodel import SQLModel, create_engine
from app.models.conversation import Conversation
from app.models.message import Message
from ..config import settings  # Use Phase 3 settings instead of Phase 2


def init_db():
    """Initialize the database with Conversation and Message tables."""
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)

    # Create all tables (only the new ones, existing tables will remain)
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()