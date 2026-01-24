import asyncio
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime
import uuid
from sqlmodel import Session, select
from ..models.task import Task, PriorityLevel
from ..config import settings


class MCPIntegrationService:
    """Service class for integrating with MCP (Model Context Protocol) tools for task operations."""

    def __init__(self, session: Session):
        """Initialize MCPIntegrationService with database session."""
        self.session = session
        self.mcp_base_url = settings.MCP_SERVER_URL

    async def create_task_via_mcp(self, user_id: uuid.UUID, title: str, description: Optional[str] = None,
                                 priority: Optional[str] = None, due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Create a task using MCP tools.

        Args:
            user_id: ID of the user creating the task
            title: Task title
            description: Task description (optional)
            priority: Task priority (low, medium, high) (optional)
            due_date: Task due date (optional)

        Returns:
            Dictionary with result of task creation
        """
        try:
            # Validate priority if provided
            priority_level = None
            if priority:
                try:
                    priority_level = PriorityLevel(priority.lower())
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid priority level. Must be one of: {[p.value for p in PriorityLevel]}"
                    }

            # Create the task in the database
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority_level if priority_level else PriorityLevel.MEDIUM,
                due_date=due_date,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "task": task,
                "message": f"Task '{title}' created successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating task: {str(e)}"
            }

    async def list_tasks_via_mcp(self, user_id: uuid.UUID, filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List tasks using MCP tools.

        Args:
            user_id: ID of the user whose tasks to list
            filter_params: Parameters to filter tasks (optional)

        Returns:
            Dictionary with list of tasks
        """
        try:
            # Build query based on filters
            query = select(Task).where(Task.user_id == user_id)

            if filter_params:
                # Apply filters if provided
                if filter_params.get("status"):
                    completed = filter_params["status"].lower() == "completed"
                    query = query.where(Task.completed == completed)

                if filter_params.get("priority"):
                    try:
                        priority = PriorityLevel(filter_params["priority"].lower())
                        query = query.where(Task.priority == priority)
                    except ValueError:
                        return {
                            "success": False,
                            "error": f"Invalid priority filter. Must be one of: {[p.value for p in PriorityLevel]}"
                        }

                if filter_params.get("completed") is not None:
                    query = query.where(Task.completed == filter_params["completed"])

            # Execute query
            tasks = self.session.exec(query).all()

            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing tasks: {str(e)}"
            }

    async def update_task_via_mcp(self, user_id: uuid.UUID, task_id: uuid.UUID,
                                updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a task using MCP tools.

        Args:
            user_id: ID of the user who owns the task
            task_id: ID of the task to update
            updates: Dictionary of fields to update

        Returns:
            Dictionary with result of task update
        """
        try:
            # Get the task
            task = self.session.get(Task, task_id)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found"
                }

            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Task does not belong to user"
                }

            # Apply updates
            for key, value in updates.items():
                if hasattr(task, key):
                    if key == "priority":
                        try:
                            setattr(task, key, PriorityLevel(value.lower()))
                        except ValueError:
                            return {
                                "success": False,
                                "error": f"Invalid priority value. Must be one of: {[p.value for p in PriorityLevel]}"
                            }
                    elif key == "due_date":
                        # Parse date string if it's a string
                        if isinstance(value, str):
                            try:
                                setattr(task, key, datetime.fromisoformat(value))
                            except ValueError:
                                return {
                                    "success": False,
                                    "error": f"Invalid date format: {value}. Expected ISO format."
                                }
                        else:
                            setattr(task, key, value)
                    else:
                        setattr(task, key, value)

            # Update timestamp
            task.updated_at = datetime.utcnow()

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "task": task,
                "message": f"Task '{task.title}' updated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating task: {str(e)}"
            }

    async def delete_task_via_mcp(self, user_id: uuid.UUID, task_id: uuid.UUID) -> Dict[str, Any]:
        """
        Delete a task using MCP tools.

        Args:
            user_id: ID of the user who owns the task
            task_id: ID of the task to delete

        Returns:
            Dictionary with result of task deletion
        """
        try:
            # Get the task
            task = self.session.get(Task, task_id)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found"
                }

            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Task does not belong to user"
                }

            # Delete the task
            self.session.delete(task)
            self.session.commit()

            return {
                "success": True,
                "message": f"Task '{task.title}' deleted successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error deleting task: {str(e)}"
            }

    async def complete_task_via_mcp(self, user_id: uuid.UUID, task_id: uuid.UUID) -> Dict[str, Any]:
        """
        Mark a task as complete using MCP tools.

        Args:
            user_id: ID of the user who owns the task
            task_id: ID of the task to mark as complete

        Returns:
            Dictionary with result of task completion
        """
        return await self.update_task_via_mcp(user_id, task_id, {"completed": True})

    async def process_task_operation(self, user_id: uuid.UUID, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task operation based on the operation type.

        Args:
            user_id: ID of the user performing the operation
            operation: Type of operation (create, list, update, delete, complete)
            params: Parameters for the operation

        Returns:
            Dictionary with result of the operation
        """
        operation_map = {
            "task_creation": self.create_task_via_mcp,
            "task_listing": self.list_tasks_via_mcp,
            "task_update": self.update_task_via_mcp,
            "task_deletion": self.delete_task_via_mcp,
            "task_completion": self.complete_task_via_mcp
        }

        operation_func = operation_map.get(operation)

        if not operation_func:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }

        # Call the appropriate function with the right parameters
        if operation == "task_creation":
            return await operation_func(
                user_id,
                title=params.get("title", ""),
                description=params.get("description"),
                priority=params.get("priority"),
                due_date=params.get("due_date")
            )
        elif operation == "task_listing":
            return await operation_func(user_id, filter_params=params.get("filters"))
        elif operation == "task_update":
            return await operation_func(user_id, params.get("task_id"), params.get("updates", {}))
        elif operation == "task_deletion":
            return await operation_func(user_id, params.get("task_id"))
        elif operation == "task_completion":
            return await operation_func(user_id, params.get("task_id"))
        else:
            return {
                "success": False,
                "error": f"Operation not supported: {operation}"
            }