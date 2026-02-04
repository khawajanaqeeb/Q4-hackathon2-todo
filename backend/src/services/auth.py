from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from typing import Optional
from datetime import timedelta
from ..models.user import User, UserCreate, UserRead
from ..utils.security import verify_password, get_password_hash, create_access_token
from ..database import get_session

security = HTTPBearer()

def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username or email and password."""
    import logging
    logger = logging.getLogger(__name__)

    logger.debug(f"Attempting to authenticate user: {username}")

    # First, try to find user by username
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    # If not found, try to find user by email
    if not user:
        statement = select(User).where(User.email == username)
        user = session.exec(statement).first()

    logger.debug(f"User lookup result: {'Found' if user else 'Not found'}")

    if not user:
        logger.info(f"User not found: {username}")
        return None

    if not verify_password(password, user.hashed_password):
        logger.info(f"Password verification failed for user: {username}")
        return None

    logger.debug(f"User authenticated successfully: {user.username}")
    return user

def create_user(session: Session, user_create: UserCreate) -> User:
    """Create a new user."""
    # Check if username or email already exists
    existing_user_by_username = session.exec(
        select(User).where(User.username == user_create.username)
    ).first()

    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )

    existing_user_by_email = session.exec(
        select(User).where(User.email == user_create.email)
    ).first()

    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create the new user
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

def get_current_user(session: Session, token: str = Depends(security)) -> User:
    """Get the current user from the token."""
    from jose import jwt
    from ..utils.security import SECRET_KEY, ALGORITHM
    from jose.exceptions import JWTError

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if user is None:
        raise credentials_exception

    return user

def create_access_token_for_user(user: User) -> str:
    """Create an access token for a user."""
    access_token_expires = timedelta(minutes=30)  # Could be configurable
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return access_token