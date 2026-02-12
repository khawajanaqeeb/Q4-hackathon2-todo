import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'phase3-chatbot'))

from backend.src.database import create_db_and_tables, engine
from backend.src.models.mcp_tool import McpTool
from sqlmodel import select
from sqlmodel import SQLModel

def reset_database():
    """Reset the database and recreate tables."""
    print("Creating database tables...")

    # Drop and recreate all tables
    from backend.src.models.user import User
    from backend.src.models.task import Task
    from backend.src.models.conversation import Conversation
    from backend.src.models.message import Message
    from backend.src.models.mcp_tool import McpTool
    from backend.src.models.api_key import ApiKey
    from backend.src.models.audit_log import AuditLog

    # Drop all tables first
    SQLModel.metadata.drop_all(engine)

    # Create all tables
    create_db_and_tables()

    print("Database tables recreated successfully!")

    # Verify McpTool table exists
    from sqlmodel import create_engine, text
    with engine.connect() as conn:
        # Check if the table exists and has the right columns
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='mcp_tools';"))
        tables = result.fetchall()
        print(f"McpTool table exists: {len(tables) > 0}")

        if tables:
            # Check columns
            result = conn.execute(text("PRAGMA table_info(mcp_tools);"))
            columns = result.fetchall()
            print("Columns in mcp_tools table:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")

if __name__ == "__main__":
    reset_database()