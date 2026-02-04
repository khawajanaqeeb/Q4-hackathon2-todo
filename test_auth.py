from sqlmodel import SQLModel, create_engine, Session, select
from backend.src.models.user import User
from backend.src.utils.security import verify_password

def test_authentication():
    # Create database engine
    engine = create_engine("sqlite:///./todo_app.db", echo=True)

    # Test authentication logic manually
    with Session(engine) as session:
        username = "testuser"

        # First, try to find user by username
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()

        print(f"Lookup by username '{username}': {'Found' if user else 'Not found'}")

        if not user:
            # If not found, try to find user by email
            statement = select(User).where(User.email == username)
            user = session.exec(statement).first()
            print(f"Lookup by email '{username}': {'Found' if user else 'Not found'}")

        if user:
            print(f"User found: ID={user.id}, Username={user.username}, Email={user.email}")

            # Test password verification
            password = "testpassword123!"
            is_valid = verify_password(password, user.hashed_password)
            print(f"Password verification: {is_valid}")

            if is_valid:
                print("Authentication successful!")
            else:
                print("Authentication failed - password mismatch")
        else:
            print("User not found in database")

if __name__ == "__main__":
    test_authentication()