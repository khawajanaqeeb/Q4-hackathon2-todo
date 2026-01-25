import asyncio
from typing import Dict, Any, List
from datetime import datetime
import uuid
from sqlmodel import Session, select
from ..models.task import Task
from ..models.user import User


class TodoTools:
    """Todo-specific MCP tools for task management operations."""

    def __init__(self, session: Session):
        """
        Initialize Todo Tools.

        Args:
            session: Database session
        """
        self.session = session

    async def create_task_tool(self, params: Dict[str, Any], api_key: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Implement task creation MCP tool.

        Args:
            params: Parameters for task creation
            api_key: API key for authentication (not used in this local implementation)
            user_id: User ID

        Returns:
            Result of task creation
        """
        from datetime import datetime

        # Extract parameters
        title = params.get("title", "")
        description = params.get("description", "")
        priority = params.get("priority", "medium")  # Default to medium
        due_date_str = params.get("due_date")

        if not title:
            return {
                "success": False,
                "error": "Title is required for task creation"
            }

        # Validate priority
        valid_priorities = ["low", "medium", "high"]
        if priority not in valid_priorities:
            priority = "medium"  # Default fallback

        # Parse due date if provided
        due_date = None
        if due_date_str:
            try:
                # Try to parse ISO format date string
                from datetime import datetime
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
            except ValueError:
                # If parsing fails, ignore the due date
                pass

        # Create the task
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
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
            "task_id": str(task.id),
            "message": f"Task '{task.title}' created successfully",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
        }

    async def list_tasks_tool(self, params: Dict[str, Any], api_key: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Implement task listing MCP tool.

        Args:
            params: Parameters for task listing (filters, etc.)
            api_key: API key for authentication (not used in this local implementation)
            user_id: User ID

        Returns:
            List of tasks matching the criteria
        """
        # Build query based on filters
        query = select(Task).where(Task.user_id == user_id)

        # Apply filters from params
        status_filter = params.get("status")
        if status_filter:
            if status_filter.lower() == "completed":
                query = query.where(Task.completed == True)
            elif status_filter.lower() == "pending":
                query = query.where(Task.completed == False)

        priority_filter = params.get("priority")
        if priority_filter:
            from ..models.task import PriorityLevel
            try:
                priority_level = PriorityLevel(priority_filter.lower())
                query = query.where(Task.priority == priority_level)
            except ValueError:
                # Invalid priority, ignore filter
                pass

        # Execute query
        tasks = self.session.exec(query).all()

        # Format response
        task_list = []
        for task in tasks:
            task_dict = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            task_list.append(task_dict)

        return {
            "success": True,
            "count": len(task_list),
            "tasks": task_list
        }

    async def update_task_tool(self, params: Dict[str, Any], api_key: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Implement task update MCP tool.

        Args:
            params: Parameters for task update (task_id, fields to update)
            api_key: API key for authentication (not used in this local implementation)
            user_id: User ID

        Returns:
            Result of task update
        """
        # Extract parameters
        task_id_str = params.get("task_id")
        if not task_id_str:
            return {
                "success": False,
                "error": "Task ID is required for update"
            }

        try:
            task_id = uuid.UUID(task_id_str)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid task ID format: {task_id_str}"
            }

        # Get the task
        task = self.session.get(Task, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

        # Verify user owns the task
        if task.user_id != user_id:
            return {
                "success": False,
                "error": "Unauthorized: You don't have permission to update this task"
            }

        # Update fields based on provided params
        updated = False

        if "title" in params and params["title"] != task.title:
            task.title = params["title"]
            updated = True

        if "description" in params and params["description"] != task.description:
            task.description = params["description"]
            updated = True

        if "priority" in params:
            priority_val = params["priority"].lower()
            if priority_val in ["low", "medium", "high"]:
                from ..models.task import PriorityLevel
                task.priority = PriorityLevel(priority_val)
                updated = True

        if "due_date" in params:
            due_date_str = params["due_date"]
            try:
                from datetime import datetime
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                task.due_date = due_date
                updated = True
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid date format: {due_date_str}. Use ISO format."
                }

        if "completed" in params:
            task.completed = bool(params["completed"])
            updated = True

        if updated:
            task.updated_at = datetime.utcnow()
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

        return {
            "success": True,
            "message": f"Task '{task.title}' updated successfully" if updated else "No changes made to task",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }

    async def complete_task_tool(self, params: Dict[str, Any], api_key: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Implement task completion MCP tool.

        Args:
            params: Parameters for task completion (task_id)
            api_key: API key for authentication (not used in this local implementation)
            user_id: User ID

        Returns:
            Result of task completion
        """
        # Extract parameters
        task_id_str = params.get("task_id")
        if not task_id_str:
            return {
                "success": False,
                "error": "Task ID is required for completion"
            }

        try:
            task_id = uuid.UUID(task_id_str)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid task ID format: {task_id_str}"
            }

        # Get the task
        task = self.session.get(Task, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

        # Verify user owns the task
        if task.user_id != user_id:
            return {
                "success": False,
                "error": "Unauthorized: You don't have permission to complete this task"
            }

        # Mark as complete
        task.completed = True
        task.updated_at = datetime.utcnow()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return {
            "success": True,
            "message": f"Task '{task.title}' marked as complete",
            "task": {
                "id": str(task.id),
                "title": task.title,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }

    async def delete_task_tool(self, params: Dict[str, Any], api_key: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Implement task deletion MCP tool.

        Args:
            params: Parameters for task deletion (task_id)
            api_key: API key for authentication (not used in this local implementation)
            user_id: User ID

        Returns:
            Result of task deletion
        """
        # Extract parameters
        task_id_str = params.get("task_id")
        if not task_id_str:
            return {
                "success": False,
                "error": "Task ID is required for deletion"
            }

        try:
            task_id = uuid.UUID(task_id_str)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid task ID format: {task_id_str}"
            }

        # Get the task
        task = self.session.get(Task, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

        # Verify user owns the task
        if task.user_id != user_id:
            return {
                "success": False,
                "error": "Unauthorized: You don't have permission to delete this task"
            }

        # Delete the task
        self.session.delete(task)
        self.session.commit()

        return {
            "success": True,
            "message": f"Task '{task.title}' deleted successfully"
        }

    async def search_tasks_tool(self, params: Dict[str, Any], api_key: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Implement task search MCP tool.

        Args:
            params: Parameters for task search (query, filters)
            api_key: API key for authentication (not used in this local implementation)
            user_id: User ID

        Returns:
            List of tasks matching the search criteria
        """
        query_text = params.get("query", "").lower()
        if not query_text:
            return {
                "success": False,
                "error": "Query text is required for search"
            }

        # Build query to search in title and description
        tasks_query = select(Task).where(
            Task.user_id == user_id,
            (Task.title.ilike(f"%{query_text}%")) | (Task.description.ilike(f"%{query_text}%"))
        )

        # Apply additional filters
        status_filter = params.get("status")
        if status_filter:
            if status_filter.lower() == "completed":
                tasks_query = tasks_query.where(Task.completed == True)
            elif status_filter.lower() == "pending":
                tasks_query = tasks_query.where(Task.completed == False)

        priority_filter = params.get("priority")
        if priority_filter:
            from ..models.task import PriorityLevel
            try:
                priority_level = PriorityLevel(priority_filter.lower())
                tasks_query = tasks_query.where(Task.priority == priority_level)
            except ValueError:
                # Invalid priority, ignore filter
                pass

        # Execute query
        tasks = self.session.exec(tasks_query).all()

        # Format response
        task_list = []
        for task in tasks:
            task_dict = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            task_list.append(task_dict)

        return {
            "success": True,
            "count": len(task_list),
            "query": query_text,
            "tasks": task_list
        }

    async def get_task_details_tool(self, params: Dict[str, Any], api_key: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Implement task details MCP tool.

        Args:
            params: Parameters for getting task details (task_id)
            api_key: API key for authentication (not used in this local implementation)
            user_id: User ID

        Returns:
            Details of the specified task
        """
        # Extract parameters
        task_id_str = params.get("task_id")
        if not task_id_str:
            return {
                "success": False,
                "error": "Task ID is required to get task details"
            }

        try:
            task_id = uuid.UUID(task_id_str)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid task ID format: {task_id_str}"
            }

        # Get the task
        task = self.session.get(Task, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

        # Verify user owns the task
        if task.user_id != user_id:
            return {
                "success": False,
                "error": "Unauthorized: You don't have permission to view this task"
            }

        return {
            "success": True,
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
        }