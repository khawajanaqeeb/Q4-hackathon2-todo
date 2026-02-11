"""Pytest configuration and shared fixtures — uses Neon DB (real PostgreSQL)."""
import pytest
import random
import string
from fastapi.testclient import TestClient
from sqlmodel import Session
from passlib.context import CryptContext

from src.main import app
from src.database import get_session, engine
from src.models.user import User
from src.dependencies.auth import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _random_suffix(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


@pytest.fixture(name="session")
def session_fixture():
    """Yield a database session connected to Neon DB."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a FastAPI TestClient with the Neon DB session injected."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a unique test user in Neon DB, clean up after test."""
    suffix = _random_suffix()
    user = User(
        email=f"test_{suffix}@example.com",
        username=f"testuser_{suffix}",
        hashed_password=pwd_context.hash("SecureTestPass123!"),
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user
    # Cleanup
    session.delete(user)
    session.commit()


@pytest.fixture(name="test_user2")
def test_user2_fixture(session: Session):
    """Create a second unique test user for isolation tests."""
    suffix = _random_suffix()
    user = User(
        email=f"test2_{suffix}@example.com",
        username=f"testuser2_{suffix}",
        hashed_password=pwd_context.hash("SecureTestPass456!"),
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user
    # Cleanup
    session.delete(user)
    session.commit()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """Return Authorization headers for the first test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="auth_headers2")
def auth_headers2_fixture(test_user2: User):
    """Return Authorization headers for the second test user."""
    token = create_access_token(data={"sub": str(test_user2.id)})
    return {"Authorization": f"Bearer {token}"}
