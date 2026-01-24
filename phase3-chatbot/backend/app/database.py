"""Database configuration and session management."""
from sqlmodel import Session, create_engine, SQLModel
from app.config import settings

# Global variable for the engine - will be set in create_db_and_tables
engine = None


def create_db_and_tables():
    """Create database tables on application startup."""
    global engine
    # Create SQLModel engine with connection pooling
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
    )
    SQLModel.metadata.create_all(engine)


def get_engine():
    """Get the database engine, creating it if it doesn't exist."""
    global engine
    if engine is None:
        # For testing, we might not have called create_db_and_tables yet
        # So create a temporary engine for testing purposes
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
    return engine


def get_session():
    """
    Dependency for database sessions.

    Yields a database session and ensures it's closed after use.
    """
    with Session(get_engine()) as session:
        yield session
