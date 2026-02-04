"""FastAPI application entry point for the AI Chatbot Todo application."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from .config import settings
from .api.compliant_chat import router as chat_router
from .api.mcp import router as mcp_router
from .api.api_keys import router as api_keys_router
from .api.auth import router as auth_router  # Import the auth router
from .database import create_db_and_tables, get_session
from .services.mcp_integration import McpIntegrationService
from .services.api_key_manager import ApiKeyManager
from .services.audit_service import AuditService
from .tools.todo_tools import TodoTools

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="AI Chatbot Todo API",
    version="1.0.0",
    description="Phase III AI Chatbot Todo Application API",
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, tags=["Authentication"])  # Add the auth router
app.include_router(chat_router, prefix="", tags=["Chat"])
app.include_router(mcp_router, prefix="/api", tags=["MCP"])
app.include_router(api_keys_router, prefix="/api", tags=["API Keys"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Chatbot Todo API"}

def register_todo_tools():
    """Register todo tools with the MCP integration service."""
    logger.info("Skipping tool registration during startup to avoid complex database schema issues")
    # For now, skip the registration to avoid database issues
    # The tools will be loaded dynamically when invoked

@app.on_event("startup")
def startup_event():
    """Application startup event handler."""
    create_db_and_tables()

    # Register todo tools
    try:
        register_todo_tools()
    except Exception as e:
        logger.error(f"Failed to register todo tools: {e}")
        # Continue startup even if tool registration fails