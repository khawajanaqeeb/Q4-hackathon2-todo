"""
Todo Tools Implementation for MCP Integration
"""
from sqlmodel import Session, select
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import json
from ..models.task import Task, PriorityLevel
from ..models.user import User


class TodoTools:
    """Implementation of todo-specific tools that connect to the database"""

    def __init__(self, session: Session):
        """
        Initialize TodoTools with database session

        Args:
            session: SQLModel database session
        """
        self.session = session

    async def create_task_tool(self, params: Dict[str, Any], api_key: str, user_id: UUID) -> Dict[str, Any]:
        """
        Create a new task tool implementation

        Args:
            params: Parameters for task creation
            api_key: API key for authentication (not used for internal tools)
            user_id: ID of the user creating the task

        Returns:
            Result of the operation
        """
        try:
            # Validate user exists
            user = self.session.get(User, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Create new task
            task = Task(
                user_id=user_id,
                title=params.get("title"),
                description=params.get("description"),
                priority=params.get("priority", "medium"),
                due_date=params.get("due_date")
            )

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Task '{task.title}' created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_tasks_tool(self, params: Dict[str, Any], api_key: str, user_id: UUID) -> Dict[str, Any]:
        """
        List tasks tool implementation

        Args:
            params: Parameters for filtering tasks
            api_key: API key for authentication
            user_id: ID of the user whose tasks to list

        Returns:
            List of tasks
        """
        try:
            # Validate user exists
            user = self.session.get(User, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Build query
            query = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            status_filter = params.get("status", "all")
            if status_filter != "all":
                completed = status_filter == "completed"
                query = query.where(Task.completed == completed)

            # Apply priority filter
            priority_filter = params.get("priority", "all")
            if priority_filter != "all":
                query = query.where(Task.priority == priority_filter)

            # Apply limit
            limit = params.get("limit", 10)
            query = query.limit(limit)

            tasks = self.session.exec(query).all()

            task_list = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }

                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()

                task_list.append(task_dict)

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_task_tool(self, params: Dict[str, Any], api_key: str, user_id: UUID) -> Dict[str, Any]:
        """
        Update task tool implementation

        Args:
            params: Parameters for updating the task
            api_key: API key for authentication
            user_id: ID of the user whose task to update

        Returns:
            Result of the operation
        """
        try:
            # Validate user exists
            user = self.session.get(User, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Get task
            task_id_str = params.get("task_id")
            if not task_id_str:
                return {"success": False, "error": "task_id is required"}

            task = self.session.get(Task, UUID(task_id_str))
            if not task or task.user_id != user_id:
                return {"success": False, "error": "Task not found or does not belong to user"}

            # Update fields if provided
            if "title" in params and params["title"] is not None:
                task.title = params["title"]
            if "description" in params and params["description"] is not None:
                task.description = params["description"]
            if "priority" in params and params["priority"] is not None:
                task.priority = params["priority"]
            if "due_date" in params and params["due_date"] is not None:
                task.due_date = params["due_date"]
            if "completed" in params and params["completed"] is not None:
                task.completed = params["completed"]

            task.updated_at = datetime.utcnow()

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "message": f"Task '{task.title}' updated successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def complete_task_tool(self, params: Dict[str, Any], api_key: str, user_id: UUID) -> Dict[str, Any]:
        """
        Complete task tool implementation

        Args:
            params: Parameters for completing the task
            api_key: API key for authentication
            user_id: ID of the user whose task to complete

        Returns:
            Result of the operation
        """
        try:
            # Validate user exists
            user = self.session.get(User, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Get task
            task_id_str = params.get("task_id")
            if not task_id_str:
                return {"success": False, "error": "task_id is required"}

            task = self.session.get(Task, UUID(task_id_str))
            if not task or task.user_id != user_id:
                return {"success": False, "error": "Task not found or does not belong to user"}

            task.completed = True
            task.updated_at = datetime.utcnow()

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "message": f"Task '{task.title}' marked as completed"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete_task_tool(self, params: Dict[str, Any], api_key: str, user_id: UUID) -> Dict[str, Any]:
        """
        Delete task tool implementation

        Args:
            params: Parameters for deleting the task
            api_key: API key for authentication
            user_id: ID of the user whose task to delete

        Returns:
            Result of the operation
        """
        try:
            # Validate user exists
            user = self.session.get(User, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Get task
            task_id_str = params.get("task_id")
            if not task_id_str:
                return {"success": False, "error": "task_id is required"}

            task = self.session.get(Task, UUID(task_id_str))
            if not task or task.user_id != user_id:
                return {"success": False, "error": "Task not found or does not belong to user"}

            self.session.delete(task)
            self.session.commit()

            return {
                "success": True,
                "message": "Task deleted successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_tasks_tool(self, params: Dict[str, Any], api_key: str, user_id: UUID) -> Dict[str, Any]:
        """
        Search tasks tool implementation

        Args:
            params: Parameters for searching tasks
            api_key: API key for authentication
            user_id: ID of the user whose tasks to search

        Returns:
            List of matching tasks
        """
        try:
            # Validate user exists
            user = self.session.get(User, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Get search parameters
            query_param = params.get("query")
            if not query_param:
                return {"success": False, "error": "query is required"}

            # Build query
            search_query = select(Task).where(
                (Task.user_id == user_id) &
                (
                    (Task.title.contains(query_param)) |
                    (Task.description.contains(query_param) if Task.description else False)
                )
            )

            # Apply status filter
            status_filter = params.get("status", "all")
            if status_filter != "all":
                completed = status_filter == "completed"
                search_query = search_query.where(Task.completed == completed)

            # Apply priority filter
            priority_filter = params.get("priority", "all")
            if priority_filter != "all":
                search_query = search_query.where(Task.priority == priority_filter)

            tasks = self.session.exec(search_query).all()

            task_list = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }

                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()

                task_list.append(task_dict)

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_task_details_tool(self, params: Dict[str, Any], api_key: str, user_id: UUID) -> Dict[str, Any]:
        """
        Get task details tool implementation

        Args:
            params: Parameters for getting task details
            api_key: API key for authentication
            user_id: ID of the user whose task details to get

        Returns:
            Details of the task
        """
        try:
            # Validate user exists
            user = self.session.get(User, user_id)
            if not user:
                return {"success": False, "error": "User not found"}

            # Get task
            task_id_str = params.get("task_id")
            if not task_id_str:
                return {"success": False, "error": "task_id is required"}

            task = self.session.get(Task, UUID(task_id_str))
            if not task or task.user_id != user_id:
                return {"success": False, "error": "Task not found or does not belong to user"}

            task_detail = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }

            if task.due_date:
                task_detail["due_date"] = task.due_date.isoformat()

            return {
                "success": True,
                "task": task_detail
            }
        except Exception as e:
            return {"success": False, "error": str(e)}