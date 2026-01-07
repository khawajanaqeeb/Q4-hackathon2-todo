"""Service layer for business logic and data operations.

This module provides the TodoService class that manages in-memory task storage
and provides CRUD operations plus advanced search, filter, and sort capabilities.
"""

from src.todo_app.models import Priority, Task


class TodoService:
    """Manages in-memory task storage and operations.

    This service class encapsulates all business logic for task management including
    CRUD operations, search, filter, and sort capabilities.

    Attributes:
        _tasks: Private list storing all Task objects in memory
        _next_id: Private counter for auto-generating sequential task IDs
    """

    def __init__(self) -> None:
        """Initialize an empty TodoService with next_id starting at 1."""
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        tags: list[str] | None = None,
    ) -> Task:
        """Add a new task to the task list.

        Args:
            title: Task title (required, non-empty after strip)
            description: Task description (optional, defaults to empty string)
            priority: Task priority level (defaults to MEDIUM)
            tags: List of categorization tags (defaults to empty list)

        Returns:
            Created Task instance

        Raises:
            ValueError: If title is empty after stripping whitespace

        Example:
            >>> service = TodoService()
            >>> task = service.add_task("Buy groceries", priority=Priority.HIGH, tags=["shopping"])
            >>> task.id
            1
            >>> task.priority
            <Priority.HIGH: 'high'>
        """
        title_stripped = title.strip()
        if not title_stripped:
            raise ValueError("Title is required and cannot be empty")

        task = Task(
            id=self._next_id,
            title=title_stripped,
            description=description.strip(),
            completed=False,
            priority=priority,
            tags=tags if tags is not None else [],
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks from the task list.

        Returns:
            Copy of the tasks list (prevents external mutation)

        Example:
            >>> service = TodoService()
            >>> service.add_task("Task 1")
            >>> len(service.get_all_tasks())
            1
        """
        return self._tasks.copy()

    def get_task_by_id(self, task_id: int) -> Task | None:
        """Find a task by its ID.

        Args:
            task_id: ID of the task to find

        Returns:
            Task if found, None otherwise

        Example:
            >>> service = TodoService()
            >>> task = service.add_task("Find me")
            >>> found = service.get_task_by_id(task.id)
            >>> found.title
            'Find me'
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: Priority | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """Update a task's attributes.

        Args:
            task_id: ID of the task to update
            title: New title (None to keep current, empty string rejected)
            description: New description (None to keep current)
            priority: New priority level (None to keep current)
            tags: New tags list (None to keep current)

        Returns:
            True if task was updated, False if task not found or title invalid

        Raises:
            ValueError: If new title is empty after stripping whitespace

        Example:
            >>> service = TodoService()
            >>> task = service.add_task("Old title")
            >>> service.update_task(task.id, title="New title", priority=Priority.HIGH)
            True
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False

        # Validate and update title if provided
        if title is not None:
            title_stripped = title.strip()
            if not title_stripped:
                raise ValueError("Title is required and cannot be empty")
            task.title = title_stripped

        # Update description if provided
        if description is not None:
            task.description = description.strip()

        # Update priority if provided
        if priority is not None:
            task.priority = priority

        # Update tags if provided
        if tags is not None:
            task.tags = tags

        return True

    def delete_task(self, task_id: int) -> bool:
        """Delete a task from the task list.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if task was deleted, False if task ID not found

        Example:
            >>> service = TodoService()
            >>> task = service.add_task("Delete me")
            >>> service.delete_task(task.id)
            True
            >>> service.delete_task(task.id)
            False
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False

        self._tasks.remove(task)
        return True

    def mark_task_complete(self, task_id: int) -> bool:
        """Toggle the completion status of a task.

        Args:
            task_id: ID of the task to toggle

        Returns:
            True if task status was toggled, False if task ID doesn't exist

        Example:
            >>> service = TodoService()
            >>> task = service.add_task("Complete me")
            >>> service.mark_task_complete(task.id)
            True
            >>> task.completed
            True
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False

        task.completed = not task.completed
        return True

    def search_tasks(self, keyword: str) -> list[Task]:
        """Search tasks by keyword in title or description.

        Performs case-insensitive matching against both title and description fields.

        Args:
            keyword: Search term to match against

        Returns:
            List of tasks matching the keyword (may be empty)

        Example:
            >>> service = TodoService()
            >>> service.add_task("Buy milk", "For breakfast")
            >>> results = service.search_tasks("milk")
            >>> len(results)
            1
        """
        return [task for task in self._tasks if task.matches_keyword(keyword)]

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Filter tasks by completion status.

        Args:
            completed: True for completed tasks, False for pending tasks

        Returns:
            List of tasks with matching status

        Example:
            >>> service = TodoService()
            >>> task1 = service.add_task("Task 1")
            >>> task2 = service.add_task("Task 2")
            >>> service.mark_task_complete(task1.id)
            >>> len(service.filter_by_status(completed=True))
            1
        """
        return [task for task in self._tasks if task.completed == completed]

    def filter_by_priority(self, priority: Priority) -> list[Task]:
        """Filter tasks by priority level.

        Args:
            priority: Priority level to filter by (HIGH, MEDIUM, or LOW)

        Returns:
            List of tasks with matching priority

        Example:
            >>> service = TodoService()
            >>> service.add_task("Urgent", priority=Priority.HIGH)
            >>> len(service.filter_by_priority(Priority.HIGH))
            1
        """
        return [task for task in self._tasks if task.priority == priority]

    def filter_by_tag(self, tag: str) -> list[Task]:
        """Filter tasks by tag (case-insensitive).

        Args:
            tag: Tag to filter by

        Returns:
            List of tasks containing the tag (case-insensitive match)

        Example:
            >>> service = TodoService()
            >>> service.add_task("Work task", tags=["Work", "Urgent"])
            >>> len(service.filter_by_tag("work"))
            1
        """
        return [task for task in self._tasks if task.has_tag(tag)]

    def sort_by_priority(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by priority (HIGH → MEDIUM → LOW).

        Args:
            tasks: List of tasks to sort (defaults to all tasks)

        Returns:
            New list with tasks sorted by priority (high priority first)

        Example:
            >>> service = TodoService()
            >>> service.add_task("Low", priority=Priority.LOW)
            >>> service.add_task("High", priority=Priority.HIGH)
            >>> sorted_tasks = service.sort_by_priority()
            >>> sorted_tasks[0].priority
            <Priority.HIGH: 'high'>
        """
        task_list = tasks if tasks is not None else self._tasks
        return sorted(task_list, key=lambda t: t.priority)

    def sort_by_title(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks alphabetically by title (A-Z, case-insensitive).

        Args:
            tasks: List of tasks to sort (defaults to all tasks)

        Returns:
            New list with tasks sorted alphabetically by title

        Example:
            >>> service = TodoService()
            >>> service.add_task("Zebra")
            >>> service.add_task("Apple")
            >>> sorted_tasks = service.sort_by_title()
            >>> sorted_tasks[0].title
            'Apple'
        """
        task_list = tasks if tasks is not None else self._tasks
        return sorted(task_list, key=lambda t: t.title.lower())

    def sort_by_id(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by ID (creation order, ascending).

        Args:
            tasks: List of tasks to sort (defaults to all tasks)

        Returns:
            New list with tasks sorted by ID (chronological order)

        Example:
            >>> service = TodoService()
            >>> task1 = service.add_task("First")
            >>> task2 = service.add_task("Second")
            >>> sorted_tasks = service.sort_by_id()
            >>> sorted_tasks[0].id < sorted_tasks[1].id
            True
        """
        task_list = tasks if tasks is not None else self._tasks
        return sorted(task_list, key=lambda t: t.id)
