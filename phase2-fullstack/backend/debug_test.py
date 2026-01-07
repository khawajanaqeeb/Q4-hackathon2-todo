import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Mock environment variables before importing the app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_purposes_only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session

def test_with_overrides():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)

    # Test register
    print("Testing registration...")
    register_response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "name": "Test User", "password": "SecurePass123!"}
    )
    print(f"Register status: {register_response.status_code}")
    print(f"Register response: {register_response.json() if register_response.status_code != 201 else 'Success'}")

    if register_response.status_code == 201:
        print("Testing login...")
        login_response = client.post(
            "/auth/login",
            data={"username": "test@example.com", "password": "SecurePass123!"}
        )
        print(f"Login status: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"Login response: {login_response.json()}")
            print(f"Login text: {login_response.text}")
        else:
            print(f"Login response: {login_response.json()}")
    else:
        print("Registration failed, skipping login test")

if __name__ == "__main__":
    test_with_overrides()