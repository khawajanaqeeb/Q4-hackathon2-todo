import sys
import os

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import create_db_and_tables

def init_db():
    """Initialize the database by creating all tables"""
    print("Initializing database...")
    create_db_and_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()