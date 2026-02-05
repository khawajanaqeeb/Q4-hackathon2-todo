"""MCP tools for todo operations in the Phase 3 chatbot system."""
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from sqlalchemy import func


class TodoTools:
    """Collection of MCP tools for todo operations."""

    def __init__(self, db_session: Session, current_user):
        self.db_session = db_session
        self.current_user = current_user

    def create_todo(self, title: str, description: Optional[str] = None,
                   priority: Optional[str] = "medium", due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new todo item for the authenticated user.

        Args:
            title: Title of the new todo item
            description: Optional description of the todo
            priority: Priority level (low, medium, high) - defaults to medium
            due_date: Optional due date in YYYY-MM-DD format

        Returns:
            Dictionary with the created todo information
        """
        # Validate inputs
        if not title or len(title.strip()) == 0:
            raise ValueError("Title is required")

        # Create new todo with current user's ID
        new_todo = Todo(
            title=title.strip(),
            description=description,
            priority=priority,
            due_date=due_date,
            completed=False,
            user_id=self.current_user.id
        )

        # Add to database
        self.db_session.add(new_todo)
        self.db_session.commit()
        self.db_session.refresh(new_todo)

        return {
            "id": str(new_todo.id),
            "title": new_todo.title,
            "description": new_todo.description,
            "priority": new_todo.priority,
            "due_date": new_todo.due_date,
            "completed": new_todo.completed,
            "status": "success",
            "message": f"Todo '{new_todo.title}' created successfully"
        }

    def list_todos(self, status: Optional[str] = None, priority: Optional[str] = None,
                  limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve todos for the authenticated user with optional filters.

        Args:
            status: Filter by status ('active', 'completed', 'all') - defaults to 'active'
            priority: Filter by priority ('low', 'medium', 'high')
            limit: Maximum number of todos to return
            offset: Offset for pagination

        Returns:
            List of todo dictionaries matching criteria
        """
        # Build query with user filter
        query = select(Todo).where(Todo.user_id == self.current_user.id)

        # Apply status filter
        if status is not None:
            if status.lower() == 'active':
                query = query.where(Todo.completed == False)
            elif status.lower() == 'completed':
                query = query.where(Todo.completed == True)
            elif status.lower() != 'all':
                # If status is provided but not 'active' or 'completed', ignore the filter
                pass
        else:
            # Default to active only if no status specified
            query = query.where(Todo.completed == False)

        # Apply priority filter
        if priority is not None:
            query = query.where(Todo.priority == priority)

        # Apply limit and offset for pagination
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        # Execute query
        todos = self.db_session.exec(query).all()

        # Convert to dictionary format
        return [
            {
                "id": str(todo.id),
                "title": todo.title,
                "description": todo.description,
                "priority": todo.priority,
                "due_date": todo.due_date,
                "completed": todo.completed,
                "created_at": todo.created_at.isoformat() if todo.created_at else None
            }
            for todo in todos
        ]

    def update_todo(self, todo_id: str, title: Optional[str] = None,
                   description: Optional[str] = None, priority: Optional[str] = None,
                   status: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a specific todo item for the authenticated user.

        Args:
            todo_id: ID of the todo to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            status: New status - 'completed' or 'active' (optional)
            due_date: New due date (optional)

        Returns:
            Dictionary with updated todo information
        """
        # Fetch the existing todo
        todo = self.db_session.get(Todo, UUID(todo_id))

        if not todo:
            raise ValueError(f"Todo with ID {todo_id} not found")

        # Verify that this todo belongs to the current user
        if todo.user_id != self.current_user.id:
            raise ValueError("Access denied: This todo does not belong to the current user")

        # Track previous state for logging
        previous_state = {
            "id": str(todo.id),
            "title": todo.title,
            "description": todo.description,
            "priority": todo.priority,
            "due_date": todo.due_date,
            "completed": todo.completed
        }

        # Update fields if provided
        if title is not None:
            todo.title = title.strip()
        if description is not None:
            todo.description = description
        if priority is not None:
            todo.priority = priority
        if status is not None:
            todo.completed = (status.lower() == 'completed')
        if due_date is not None:
            todo.due_date = due_date

        # Update timestamp
        from datetime import datetime
        todo.updated_at = datetime.utcnow()

        # Commit changes
        self.db_session.add(todo)
        self.db_session.commit()
        self.db_session.refresh(todo)

        # Return updated todo info
        updated_state = {
            "id": str(todo.id),
            "title": todo.title,
            "description": todo.description,
            "priority": todo.priority,
            "due_date": todo.due_date,
            "completed": todo.completed,
            "status": "success",
            "message": f"Todo '{todo.title}' updated successfully"
        }

        return updated_state

    def delete_todo(self, todo_id: str) -> Dict[str, Any]:
        """
        Delete a specific todo item for the authenticated user.

        Args:
            todo_id: ID of the todo to delete

        Returns:
            Confirmation dictionary of the deletion
        """
        # Fetch the existing todo
        todo = self.db_session.get(Todo, UUID(todo_id))

        if not todo:
            raise ValueError(f"Todo with ID {todo_id} not found")

        # Verify that this todo belongs to the current user
        if todo.user_id != self.current_user.id:
            raise ValueError("Access denied: This todo does not belong to the current user")

        # Delete the todo
        self.db_session.delete(todo)
        self.db_session.commit()

        return {
            "id": todo_id,
            "status": "success",
            "message": f"Todo with ID {todo_id} deleted successfully"
        }

    def complete_todo(self, todo_id: str, completed: bool = True) -> Dict[str, Any]:
        """
        Mark a specific todo item as complete/incomplete for the authenticated user.

        Args:
            todo_id: ID of the todo to update
            completed: Whether to mark as completed (True) or active (False)

        Returns:
            Dictionary with updated todo information
        """
        # Fetch the existing todo
        todo = self.db_session.get(Todo, UUID(todo_id))

        if not todo:
            raise ValueError(f"Todo with ID {todo_id} not found")

        # Verify that this todo belongs to the current user
        if todo.user_id != self.current_user.id:
            raise ValueError("Access denied: This todo does not belong to the current user")

        # Store previous state
        previous_completed = todo.completed

        # Update completion status
        todo.completed = completed
        todo.updated_at = self.db_session.exec(select(func.now())).first()

        # Commit changes
        self.db_session.add(todo)
        self.db_session.commit()
        self.db_session.refresh(todo)

        status_text = "completed" if completed else "marked as active"
        return {
            "id": str(todo.id),
            "title": todo.title,
            "completed": todo.completed,
            "status": "success",
            "message": f"Todo '{todo.title}' {status_text} successfully"
        }