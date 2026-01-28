import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Phase 3 Chatbot Todo API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Security
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    COOKIE_HTTPONLY: bool = os.getenv("COOKIE_HTTPONLY", "true").lower() == "true"
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "strict")

settings = Settings()