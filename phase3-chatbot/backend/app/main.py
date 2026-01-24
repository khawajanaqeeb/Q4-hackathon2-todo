"""FastAPI application entry point."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, todos
from app.database import create_db_and_tables

# Create FastAPI application instance
app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="Phase II Full-Stack Todo Application API",
)

# Initialize rate limiter only if not disabled
if not settings.DISABLE_RATE_LIMIT:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS middleware - More restrictive than default
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],  # More specific
    allow_headers=["*"],  # Still allow all headers for flexibility
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(todos.router, prefix="/todos", tags=["Todos"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
def startup_event():
    """Application startup event handler."""
    create_db_and_tables()
