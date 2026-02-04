"""
Script to reset the database schema
"""
from backend.src.database import engine
from backend.src.models.user import User
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from backend.src.models.task import Task
from backend.src.models.api_key import ApiKey
from sqlmodel import SQLModel

def reset_database():
    """Drop and recreate all tables"""
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    print("Creating all tables...")
    SQLModel.metadata.create_all(engine)
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()