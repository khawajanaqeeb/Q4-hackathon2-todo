"""Authentication routes for Phase 3 backend with chatbot functionality.

This module implements the authentication endpoints that should be preserved
from Phase 2 while maintaining compatibility with the Phase 3 backend structure.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from sqlmodel import Session, select
from datetime import timedelta
from passlib.context import CryptContext
import re
from typing import Optional

from ..database import get_session
from ..models.user import User
from ..dependencies.auth import create_access_token, verify_token
from ..config import settings

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Import limiter for rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter that respects the DISABLE_RATE_LIMIT setting
limiter = Limiter(key_func=get_remote_address)

# Define conditional rate limiter decorator
def conditional_rate_limit(limit_str: str):
    if settings.DISABLE_RATE_LIMIT:
        # Return a decorator that does nothing
        def no_rate_limit(func):
            return func
        return no_rate_limit
    else:
        # Return the actual rate limiter
        return limiter.limit(limit_str)

router = APIRouter()


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength against security requirements.

    Args:
        password: Plain text password to validate

    Returns:
        Tuple of (is_valid, message) where is_valid is boolean and message explains result
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    return True, "Password is valid"


class TokenResponse:
    """Response model for token endpoints."""
    def __init__(self, access_token: str, refresh_token: str, token_type: str):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type


@router.post("/auth/register", response_model=dict)  # Using dict since we don't have UserResponse in src
async def register(
    response: Response,
    request: Request,  # Added for rate limiting compatibility
    email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    session: Session = Depends(get_session),
):
    """Register a new user account.

    Creates a new user with hashed password (bcrypt).
    Email and username must be unique in the database.

    Args:
        request: FastAPI request object (for rate limiting)
        email: User's email address
        password: User's password
        username: User's username
        session: Database session (injected)

    Returns:
        User data (no password)

    Raises:
        HTTPException 400: Validation error (invalid email, weak password, etc.)
        HTTPException 409: Email or username already registered
        HTTPException 500: Database or server error
    """
    try:
        # Check if email already exists
        statement = select(User).where(User.email == email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Check if username already exists
        statement = select(User).where(User.username == username)
        existing_username = session.exec(statement).first()

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

        # Validate password strength
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Hash password with bcrypt
        hashed_password = hash_password(password)

        # Create new user
        from uuid import uuid4
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=hashed_password,
            username=username,
            is_active=True,
            is_superuser=False,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # Create JWT tokens for the newly registered user (auto-login)
        from datetime import timedelta
        from ..dependencies.auth import create_access_token

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "email": user.email}
        )
        refresh_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "email": user.email},
            expires_delta=timedelta(days=7)  # 7 days for refresh token
        )

        # Set the access token as an HTTP-only cookie (matching frontend expectation)
        # Determine cookie settings based on environment
        is_prod = settings.ENVIRONMENT.lower() == "production"
        secure_flag = is_prod  # Only use secure cookies in production
        samesite_setting = "none" if is_prod else "lax"  # "none" requires secure=True

        response.set_cookie(
            key="auth_token",
            value=access_token,
            httponly=True,
            secure=secure_flag,
            samesite=samesite_setting,
            max_age=1800,  # 30 minutes in seconds (same as ACCESS_TOKEN_EXPIRE_MINUTES)
            path="/"
        )

        # Return user data with tokens
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        # Catch database/hashing errors and rollback
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm


@router.post("/auth/login", response_model=dict)
@conditional_rate_limit("5/minute")  # Rate limit login attempts to 5 per minute per IP
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Authenticate user and return JWT access token.

    Uses OAuth2PasswordRequestForm which expects:
    - username: User's username or email
    - password: User's password

    Validates credentials and returns JWT token on success.
    Token expires after ACCESS_TOKEN_EXPIRE_MINUTES (default: 30).

    Args:
        request: FastAPI request object (for rate limiting)
        form_data: OAuth2 form data with username and password
        session: Database session (injected)

    Returns:
        TokenResponse: JWT access token and token type

    Raises:
        HTTPException 401: Invalid credentials or inactive account
    """
    # OAuth2PasswordRequestForm uses 'username' field, which can be username or email
    username_or_email = form_data.username
    password = form_data.password

    # Find user by username or email
    statement = select(User).where((User.username == username_or_email) | (User.email == username_or_email))
    user = session.exec(statement).first()

    # Generic error message to prevent user enumeration
    invalid_credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username/email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise invalid_credentials_error

    # Verify password
    if not verify_password(password, user.hashed_password):
        raise invalid_credentials_error

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT tokens with user ID (UUID as string)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "email": user.email}
    )
    # Note: refresh tokens are typically handled differently in modern apps
    # For compatibility with frontend expectations, we'll return a placeholder
    refresh_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "email": user.email},
        expires_delta=timedelta(days=7)  # 7 days for refresh token
    )

    # Set the access token as an HTTP-only cookie (matching frontend expectation)
    # Determine cookie settings based on environment
    is_prod = settings.ENVIRONMENT.lower() == "production"
    secure_flag = is_prod  # Only use secure cookies in production
    samesite_setting = "none" if is_prod else "lax"  # "none" requires secure=True

    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,
        secure=secure_flag,
        samesite=samesite_setting,
        max_age=1800,  # 30 minutes in seconds (same as ACCESS_TOKEN_EXPIRE_MINUTES)
        path="/"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/auth/refresh", response_model=dict)
