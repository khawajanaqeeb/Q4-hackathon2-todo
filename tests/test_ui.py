"""Tests for UI layer functions."""

from io import StringIO
from todo_app.models import Task
from todo_app import ui


def test_display_tasks_empty(capsys) -> None:
    """Test handles empty list message."""
    ui.display_tasks([])

    captured = capsys.readouterr()
    assert "No tasks found" in captured.out


def test_display_tasks_multiple(capsys) -> None:
    """Test formats table correctly."""
    tasks = [
        Task(id=1, title="Buy groceries", description="Milk and bread", completed=False),
        Task(id=2, title="Call dentist", description="", completed=True),
    ]

    ui.display_tasks(tasks)

    captured = capsys.readouterr()
    assert "ID" in captured.out
    assert "Title" in captured.out
    assert "Description" in captured.out
    assert "Status" in captured.out
    assert "Buy groceries" in captured.out
    assert "Call dentist" in captured.out
    assert "○ Pending" in captured.out
    assert "✓ Complete" in captured.out


def test_display_menu(capsys) -> None:
    """Test displays 6 menu options."""
    ui.display_menu()

    captured = capsys.readouterr()
    assert "1. Add Task" in captured.out or "Add Task" in captured.out
    assert "2. View Tasks" in captured.out or "View Tasks" in captured.out
    assert "3. Update Task" in captured.out or "Update Task" in captured.out
    assert "4. Delete Task" in captured.out or "Delete Task" in captured.out
    assert "5. Mark Complete" in captured.out or "Mark Complete" in captured.out
    assert "6. Exit" in captured.out or "Exit" in captured.out


def test_display_message_success(capsys) -> None:
    """Test displays success message."""
    ui.display_message("Task added successfully ✓")

    captured = capsys.readouterr()
    assert "Task added successfully" in captured.out


def test_display_message_error(capsys) -> None:
    """Test displays error message."""
    ui.display_message("Task ID 99 not found", is_error=True)

    captured = capsys.readouterr()
    assert "Task ID 99 not found" in captured.out


def test_display_exit_warning(capsys) -> None:
    """Test displays data loss warning."""
    ui.display_exit_warning()

    captured = capsys.readouterr()
    assert "tasks will be lost" in captured.out.lower() or "data is not persisted" in captured.out.lower()


def test_get_menu_choice_valid(monkeypatch) -> None:
    """Test get_menu_choice with valid input."""
    inputs = iter(["3"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = ui.get_menu_choice()

    assert result == 3


def test_get_menu_choice_invalid_then_valid(monkeypatch, capsys) -> None:
    """Test get_menu_choice with invalid input, then valid."""
    inputs = iter(["0", "7", "abc", "5"])  # 0, 7, abc are invalid; 5 is valid
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = ui.get_menu_choice()

    assert result == 5
    captured = capsys.readouterr()
    # Should have shown error messages for invalid inputs
    assert "Invalid" in captured.out or "invalid" in captured.out


def test_prompt_task_details(monkeypatch) -> None:
    """Test prompting for task details."""
    inputs = iter(["Test Title", "Test Description"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    title, description = ui.prompt_task_details()

    assert title == "Test Title"
    assert description == "Test Description"


def test_prompt_task_details_no_description(monkeypatch) -> None:
    """Test prompting with empty description."""
    inputs = iter(["Test Title", ""])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    title, description = ui.prompt_task_details()

    assert title == "Test Title"
    assert description == ""


def test_prompt_task_id_valid(monkeypatch) -> None:
    """Test prompt_task_id with valid input."""
    inputs = iter(["5"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = ui.prompt_task_id()

    assert result == 5


def test_prompt_task_id_invalid_then_valid(monkeypatch, capsys) -> None:
    """Test prompt_task_id with invalid input, then valid."""
    inputs = iter(["0", "-1", "abc", "10"])  # 0, -1, abc are invalid; 10 is valid
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    result = ui.prompt_task_id()

    assert result == 10
    captured = capsys.readouterr()
    # Should have shown error messages for invalid inputs
    assert "Invalid" in captured.out or "invalid" in captured.out
