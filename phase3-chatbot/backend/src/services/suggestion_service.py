from typing import List, Dict, Any, Optional
from sqlmodel import Session
from datetime import datetime
from ..models.conversation import Message
from ..models.task import Task


class SuggestionService:
    """Service class for generating contextual suggestions based on tasks and conversations."""

    def __init__(self, session: Session):
        """Initialize SuggestionService with database session."""
        self.session = session

    def get_contextual_suggestions(self, user_id: str, conversation_context: List[Message] = None) -> List[str]:
        """
        Generate contextual suggestions based on user's tasks and conversation history.

        Args:
            user_id: ID of the user
            conversation_context: Recent messages in the conversation for context

        Returns:
            List of suggested actions or commands
        """
        suggestions = []

        # Get user's tasks to provide context-aware suggestions
        user_tasks = self._get_user_tasks(user_id)

        # Add suggestions based on task status
        incomplete_tasks = [task for task in user_tasks if not task.completed]
        completed_tasks = [task for task in user_tasks if task.completed]

        if len(incomplete_tasks) > 0:
            suggestions.append(f"You have {len(incomplete_tasks)} pending tasks. Would you like to see them?")

            # If there are high priority tasks
            high_priority_tasks = [t for t in incomplete_tasks if t.priority.value == "high"]
            if high_priority_tasks:
                suggestions.append(f"You have {len(high_priority_tasks)} high priority tasks that need attention.")

        if len(completed_tasks) > 0:
            suggestions.append(f"You've completed {len(completed_tasks)} tasks recently. Great job!")

        # Analyze conversation context for more specific suggestions
        if conversation_context:
            recent_user_messages = [
                msg.content for msg in conversation_context
                if msg.role.value == "user"
            ][-3:]  # Last 3 user messages

            # Look for patterns in recent user requests
            for msg in recent_user_messages:
                if "add" in msg.lower() or "create" in msg.lower() or "new" in msg.lower():
                    suggestions.append("Would you like to add a task with a specific priority or due date?")

                if "complete" in msg.lower() or "done" in msg.lower():
                    if incomplete_tasks:
                        suggestions.append("Which task would you like to mark as complete?")

        # Add general suggestions
        suggestions.extend([
            "You can ask me to add, list, update, or complete tasks.",
            "Try asking 'show me my high priority tasks' or 'what do I need to do today?'",
            "You can set due dates and priorities for your tasks."
        ])

        # Limit to top 5 suggestions
        return suggestions[:5]

    def _get_user_tasks(self, user_id: str) -> List[Task]:
        """Get all tasks for a user."""
        from sqlmodel import select
        # Import here to avoid circular import
        from ..database import get_session

        # In actual implementation, we'd query the database for user's tasks
        # For now, we'll return an empty list as placeholder
        # This would normally be: SELECT * FROM task WHERE user_id = user_id
        return []

    def get_task_suggestions(self, user_id: str, current_task: Optional[Task] = None) -> List[str]:
        """
        Generate suggestions related to task management.

        Args:
            user_id: ID of the user
            current_task: Current task context if available

        Returns:
            List of task-related suggestions
        """
        suggestions = []

        # Get user's tasks to provide relevant suggestions
        user_tasks = self._get_user_tasks(user_id)

        if current_task:
            suggestions.append(f"What would you like to do with '{current_task.title}'?")

        # Suggest common task operations
        suggestions.extend([
            "You can add a new task by saying 'Add a task to ...'",
            "List your tasks by asking 'Show me my tasks'",
            "Mark a task as complete by saying 'Complete task ...'",
            "Update a task priority by saying 'Set priority of task ... to high'"
        ])

        return suggestions[:4]