@conditional_rate_limit("10/minute")  # Rate limit refresh attempts to 10 per minute per IP
async def refresh_token(
    response: Response,
    request: Request,
    refresh_token: str = Form(...),
    session: Session = Depends(get_session),
):
    """Refresh access token using refresh token.

    Args:
        request: FastAPI request object (for rate limiting)
        refresh_token: JWT refresh token (form field)
        session: Database session (injected)

    Returns:
        TokenResponse: New JWT access token and refresh token

    Raises:
        HTTPException 401: Invalid or expired refresh token
    """
    try:
        from jose import jwt
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch user from database
        from uuid import UUID
        try:
            user_uuid = UUID(user_id_str)
            user = session.get(User, user_uuid)
        except ValueError:
            # Handle case where user_id_str is not a valid UUID (legacy support)
            # This might happen if using old tokens with integer IDs
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID is not a valid UUID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        new_access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "email": user.email}
        )
        new_refresh_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "email": user.email},
            expires_delta=timedelta(days=7)  # 7 days for refresh token
        )

        # Set the new access token as an HTTP-only cookie (matching frontend expectation)
        # Determine cookie settings based on environment
        is_prod = settings.ENVIRONMENT.lower() == "production"
        secure_flag = is_prod  # Only use secure cookies in production
        samesite_setting = "none" if is_prod else "lax"  # "none" requires secure=True

        response.set_cookie(
            key="auth_token",
            value=new_access_token,
            httponly=True,
            secure=secure_flag,
            samesite=samesite_setting,
            max_age=1800,  # 30 minutes in seconds (same as ACCESS_TOKEN_EXPIRE_MINUTES)
            path="/"
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/auth/logout")
async def logout(response: Response):
    """Logout user by clearing the authentication cookie.

    Args:
        response: FastAPI response object to set cookie

    Returns:
        Success message
    """
    # Clear the auth cookie by setting it to expire immediately
    # Determine cookie settings based on environment
    is_prod = settings.ENVIRONMENT.lower() == "production"
    secure_flag = is_prod  # Only use secure cookies in production
    samesite_setting = "none" if is_prod else "lax"  # "none" requires secure=True

    response.set_cookie(
        key="auth_token",
        value="",
        httponly=True,
        secure=secure_flag,
        samesite=samesite_setting,
        max_age=0,  # Expire immediately
        path="/"
    )

    return {"message": "Successfully logged out"}


@router.post("/auth/verify", response_model=dict)
async def verify_token_endpoint(
    request: Request,
    session: Session = Depends(get_session),
):
    """Verify JWT access token and return user data.

    This endpoint is used by the frontend proxy to validate tokens
    and retrieve current user information.

    Args:
        request: FastAPI request object (contains authorization header or cookie)
        session: Database session (injected)

    Returns:
        User data (no password)

    Raises:
        HTTPException 401: Invalid or expired token, or user not found
    """
    # Extract token from either Authorization header or session_token cookie
    token = None

    # First, try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]

    # If not found in header, try to get from auth_token cookie (used by frontend)
    if not token:
        token = request.cookies.get("auth_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate the access token
    try:
        from jose import jwt
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch user from database
        from uuid import UUID
        try:
            user_uuid = UUID(user_id_str)
            user = session.get(User, user_uuid)
        except ValueError:
            # Handle case where user_id_str is not a valid UUID (legacy support)
            # This might happen if using old tokens with integer IDs
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID is not a valid UUID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Return user data without sensitive information
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )