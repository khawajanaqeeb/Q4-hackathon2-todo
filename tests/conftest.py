"""Pytest configuration and fixtures for Enhanced Phase I tests."""

import pytest
from src.todo_app.models import Priority, Task
from src.todo_app.services import TodoService


@pytest.fixture
def service() -> TodoService:
    """Provide an empty TodoService for tests.

    Returns:
        Empty TodoService with next_id=1 and empty task list
    """
    return TodoService()


@pytest.fixture
def service_with_tasks() -> TodoService:
    """Provide a TodoService with pre-populated tasks.

    Returns:
        TodoService containing 3 tasks with various priorities and tags:
        - ID 1: "Buy groceries" (HIGH, tags: ["shopping", "urgent"])
        - ID 2: "Write report" (MEDIUM, tags: ["work"])
        - ID 3: "Read book" (LOW, tags: ["personal"])
    """
    service = TodoService()
    service.add_task("Buy groceries", "Milk and bread", Priority.HIGH, ["shopping", "urgent"])
    service.add_task("Write report", "Q4 summary", Priority.MEDIUM, ["work"])
    service.add_task("Read book", "Fiction", Priority.LOW, ["personal"])
    return service
