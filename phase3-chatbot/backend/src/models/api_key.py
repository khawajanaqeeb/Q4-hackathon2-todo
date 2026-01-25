from sqlmodel import SQLModel, Field, Column, DateTime, func
from sqlalchemy import String, LargeBinary
from datetime import datetime
import uuid
from typing import Optional


class ApiKeyBase(SQLModel):
    """Base class for API Key model with common fields."""
    provider: str = Field(sa_column=Column(String, nullable=False))
    user_id: uuid.UUID = Field(nullable=False)
    encrypted_key: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    encrypted_key_iv: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    encrypted_key_salt: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(sa_column=Column(DateTime, nullable=True))


class ApiKey(ApiKeyBase, table=True):
    """Encrypted API key entity for secure storage."""
    __tablename__ = "api_keys"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    )

    # Relationship back-reference would go here if needed