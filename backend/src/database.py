from sqlmodel import create_engine, Session
from sqlalchemy import event
from sqlalchemy.pool import Pool
import os
from dotenv import load_dotenv
from .models import *  # Import all models to register them

load_dotenv()

# Database URL - defaults to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    """Create database tables."""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session

# For SQLite, we need to enable foreign key support
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()