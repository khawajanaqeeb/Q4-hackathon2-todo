"""
Script to create the database tables
"""
from backend.src.database import engine
from backend.src.models.user import User
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from backend.src.models.task import Task
from backend.src.models.api_key import ApiKey
from sqlmodel import SQLModel

def create_tables():
    """Create all tables"""
    print("Creating all tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()