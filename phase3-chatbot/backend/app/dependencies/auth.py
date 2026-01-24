"""Authentication dependencies for FastAPI."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.utils.security import decode_access_token

# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """
    Validate JWT token and return the current authenticated user.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        session: Database session
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token
    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
