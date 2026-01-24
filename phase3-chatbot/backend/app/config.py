"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000"

    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    DISABLE_RATE_LIMIT: bool = False

    # Optional: Rate Limiting
    LOGIN_RATE_LIMIT: int = 5

    # OpenAI (for the new chatbot feature)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"

    # MCP (for the new chatbot feature)
    MCP_SERVER_URL: str = ""

    # Redis (for caching/rate limiting)
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields to prevent validation errors
        extra = "allow"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
