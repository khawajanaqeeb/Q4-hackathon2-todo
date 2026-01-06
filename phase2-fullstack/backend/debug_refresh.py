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

def test_refresh():
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
    if register_response.status_code == 201:
        print("Registration successful")
    else:
        print(f"Registration failed: {register_response.json()}")

    # Test login
    print("\nTesting login...")
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "SecurePass123!"}
    )
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"Login successful, refresh token: {login_data.get('refresh_token')[:30]}...")

        # Test refresh
        print("\nTesting refresh...")
        refresh_response = client.post(
            "/auth/refresh",
            data={"refresh_token": login_data["refresh_token"]}
        )
        print(f"Refresh status: {refresh_response.status_code}")
        if refresh_response.status_code != 200:
            print(f"Refresh response: {refresh_response.json()}")
            print(f"Refresh text: {refresh_response.text}")
        else:
            print(f"Refresh successful: {refresh_response.json()}")
    else:
        print(f"Login failed: {login_response.json()}")

if __name__ == "__main__":
    test_refresh()