"""JWT dependencies for Phase 3 Todo AI Chatbot."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
import sys
from pathlib import Path

# Add the project root to the path so we can import from phase2-fullstack
project_root = Path(__file__).parent.parent.parent
phase2_backend = project_root / "phase2-fullstack" / "backend"

# Add to sys.path if not already there
if str(phase2_backend) not in sys.path:
    sys.path.insert(0, str(phase2_backend))

try:
    from app.dependencies.auth import get_current_user
    from app.models.user import User
    from app.schemas.auth import TokenData
except ImportError as e:
    print(f"Error importing from Phase II backend: {e}")
    raise


# Re-export the existing authentication dependency
async def get_current_user_phase3(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current authenticated user using the existing Phase II auth system.

    Args:
        credentials: HTTP Bearer token from Authorization header
        current_user: The authenticated user from Phase II system

    Returns:
        Authenticated User object
    """
    return current_user