"""Setup script for Phase 3 database tables.

This script creates the Conversation and Message tables for the AI Chatbot
using SQLModel metadata directly without relying on Alembic migrations.
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Change to the Phase II backend directory to access its structure
project_root = Path(__file__).parent.parent
phase2_backend_dir = project_root / "phase2-fullstack" / "backend"
phase3_models_dir = Path(__file__).parent / "backend" / "app" / "models"

# Add the Phase II backend to the Python path
sys.path.insert(0, str(phase2_backend_dir))

# Add the Phase III models directory to the Python path
sys.path.insert(0, str(phase3_models_dir))

# Change to the Phase II backend directory
os.chdir(phase2_backend_dir)

from sqlmodel import SQLModel, create_engine
from app.config import settings

# Import Phase II models to satisfy foreign key dependencies
from app.models.user import User  # noqa: F401
from app.models.todo import Todo  # noqa: F401

# Import Phase III models (relative to their location)
import sys
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.models.conversation import Conversation  # noqa: F401
from app.models.message import Message  # noqa: F401

def setup_database():
    """Create the database tables."""
    print("Setting up Phase 3 database tables...")

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)

    # Create all tables (only the new ones, existing tables will remain)
    SQLModel.metadata.create_all(engine)

    print("Database tables created successfully!")
    print("- Conversation table created")
    print("- Message table created")
    print("Migration completed!")

if __name__ == "__main__":
    setup_database()