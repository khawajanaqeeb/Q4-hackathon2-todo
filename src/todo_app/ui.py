"""UI layer for command-line interface.

This module handles all user interaction including menu display,
input prompts, and output formatting.
"""


from todo_app import constants
from todo_app.models import Task


def display_menu() -> None:
    """Display the main menu with numbered options."""
    print("\n===== Todo App - Phase I =====\n")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete/Pending")
    print("6. Exit")


def get_menu_choice() -> int:
    """Get and validate user's menu choice.

    Loops until user enters a valid integer between 1-6.

    Returns:
        Validated menu choice (1-6)
    """
    while True:
        try:
            choice = int(input("\nEnter choice (1-6): "))
            if constants.MENU_MIN <= choice <= constants.MENU_MAX:
                return choice
            print("Invalid choice. Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def prompt_task_details() -> tuple[str, str]:
    """Prompt user for task title and description.

    Returns:
        Tuple of (title, description) where both are strings
    """
    title = input("\nEnter task title: ")
    description = input("Enter task description (optional, press Enter to skip): ")
    return title, description


def prompt_task_id() -> int:
    """Prompt user for a task ID.

    Loops until user enters a valid positive integer.

    Returns:
        Validated task ID (positive integer)
    """
    while True:
        try:
            task_id = int(input("\nEnter task ID: "))
            if task_id > 0:
                return task_id
            print("Invalid ID. Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def display_tasks(tasks: list[Task]) -> None:
    """Display all tasks in a formatted table.

    Args:
        tasks: List of Task objects to display
    """
    if not tasks:
        print("\nNo tasks found")
        return

    print(f"\n{'ID':<4} | {'Title':<30} | {'Description':<30} | {'Status':<15}")
    print("-" * 85)

    for task in tasks:
        status = constants.STATUS_COMPLETE if task.completed else constants.STATUS_PENDING
        # Truncate long text for display
        title_display = (
            task.title[:constants.TRUNCATE_AT] + "..."
            if len(task.title) > constants.MAX_DISPLAY_LENGTH
            else task.title
        )
        desc_display = (
            task.description[:constants.TRUNCATE_AT] + "..."
            if len(task.description) > constants.MAX_DISPLAY_LENGTH
            else task.description
        )

        print(f"{task.id:<4} | {title_display:<30} | {desc_display:<30} | {status:<15}")


def display_message(message: str, is_error: bool = False) -> None:  # noqa: ARG001
    """Display a success or error message to the user.

    Args:
        message: Message text to display
        is_error: Whether this is an error message (currently unused, could add color)
    """
    print(f"\n{message}")


def display_exit_warning() -> None:
    """Display warning about data loss when exiting."""
    print("\n⚠️  All tasks will be lost. Data is not persisted in Phase I.")
    print("Goodbye!")
