from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .api.auth import router as auth_router
# from .api.todos import router as todos_router  # Temporarily commented out due to dependency issues
# from .api.chat import router as chat_router  # Temporarily commented out due to dependency issues
from .database import create_db_and_tables
from .config import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware with credentials support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
# app.include_router(todos_router, prefix="/api", tags=["Todos"])  # Temporarily commented out due to dependency issues
# app.include_router(chat_router, prefix="/api", tags=["Chat"])  # Temporarily commented out due to dependency issues

@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    create_db_and_tables()

@app.get("/")
def read_root():
    """Root endpoint for API."""
    return {"message": "Phase 3 Chatbot Authentication & Integration API"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Phase 3 API"}