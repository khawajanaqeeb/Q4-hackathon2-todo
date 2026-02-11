from sqlmodel import SQLModel, Field, Column, DateTime, func, Relationship
from sqlalchemy import String, LargeBinary
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class ApiKeyBase(SQLModel):
    """Base class for API Key model with common fields."""
    provider: str = Field(sa_column=Column(String, nullable=False))
    user_id: str = Field(foreign_key="user.id", nullable=False)
    encrypted_key: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    encrypted_key_iv: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    encrypted_key_salt: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(sa_column=Column(DateTime, nullable=True))


class ApiKey(ApiKeyBase, table=True):
    """Encrypted API key entity for secure storage."""
    __tablename__ = "api_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    )

    # Relationship to user
    user: "User" = Relationship(back_populates="api_keys")