"""Test suite for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from uuid import uuid4
import uuid

from src.main import app
from src.database import get_session, engine
from src.models.user import User
from src.dependencies.auth import get_current_user
from src.config import settings
from src.utils.security import create_access_token


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password=pwd_context.hash("testpassword123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_register_success(client: TestClient, db_session: Session):
    """Test successful user registration."""
    response = client.post(
        "/auth/register",
        data={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "username": "newuser"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    
    # Verify user was created in database
    statement = select(User).where(User.email == "newuser@example.com")
    user = db_session.exec(statement).first()
    assert user is not None
    assert user.username == "newuser"


def test_register_weak_password(client: TestClient):
    """Test registration with weak password."""
    response = client.post(
        "/auth/register",
        data={
            "email": "weakpass@example.com",
            "password": "123",  # Too weak
            "username": "weakuser"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_register_duplicate_email(client: TestClient, test_user: User):
    """Test registration with duplicate email."""
    response = client.post(
        "/auth/register",
        data={
            "email": test_user.email,
            "password": "AnotherPass123!",
            "username": "anotheruser"
        }
    )
    
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert "already registered" in data["detail"]


def test_register_duplicate_username(client: TestClient, test_user: User):
    """Test registration with duplicate username."""
    response = client.post(
        "/auth/register",
        data={
            "email": "different@example.com",
            "password": "AnotherPass123!",
            "username": test_user.username
        }
    )
    
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert "already taken" in data["detail"]


def test_login_success(client: TestClient, test_user: User):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,  # Can use email as username
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_username(client: TestClient, test_user: User):
    """Test successful login using username instead of email."""
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_login_inactive_user(client: TestClient, db_session: Session):
    """Test login with inactive user."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    inactive_user = User(
        id=uuid.uuid4(),
        email="inactive@example.com",
        username="inactiveuser",
        hashed_password=pwd_context.hash("testpassword123"),
        is_active=False,  # Inactive user
        is_superuser=False
    )
    db_session.add(inactive_user)
    db_session.commit()
    
    response = client.post(
        "/auth/login",
        data={
            "username": "inactive@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "inactive" in data["detail"]


def test_logout(client: TestClient):
    """Test logout functionality."""
    response = client.post("/auth/logout")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out"


def test_verify_token_success(client: TestClient, test_user: User):
    """Test token verification with valid token."""
    # Create a valid token for the test user
    token = create_access_token(data={"sub": str(test_user.id), "username": test_user.username, "email": test_user.email})
    
    response = client.post(
        "/auth/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_verify_token_invalid(client: TestClient):
    """Test token verification with invalid token."""
    response = client.post(
        "/auth/verify",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_verify_token_missing(client: TestClient):
    """Test token verification without token."""
    response = client.post("/auth/verify")
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data