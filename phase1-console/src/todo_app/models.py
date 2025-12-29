"""Data models for the Todo Console App.

This module defines the core data structures:
- Task: Represents a single todo item
- TaskList: Manages the collection of tasks in memory
"""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Unique auto-generated identifier (sequential starting from 1)
        title: Required non-empty task title
        description: Optional additional details about the task
        completed: Completion status (False by default, toggleable)
    """

    id: int
    title: str
    description: str
    completed: bool = False


class TaskList:
    """Manages the in-memory collection of Task objects.

    Attributes:
        tasks: List of Task objects stored in memory
        next_id: Next available ID for new tasks (auto-incrementing)
    """

    def __init__(self) -> None:
        """Initialize an empty TaskList with next_id starting at 1."""
        self.tasks: list[Task] = []
        self.next_id: int = 1
