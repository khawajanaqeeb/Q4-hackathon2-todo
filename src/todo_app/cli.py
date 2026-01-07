"""Command-line interface for the Enhanced Phase I - Advanced Console Todo Application.

This module provides the interactive menu system and user-facing operations
for the in-memory todo application with advanced features including priorities,
tags, search, filter, and sort capabilities.

Implements all CLI requirements from specs/phase-1/spec.md including:
- FR-010: Main menu with 9 numbered options
- FR-041: Rich table display with professional formatting
- FR-043: Color-coded priorities and status indicators
- FR-007, FR-021, FR-024: Comprehensive input validation
"""

import sys
from typing import Any

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.todo_app.models import Priority, Task
from src.todo_app.services import TodoService

# Try to import rich for professional table formatting
try:
    from rich.console import Console
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ============================================================================
# HELPER FUNCTIONS - Input Validation
# ============================================================================


def get_menu_choice() -> int:
    """Get and validate user menu choice.

    Continuously prompts until user enters a valid menu choice (1-9).

    Returns:
        Valid menu choice as integer (1-9)

    Handles:
        - Non-numeric input
        - Out-of-range numbers
        - Empty input
        - Whitespace
    """
    while True:
        try:
            choice_str = input("\nEnter your choice (1-9): ").strip()
            if not choice_str:
                print("❌ Error: Please enter a number between 1-9")
                continue

            choice = int(choice_str)
            if 1 <= choice <= 9:
                return choice
            else:
                print("❌ Error: Please enter a number between 1-9")
        except ValueError:
            print("❌ Error: Invalid input. Please enter a number between 1-9")


def get_task_id() -> int:
    """Get and validate task ID from user.

    Continuously prompts until user enters a valid positive integer.

    Returns:
        Task ID as positive integer

    Handles:
        - Non-numeric input
        - Negative numbers
        - Zero
        - Whitespace
    """
    while True:
        try:
            id_str = input("Enter task ID: ").strip()
            task_id = int(id_str)
            if task_id > 0:
                return task_id
            else:
                print("❌ Error: Task ID must be a positive number")
        except ValueError:
            print("❌ Error: Invalid input. Please enter a valid task ID number")


