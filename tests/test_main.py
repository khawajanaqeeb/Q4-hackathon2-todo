"""Tests for main application handlers."""

from unittest.mock import patch
from todo_app.models import TaskList
from todo_app import main, services


def test_handle_add_task_success(monkeypatch, capsys) -> None:
    """Test adding a task successfully."""
    task_list = TaskList()

    # Mock user input
    inputs = iter(["Buy groceries", "Milk and bread"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.handle_add_task(task_list)

    captured = capsys.readouterr()
    assert "Task added successfully" in captured.out
    assert len(task_list.tasks) == 1
    assert task_list.tasks[0].title == "Buy groceries"


def test_handle_add_task_empty_title(monkeypatch, capsys) -> None:
    """Test adding a task with empty title shows error."""
    task_list = TaskList()

    # Mock user input with empty title
    inputs = iter(["", "Some description"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.handle_add_task(task_list)

    captured = capsys.readouterr()
    assert "Title is required" in captured.out
    assert len(task_list.tasks) == 0


def test_handle_view_tasks_empty(capsys) -> None:
    """Test viewing tasks when list is empty."""
    task_list = TaskList()

    main.handle_view_tasks(task_list)

    captured = capsys.readouterr()
    assert "No tasks found" in captured.out


def test_handle_view_tasks_with_data(capsys) -> None:
    """Test viewing tasks with data."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "Description 1")
    services.add_task(task_list, "Task 2", "Description 2")

    main.handle_view_tasks(task_list)

    captured = capsys.readouterr()
    assert "Task 1" in captured.out
    assert "Task 2" in captured.out


def test_handle_update_task_success(monkeypatch, capsys) -> None:
    """Test updating a task successfully."""
    task_list = TaskList()
    services.add_task(task_list, "Old Title", "Old Desc")

    # Mock user input: task_id, new_title, new_desc
    inputs = iter(["1", "New Title", "New Desc"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))

    main.handle_update_task(task_list)

    captured = capsys.readouterr()
    assert "Task updated successfully" in captured.out
    task = services.find_task_by_id(task_list, 1)
    assert task is not None
    assert task.title == "New Title"
    assert task.description == "New Desc"


def test_handle_update_task_not_found(monkeypatch, capsys) -> None:
    """Test updating non-existent task shows error."""
    task_list = TaskList()

    # Mock user input: non-existent task_id
    inputs = iter(["99"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.handle_update_task(task_list)

    captured = capsys.readouterr()
    assert "Task ID 99 not found" in captured.out


def test_handle_update_task_keep_current(monkeypatch, capsys) -> None:
    """Test updating task with Enter to keep current values."""
    task_list = TaskList()
    services.add_task(task_list, "Original Title", "Original Desc")

    # Mock user input: task_id, press Enter (empty) to keep both
    inputs = iter(["1", "", ""])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))

    main.handle_update_task(task_list)

    captured = capsys.readouterr()
    assert "Task updated successfully" in captured.out
    task = services.find_task_by_id(task_list, 1)
    assert task is not None
    assert task.title == "Original Title"  # Unchanged
    assert task.description == "Original Desc"  # Unchanged


def test_handle_update_task_empty_title(monkeypatch, capsys) -> None:
    """Test updating with empty title shows error."""
    task_list = TaskList()
    services.add_task(task_list, "Original Title", "Original Desc")

    # Mock user input: task_id, empty title (spaces), new desc
    inputs = iter(["1", "  ", "New Desc"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))

    main.handle_update_task(task_list)

    captured = capsys.readouterr()
    assert "Title cannot be empty" in captured.out


def test_handle_delete_task_success(monkeypatch, capsys) -> None:
    """Test deleting a task successfully."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "")

    # Mock user input: task_id
    inputs = iter(["1"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.handle_delete_task(task_list)

    captured = capsys.readouterr()
    assert "Task deleted successfully" in captured.out
    assert len(task_list.tasks) == 0


def test_handle_delete_task_not_found(monkeypatch, capsys) -> None:
    """Test deleting non-existent task shows error."""
    task_list = TaskList()

    # Mock user input: non-existent task_id
    inputs = iter(["99"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.handle_delete_task(task_list)

    captured = capsys.readouterr()
    assert "Task ID 99 not found" in captured.out


def test_handle_toggle_complete_success(monkeypatch, capsys) -> None:
    """Test toggling task completion successfully."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "")

    # Mock user input: task_id
    inputs = iter(["1"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.handle_toggle_complete(task_list)

    captured = capsys.readouterr()
    assert "Task marked as complete" in captured.out
    task = services.find_task_by_id(task_list, 1)
    assert task is not None and task.completed is True


def test_handle_toggle_complete_to_pending(monkeypatch, capsys) -> None:
    """Test toggling task from complete to pending."""
    task_list = TaskList()
    services.add_task(task_list, "Task 1", "")
    services.toggle_complete(task_list, 1)  # Make it complete first

    # Mock user input: task_id
    inputs = iter(["1"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.handle_toggle_complete(task_list)

    captured = capsys.readouterr()
    assert "Task marked as pending" in captured.out
    task = services.find_task_by_id(task_list, 1)
    assert task is not None and task.completed is False


def test_handle_toggle_complete_not_found(monkeypatch, capsys) -> None:
    """Test toggling non-existent task shows error."""
    task_list = TaskList()

    # Mock user input: non-existent task_id
    inputs = iter(["99"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.handle_toggle_complete(task_list)

    captured = capsys.readouterr()
    assert "Task ID 99 not found" in captured.out


def test_main_loop_exit(monkeypatch, capsys) -> None:
    """Test main loop exits cleanly when user chooses option 6."""
    # Mock user input: menu choice 6 (exit)
    inputs = iter(["6"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    main.main()

    captured = capsys.readouterr()
    assert "tasks will be lost" in captured.out.lower() or "Goodbye" in captured.out


def test_main_loop_keyboard_interrupt(monkeypatch, capsys) -> None:
    """Test main loop handles KeyboardInterrupt (Ctrl+C)."""
    # Mock user input that raises KeyboardInterrupt
    def mock_input(_):
        raise KeyboardInterrupt()

    monkeypatch.setattr('builtins.input', mock_input)

    main.main()

    captured = capsys.readouterr()
    assert "tasks will be lost" in captured.out.lower() or "Goodbye" in captured.out


def test_main_loop_add_and_view(monkeypatch, capsys) -> None:
    """Test main loop with add task (option 1) and view tasks (option 2), then exit (option 6)."""
    # Mock user input: add task, view tasks, exit
    inputs = iter([
        "1",                    # Choice: Add task
        "Test Task",           # Title
        "Test Description",    # Description
        "2",                   # Choice: View tasks
        "6"                    # Choice: Exit
    ])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))

    main.main()

    captured = capsys.readouterr()
    assert "Task added successfully" in captured.out
    assert "Test Task" in captured.out
