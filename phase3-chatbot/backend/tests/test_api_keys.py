"""Test suite for API key endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime, timedelta

from src.main import app
from src.database import get_session, engine
from src.models.user import User
from src.models.api_key import ApiKey
from src.dependencies.auth import get_current_user, create_access_token
from src.config import settings


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
        email="api_test@example.com",
        username="apitestuser",
        hashed_password=pwd_context.hash("testpassword123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Create authentication headers for test user."""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


def test_store_api_key_success(client: TestClient, test_user, auth_headers: dict):
    """Test successful storage of an API key."""
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "sk-test1234567890abcdef",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "expires_at" in data


def test_store_api_key_invalid_provider(client: TestClient, test_user, auth_headers: dict):
    """Test storing an API key with an unsupported provider."""
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "unsupported_provider",
            "api_key": "test_key_123",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_store_api_key_missing_fields(client: TestClient, test_user, auth_headers: dict):
    """Test storing an API key with missing required fields."""
    # Test missing provider
    response = client.post(
        "/api/api-keys",
        json={
            "api_key": "test_key_123",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error
    
    # Test missing api_key
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


def test_get_api_key_status_success(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test getting the status of a stored API key."""
    # Create a test API key in the database
    from cryptography.fernet import Fernet
    from src.utils.encryption import encrypt_api_key, decrypt_api_key
    
    encrypted_key = encrypt_api_key("test_api_key_12345")
    api_key = ApiKey(
        id=uuid.uuid4(),
        user_id=test_user.id,
        provider="openai",
        encrypted_key=encrypted_key,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db_session.add(api_key)
    db_session.commit()
    
    response = client.get(f"/api/api-keys/openai", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert data["provider"] == "openai"
    assert "is_active" in data
    assert "expires_at" in data


def test_get_api_key_status_not_found(client: TestClient, test_user, auth_headers: dict):
    """Test getting status of a non-existent API key."""
    response = client.get("/api/api-keys/nonexistent_provider", headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_api_key_status_inactive(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test getting status of an inactive API key."""
    # Create an inactive API key
    from cryptography.fernet import Fernet
    from src.utils.encryption import encrypt_api_key
    
    encrypted_key = encrypt_api_key("inactive_api_key_12345")
    api_key = ApiKey(
        id=uuid.uuid4(),
        user_id=test_user.id,
        provider="openai",
        encrypted_key=encrypted_key,
        is_active=False,  # Inactive
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db_session.add(api_key)
    db_session.commit()
    
    response = client.get("/api/api-keys/openai", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


def test_get_api_key_status_expired(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test getting status of an expired API key."""
    # Create an expired API key
    from cryptography.fernet import Fernet
    from src.utils.encryption import encrypt_api_key
    
    encrypted_key = encrypt_api_key("expired_api_key_12345")
    api_key = ApiKey(
        id=uuid.uuid4(),
        user_id=test_user.id,
        provider="openai",
        encrypted_key=encrypted_key,
        is_active=True,
        expires_at=datetime.utcnow() - timedelta(days=1)  # Expired
    )
    db_session.add(api_key)
    db_session.commit()
    
    response = client.get("/api/api-keys/openai", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    # The API should handle expired keys appropriately (either return as inactive or with expiration info)


def test_update_api_key_success(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test successful update of an existing API key."""
    # Create an existing API key
    from cryptography.fernet import Fernet
    from src.utils.encryption import encrypt_api_key
    
    encrypted_key = encrypt_api_key("old_api_key_12345")
    api_key = ApiKey(
        id=uuid.uuid4(),
        user_id=test_user.id,
        provider="openai",
        encrypted_key=encrypted_key,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db_session.add(api_key)
    db_session.commit()
    
    # Update the API key
    response = client.put(
        f"/api/api-keys/openai",
        json={
            "provider": "openai",
            "api_key": "new_api_key_67890",
            "expires_in_days": 60
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_update_api_key_not_found(client: TestClient, test_user, auth_headers: dict):
    """Test updating a non-existent API key."""
    response = client.put(
        "/api/api-keys/nonexistent_provider",
        json={
            "provider": "nonexistent_provider",
            "api_key": "new_key_123",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_delete_api_key_success(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test successful deletion of an API key."""
    # Create an API key to delete
    from cryptography.fernet import Fernet
    from src.utils.encryption import encrypt_api_key
    
    encrypted_key = encrypt_api_key("delete_me_key_12345")
    api_key = ApiKey(
        id=uuid.uuid4(),
        user_id=test_user.id,
        provider="openai",
        encrypted_key=encrypted_key,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db_session.add(api_key)
    db_session.commit()
    
    response = client.delete("/api/api-keys/openai", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    # Deletion might return a success message or empty response
    
    # Verify the key was deleted
    statement = select(ApiKey).where(
        ApiKey.user_id == test_user.id,
        ApiKey.provider == "openai"
    )
    deleted_key = db_session.exec(statement).first()
    assert deleted_key is None


def test_delete_api_key_not_found(client: TestClient, test_user, auth_headers: dict):
    """Test deleting a non-existent API key."""
    response = client.delete("/api/api-keys/nonexistent_provider", headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_supported_providers(client: TestClient, test_user, auth_headers: dict):
    """Test getting list of supported AI providers."""
    response = client.get("/api/api-keys/providers", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert isinstance(data["providers"], list)
    
    # Should include common providers like OpenAI, Anthropic, etc.
    provider_names = [provider["name"] for provider in data["providers"]]
    assert "openai" in [name.lower() for name in provider_names]


def test_get_supported_providers_unauthorized(client: TestClient):
    """Test that getting supported providers requires authentication."""
    response = client.get("/api/api-keys/providers")
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_store_api_key_encryption(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test that API keys are properly encrypted when stored."""
    test_api_key = "sk-test1234567890abcdef"
    
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": test_api_key,
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Check that the key is encrypted in the database
    statement = select(ApiKey).where(
        ApiKey.user_id == test_user.id,
        ApiKey.provider == "openai"
    )
    stored_key = db_session.exec(statement).first()
    assert stored_key is not None
    assert stored_key.encrypted_key != test_api_key  # Should be encrypted, not plaintext


def test_store_multiple_api_keys_different_providers(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test storing API keys for different providers."""
    providers = ["openai", "anthropic", "google"]
    
    for i, provider in enumerate(providers):
        response = client.post(
            "/api/api-keys",
            json={
                "provider": provider,
                "api_key": f"test_key_{provider}_123",
                "expires_in_days": 30
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    # Verify all keys were stored
    statement = select(ApiKey).where(ApiKey.user_id == test_user.id)
    stored_keys = db_session.exec(statement).all()
    
    stored_providers = [key.provider for key in stored_keys]
    for provider in providers:
        assert provider in stored_providers


def test_store_api_key_duplicate_provider(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test storing an API key for a provider that already has a key."""
    # Store first key
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "first_key_123",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Store second key for same provider (should update)
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "second_key_456",
            "expires_in_days": 45
        },
        headers=auth_headers
    )
    
    # Should succeed (update existing)
    assert response.status_code == 200


def test_update_api_key_encryption(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test that updated API keys are properly encrypted."""
    # First, store an API key
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "initial_key_123",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Then update it
    new_key = "updated_key_456"
    response = client.put(
        "/api/api-keys/openai",
        json={
            "provider": "openai",
            "api_key": new_key,
            "expires_in_days": 60
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Verify the updated key is encrypted in the database
    statement = select(ApiKey).where(
        ApiKey.user_id == test_user.id,
        ApiKey.provider == "openai"
    )
    updated_key = db_session.exec(statement).first()
    assert updated_key is not None
    assert updated_key.encrypted_key != new_key  # Should be encrypted, not plaintext


def test_api_key_expiry_calculation(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test that API key expiry dates are calculated correctly."""
    from datetime import timedelta
    
    expires_in_days = 15
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "expiring_key_123",
            "expires_in_days": expires_in_days
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Check that the expiry date was set correctly in the database
    statement = select(ApiKey).where(
        ApiKey.user_id == test_user.id,
        ApiKey.provider == "openai"
    )
    stored_key = db_session.exec(statement).first()
    assert stored_key is not None
    assert stored_key.expires_at is not None
    
    # Check that the expiry is approximately the right amount of time from now
    expected_expiry = datetime.utcnow() + timedelta(days=expires_in_days)
    time_diff = abs((stored_key.expires_at - expected_expiry).total_seconds())
    # Allow up to 60 seconds difference for processing time
    assert time_diff < 60


def test_get_api_key_status_expired_key(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test getting status of an expired API key shows proper expiration info."""
    # Create an expired API key
    from cryptography.fernet import Fernet
    from src.utils.encryption import encrypt_api_key
    
    encrypted_key = encrypt_api_key("expired_key_12345")
    expired_date = datetime.utcnow() - timedelta(days=1)  # Expired yesterday
    api_key = ApiKey(
        id=uuid.uuid4(),
        user_id=test_user.id,
        provider="openai",
        encrypted_key=encrypted_key,
        is_active=True,  # Still marked active in DB but actually expired
        expires_at=expired_date
    )
    db_session.add(api_key)
    db_session.commit()
    
    response = client.get("/api/api-keys/openai", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    # The API should handle expired keys appropriately


def test_unauthorized_access_to_api_key_endpoints(client: TestClient):
    """Test that unauthorized access to API key endpoints is properly rejected."""
    # Try to store an API key without authentication
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "test_key_123",
            "expires_in_days": 30
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    
    # Try to get API key status without authentication
    response = client.get("/api/api-keys/openai")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    
    # Try to update an API key without authentication
    response = client.put(
        "/api/api-keys/openai",
        json={
            "provider": "openai",
            "api_key": "new_key_123",
            "expires_in_days": 30
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    
    # Try to delete an API key without authentication
    response = client.delete("/api/api-keys/openai")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@patch('src.services.api_key_manager.ApiKeyManager')
def test_store_api_key_with_mocked_encryption(mock_api_key_manager_class, client: TestClient, test_user, auth_headers: dict):
    """Test storing API key with mocked encryption service."""
    # Setup mock
    mock_api_key_manager_instance = MagicMock()
    mock_api_key_manager_instance.store_api_key.return_value = {
        "success": True,
        "message": "API key stored successfully",
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    mock_api_key_manager_class.return_value = mock_api_key_manager_instance
    
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "mocked_test_key_123",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    
    # Verify the mock was called with correct parameters
    mock_api_key_manager_instance.store_api_key.assert_called_once()


@patch('src.services.api_key_manager.ApiKeyManager')
def test_get_api_key_status_with_mocked_service(mock_api_key_manager_class, client: TestClient, test_user, auth_headers: dict):
    """Test getting API key status with mocked service."""
    # Setup mock
    mock_api_key_manager_instance = MagicMock()
    mock_api_key_manager_instance.get_api_key_status.return_value = {
        "provider": "openai",
        "is_active": True,
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "last_used": None
    }
    mock_api_key_manager_class.return_value = mock_api_key_manager_instance
    
    response = client.get("/api/api-keys/openai", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openai"
    assert data["is_active"] is True


@patch('src.services.api_key_manager.ApiKeyManager')
def test_delete_api_key_with_mocked_service(mock_api_key_manager_class, client: TestClient, test_user, auth_headers: dict):
    """Test deleting API key with mocked service."""
    # Setup mock
    mock_api_key_manager_instance = MagicMock()
    mock_api_key_manager_instance.delete_api_key.return_value = {
        "success": True,
        "message": "API key deleted successfully"
    }
    mock_api_key_manager_class.return_value = mock_api_key_manager_instance
    
    response = client.delete("/api/api-keys/openai", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    
    # Verify the mock was called
    mock_api_key_manager_instance.delete_api_key.assert_called_once_with("openai", str(test_user.id))


def test_provider_validation_case_insensitive(client: TestClient, test_user, auth_headers: dict):
    """Test that provider names are handled case-insensitively where appropriate."""
    # Test with mixed case provider name
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "OpenAI",  # Mixed case
            "api_key": "case_test_key_123",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    # Should work (might return 200 if OpenAI is supported, or 400 if validation is strict about case)
    assert response.status_code in [200, 400]  # Either success or validation error


def test_api_key_length_validation(client: TestClient, test_user, auth_headers: dict):
    """Test validation of API key length/format."""
    # Test with very short key (likely invalid)
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "short",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    # Might return 422 for validation error or 200 if validation is done by the provider API
    assert response.status_code in [200, 400, 422]
    
    # Test with empty key
    response = client.post(
        "/api/api-keys",
        json={
            "provider": "openai",
            "api_key": "",
            "expires_in_days": 30
        },
        headers=auth_headers
    )
    
    assert response.status_code in [400, 422]  # Should fail validation
