from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Unified application settings loaded from environment variables."""

    # Database - Use Neon DB connection string
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/chatbot_todo_db")

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"

    # MCP
    MCP_SERVER_URL: str = ""

    # Redis (for caching/rate limiting)
    REDIS_URL: str = "redis://localhost:6379"

    # Additional MCP-specific settings
    # MCP Protocol Settings
    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 8000
    MCP_SERVER_LOG_LEVEL: str = "info"

    # Database Settings
    DATABASE_POOL_SIZE: int = 20
    DATABASE_POOL_TIMEOUT: int = 30

    # Security Settings
    ENCRYPTION_PASSWORD: str = os.getenv("ENCRYPTION_PASSWORD", "default-encryption-password-change-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"

    # Redis Settings (for caching)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # API Provider Settings
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "openai")
    PROVIDER_TIMEOUT_SECONDS: int = int(os.getenv("PROVIDER_TIMEOUT_SECONDS", "30"))

    # Rate Limiting Settings
    DISABLE_RATE_LIMIT: bool = os.getenv("DISABLE_RATE_LIMIT", "false").lower() == "true"
    LOGIN_RATE_LIMIT: str = "5"  # Added to match original config
    RATE_LIMIT_DEFAULT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_DEFAULT_MAX_REQUESTS", "100"))
    RATE_LIMIT_DEFAULT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_DEFAULT_WINDOW_SECONDS", "60"))
    RATE_LIMIT_USER_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_USER_MAX_REQUESTS", "1000"))
    RATE_LIMIT_USER_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_USER_WINDOW_SECONDS", "60"))

    # Quota Settings
    QUOTA_DEFAULT_MAX_REQUESTS: int = int(os.getenv("QUOTA_DEFAULT_MAX_REQUESTS", "10000"))
    QUOTA_DEFAULT_MAX_COST: float = float(os.getenv("QUOTA_DEFAULT_MAX_COST", "100.0"))
    QUOTA_DEFAULT_MAX_TOKENS: int = int(os.getenv("QUOTA_DEFAULT_MAX_TOKENS", "1000000"))

    # Caching Settings
    CACHE_TTL_SHORT: int = int(os.getenv("CACHE_TTL_SHORT", "300"))  # 5 minutes
    CACHE_TTL_MEDIUM: int = int(os.getenv("CACHE_TTL_MEDIUM", "1800"))  # 30 minutes
    CACHE_TTL_LONG: int = int(os.getenv("CACHE_TTL_LONG", "3600"))  # 1 hour
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"

    # Audit Settings
    AUDIT_LOG_RETENTION_DAYS: int = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "90"))
    ENABLE_AUDIT_LOGGING: bool = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"

    # Fallback Settings
    FALLBACK_MAX_RETRIES: int = int(os.getenv("FALLBACK_MAX_RETRIES", "3"))
    FALLBACK_BASE_DELAY: float = float(os.getenv("FALLBACK_BASE_DELAY", "1.0"))
    FALLBACK_MAX_DELAY: float = float(os.getenv("FALLBACK_MAX_DELAY", "60.0"))

    # MCP Integration Settings
    MCP_TOOL_REGISTRY_REFRESH_INTERVAL: int = int(os.getenv("MCP_TOOL_REGISTRY_REFRESH_INTERVAL", "300"))  # 5 minutes
    MCP_INTEGRATION_TIMEOUT: int = int(os.getenv("MCP_INTEGRATION_TIMEOUT", "60"))

    # Security Headers
    ENABLE_SECURITY_HEADERS: bool = os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    CSP_POLICY: str = os.getenv("CSP_POLICY", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';")

    # CORS Settings (for compatibility with new structure)
    CORS_ALLOW_ORIGINS: List[str] = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost,http://localhost:3000,http://127.0.0.1,http://127.0.0.1:3000,https://q4-hackathon2-todo-fullstack.vercel.app").split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields to prevent validation errors (for backward compatibility)
        extra = "allow"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to a list."""
        return self.CORS_ALLOW_ORIGINS


# Create settings instance
settings = Settings()

# Override with environment variable if present
if os.getenv("DATABASE_URL"):
    settings.DATABASE_URL = os.getenv("DATABASE_URL")


def get_settings():
    """Get the settings instance."""
    return settings