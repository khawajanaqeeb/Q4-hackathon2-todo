from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlmodel import Session
from typing import Optional
from datetime import datetime, timedelta
import uuid
from ..services.api_key_manager import ApiKeyManager
from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User


# Define the request/response models
from pydantic import BaseModel


class StoreApiKeyRequest(BaseModel):
    provider: str
    api_key: str
    expires_in_days: Optional[int] = None  # Number of days until expiration


class StoreApiKeyResponse(BaseModel):
    success: bool
    message: str
    expires_at: Optional[datetime] = None


class GetProvidersResponse(BaseModel):
    providers: list[dict]


class ValidateApiKeyRequest(BaseModel):
    provider: str


class ValidateApiKeyResponse(BaseModel):
    valid: bool
    message: str


router = APIRouter()


@router.post("/api-keys", response_model=StoreApiKeyResponse)
async def store_api_key(
    request: StoreApiKeyRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Store encrypted API key for user.

    Args:
        request: Contains provider name and API key to store
        current_user: Authenticated user
        session: Database session

    Returns:
        Confirmation of successful storage
    """
    api_key_manager = ApiKeyManager()

    try:
        # Validate the API key format
        if not api_key_manager.validate_key(request.api_key):
            raise HTTPException(
                status_code=400,
                detail="Invalid API key format"
            )

        # Determine expiration date if specified
        expires_at = None
        if request.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)

        # Store the encrypted API key
        db_api_key = api_key_manager.store_key(
            session=session,
            user_id=current_user.id,
            provider=request.provider,
            api_key=request.api_key,
            expires_at=expires_at
        )

        return StoreApiKeyResponse(
            success=True,
            message=f"API key for {request.provider} stored successfully",
            expires_at=db_api_key.expires_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error storing API key: {str(e)}"
        )


@router.get("/api-keys/providers", response_model=GetProvidersResponse)
async def get_supported_providers(
    current_user: User = Depends(get_current_user)
):
    """
    List supported AI providers.

    Args:
        current_user: Authenticated user (just for auth)

    Returns:
        List of supported providers with their features
    """
    # Define supported providers with their features
    supported_providers = [
        {
            "name": "openai",
            "display_name": "OpenAI",
            "features": ["gpt-3.5-turbo", "gpt-4", "embeddings", "moderations"],
            "docs_url": "https://platform.openai.com/docs"
        },
        {
            "name": "anthropic",
            "display_name": "Anthropic",
            "features": ["claude-2", "claude-instant"],
            "docs_url": "https://docs.anthropic.com"
        },
        {
            "name": "google",
            "display_name": "Google",
            "features": ["palm-2", "embedding-gecko-001"],
            "docs_url": "https://cloud.google.com/docs"
        }
    ]

    return GetProvidersResponse(providers=supported_providers)


@router.get("/api-keys/{provider}", response_model=dict)
async def get_api_key_status(
    provider: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the status of a stored API key for a provider.

    Args:
        provider: Provider name to check
        current_user: Authenticated user
        session: Database session

    Returns:
        Status information about the stored API key
    """
    api_key_manager = ApiKeyManager()

    # Try to retrieve the key (this will check if it exists and is valid)
    api_key = api_key_manager.retrieve_key(
        session=session,
        user_id=current_user.id,
        provider=provider
    )

    if api_key is None:
        return {
            "provider": provider,
            "has_key": False,
            "message": f"No API key found for {provider}",
            "expires_at": None
        }

    # Get the raw key entry to check expiration
    from sqlmodel import select
    from ..models.api_key import ApiKey

    statement = select(ApiKey).where(
        ApiKey.user_id == current_user.id,
        ApiKey.provider == provider,
        ApiKey.is_active == True
    )
    db_api_key = session.exec(statement).first()

    if not db_api_key:
        return {
            "provider": provider,
            "has_key": False,
            "message": f"No active API key found for {provider}",
            "expires_at": None
        }

    return {
        "provider": provider,
        "has_key": True,
        "message": f"Valid API key exists for {provider}",
        "expires_at": db_api_key.expires_at,
        "created_at": db_api_key.created_at
    }


@router.delete("/api-keys/{provider}")
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a stored API key for a provider.

    Args:
        provider: Provider name to delete key for
        current_user: Authenticated user
        session: Database session

    Returns:
        Confirmation of deletion
    """
    from sqlmodel import select
    from ..models.api_key import ApiKey

    # Find the API key
    statement = select(ApiKey).where(
        ApiKey.user_id == current_user.id,
        ApiKey.provider == provider
    )
    db_api_key = session.exec(statement).first()

    if not db_api_key:
        raise HTTPException(
            status_code=404,
            detail=f"No API key found for provider {provider}"
        )

    # Mark as inactive instead of deleting
    db_api_key.is_active = False
    session.add(db_api_key)
    session.commit()

    return {
        "success": True,
        "message": f"API key for {provider} deactivated successfully"
    }


@router.put("/api-keys/{provider}")
async def update_api_key(
    provider: str,
    request: StoreApiKeyRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update an existing API key for a provider.

    Args:
        provider: Provider name to update key for
        request: Contains the new API key
        current_user: Authenticated user
        session: Database session

    Returns:
        Confirmation of update
    """
    api_key_manager = ApiKeyManager()

    # Validate the new API key format
    if not api_key_manager.validate_key(request.api_key):
        raise HTTPException(
            status_code=400,
            detail="Invalid API key format"
        )

    # Rotate the key
    success = api_key_manager.rotate_key(
        session=session,
        user_id=current_user.id,
        provider=provider,
        new_api_key=request.api_key
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No existing API key found for provider {provider} to update"
        )

    return {
        "success": True,
        "message": f"API key for {provider} updated successfully"
    }