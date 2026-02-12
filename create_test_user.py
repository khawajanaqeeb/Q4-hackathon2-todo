import asyncio
from sqlmodel import SQLModel, create_engine, Session, select
from uuid import uuid4
from datetime import datetime
from backend.src.models.user import User
from backend.src.utils.security import get_password_hash

def create_test_user():
    # Create database engine for backend
    engine = create_engine("sqlite:///./backend/todo_app.db", echo=True)

    # Create tables
    SQLModel.metadata.create_all(engine)

    # Create a test user
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.username == "testuser")).first()

        if not existing_user:
            hashed_password = get_password_hash("testpassword123!")

            test_user = User(
                id=1,  # Using integer ID for the main backend
                username="testuser",
                email="test@example.com",
                hashed_password=hashed_password
            )

            session.add(test_user)
            session.commit()
            print("Test user created successfully!")
        else:
            print("Test user already exists!")

if __name__ == "__main__":
    create_test_user()