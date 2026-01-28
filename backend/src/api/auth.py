from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session
from typing import Optional
from datetime import timedelta
import os
from jose import jwt
from jose.exceptions import JWTError

from ..models.user import User, UserCreate, UserRead
from ..services.auth import authenticate_user, create_user, create_access_token_for_user
from ..database import get_session
from ..utils.security import SECRET_KEY, ALGORITHM, verify_token

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Configuration from environment variables
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
COOKIE_HTTPONLY = os.getenv("COOKIE_HTTPONLY", "true").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "strict")

@router.post("/register", response_model=UserRead)
@limiter.limit("5 per minute")
def register_user(request: Request, user_create: UserCreate, session: Session = Depends(get_session)):
    """Register a new user."""
    try:
        db_user = create_user(session, user_create)

        # Create access token for the new user
        access_token = create_access_token_for_user(db_user)

        # Set the token in an HTTP-only cookie
        response = Response()
        response.set_cookie(
            key="session_token",
            value=access_token,
            httponly=COOKIE_HTTPONLY,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            max_age=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).seconds
        )

        # Return the user info in the response body as well
        user_response = UserRead(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )

        return user_response
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login")
@limiter.limit("10 per minute")
def login_user(request: Request, response: Response, username: str, password: str, session: Session = Depends(get_session)):
    """Authenticate user and create session."""
    user = authenticate_user(session, username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token_for_user(user)

    # Set the token in an HTTP-only cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).seconds
    )

    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "message": "Login successful"
    }


@router.get("/verify")
@limiter.limit("30 per minute")
def verify_user(request: Request, session: Session = Depends(get_session)):
    """Verify current user session."""
    # Get the session token from cookies
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session token provided"
        )

    # Verify the token
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    # Get the username from the payload
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Find the user in the database
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@router.post("/logout")
def logout_user(response: Response):
    """Terminate current user session."""
    # Clear the session token cookie by setting it to expire immediately
    response.set_cookie(
        key="session_token",
        value="",
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        expires=0
    )

    return {
        "success": True,
        "message": "Logout successful"
    }