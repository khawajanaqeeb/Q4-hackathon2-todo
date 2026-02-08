from sqlmodel import create_engine, Session
from sqlalchemy import event
from sqlalchemy.pool import Pool
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/chatbot_todo_db")

# Create engine with connection pooling settings
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Additional connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections after 5 minutes
)


def create_db_and_tables():
    """Create database tables."""
    from sqlmodel import SQLModel
    # Import all models to register them with SQLModel metadata
    from .models.user import User
    from .models.conversation import Conversation
    from .models.message import Message
    from .models.task import Task
    from .models.api_key import ApiKey
    from .models.mcp_tool import McpTool
    from .models.audit_log import AuditLog

    # Create tables
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(engine) as session:
        yield session


# Optional: Add event listeners for connection debugging
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragma for foreign key support (only needed if using SQLite)."""
    if 'sqlite' in str(engine.url):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()