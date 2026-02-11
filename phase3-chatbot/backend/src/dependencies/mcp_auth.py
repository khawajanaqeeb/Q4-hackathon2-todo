from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session
from ..config import settings
from ..models.user import User
from ..database import get_session


security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create an access token with the provided data.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token data

    Raises:
        JWTError: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


async def get_current_user(
    request: Request,
    session: Session = Depends(get_session)
) -> User:
    """
    Get the current authenticated user based on the JWT token from either header or cookie.

    Args:
        request: FastAPI request object
        session: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    token = None

    # First, try to get token from Authorization header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
    elif auth_header and auth_header.startswith("bearer "):  # Case insensitive
        token = auth_header[len("bearer "):]

    # If not found in header, try to get from auth_token cookie
    if not token:
        token = request.cookies.get("auth_token")

    # If still no token, raise unauthorized
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user, verifying that they are active.

    Args:
        current_user: Current authenticated user

    Returns:
        Active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_api_key_permission(user: User, required_permission: str) -> bool:
    """
    Verify that the user has the required permission for API key operations.

    Args:
        user: User to check permissions for
        required_permission: Permission required for the operation

    Returns:
        True if user has the required permission, False otherwise
    """
    # For now, we'll implement a simple permission system
    # In a real application, you'd have roles and permissions
    if required_permission == "api_key_management":
        # For now, all active users can manage their own API keys
        return True

    if required_permission == "admin_api_key_management":
        # Only admin users can manage API keys for other users
        return getattr(user, 'is_admin', False)

    return False


def check_api_key_access(user: User, target_user_id: str) -> bool:
    """
    Check if a user has access to manage API keys for a target user.

    Args:
        user: Requesting user
        target_user_id: Target user ID

    Returns:
        True if access is granted, False otherwise
    """
    # Users can manage their own API keys
    if user.id == target_user_id:
        return True

    # Admins can manage API keys for other users
    if getattr(user, 'is_admin', False):
        return True

    return False


def get_required_api_key_scopes(required_scopes: list[str]):
    """
    Dependency to verify that the token has the required scopes.

    Args:
        required_scopes: List of required scopes

    Returns:
        Callable dependency function
    """
    async def verify_scopes(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        token = credentials.credentials
        payload = verify_token(token)

        # Check if token has required scopes
        token_scopes = payload.get("scopes", [])
        for scope in required_scopes:
            if scope not in token_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}"
                )

        return payload

    return verify_scopes


def rate_limit_check(user_id: str, action: str = "default"):
    """
    Check if the user has exceeded rate limits for the specified action.

    Args:
        user_id: User ID to check rate limits for
        action: Action type to check rate limits for

    Returns:
        True if within rate limits, raises HTTPException if exceeded
    """
    # This would typically integrate with a rate limiting service
    # For now, we'll return True to allow all requests
    # In a real implementation, this would check Redis or similar
    return True


def validate_api_key_format(api_key: str, provider: str) -> bool:
    """
    Validate the format of an API key for a specific provider.

    Args:
        api_key: API key to validate
        provider: Provider name

    Returns:
        True if valid format, False otherwise
    """
    if not api_key or len(api_key) < 10:
        return False

    # Basic provider-specific validation
    if provider.lower() == "openai":
        # OpenAI keys typically start with 'sk-'
        return api_key.startswith('sk-') and len(api_key) >= 40
    elif provider.lower() == "anthropic":
        # Anthropic keys typically start with 'sk-ant-'
        return api_key.startswith('sk-ant-') and len(api_key) >= 50
    else:
        # For other providers, just check minimum length
        return len(api_key) >= 20

    return True