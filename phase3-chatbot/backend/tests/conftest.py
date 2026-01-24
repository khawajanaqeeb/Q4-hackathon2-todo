"""Pytest configuration and shared fixtures."""
import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Mock environment variables before importing the app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_purposes_only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

from app.main import app
from app.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """
    Create an in-memory SQLite database for testing.

    Yields a database session with all tables created.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create a test client with overridden database session.

    Args:
        session: Test database session fixture

    Returns:
        FastAPI TestClient
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient, session: Session):
    """
    Create a test user and return authentication headers.

    Args:
        client: Test client fixture
        session: Test database session

    Returns:
        Dictionary with Authorization header containing JWT token
    """
    # Register a test user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "SecureTestPass123!"
        }
    )
    assert register_response.status_code == 201

    # Login to get JWT token
    login_response = client.post(
        "/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "SecureTestPass123!"
        }
    )
    assert login_response.status_code == 200
    token_data = login_response.json()

    # Return authorization headers
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
def auth_headers_user2(client: TestClient, session: Session):
    """
    Create a second test user and return authentication headers.
    Used for testing user isolation (ensuring users can't access each other's data).

    Args:
        client: Test client fixture
        session: Test database session

    Returns:
        Dictionary with Authorization header containing JWT token for second user
    """
    # Register a second test user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "testuser2@example.com",
            "name": "Test User 2",
            "password": "SecureTestPass456!"
        }
    )
    assert register_response.status_code == 201

    # Login to get JWT token
    login_response = client.post(
        "/auth/login",
        data={
            "username": "testuser2@example.com",
            "password": "SecureTestPass456!"
        }
    )
    assert login_response.status_code == 200
    token_data = login_response.json()

    # Return authorization headers
    return {"Authorization": f"Bearer {token_data['access_token']}"}
