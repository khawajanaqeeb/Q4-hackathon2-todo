from sqlmodel import SQLModel, create_engine, Session, select
from backend.src.models.user import User

def check_users():
    # Create database engine
    engine = create_engine("sqlite:///./todo_app.db", echo=True)

    # Query users
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        print("All users in database:")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

if __name__ == "__main__":
    check_users()