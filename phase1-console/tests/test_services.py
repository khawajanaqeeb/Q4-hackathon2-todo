"""Tests for service layer functions."""

from todo_app.models import Task, TaskList
from todo_app import services


# US1 Tests - Add Task

def test_add_task_success() -> None:
    """Test adding a task with valid title creates task with ID 1."""
    task_list = TaskList()

    result = services.add_task(task_list, "Buy groceries", "Milk and bread")

    assert result is not None
    assert result.id == 1
    assert result.title == "Buy groceries"
    assert result.description == "Milk and bread"
    assert result.completed is False
    assert len(task_list.tasks) == 1
    assert task_list.next_id == 2


def test_add_task_empty_title() -> None:
    """Test that empty title returns None."""
    task_list = TaskList()

    result = services.add_task(task_list, "", "Some description")

    assert result is None
    assert len(task_list.tasks) == 0
    assert task_list.next_id == 1


def test_add_task_increments_id() -> None:
    """Test that multiple adds increment IDs (1, 2, 3)."""
    task_list = TaskList()

    task1 = services.add_task(task_list, "Task 1", "")
    task2 = services.add_task(task_list, "Task 2", "")
    task3 = services.add_task(task_list, "Task 3", "")

    assert task1 is not None and task1.id == 1
    assert task2 is not None and task2.id == 2
    assert task3 is not None and task3.id == 3
    assert task_list.next_id == 4


def test_get_all_tasks_empty() -> None:
    """Test that empty list returns []."""
    task_list = TaskList()

    result = services.get_all_tasks(task_list)

    assert result == []


def test_get_all_tasks_multiple() -> None:
    """Test that get_all_tasks returns all tasks."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "Desc 1")
    services.add_task(task_list, "Task 2", "Desc 2")

    result = services.get_all_tasks(task_list)

    assert len(result) == 2
    assert result[0].title == "Task 1"
    assert result[1].title == "Task 2"


# US2 Tests - Toggle Complete

def test_toggle_complete_pending_to_complete() -> None:
    """Test toggles False → True."""
    task_list = TaskList()
    task = services.add_task(task_list, "Task 1", "")
    assert task is not None and task.completed is False

    result = services.toggle_complete(task_list, 1)

    assert result is not None
    assert result.id == 1
    assert result.completed is True


def test_toggle_complete_complete_to_pending() -> None:
    """Test toggles True → False."""
    task_list = TaskList()
    task = services.add_task(task_list, "Task 1", "")
    assert task is not None
    services.toggle_complete(task_list, 1)  # Make it complete

    result = services.toggle_complete(task_list, 1)  # Toggle back

    assert result is not None
    assert result.completed is False


def test_toggle_complete_not_found() -> None:
    """Test non-existent ID returns None."""
    task_list = TaskList()

    result = services.toggle_complete(task_list, 999)

    assert result is None


def test_find_task_by_id_found() -> None:
    """Test existing ID returns Task."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "")
    services.add_task(task_list, "Task 2", "")

    result = services.find_task_by_id(task_list, 2)

    assert result is not None
    assert result.id == 2
    assert result.title == "Task 2"


def test_find_task_by_id_not_found() -> None:
    """Test non-existent ID returns None."""
    task_list = TaskList()

    result = services.find_task_by_id(task_list, 99)

    assert result is None


# US3 Tests - Update Task

def test_update_task_both_fields() -> None:
    """Test updates title and description."""
    task_list = TaskList()
    services.add_task(task_list, "Old Title", "Old Desc")

    result = services.update_task(task_list, 1, "New Title", "New Desc")

    assert result is not None
    assert result.id == 1
    assert result.title == "New Title"
    assert result.description == "New Desc"


def test_update_task_title_only() -> None:
    """Test updates only title, description unchanged."""
    task_list = TaskList()
    services.add_task(task_list, "Old Title", "Old Desc")

    result = services.update_task(task_list, 1, title="New Title")

    assert result is not None
    assert result.title == "New Title"
    assert result.description == "Old Desc"


def test_update_task_description_only() -> None:
    """Test updates only description, title unchanged."""
    task_list = TaskList()
    services.add_task(task_list, "Old Title", "Old Desc")

    result = services.update_task(task_list, 1, description="New Desc")

    assert result is not None
    assert result.title == "Old Title"
    assert result.description == "New Desc"


def test_update_task_empty_title() -> None:
    """Test empty title returns None, no changes."""
    task_list = TaskList()
    services.add_task(task_list, "Old Title", "Old Desc")

    result = services.update_task(task_list, 1, title="")

    assert result is None
    # Verify original task unchanged
    task = services.find_task_by_id(task_list, 1)
    assert task is not None
    assert task.title == "Old Title"


def test_update_task_not_found() -> None:
    """Test non-existent ID returns None."""
    task_list = TaskList()

    result = services.update_task(task_list, 99, title="New Title")

    assert result is None


# US4 Tests - Delete Task

def test_delete_task_success() -> None:
    """Test existing ID deletes task, returns True."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "")
    services.add_task(task_list, "Task 2", "")
    services.add_task(task_list, "Task 3", "")

    result = services.delete_task(task_list, 2)

    assert result is True
    assert len(task_list.tasks) == 2
    assert services.find_task_by_id(task_list, 2) is None


def test_delete_task_not_found() -> None:
    """Test non-existent ID returns False."""
    task_list = TaskList()

    result = services.delete_task(task_list, 99)

    assert result is False


def test_delete_task_preserves_ids() -> None:
    """Test delete ID 2, IDs 1 and 3 unchanged."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "")
    services.add_task(task_list, "Task 2", "")
    services.add_task(task_list, "Task 3", "")

    services.delete_task(task_list, 2)

    task1 = services.find_task_by_id(task_list, 1)
    task3 = services.find_task_by_id(task_list, 3)
    assert task1 is not None and task1.id == 1
    assert task3 is not None and task3.id == 3
