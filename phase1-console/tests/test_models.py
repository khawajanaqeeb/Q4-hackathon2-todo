"""Tests for data models (Task and TaskList)."""

from todo_app.models import Task, TaskList


def test_task_creation() -> None:
    """Test creating a Task with all fields."""
    task = Task(id=1, title="Buy groceries", description="Milk and bread", completed=False)

    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.description == "Milk and bread"
    assert task.completed is False


def test_task_creation_with_default_completed() -> None:
    """Test that completed defaults to False."""
    task = Task(id=2, title="Call dentist", description="")

    assert task.completed is False


def test_task_list_initialization() -> None:
    """Test TaskList initializes with empty list and next_id of 1."""
    task_list = TaskList()

    assert task_list.tasks == []
    assert task_list.next_id == 1


def test_task_list_can_store_tasks() -> None:
    """Test that tasks can be added to TaskList."""
    task_list = TaskList()
    task1 = Task(id=1, title="Task 1", description="Desc 1", completed=False)
    task2 = Task(id=2, title="Task 2", description="Desc 2", completed=True)

    task_list.tasks.append(task1)
    task_list.tasks.append(task2)

    assert len(task_list.tasks) == 2
    assert task_list.tasks[0] == task1
    assert task_list.tasks[1] == task2
