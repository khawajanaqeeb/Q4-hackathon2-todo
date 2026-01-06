import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models.user import User


# Create a test database
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "name": "Test User", "password": "SecurePass123!"}
    )
    assert response.status_code == 201  # 201 Created as set in the endpoint
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


def test_register_user_weak_password(client: TestClient):
    # Test weak password (no special character)
    response = client.post(
        "/auth/register",
        json={"email": "test2@example.com", "name": "Test User", "password": "weakpass123"}
    )
    assert response.status_code == 400
    # The password is weak because it doesn't have uppercase letter, number, or special char
    assert "uppercase" in response.json()["detail"].lower() or "special character" in response.json()["detail"].lower()


def test_login_user(client: TestClient):
    # First register a user
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "name": "Test User", "password": "SecurePass123!"}
    )

    # Then try to login - OAuth2PasswordRequestForm expects "username" and "password"
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "SecurePass123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_invalid_credentials(client: TestClient):
    # First register a user
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "name": "Test User", "password": "SecurePass123!"}
    )

    # Try to login with wrong password - OAuth2PasswordRequestForm expects "username" and "password"
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_refresh_token(client: TestClient):
    # First register a user
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "name": "Test User", "password": "SecurePass123!"}
    )

    # Login to get tokens - OAuth2PasswordRequestForm expects "username" and "password"
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "SecurePass123!"}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]

    # Use refresh token to get new access token - refresh expects form data
    refresh_response = client.post(
        "/auth/refresh",
        data={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert "refresh_token" in refresh_data
    assert refresh_data["token_type"] == "bearer"


def test_refresh_token_invalid(client: TestClient):
    # Try to refresh with invalid token - refresh expects form data
    response = client.post(
        "/auth/refresh",
        data={"refresh_token": "invalid_token"}
    )
    assert response.status_code == 401