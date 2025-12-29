"""Pytest configuration and fixtures for tests."""

import pytest
from todo_app.models import TaskList
from todo_app import services


@pytest.fixture
def empty_task_list() -> TaskList:
    """Provide an empty TaskList for tests.

    Returns:
        Empty TaskList with next_id=1
    """
    return TaskList()


@pytest.fixture
def task_list_with_data() -> TaskList:
    """Provide a TaskList with 2 pre-populated tasks.

    Returns:
        TaskList containing 2 tasks (IDs 1 and 2)
    """
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "Description 1")
    services.add_task(task_list, "Task 2", "Description 2")
    return task_list
