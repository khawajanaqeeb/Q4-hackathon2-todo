from sqlmodel import SQLModel, Field, Column, DateTime, func
from sqlalchemy import String, JSON
from datetime import datetime
import uuid
from typing import Optional


class McpToolBase(SQLModel):
    """Base class for MCP Tool model with common fields."""
    name: str = Field(sa_column=Column(String, nullable=False, unique=True))
    description: str = Field(sa_column=Column(String, nullable=True))
    provider: str = Field(sa_column=Column(String, nullable=False))
    schema_json: str = Field(sa_column=Column(String, nullable=False))  # Store as JSON string
    is_active: bool = Field(default=True)


class McpTool(McpToolBase, table=True):
    """MCP tool definitions for integration with external services."""
    __tablename__ = "mcp_tools"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    )
    user_id: Optional[uuid.UUID] = Field(nullable=True)  # Optional - some tools may be system-wide