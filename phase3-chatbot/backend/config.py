"""Phase 3 specific settings configuration that extends Phase 2 settings while including Phase 3-specific environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Phase3Settings(BaseSettings):
    """Extended settings class for Phase 3 that includes all required environment variables from both Phase 2 and Phase 3."""

    # Phase 2 inherited settings
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000"
    DEBUG: bool = False
    LOGIN_RATE_LIMIT: int = 5

    # Phase 3 specific settings
    OPENAI_API_KEY: str
    BETTER_AUTH_SECRET: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    PHASE2_BACKEND_PATH: str = "./phase2-fullstack/backend"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables to prevent validation errors


# Create an instance of the settings
settings = Phase3Settings()