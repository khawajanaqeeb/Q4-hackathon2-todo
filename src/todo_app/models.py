"""Data models for the Enhanced Phase I - Advanced Console Todo Application.

This module contains the Task dataclass and Priority enum that form the foundation
of the todo application's data layer.
"""

from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    """Task priority levels with sorting support.

    Attributes:
        HIGH: High priority tasks (urgent, important)
        MEDIUM: Medium priority tasks (default)
        LOW: Low priority tasks (can wait)
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def __lt__(self, other: "Priority") -> bool:
        """Enable priority comparison for sorting.

        Sorting order: HIGH < MEDIUM < LOW (high priority tasks come first)

        Args:
            other: Another Priority enum value to compare with

        Returns:
            bool: True if self should come before other in sorted order

        Example:
            >>> Priority.HIGH < Priority.MEDIUM
            True
            >>> Priority.LOW < Priority.HIGH
            False
        """
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return order[self] < order[other]


@dataclass
class Task:
    """Represents a single todo item with enhanced features.

    Attributes:
        id: Unique auto-generated identifier (sequential)
        title: Required non-empty task description
        description: Optional additional details about the task
        completed: Completion status (False = pending, True = complete)
        priority: Task priority level (defaults to MEDIUM)
        tags: List of categorization tags (defaults to empty list)
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    tags: list[str] = field(default_factory=list)

    def matches_keyword(self, keyword: str) -> bool:
        """Check if task matches search keyword in title or description.

        Performs case-insensitive matching against both title and description fields.

        Args:
            keyword: Search term to match against

        Returns:
            bool: True if keyword found in title or description (case-insensitive)

        Example:
            >>> task = Task(id=1, title="Buy groceries", description="Milk and bread")
            >>> task.matches_keyword("milk")
            True
            >>> task.matches_keyword("urgent")
            False
        """
        keyword_lower = keyword.lower()
        return (
            keyword_lower in self.title.lower() or
            keyword_lower in self.description.lower()
        )

    def has_tag(self, tag: str) -> bool:
        """Check if task has specific tag (case-insensitive).

        Args:
            tag: Tag to check for

        Returns:
            bool: True if task has the tag (case-insensitive match)

        Example:
            >>> task = Task(id=1, title="Meeting", tags=["Work", "Urgent"])
            >>> task.has_tag("work")
            True
            >>> task.has_tag("URGENT")
            True
            >>> task.has_tag("personal")
            False
        """
        return tag.lower() in [t.lower() for t in self.tags]
