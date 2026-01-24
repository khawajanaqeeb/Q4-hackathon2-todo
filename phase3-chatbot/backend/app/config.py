"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings


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

    # Optional: Rate Limiting
    LOGIN_RATE_LIMIT: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
