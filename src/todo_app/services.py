"""Service layer for business logic and data operations.

This module provides pure functions for CRUD operations on tasks.
All functions are stateless and accept/return data explicitly.
"""


from todo_app.models import Task, TaskList


def validate_title(title: str) -> bool:
    """Validate that a task title is non-empty after stripping whitespace.

    Args:
        title: Task title to validate

    Returns:
        True if title is valid (non-empty after strip), False otherwise
    """
    return bool(title.strip())


def add_task(task_list: TaskList, title: str, description: str = "") -> Task | None:
    """Add a new task to the task list.

    Args:
        task_list: TaskList instance to add task to
        title: Task title (required, non-empty after strip)
        description: Task description (optional, defaults to empty string)

    Returns:
        Created Task if successful, None if title invalid
    """
    if not validate_title(title):
        return None

    task = Task(
        id=task_list.next_id,
        title=title.strip(),
        description=description.strip(),
        completed=False,
    )
    task_list.tasks.append(task)
    task_list.next_id += 1
    return task


def get_all_tasks(task_list: TaskList) -> list[Task]:
    """Get all tasks from the task list.

    Args:
        task_list: TaskList instance to retrieve tasks from

    Returns:
        Shallow copy of the tasks list (prevents external mutation)
    """
    return task_list.tasks.copy()


def find_task_by_id(task_list: TaskList, task_id: int) -> Task | None:
    """Find a task by its ID.

    Args:
        task_list: TaskList instance to search
        task_id: ID of the task to find

    Returns:
        Task if found, None otherwise
    """
    for task in task_list.tasks:
        if task.id == task_id:
            return task
    return None


def toggle_complete(task_list: TaskList, task_id: int) -> Task | None:
    """Toggle the completion status of a task.

    Args:
        task_list: TaskList instance containing the task
        task_id: ID of the task to toggle

    Returns:
        Updated Task if found, None if task ID doesn't exist
    """
    task = find_task_by_id(task_list, task_id)
    if task is None:
        return None

    task.completed = not task.completed
    return task


def update_task(
    task_list: TaskList,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
) -> Task | None:
    """Update a task's title and/or description.

    Args:
        task_list: TaskList instance containing the task
        task_id: ID of the task to update
        title: New title (None to keep current, empty string rejected)
        description: New description (None to keep current, empty string allowed)

    Returns:
        Updated Task if successful, None if task not found or title invalid
    """
    task = find_task_by_id(task_list, task_id)
    if task is None:
        return None

    # Validate title if provided
    if title is not None:
        if not validate_title(title):
            return None
        task.title = title.strip()

    # Update description if provided
    if description is not None:
        task.description = description.strip()

    return task


def delete_task(task_list: TaskList, task_id: int) -> bool:
    """Delete a task from the task list.

    Args:
        task_list: TaskList instance to delete from
        task_id: ID of the task to delete

    Returns:
        True if task was deleted, False if task ID not found
    """
    task = find_task_by_id(task_list, task_id)
    if task is None:
        return False

    task_list.tasks.remove(task)
    return True
