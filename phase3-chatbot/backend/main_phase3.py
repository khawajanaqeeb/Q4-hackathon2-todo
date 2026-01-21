"""Main FastAPI application for Phase 3 Todo AI Chatbot."""

import sys
from pathlib import Path

# Add the backend directory to the path to allow proper imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Add the app directory to the path to allow direct imports
app_dir = backend_dir / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Add the phase2 backend to the path to allow imports from phase2-fullstack
project_root = backend_dir.parent.parent.parent
phase2_backend = project_root / "phase2-fullstack" / "backend"
if str(phase2_backend) not in sys.path:
    sys.path.insert(0, str(phase2_backend))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

# Import Phase 3 settings
from .config import settings

from routers import chat_router

# Create FastAPI application instance
app = FastAPI(
    title="Phase 3 Todo AI Chatbot",
    version="1.0.0",
    description="AI-powered chatbot for managing todo lists with real OpenAI integration"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router.router)

@app.get("/")
async def root():
    """Root endpoint for the Phase 3 chatbot API."""
    return {
        "message": "Welcome to the Phase 3 Todo AI Chatbot API",
        "status": "running",
        "features": ["real OpenAI integration", "router agent", "secure authentication"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Phase 3 Todo AI Chatbot",
        "openai_api_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_phase3:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )