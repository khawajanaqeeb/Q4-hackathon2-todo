from sqlmodel import SQLModel, Field, Column, DateTime, func
from sqlalchemy import String, JSON
from datetime import datetime
from typing import Optional, Dict, Any


class AuditLogBase(SQLModel):
    """Base class for Audit Log model with common fields."""
    user_id: Optional[str] = Field(nullable=True)
    action_type: str = Field(sa_column=Column(String, nullable=False))
    resource_type: str = Field(sa_column=Column(String, nullable=True))
    resource_id: Optional[int] = Field(nullable=True)
    log_metadata: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON, nullable=True))  # Renamed from metadata to avoid conflict
    success: bool = Field(default=True)
    response_time_ms: Optional[int] = Field(nullable=True)
    ip_address: Optional[str] = Field(sa_column=Column(String, nullable=True))
    user_agent: Optional[str] = Field(sa_column=Column(String, nullable=True))


class AuditLog(AuditLogBase, table=True):
    """Audit trail entity for tracking API usage and operations."""
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=func.now())
    )
    error_message: Optional[str] = Field(sa_column=Column(String, nullable=True))