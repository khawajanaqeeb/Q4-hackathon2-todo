"""MCP Tools for Phase 3 Todo AI Chatbot.

This module implements the MCP (Multi-Agent Communication Protocol) tools
that enable the AI agents to interact with the backend systems.
Each tool follows the specification in specs/phase-3/mcp-tools.md
"""
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
import os

# Add the phase2 backend to the path to get the models
phase2_backend_dir = Path(__file__).parent.parent.parent.parent / "phase2-fullstack" / "backend"
sys.path.insert(0, str(phase2_backend_dir))

from sqlmodel import Session, select, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.todo import Todo, Priority
from app.models.user import User
from mcp.server import FastMCP
import json
from datetime import datetime
from app.config import settings


# Create the FastMCP server instance
mcp_server = FastMCP(
    name="phase3-todo-mcp-server",
    version="1.0.0"
)


@mcp_server.tool(
    name="add_task",
    description="Create a new todo item for the authenticated user",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "The ID of the authenticated user"
            },
            "title": {
                "type": "string",
                "description": "The title of the task"
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the task",
                "default": ""
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Priority level of the task",
                "default": "medium"
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Tags to categorize the task",
                "default": []
            },
            "due_date": {
                "type": "string",
                "format": "date-time",
                "description": "Due date for the task (ISO 8601 format)",
                "default": None
            }
        },
        "required": ["user_id", "title"]
    }
)
async def add_task(user_id: int, title: str, description: Optional[str] = "",
                  priority: str = "medium", tags: Optional[List[str]] = None,
                  due_date: Optional[str] = None) -> Dict[str, Any]:
    """Create a new todo item for the authenticated user."""
    if tags is None:
        tags = []

    # Validate priority
    try:
        priority_enum = Priority(priority.lower())
    except ValueError:
        return {
            "success": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": f"Invalid priority: {priority}. Must be 'low', 'medium', or 'high'"
            }
        }

    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL)

    # Create new todo item
    new_todo = Todo(
        title=title,
        description=description,
        priority=priority_enum,
        tags=tags,
        user_id=user_id,
        completed=False
    )

    try:
        # Use synchronous session since we're not in an async context with existing session
        with Session(engine) as session:
            session.add(new_todo)
            session.commit()
            session.refresh(new_todo)

        return {
            "success": True,
            "task_id": new_todo.id,
            "message": f"Task '{title}' created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": f"Failed to create task: {str(e)}"
            }
        }


@mcp_server.tool(
    name="list_tasks",
    description="Retrieve a list of todo items for the authenticated user with optional filtering",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "The ID of the authenticated user"
            },
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter by task completion status",
                "default": "all"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "all"],
                "description": "Filter by task priority",
                "default": "all"
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Filter by tags",
                "default": []
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Maximum number of tasks to return",
                "default": 10
            },
            "offset": {
                "type": "integer",
                "minimum": 0,
                "description": "Offset for pagination",
                "default": 0
            }
        },
        "required": ["user_id"]
    }
)
async def list_tasks(user_id: int, status: str = "all", priority: str = "all",
                    tags: Optional[List[str]] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """Retrieve a list of todo items for the authenticated user with optional filtering."""
    if tags is None:
        tags = []

    try:
        # Create database engine and session
        engine = create_engine(settings.DATABASE_URL)

        # Build the query with filters
        query = select(Todo).where(Todo.user_id == user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(Todo.completed == False)
        elif status == "completed":
            query = query.where(Todo.completed == True)

        # Apply priority filter
        if priority != "all":
            try:
                priority_enum = Priority(priority.lower())
                query = query.where(Todo.priority == priority_enum)
            except ValueError:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": f"Invalid priority: {priority}"
                    }
                }

        # Apply ordering and pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        with Session(engine) as session:
            result = session.execute(query)
            todos = result.scalars().all()

        # Format the results
        tasks = []
        for todo in todos:
            task_dict = {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "priority": todo.priority.value,
                "tags": todo.tags,
                "completed": todo.completed,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None
            }
            tasks.append(task_dict)

        # Get total count for pagination info
        count_query = select(Todo).where(Todo.user_id == user_id)
        if status == "pending":
            count_query = count_query.where(Todo.completed == False)
        elif status == "completed":
            count_query = count_query.where(Todo.completed == True)

        if priority != "all":
            try:
                priority_enum = Priority(priority.lower())
                count_query = count_query.where(Todo.priority == priority_enum)
            except ValueError:
                pass  # Already handled above

        # Execute count query
        with Session(engine) as session:
            count_result = session.execute(count_query)
            total_count = len(count_result.scalars().all())

        return {
            "success": True,
            "tasks": tasks,
            "total_count": total_count
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": f"Failed to list tasks: {str(e)}"
            }
        }


