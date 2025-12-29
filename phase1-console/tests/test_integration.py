"""Integration tests for end-to-end workflows."""

from todo_app.models import TaskList
from todo_app import services


def test_add_and_view_workflow() -> None:
    """Test end-to-end: add tasks and view them."""
    task_list = TaskList()

    # Add 3 tasks
    task1 = services.add_task(task_list, "Buy groceries", "Milk and bread")
    task2 = services.add_task(task_list, "Call dentist", "")
    task3 = services.add_task(task_list, "Write report", "Q4 summary")

    # Verify all added
    assert task1 is not None
    assert task2 is not None
    assert task3 is not None

    # View all tasks
    all_tasks = services.get_all_tasks(task_list)
    assert len(all_tasks) == 3
    assert all_tasks[0].title == "Buy groceries"
    assert all_tasks[1].title == "Call dentist"
    assert all_tasks[2].title == "Write report"


def test_mark_complete_workflow() -> None:
    """Test end-to-end: add tasks, mark some complete, view."""
    task_list = TaskList()

    # Add 3 tasks
    services.add_task(task_list, "Task 1", "")
    services.add_task(task_list, "Task 2", "")
    services.add_task(task_list, "Task 3", "")

    # Mark task 2 complete
    result = services.toggle_complete(task_list, 2)
    assert result is not None and result.completed is True

    # Verify statuses
    all_tasks = services.get_all_tasks(task_list)
    assert all_tasks[0].completed is False  # Task 1
    assert all_tasks[1].completed is True   # Task 2
    assert all_tasks[2].completed is False  # Task 3

    # Toggle task 2 back to pending
    result2 = services.toggle_complete(task_list, 2)
    assert result2 is not None and result2.completed is False


def test_update_workflow() -> None:
    """Test end-to-end: add task, update it, view changes."""
    task_list = TaskList()

    # Add task
    services.add_task(task_list, "Write report", "Q3 summary")

    # Update both fields
    result = services.update_task(task_list, 1, "Write annual report", "Q3 and Q4 summary")
    assert result is not None

    # Verify changes
    task = services.find_task_by_id(task_list, 1)
    assert task is not None
    assert task.title == "Write annual report"
    assert task.description == "Q3 and Q4 summary"
    assert task.id == 1  # ID unchanged


def test_delete_workflow() -> None:
    """Test end-to-end: add 3 tasks, delete 2nd, verify IDs preserved."""
    task_list = TaskList()

    # Add 3 tasks
    services.add_task(task_list, "Task 1", "")
    services.add_task(task_list, "Task 2", "")
    services.add_task(task_list, "Task 3", "")

    # Delete task 2
    success = services.delete_task(task_list, 2)
    assert success is True

    # Verify only 2 tasks remain
    all_tasks = services.get_all_tasks(task_list)
    assert len(all_tasks) == 2

    # Verify IDs 1 and 3 still exist with original IDs
    task1 = services.find_task_by_id(task_list, 1)
    task3 = services.find_task_by_id(task_list, 3)
    assert task1 is not None and task1.id == 1
    assert task3 is not None and task3.id == 3

    # Verify task 2 is gone
    assert services.find_task_by_id(task_list, 2) is None


def test_full_crud_workflow() -> None:
    """Test complete workflow: add, view, update, mark complete, delete."""
    task_list = TaskList()

    # 1. Add tasks
    task1 = services.add_task(task_list, "Buy groceries", "Milk and bread")
    task2 = services.add_task(task_list, "Call dentist", "Appointment")
    assert task1 is not None and task2 is not None

    # 2. View tasks
    assert len(services.get_all_tasks(task_list)) == 2

    # 3. Update task 1
    updated = services.update_task(task_list, 1, "Buy weekly groceries", "Milk, bread, eggs")
    assert updated is not None

    # 4. Mark task 1 complete
    completed = services.toggle_complete(task_list, 1)
    assert completed is not None and completed.completed is True

    # 5. Delete task 2
    deleted = services.delete_task(task_list, 2)
    assert deleted is True

    # 6. Verify final state
    final_tasks = services.get_all_tasks(task_list)
    assert len(final_tasks) == 1
    assert final_tasks[0].id == 1
    assert final_tasks[0].title == "Buy weekly groceries"
    assert final_tasks[0].description == "Milk, bread, eggs"
    assert final_tasks[0].completed is True
