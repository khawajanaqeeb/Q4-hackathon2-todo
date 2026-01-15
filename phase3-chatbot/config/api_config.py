"""
API Configuration for Todo AI Chatbot

Configuration settings for connecting to the Phase II backend API.
"""

import os
from typing import Optional


class APIConfig:
    """Configuration class for API integration."""

    def __init__(self):
        self.base_url: str = os.getenv('PHASE_II_API_URL', 'http://localhost:8000')
        self.jwt_secret: str = os.getenv('PHASE_II_JWT_SECRET', '')
        self.timeout: int = int(os.getenv('API_TIMEOUT', '30'))
        self.max_retries: int = int(os.getenv('API_MAX_RETRIES', '3'))
        self.api_key: Optional[str] = os.getenv('PHASE_II_API_KEY')

    def get_base_url(self) -> str:
        """Get the API base URL."""
        return self.base_url

    def get_jwt_secret(self) -> str:
        """Get the JWT secret."""
        return self.jwt_secret

    def get_timeout(self) -> int:
        """Get the request timeout."""
        return self.timeout

    def get_max_retries(self) -> int:
        """Get the maximum number of retries."""
        return self.max_retries

    def get_api_key(self) -> Optional[str]:
        """Get the API key if available."""
        return self.api_key

    def is_production(self) -> bool:
        """Check if running in production."""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'

    def validate(self) -> bool:
        """Validate the configuration."""
        if not self.base_url:
            raise ValueError("PHASE_II_API_URL must be set")

        if not self.jwt_secret and not self.api_key:
            # For development, we might not have these set yet
            # In production, this would be an issue
            if self.is_production():
                raise ValueError("Either JWT_SECRET or API_KEY must be set in production")

        return True


# Singleton instance
_config = None


def get_api_config() -> APIConfig:
    """Get the API configuration singleton."""
    global _config
    if _config is None:
        _config = APIConfig()
        _config.validate()
    return _config


# Example usage
if __name__ == "__main__":
    config = get_api_config()
    print(f"Base URL: {config.get_base_url()}")
    print(f"Timeout: {config.get_timeout()}")
    print(f"Is Production: {config.is_production()}")