@mcp_server.tool(
    name="complete_task",
    description="Mark a todo item as completed for the authenticated user",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "The ID of the authenticated user"
            },
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to mark as completed"
            }
        },
        "required": ["user_id", "task_id"]
    }
)
async def complete_task(user_id: int, task_id: int) -> Dict[str, Any]:
    """Mark a todo item as completed for the authenticated user."""
    try:
        # Create database engine and session
        engine = create_engine(settings.DATABASE_URL)

        # Get the task by ID and user_id to ensure ownership
        query = select(Todo).where(Todo.id == task_id, Todo.user_id == user_id)

        with Session(engine) as session:
            result = session.execute(query)
            todo = result.scalar_one_or_none()

            if not todo:
                return {
                    "success": False,
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": f"Task with ID {task_id} not found or not owned by user {user_id}"
                    }
                }

            # Update the task as completed
            todo.completed = True
            todo.updated_at = datetime.utcnow()

            session.add(todo)
            session.commit()
            session.refresh(todo)

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task '{todo.title}' marked as completed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": f"Failed to complete task: {str(e)}"
            }
        }


@mcp_server.tool(
    name="delete_task",
    description="Delete a todo item for the authenticated user",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "The ID of the authenticated user"
            },
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to delete"
            }
        },
        "required": ["user_id", "task_id"]
    }
)
async def delete_task(user_id: int, task_id: int) -> Dict[str, Any]:
    """Delete a todo item for the authenticated user."""
    try:
        # Create database engine and session
        engine = create_engine(settings.DATABASE_URL)

        # Get the task by ID and user_id to ensure ownership
        query = select(Todo).where(Todo.id == task_id, Todo.user_id == user_id)

        with Session(engine) as session:
            result = session.execute(query)
            todo = result.scalar_one_or_none()

            if not todo:
                return {
                    "success": False,
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": f"Task with ID {task_id} not found or not owned by user {user_id}"
                    }
                }

            # Delete the task
            session.delete(todo)
            session.commit()

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task '{todo.title}' deleted successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": f"Failed to delete task: {str(e)}"
            }
        }


@mcp_server.tool(
    name="update_task",
    description="Update properties of an existing todo item for the authenticated user",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "The ID of the authenticated user"
            },
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to update"
            },
            "title": {
                "type": "string",
                "description": "New title for the task (optional)"
            },
            "description": {
                "type": "string",
                "description": "New description for the task (optional)"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "New priority for the task (optional)"
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "New tags for the task (optional)"
            },
            "due_date": {
                "type": "string",
                "format": "date-time",
                "description": "New due date for the task (optional)"
            },
            "completed": {
                "type": "boolean",
                "description": "New completion status for the task (optional)"
            }
        },
        "required": ["user_id", "task_id"]
    }
)
async def update_task(user_id: int, task_id: int, title: Optional[str] = None,
                     description: Optional[str] = None, priority: Optional[str] = None,
                     tags: Optional[List[str]] = None, due_date: Optional[str] = None,
                     completed: Optional[bool] = None) -> Dict[str, Any]:
    """Update properties of an existing todo item for the authenticated user."""
    try:
        # Create database engine and session
        engine = create_engine(settings.DATABASE_URL)

        # Get the task by ID and user_id to ensure ownership
        query = select(Todo).where(Todo.id == task_id, Todo.user_id == user_id)

        with Session(engine) as session:
            result = session.execute(query)
            todo = result.scalar_one_or_none()

            if not todo:
                return {
                    "success": False,
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": f"Task with ID {task_id} not found or not owned by user {user_id}"
                    }
                }

            # Update the task properties if provided
            if title is not None:
                todo.title = title
            if description is not None:
                todo.description = description
            if priority is not None:
                try:
                    todo.priority = Priority(priority.lower())
                except ValueError:
                    return {
                        "success": False,
                        "error": {
                            "code": "INVALID_INPUT",
                            "message": f"Invalid priority: {priority}. Must be 'low', 'medium', or 'high'"
                        }
                    }
            if tags is not None:
                todo.tags = tags
            if completed is not None:
                todo.completed = completed

            # Update the timestamp
            todo.updated_at = datetime.utcnow()

            session.add(todo)
            session.commit()
            session.refresh(todo)

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task '{todo.title}' updated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": f"Failed to update task: {str(e)}"
            }
        }