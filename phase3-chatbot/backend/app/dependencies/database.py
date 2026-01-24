"""Database dependencies for FastAPI."""
from app.database import get_session

# Export get_session for use in route dependencies
__all__ = ["get_session"]