def get_non_empty_string(prompt: str) -> str:
    """Get non-empty string input from user.

    Continuously prompts until user enters a non-empty string.

    Args:
        prompt: Input prompt to display to user

    Returns:
        Non-empty trimmed string
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("❌ Error: This field cannot be empty")


def get_optional_string(prompt: str) -> str:
    """Get optional string input from user.

    Args:
        prompt: Input prompt to display to user

    Returns:
        Trimmed string (can be empty)
    """
    return input(prompt).strip()


def get_priority_input() -> Priority:
    """Get and validate priority level from user.

    Displays numbered priority options and validates input.
    Defaults to MEDIUM if user presses Enter.

    Returns:
        Priority enum value (HIGH, MEDIUM, or LOW)

    Handles:
        - Non-numeric input
        - Out-of-range numbers
        - Empty input (defaults to MEDIUM)
    """
    print("\nPriority levels:")
    print("  1. HIGH")
    print("  2. MEDIUM (default)")
    print("  3. LOW")

    while True:
        choice_str = input("Enter priority (1-3, or press Enter for default): ").strip()

        # Default to MEDIUM if empty
        if not choice_str:
            return Priority.MEDIUM

        try:
            choice = int(choice_str)
            if choice == 1:
                return Priority.HIGH
            elif choice == 2:
                return Priority.MEDIUM
            elif choice == 3:
                return Priority.LOW
            else:
                print("❌ Error: Please enter 1, 2, or 3 (or press Enter for default)")
        except ValueError:
            print("❌ Error: Invalid input. Please enter 1, 2, or 3")


def get_tags_input() -> list[str]:
    """Get and parse comma-separated tags from user.

    Parses comma-separated tag input, strips whitespace, and removes empty tags.

    Returns:
        List of non-empty trimmed tag strings (may be empty list)

    Example:
        >>> # User enters: "work, urgent, meeting"
        >>> get_tags_input()
        ['work', 'urgent', 'meeting']
    """
    tags_str = input("Enter tags (comma-separated, or press Enter to skip): ").strip()

    if not tags_str:
        return []

    # Split by comma, strip whitespace, filter out empty strings
    tags = [tag.strip() for tag in tags_str.split(",")]
    return [tag for tag in tags if tag]


# ============================================================================
# HELPER FUNCTIONS - Display
# ============================================================================


def show_success(message: str) -> None:
    """Display success message with visual indicator.

    Args:
        message: Success message to display
    """
    print(f"\n✅ {message}\n")


def show_error(message: str) -> None:
    """Display error message with visual indicator.

    Args:
        message: Error message to display
    """
    print(f"\n❌ {message}\n")


def show_info(message: str) -> None:
    """Display informational message with visual indicator.

    Args:
        message: Information message to display
    """
    print(f"\n📋 {message}\n")


def get_priority_color(priority: Priority) -> str:
    """Get ANSI color code for priority level (for fallback display).

    Args:
        priority: Priority enum value

    Returns:
        ANSI color code string
    """
    if priority == Priority.HIGH:
        return "\033[91m"  # Red
    elif priority == Priority.MEDIUM:
        return "\033[93m"  # Yellow
    else:  # LOW
        return "\033[92m"  # Green


def display_tasks_rich(tasks: list[Task]) -> None:
    """Display tasks using rich library with professional formatting.

    Implements FR-041, FR-043: Rich table display with color-coded priorities.

    Args:
        tasks: List of Task objects to display
    """
    if not tasks:
        print("\n📋 No tasks found. Add your first task to get started!\n")
        return

    console = Console()

    # Create rich table with title showing total count
    table = Table(title=f"[bold cyan]Total Tasks: {len(tasks)}[/bold cyan]", show_header=True)

    # Add columns
    table.add_column("ID", style="cyan", justify="right", width=5)
    table.add_column("Title", style="white", width=25)
    table.add_column("Description", style="dim", width=25)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Tags", style="magenta", width=20)
    table.add_column("Status", justify="center", width=12)

    # Add rows
    for task in tasks:
        # Format title with truncation
        title = task.title[:23] + ".." if len(task.title) > 25 else task.title

        # Format description with truncation
        desc = task.description[:23] + ".." if len(task.description) > 25 else task.description

        # Color-coded priority (FR-043)
        if task.priority == Priority.HIGH:
            priority_str = "[bold red]HIGH[/bold red]"
        elif task.priority == Priority.MEDIUM:
            priority_str = "[bold yellow]MEDIUM[/bold yellow]"
        else:  # LOW
            priority_str = "[bold green]LOW[/bold green]"

        # Format tags
        tags_str = ", ".join(task.tags) if task.tags else "-"
        if len(tags_str) > 20:
            tags_str = tags_str[:18] + ".."

        # Status with visual indicator
        status = "[bold green]✓ Complete[/bold green]" if task.completed else "[dim]○ Pending[/dim]"

        table.add_row(str(task.id), title, desc, priority_str, tags_str, status)

    # Display table
    console.print("\n", table)

    # Summary statistics
    complete_count = sum(1 for t in tasks if t.completed)
    pending_count = len(tasks) - complete_count
    print(f"Complete: {complete_count} | Pending: {pending_count}\n")


def display_tasks_fallback(tasks: list[Task]) -> None:
    """Display tasks using basic formatting (fallback when rich not available).

    Implements FR-042: Graceful fallback if rich library not installed.

    Args:
        tasks: List of Task objects to display
    """
    if not tasks:
        print("\n📋 No tasks found. Add your first task to get started!\n")
        return

    # ANSI color reset
    RESET = "\033[0m"

    print("\n" + "=" * 120)
    print(f"{'ID':<5} {'Title':<25} {'Description':<25} {'Priority':<12} {'Tags':<20} {'Status':<15}")
    print("=" * 120)

    for task in tasks:
        # Truncate long fields
        title = task.title[:23] + ".." if len(task.title) > 25 else task.title
        desc = task.description[:23] + ".." if len(task.description) > 25 else task.description

        # Color-coded priority
        priority_color = get_priority_color(task.priority)
        priority_str = f"{priority_color}{task.priority.value.upper()}{RESET}"

        # Format tags
        tags_str = ", ".join(task.tags) if task.tags else "-"
        if len(tags_str) > 20:
            tags_str = tags_str[:18] + ".."

        # Status
        status = "✓ Complete" if task.completed else "○ Pending"

        print(f"{task.id:<5} {title:<25} {desc:<25} {priority_str:<20} {tags_str:<20} {status:<15}")

    print("=" * 120)

    # Summary statistics
    complete_count = sum(1 for t in tasks if t.completed)
    pending_count = len(tasks) - complete_count
    print(f"\nTotal: {len(tasks)} | Complete: {complete_count} | Pending: {pending_count}\n")


def display_tasks(tasks: list[Task]) -> None:
    """Display all tasks in formatted table.

    Automatically selects rich or fallback display based on availability.
    Implements FR-003, FR-041, FR-042, FR-043.

    Args:
        tasks: List of Task objects to display
    """
    if RICH_AVAILABLE:
        display_tasks_rich(tasks)
    else:
        display_tasks_fallback(tasks)


# ============================================================================
# UI OPERATION FUNCTIONS
# ============================================================================


def add_task_ui(service: TodoService) -> None:
    """Interactive UI for adding a new task.

    Validates: User Story - Add Tasks with Priority and Tags
    Implements: FR-001, FR-002, FR-007, FR-021

    Args:
        service: TodoService instance to use for adding task
    """
    print("\n" + "=" * 50)
    print("           ADD NEW TASK")
    print("=" * 50)

    # Get title (required)
    title = get_non_empty_string("Enter task title: ")

    # Get description (optional)
    description = get_optional_string("Enter task description (optional, press Enter to skip): ")

    # Get priority
    priority = get_priority_input()

    # Get tags
    tags = get_tags_input()

    try:
        task = service.add_task(title, description, priority, tags)
        show_success(f"Task added successfully! (ID: {task.id})")

        # Display created task details
        print(f"Title: {task.title}")
        print(f"Description: {task.description if task.description else '(No description)'}")
        print(f"Priority: {task.priority.value.upper()}")
        print(f"Tags: {', '.join(task.tags) if task.tags else '(No tags)'}")
        print(f"Status: ○ Pending")

    except ValueError as e:
        show_error(str(e))


def view_tasks_ui(service: TodoService) -> None:
    """Interactive UI for viewing all tasks.

    Validates: User Story - View All Tasks
    Implements: FR-003, FR-041, FR-043

    Args:
        service: TodoService instance to use for retrieving tasks
    """
    tasks = service.get_all_tasks()
    display_tasks(tasks)


def update_task_ui(service: TodoService) -> None:
    """Interactive UI for updating a task.

    Validates: User Story - Update Task Details
    Implements: FR-005, FR-007, FR-008, FR-021

    Args:
        service: TodoService instance to use for updating task
    """
    print("\n" + "=" * 50)
    print("           UPDATE TASK")
    print("=" * 50)

    # Show current tasks
    tasks = service.get_all_tasks()
    if not tasks:
        show_info("No tasks available to update.")
        return

    display_tasks(tasks)

    # Get task ID
    task_id = get_task_id()

    # Check if task exists
    task = service.get_task_by_id(task_id)
    if not task:
        show_error(f"Task ID {task_id} not found.")
        return

    # Show current values
    print(f"\nCurrent title: {task.title}")
    print(f"Current description: {task.description if task.description else '(No description)'}")
    print(f"Current priority: {task.priority.value.upper()}")
    print(f"Current tags: {', '.join(task.tags) if task.tags else '(No tags)'}")

    # Get new values
    print("\n(Press Enter to keep current value)")
    new_title = get_optional_string("Enter new title: ")
    new_description = get_optional_string("Enter new description: ")

    # Priority update
    update_priority_str = input("Update priority? (y/n): ").strip().lower()
    new_priority = None
    if update_priority_str in ["y", "yes"]:
        new_priority = get_priority_input()

    # Tags update
    update_tags_str = input("Update tags? (y/n): ").strip().lower()
    new_tags = None
    if update_tags_str in ["y", "yes"]:
        new_tags = get_tags_input()

    # Use current values if user skipped input
    final_title = new_title if new_title else None
    final_description = new_description if new_description else None

    try:
        success = service.update_task(
            task_id,
            title=final_title,
            description=final_description,
            priority=new_priority,
            tags=new_tags,
        )
        if success:
            show_success("Task updated successfully!")
        else:
            show_error(f"Failed to update task ID {task_id}.")
    except ValueError as e:
        show_error(str(e))


def delete_task_ui(service: TodoService) -> None:
    """Interactive UI for deleting a task.

    Validates: User Story - Delete Unwanted Tasks
    Implements: FR-004, FR-008

    Args:
        service: TodoService instance to use for deleting task
    """
    print("\n" + "=" * 50)
    print("           DELETE TASK")
    print("=" * 50)

    tasks = service.get_all_tasks()
    if not tasks:
        show_info("No tasks available to delete.")
        return

    display_tasks(tasks)

    task_id = get_task_id()

    # Confirmation prompt
    confirm = input(f"Are you sure you want to delete task ID {task_id}? (yes/no): ").strip().lower()
    if confirm not in ["yes", "y"]:
        show_info("Delete operation cancelled.")
        return

    success = service.delete_task(task_id)
    if success:
        show_success(f"Task ID {task_id} deleted successfully!")
    else:
        show_error(f"Task ID {task_id} not found.")


def mark_complete_ui(service: TodoService) -> None:
    """Interactive UI for marking task complete/pending.

    Validates: User Story - Mark Tasks Complete
    Implements: FR-006, FR-008

    Args:
        service: TodoService instance to use for toggling completion
    """
    print("\n" + "=" * 50)
    print("           MARK TASK COMPLETE/PENDING")
    print("=" * 50)

    tasks = service.get_all_tasks()
    if not tasks:
        show_info("No tasks available to update.")
        return

    display_tasks(tasks)

    task_id = get_task_id()

    success = service.mark_task_complete(task_id)
    if success:
        task = service.get_task_by_id(task_id)
        if task:
            status = "complete" if task.completed else "pending"
            show_success(f"Task ID {task_id} marked as {status}!")
    else:
        show_error(f"Task ID {task_id} not found.")


def search_tasks_ui(service: TodoService) -> None:
    """Interactive UI for searching tasks by keyword.

    Validates: User Story - Search Tasks
    Implements: FR-031, FR-032

    Args:
        service: TodoService instance to use for searching
    """
    print("\n" + "=" * 50)
    print("           SEARCH TASKS")
    print("=" * 50)

    keyword = get_non_empty_string("Enter search keyword (searches title and description): ")

    results = service.search_tasks(keyword)

    if results:
        print(f"\nFound {len(results)} task(s) matching '{keyword}':")
        display_tasks(results)
    else:
        show_info(f"No tasks found matching '{keyword}'.")


def filter_tasks_ui(service: TodoService) -> None:
    """Interactive UI for filtering tasks by status/priority/tag.

    Validates: User Story - Filter Tasks
    Implements: FR-033, FR-034, FR-035

    Args:
        service: TodoService instance to use for filtering
    """
    print("\n" + "=" * 50)
    print("           FILTER TASKS")
    print("=" * 50)
    print("Filter by:")
    print("  1. Status (Complete/Pending)")
    print("  2. Priority (High/Medium/Low)")
    print("  3. Tag")

    while True:
        try:
            choice_str = input("\nEnter filter type (1-3): ").strip()
            choice = int(choice_str)
            if 1 <= choice <= 3:
                break
            else:
                print("❌ Error: Please enter 1, 2, or 3")
        except ValueError:
            print("❌ Error: Invalid input. Please enter 1, 2, or 3")

    results: list[Task] = []

    if choice == 1:
        # Filter by status
        status_str = input("Show (c)omplete or (p)ending tasks? (c/p): ").strip().lower()
        if status_str in ["c", "complete"]:
            results = service.filter_by_status(completed=True)
            filter_desc = "completed"
        elif status_str in ["p", "pending"]:
            results = service.filter_by_status(completed=False)
            filter_desc = "pending"
        else:
            show_error("Invalid status choice. Please enter 'c' or 'p'.")
            return

    elif choice == 2:
        # Filter by priority
        priority = get_priority_input()
        results = service.filter_by_priority(priority)
        filter_desc = f"{priority.value.upper()} priority"

    elif choice == 3:
        # Filter by tag
        tag = get_non_empty_string("Enter tag to filter by: ")
        results = service.filter_by_tag(tag)
        filter_desc = f"tag '{tag}'"

    if results:
        print(f"\nFound {len(results)} {filter_desc} task(s):")
        display_tasks(results)
    else:
        show_info(f"No {filter_desc} tasks found.")


def sort_tasks_ui(service: TodoService) -> None:
    """Interactive UI for sorting tasks by priority/title/ID.

    Validates: User Story - Sort Tasks
    Implements: FR-036, FR-037, FR-038

    Args:
        service: TodoService instance to use for sorting
    """
    print("\n" + "=" * 50)
    print("           SORT TASKS")
    print("=" * 50)
    print("Sort by:")
    print("  1. Priority (HIGH → MEDIUM → LOW)")
    print("  2. Title (A-Z)")
    print("  3. ID (Creation order)")

    while True:
        try:
            choice_str = input("\nEnter sort option (1-3): ").strip()
            choice = int(choice_str)
            if 1 <= choice <= 3:
                break
            else:
                print("❌ Error: Please enter 1, 2, or 3")
        except ValueError:
            print("❌ Error: Invalid input. Please enter 1, 2, or 3")

    if choice == 1:
        sorted_tasks = service.sort_by_priority()
        print("\nTasks sorted by Priority (HIGH → MEDIUM → LOW):")
    elif choice == 2:
        sorted_tasks = service.sort_by_title()
        print("\nTasks sorted by Title (A-Z):")
    elif choice == 3:
        sorted_tasks = service.sort_by_id()
        print("\nTasks sorted by ID (Creation order):")

    display_tasks(sorted_tasks)


# ============================================================================
# MAIN LOOP
# ============================================================================


def main() -> None:
    """Main application loop.

    Implements: FR-010, FR-044, FR-045
    Success Criteria: SC-010 (startup under 2 seconds)
    """
    # Initialize service
    service = TodoService()

    # Welcome message
    print("\n" + "=" * 70)
    print("  WELCOME TO YOUR TODO APP - ENHANCED PHASE I")
    print("  Advanced Console Todo Manager with Priorities, Tags & Search")
    print("=" * 70)

    if not RICH_AVAILABLE:
        print("\n⚠️  Note: 'rich' library not installed - using basic table formatting.")
        print("   Install with: pip install rich (for enhanced display)")

    show_info("Note: All tasks are stored in memory and will be lost when you exit.")

    while True:
        # Display menu
        print("\n" + "=" * 70)
        print("                          MAIN MENU")
        print("=" * 70)
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Task Complete/Pending")
        print("6. Search Tasks")
        print("7. Filter Tasks")
        print("8. Sort Tasks")
        print("9. Exit")
        print("=" * 70)

        choice = get_menu_choice()

        if choice == 1:
            add_task_ui(service)
        elif choice == 2:
            view_tasks_ui(service)
        elif choice == 3:
            update_task_ui(service)
        elif choice == 4:
            delete_task_ui(service)
        elif choice == 5:
            mark_complete_ui(service)
        elif choice == 6:
            search_tasks_ui(service)
        elif choice == 7:
            filter_tasks_ui(service)
        elif choice == 8:
            sort_tasks_ui(service)
        elif choice == 9:
            # Exit confirmation
            confirm = input("\nAre you sure you want to exit? All tasks will be lost. (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]:
                print("\n" + "=" * 70)
                print("  Thank you for using Todo App!")
                print("  All tasks have been cleared from memory.")
                print("=" * 70 + "\n")
                break
            else:
                show_info("Continuing session...")


if __name__ == "__main__":
    main()
