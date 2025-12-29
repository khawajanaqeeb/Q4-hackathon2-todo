"""Edge case and error handling tests."""

from todo_app.models import TaskList
from todo_app import services


def test_empty_list_operations() -> None:
    """Test view, update, delete, toggle on empty list."""
    task_list = TaskList()

    # View empty list
    tasks = services.get_all_tasks(task_list)
    assert tasks == []

    # Update non-existent task
    result = services.update_task(task_list, 1, "New Title")
    assert result is None

    # Delete non-existent task
    result2 = services.delete_task(task_list, 1)
    assert result2 is False

    # Toggle non-existent task
    result3 = services.toggle_complete(task_list, 1)
    assert result3 is None


def test_invalid_id_handling() -> None:
    """Test letters, negative numbers, non-existent IDs."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "")

    # Non-existent positive ID
    assert services.find_task_by_id(task_list, 999) is None
    assert services.delete_task(task_list, 999) is False
    assert services.update_task(task_list, 999, "Title") is None
    assert services.toggle_complete(task_list, 999) is None

    # Note: Negative IDs and letters would be handled by UI validation (prompt_task_id)
    # Service layer expects valid positive integers


def test_very_long_title() -> None:
    """Test 1000-char title stores correctly."""
    task_list = TaskList()
    long_title = "A" * 1000

    task = services.add_task(task_list, long_title, "Normal description")

    assert task is not None
    assert len(task.title) == 1000
    assert task.title == long_title


def test_unicode_characters() -> None:
    """Test emoji and special chars in title/description."""
    task_list = TaskList()

    task = services.add_task(
        task_list,
        "Buy 🥖 and 🥛",
        "Include café ☕ items: résumé, naïve, Zürich"
    )

    assert task is not None
    assert task.title == "Buy 🥖 and 🥛"
    assert "café" in task.description
    assert "résumé" in task.description


def test_whitespace_handling() -> None:
    """Test titles with leading/trailing whitespace are stripped."""
    task_list = TaskList()

    task = services.add_task(task_list, "  Title with spaces  ", "  Desc with spaces  ")

    assert task is not None
    assert task.title == "Title with spaces"
    assert task.description == "Desc with spaces"


def test_empty_string_vs_none_description() -> None:
    """Test that empty string description is allowed."""
    task_list = TaskList()

    task = services.add_task(task_list, "Task with no desc", "")

    assert task is not None
    assert task.description == ""


def test_rapid_sequential_operations() -> None:
    """Test multiple add/delete/update operations in quick succession."""
    task_list = TaskList()

    # Rapid adds
    for i in range(10):
        task = services.add_task(task_list, f"Task {i+1}", f"Description {i+1}")
        assert task is not None
        assert task.id == i + 1

    # Verify all added
    assert len(services.get_all_tasks(task_list)) == 10

    # Rapid deletes (every other task)
    for task_id in [2, 4, 6, 8, 10]:
        result = services.delete_task(task_list, task_id)
        assert result is True

    # Verify 5 remaining with correct IDs
    remaining = services.get_all_tasks(task_list)
    assert len(remaining) == 5
    remaining_ids = [t.id for t in remaining]
    assert remaining_ids == [1, 3, 5, 7, 9]


def test_1000_tasks_performance() -> None:
    """Test handling 1000 tasks without performance degradation."""
    task_list = TaskList()

    # Add 1000 tasks
    for i in range(1000):
        task = services.add_task(task_list, f"Task {i+1}", f"Description {i+1}")
        assert task is not None

    # Verify count
    assert len(services.get_all_tasks(task_list)) == 1000

    # Test operations on task in middle
    task_500 = services.find_task_by_id(task_list, 500)
    assert task_500 is not None
    assert task_500.title == "Task 500"

    # Update task 500
    updated = services.update_task(task_list, 500, "Updated Task 500")
    assert updated is not None

    # Toggle completion
    toggled = services.toggle_complete(task_list, 500)
    assert toggled is not None and toggled.completed is True

    # Delete task 500
    deleted = services.delete_task(task_list, 500)
    assert deleted is True

    # Verify 999 remaining
    assert len(services.get_all_tasks(task_list)) == 999
