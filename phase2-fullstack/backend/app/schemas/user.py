"""User request and response schemas.

This module defines Pydantic schemas for user-related API operations
including registration, login, and authentication responses.

Spec Reference: specs/001-fullstack-web-app/contracts/auth.yaml
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration request.

    Used in POST /auth/register endpoint.
    Password will be hashed with bcrypt before storage.
    """
    email: EmailStr = Field(
        ...,
        description="Valid email address (unique in database)",
        json_schema_extra={"example": "user@example.com"}
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=255,
        description="Plain text password (will be hashed with bcrypt)",
        json_schema_extra={"example": "SecurePass123"}
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's display name",
        json_schema_extra={"example": "John Doe"}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "name": "John Doe"
            }
        }


class LoginRequest(BaseModel):
    """Schema for login request.

    Used in POST /auth/login endpoint.
    Credentials validated against database.
    """
    email: EmailStr = Field(
        ...,
        description="User's registered email address",
        json_schema_extra={"example": "user@example.com"}
    )
    password: str = Field(
        ...,
        description="User's password (plain text)",
        json_schema_extra={"example": "SecurePass123"}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class UserResponse(BaseModel):
    """Schema for user data in responses.

    Used in POST /auth/register and user profile endpoints.
    NEVER includes password (hashed or plain).
    """
    id: int = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's display name")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="UTC timestamp of account creation")
    updated_at: datetime = Field(..., description="UTC timestamp of last update")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
                "created_at": "2026-01-02T12:00:00Z",
                "updated_at": "2026-01-02T12:00:00Z"
            }
        }


class TokenResponse(BaseModel):
    """Schema for JWT authentication token response.

    Used in POST /auth/login endpoint.
    Token expires based on ACCESS_TOKEN_EXPIRE_MINUTES setting.
    """
    access_token: str = Field(
        ...,
        description="JWT access token (expires in 30 minutes)",
        json_schema_extra={
            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJleHAiOjE3MDQxNTM2MDB9.signature"
        }
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token (expires in 7 days)",
        json_schema_extra={
            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJleHAiOjE3MDQxNTM2MDB9.signature"
        }
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        json_schema_extra={"example": "bearer"}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
