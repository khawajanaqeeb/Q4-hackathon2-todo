import uuid
from sqlmodel import SQLModel, create_engine, Session, select
from datetime import datetime
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.src.models.user import User
from backend.src.utils.security import hash_password

def create_phase3_test_user():
    # Create database engine for phase3
    engine = create_engine("sqlite:///./backend/test_todo_app.db", echo=True)

    # Create tables
    SQLModel.metadata.create_all(engine)

    # Create a test user
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.username == "testuser3")).first()

        if not existing_user:
            hashed_password = hash_password("testpassword123!")

            test_user = User(
                username="testuser3",
                email="test3@example.com",
                hashed_password=hashed_password
            )

            session.add(test_user)
            session.commit()
            session.refresh(test_user)  # Refresh to get the generated ID
            print(f"Phase 3 test user created successfully! ID: {test_user.id}")
        else:
            print(f"Phase 3 test user already exists! ID: {existing_user.id}")

if __name__ == "__main__":
    create_phase3_test_user()