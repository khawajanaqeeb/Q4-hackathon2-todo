from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from sqlmodel import Session
from ..database import get_session
from ..models.user import User

# Import settings
from ..config import settings

# Security scheme for API docs (for header-based auth)
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token with expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


def get_current_user_from_token(token: str):
    """Helper function to get current user from token string."""
    token_data = verify_token(token)
    user_id = token_data.get("sub")

    # Import here to avoid circular imports
    from ..database import engine
    from sqlmodel import Session

    # Create a temporary session to fetch user
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user


async def get_current_user(
    request: Request,
    session: Session = Depends(get_session)
):
    """Get current user from token (from either Authorization header or auth_token cookie)."""
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

    # Verify the token and get user data
    try:
        token_data = verify_token(token)
        user_id = token_data.get("sub")

        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid token)
        raise
    except Exception:
        # For any other error during token verification, return 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )