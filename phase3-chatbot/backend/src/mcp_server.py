"""
Official MCP Server Implementation for Todo Operations
"""
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlmodel import create_engine, Session, select
from .models.task import Task
from .models.user import User
from .config import DATABASE_URL
from mcp.server import Server
from mcp.types import Tool, RequestContext
from pydantic import BaseModel, Field


# Define Pydantic models for tool parameters
class CreateTaskParams(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    due_date: Optional[str] = None


class ListTasksParams(BaseModel):
    user_id: str
    status: Optional[str] = "all"  # "all", "completed", "pending"
    priority: Optional[str] = "all"  # "all", "high", "medium", "low"
    limit: Optional[int] = 10


class UpdateTaskParams(BaseModel):
    user_id: str
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    completed: Optional[bool] = None


class CompleteTaskParams(BaseModel):
    user_id: str
    task_id: str


class DeleteTaskParams(BaseModel):
    user_id: str
    task_id: str


class SearchTasksParams(BaseModel):
    user_id: str
    query: str
    status: Optional[str] = "all"
    priority: Optional[str] = "all"


class TodoMcpServer:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.server = Server("todo-mcp-server")

        # Register all todo tools
        self._register_todo_tools()

    def _register_todo_tools(self):
        """Register all todo operation tools with the MCP server"""
        # Create task tool
        self.server.tools.register(
            Tool(
                name="create_task",
                description="Create a new todo task",
                input_schema={
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
            ),
            self._create_task_handler
        )

        # List tasks tool
        self.server.tools.register(
            Tool(
                name="list_tasks",
                description="List all tasks for a user with optional filters",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose tasks to list"},
                        "status": {"type": "string", "enum": ["all", "completed", "pending"], "default": "all"},
                        "priority": {"type": "string", "enum": ["all", "high", "medium", "low"], "default": "all"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["user_id"]
                }
            ),
            self._list_tasks_handler
        )

        # Update task tool
        self.server.tools.register(
            Tool(
                name="update_task",
                description="Update an existing task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose task to update"},
                        "task_id": {"type": "integer", "description": "ID of the task to update"},
                        "title": {"type": "string", "description": "New title for the task"},
                        "description": {"type": "string", "description": "New description for the task"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                        "due_date": {"type": "string", "format": "date", "description": "New due date in YYYY-MM-DD format"},
                        "completed": {"type": "boolean", "description": "Whether the task is completed"}
                    },
                    "required": ["user_id", "task_id"]
                }
            ),
            self._update_task_handler
        )

        # Complete task tool
        self.server.tools.register(
            Tool(
                name="complete_task",
                description="Mark a task as completed",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose task to complete"},
                        "task_id": {"type": "integer", "description": "ID of the task to complete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            ),
            self._complete_task_handler
        )

        # Delete task tool
        self.server.tools.register(
            Tool(
                name="delete_task",
                description="Delete a task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose task to delete"},
                        "task_id": {"type": "integer", "description": "ID of the task to delete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            ),
            self._delete_task_handler
        )

        # Search tasks tool
        self.server.tools.register(
            Tool(
                name="search_tasks",
                description="Search tasks by keyword",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose tasks to search"},
                        "query": {"type": "string", "description": "Keyword to search for in titles and descriptions"},
                        "status": {"type": "string", "enum": ["all", "completed", "pending"], "default": "all"},
                        "priority": {"type": "string", "enum": ["all", "high", "medium", "low"], "default": "all"}
                    },
                    "required": ["user_id", "query"]
                }
            ),
            self._search_tasks_handler
        )

    async def _create_task_handler(self, params: Dict[str, Any], request_context: RequestContext) -> Dict[str, Any]:
        """Handler for create_task tool"""
        validated_params = CreateTaskParams(**params)

        with Session(self.engine) as session:
            # Verify user exists
            user = session.get(User, int(validated_params.user_id))
            if not user:
                return {"error": "User not found", "success": False}

            # Create new task
            task = Task(
                user_id=int(validated_params.user_id),
                title=validated_params.title,
                description=validated_params.description,
                priority=validated_params.priority,
                due_date=validated_params.due_date
            )

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Task '{task.title}' created successfully"
            }

    async def _list_tasks_handler(self, params: Dict[str, Any], request_context: RequestContext) -> Dict[str, Any]:
        """Handler for list_tasks tool"""
        validated_params = ListTasksParams(**params)

        with Session(self.engine) as session:
            # Verify user exists
            user = session.get(User, int(validated_params.user_id))
            if not user:
                return {"error": "User not found", "success": False}

            # Build query
            query = select(Task).where(Task.user_id == int(validated_params.user_id))

            if validated_params.status != "all":
                query = query.where(Task.completed == (validated_params.status == "completed"))

            if validated_params.priority != "all":
                query = query.where(Task.priority == validated_params.priority)

            query = query.limit(validated_params.limit)

            tasks = session.exec(query).all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                })

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list)
            }

    async def _update_task_handler(self, params: Dict[str, Any], request_context: RequestContext) -> Dict[str, Any]:
        """Handler for update_task tool"""
        validated_params = UpdateTaskParams(**params)

        with Session(self.engine) as session:
            # Verify user exists
            user = session.get(User, int(validated_params.user_id))
            if not user:
                return {"error": "User not found", "success": False}

            # Get task
            task = session.get(Task, int(validated_params.task_id))
            if not task or task.user_id != int(validated_params.user_id):
                return {"error": "Task not found or does not belong to user", "success": False}

            # Update task fields
            if validated_params.title is not None:
                task.title = validated_params.title
            if validated_params.description is not None:
                task.description = validated_params.description
            if validated_params.priority is not None:
                task.priority = validated_params.priority
            if validated_params.due_date is not None:
                task.due_date = validated_params.due_date
            if validated_params.completed is not None:
                task.completed = validated_params.completed

            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "message": f"Task '{task.title}' updated successfully"
            }

    async def _complete_task_handler(self, params: Dict[str, Any], request_context: RequestContext) -> Dict[str, Any]:
        """Handler for complete_task tool"""
        validated_params = CompleteTaskParams(**params)

        with Session(self.engine) as session:
            # Verify user exists
            user = session.get(User, int(validated_params.user_id))
            if not user:
                return {"error": "User not found", "success": False}

            # Get task
            task = session.get(Task, int(validated_params.task_id))
            if not task or task.user_id != int(validated_params.user_id):
                return {"error": "Task not found or does not belong to user", "success": False}

            task.completed = True
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "message": f"Task '{task.title}' marked as completed"
            }

    async def _delete_task_handler(self, params: Dict[str, Any], request_context: RequestContext) -> Dict[str, Any]:
        """Handler for delete_task tool"""
        validated_params = DeleteTaskParams(**params)

        with Session(self.engine) as session:
            # Verify user exists
            user = session.get(User, int(validated_params.user_id))
            if not user:
                return {"error": "User not found", "success": False}

            # Get task
            task = session.get(Task, int(validated_params.task_id))
            if not task or task.user_id != int(validated_params.user_id):
                return {"error": "Task not found or does not belong to user", "success": False}

            session.delete(task)
            session.commit()

            return {
                "success": True,
                "message": "Task deleted successfully"
            }

    async def _search_tasks_handler(self, params: Dict[str, Any], request_context: RequestContext) -> Dict[str, Any]:
        """Handler for search_tasks tool"""
        validated_params = SearchTasksParams(**params)

        with Session(self.engine) as session:
            # Verify user exists
            user = session.get(User, int(validated_params.user_id))
            if not user:
                return {"error": "User not found", "success": False}

            # Build query with search
            query = select(Task).where(Task.user_id == int(validated_params.user_id))

            # Add search condition - check both title and description
            query = query.where(
                (Task.title.contains(validated_params.query)) |
                ((Task.description.is_not(None)) & (Task.description.contains(validated_params.query)))
            )

            if validated_params.status != "all":
                query = query.where(Task.completed == (validated_params.status == "completed"))

            if validated_params.priority != "all":
                query = query.where(Task.priority == validated_params.priority)

            tasks = session.exec(query).all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                })

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list)
            }

    async def start_server(self, host: str = "localhost", port: int = 3000):
        """Start the MCP server"""
        from datetime import datetime  # Import here to avoid conflicts

        print(f"Starting MCP Server on {host}:{port}")
        await self.server.run_tcp(host, port)


# For standalone execution
if __name__ == "__main__":
    import asyncio

    server = TodoMcpServer()
    asyncio.run(server.start_server())