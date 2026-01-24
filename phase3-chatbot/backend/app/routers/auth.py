"""Authentication routes for user registration and login.

This module implements the authentication endpoints defined in
specs/001-fullstack-web-app/contracts/auth.yaml

Endpoints:
    - POST /auth/register: Create new user account
    - POST /auth/login: Authenticate user and return JWT token
    - POST /auth/refresh: Refresh access token using refresh token
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    validate_password_strength
)

# Import limiter for rate limiting
# Note: This creates a local instance. In production, consider using
# request.app.state.limiter (set in main.py) for centralized config
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session),
):
    """Register a new user account.

    Creates a new user with hashed password (bcrypt).
    Email must be unique in the database.

    Args:
        user_data: User registration data (email, password, name)
        session: Database session (injected)

    Returns:
        UserResponse: Created user data (no password)

    Raises:
        HTTPException 400: Validation error (invalid email, weak password, etc.)
        HTTPException 409: Email already registered
        HTTPException 500: Database or server error
    """
    try:
        # Check if email already exists
        statement = select(User).where(User.email == user_data.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Validate password strength
        is_valid, message = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Hash password with bcrypt
        hashed_password = hash_password(user_data.password)

        # Create new user
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            name=user_data.name,
            is_active=True,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

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


from fastapi import Request, Form
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # Rate limit login attempts to 5 per minute per IP
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Authenticate user and return JWT access token.

    Uses OAuth2PasswordRequestForm which expects:
    - username: User's email (we use email as username)
    - password: User's password

    Validates credentials and returns JWT token on success.
    Token expires after ACCESS_TOKEN_EXPIRE_MINUTES (default: 30).

    Args:
        request: FastAPI request object (for rate limiting)
        form_data: OAuth2 form data with username (email) and password
        session: Database session (injected)

    Returns:
        TokenResponse: JWT access token and token type

    Raises:
        HTTPException 401: Invalid credentials or inactive account
    """
    # OAuth2PasswordRequestForm uses 'username' field, but we use email as username
    email = form_data.username
    password = form_data.password

    # Find user by email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    # Generic error message to prevent user enumeration
    invalid_credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
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

    # Create JWT tokens with user ID and email (sub must be string for JWT spec)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")  # Rate limit refresh attempts to 10 per minute per IP
async def refresh_token(
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
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens (sub must be string for JWT spec)
    new_access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


@router.post("/verify", response_model=UserResponse)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
):
    """Verify JWT access token and return user data.

    This endpoint is used by the frontend proxy to validate tokens
    and retrieve current user information.

    Args:
        credentials: JWT token from Authorization header (injected by HTTPBearer)
        session: Database session (injected)

    Returns:
        UserResponse: Current user data (no password)

    Raises:
        HTTPException 401: Invalid or expired token, or user not found
    """
    token = credentials.credentials

    # Decode and validate the access token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token payload (it's stored as string)
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user