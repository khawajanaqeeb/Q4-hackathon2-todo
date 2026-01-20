"""Verification script to confirm Phase 3 database tables were created."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the phase2 backend to the path to get the config
phase2_backend_path = Path(__file__).parent.parent / "phase2-fullstack" / "backend"
sys.path.insert(0, str(phase2_backend_path))

# Import settings from Phase II
from app.config import settings

# Import SQLModel and create engine
from sqlmodel import SQLModel, create_engine, text
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum
from sqlalchemy import inspect

def verify_tables():
    """Verify that the database tables were created."""
    print("Verifying Phase 3 database tables...")

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)

    # Get inspector to check for tables
    inspector = inspect(engine)

    # Get list of table names
    table_names = inspector.get_table_names()

    print(f"Found {len(table_names)} tables in the database:")
    for table in sorted(table_names):
        print(f"  - {table}")

    # Check for our specific tables
    required_tables = ['conversations', 'messages']
    missing_tables = [table for table in required_tables if table not in table_names]

    if missing_tables:
        print(f"\n[X] Missing tables: {missing_tables}")
        return False
    else:
        print(f"\n[V] All required tables created successfully!")

        # Show details for the new tables
        for table_name in ['conversations', 'messages']:
            print(f"\nDetails for {table_name}:")
            columns = inspector.get_columns(table_name)
            for col in columns:
                print(f"  - {col['name']}: {col['type']} ({'nullable' if col['nullable'] else 'not nullable'})")

        return True

if __name__ == "__main__":
    success = verify_tables()
    if success:
        print("\n[SUCCESS] Phase 3 database schema setup completed successfully!")
    else:
        print("\n[ERROR] Phase 3 database schema setup failed!")
        sys.exit(1)