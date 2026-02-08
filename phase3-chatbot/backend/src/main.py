"""FastAPI application entry point for the AI Chatbot Todo application."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from .config import settings
from .api.chat import router as chat_router
from .api.mcp import router as mcp_router
from .api.api_keys import router as api_keys_router
from .api.auth import router as auth_router  # Import the auth router
from .api.todos import router as todos_router  # Import the todos router
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
app.include_router(auth_router, tags=["Authentication"])  # Add the auth router without prefix for frontend compatibility
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])  # Mount chat at /api/chat to match frontend expectations
app.include_router(mcp_router, prefix="/api", tags=["MCP"])
app.include_router(api_keys_router, prefix="/api", tags=["API Keys"])
app.include_router(todos_router, prefix="/api", tags=["Todos"])  # Add the todos router with /api prefix for frontend compatibility

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Chatbot Todo API"}

def register_todo_tools():
    """Register todo tools with the MCP integration service."""
    from .database import get_session
    from .models.mcp_tool import McpTool
    from .tools.todo_tools import TodoTools
    from sqlmodel import Session, select
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Use a temporary session to check if tools already exist
        # get_session() returns a generator, so we need to use it properly
        session_gen = get_session()
        session = next(session_gen)

        try:
            # Check if todo tools are already registered
            existing_tool_names = ["create_task", "list_tasks", "update_task", "complete_task", "delete_task", "search_tasks", "get_task_details"]

            for tool_name in existing_tool_names:
                existing_tool = session.exec(select(McpTool).where(McpTool.name == tool_name)).first()
                if not existing_tool:
                    # Register the tool
                    tool_functions = {
                        "create_task": {
                            "description": "Create a new task",
                            "provider": "internal",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user creating the task"},
                                    "title": {"type": "string", "description": "Title of the task"},
                                    "description": {"type": "string", "description": "Description of the task"},
                                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                                    "due_date": {"type": "string", "format": "date", "description": "Due date in YYYY-MM-DD format"}
                                },
                                "required": ["user_id", "title"]
                            }
                        },
                        "list_tasks": {
                            "description": "List all tasks for a user with optional filters",
                            "provider": "internal",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user whose tasks to list"},
                                    "status": {"type": "string", "enum": ["all", "completed", "pending"], "default": "all"},
                                    "priority": {"type": "string", "enum": ["all", "high", "medium", "low"], "default": "all"},
                                    "limit": {"type": "integer", "default": 10}
                                },
                                "required": ["user_id"]
                            }
                        },
                        "update_task": {
                            "description": "Update an existing task",
                            "provider": "internal",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user whose task to update"},
                                    "task_id": {"type": "string", "description": "ID of the task to update"},
                                    "title": {"type": "string", "description": "New title for the task"},
                                    "description": {"type": "string", "description": "New description for the task"},
                                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                                    "due_date": {"type": "string", "format": "date", "description": "New due date in YYYY-MM-DD format"},
                                    "completed": {"type": "boolean", "description": "Whether the task is completed"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        },
                        "complete_task": {
                            "description": "Mark a task as completed",
                            "provider": "internal",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user whose task to complete"},
                                    "task_id": {"type": "string", "description": "ID of the task to complete"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        },
                        "delete_task": {
                            "description": "Delete a task",
                            "provider": "internal",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user whose task to delete"},
                                    "task_id": {"type": "string", "description": "ID of the task to delete"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        },
                        "search_tasks": {
                            "description": "Search tasks by keyword",
                            "provider": "internal",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user whose tasks to search"},
                                    "query": {"type": "string", "description": "Keyword to search for in titles and descriptions"},
                                    "status": {"type": "string", "enum": ["all", "completed", "pending"], "default": "all"},
                                    "priority": {"type": "string", "enum": ["all", "high", "medium", "low"], "default": "all"}
                                },
                                "required": ["user_id", "query"]
                            }
                        },
                        "get_task_details": {
                            "description": "Get details of a specific task",
                            "provider": "internal",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "ID of the user whose task to get details for"},
                                    "task_id": {"type": "string", "description": "ID of the task to get details for"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        }
                    }

                    if tool_name in tool_functions:
                        tool_info = tool_functions[tool_name]

                        # Create new tool record
                        new_tool = McpTool(
                            name=tool_name,
                            description=tool_info["description"],
                            provider=tool_info["provider"],
                            tool_schema=tool_info["schema"]
                        )

                        session.add(new_tool)
                        logger.info(f"Registered tool: {tool_name}")

            session.commit()

        finally:
            # Close the session by exhausting the generator
            try:
                next(session_gen)
            except StopIteration:
                pass  # Normal completion

        logger.info("All todo tools registered successfully")

    except Exception as e:
        logger.error(f"Error registering tools: {e}")
        # Continue anyway to avoid blocking startup

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