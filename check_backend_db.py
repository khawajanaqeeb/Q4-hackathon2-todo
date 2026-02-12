from sqlmodel import SQLModel, create_engine, Session, select
from backend.src.models.user import User

def check_backend_users():
    # Create database engine for backend
    engine = create_engine("sqlite:///./backend/todo_app.db", echo=True)

    # Query users
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        print("All users in backend database:")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

if __name__ == "__main__":
    check_backend_users()