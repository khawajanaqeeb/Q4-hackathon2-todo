"""Main application entry point and orchestration.

This module contains the main loop and handler functions that coordinate
between the UI and service layers.
"""

import sys

from todo_app import constants, services, ui
from todo_app.models import TaskList


def handle_add_task(task_list: TaskList) -> None:
    """Handle adding a new task.

    Args:
        task_list: TaskList instance to add task to
    """
    title, description = ui.prompt_task_details()
    task = services.add_task(task_list, title, description)

    if task:
        ui.display_message("Task added successfully ✓")
    else:
        ui.display_message("Title is required. Please enter a non-empty title.", is_error=True)


def handle_view_tasks(task_list: TaskList) -> None:
    """Handle viewing all tasks.

    Args:
        task_list: TaskList instance to retrieve tasks from
    """
    tasks = services.get_all_tasks(task_list)
    ui.display_tasks(tasks)


def handle_update_task(task_list: TaskList) -> None:
    """Handle updating a task's title and/or description.

    Args:
        task_list: TaskList instance containing the task to update
    """
    task_id = ui.prompt_task_id()

    # Check if task exists first
    existing_task = services.find_task_by_id(task_list, task_id)
    if existing_task is None:
        ui.display_message(f"Task ID {task_id} not found", is_error=True)
        return

    # Prompt for new values
    print(f"\nCurrent title: {existing_task.title}")
    new_title_input = input("Enter new title (or press Enter to keep current): ")
    new_title = new_title_input if new_title_input else None

    print(f"Current description: {existing_task.description}")
    new_desc_input = input("Enter new description (or press Enter to keep current): ")
    new_desc = new_desc_input if new_desc_input else None

    # Update task
    result = services.update_task(task_list, task_id, title=new_title, description=new_desc)

    if result:
        ui.display_message("Task updated successfully ✓")
    else:
        ui.display_message("Title cannot be empty", is_error=True)


def handle_delete_task(task_list: TaskList) -> None:
    """Handle deleting a task.

    Args:
        task_list: TaskList instance to delete from
    """
    task_id = ui.prompt_task_id()
    success = services.delete_task(task_list, task_id)

    if success:
        ui.display_message("Task deleted successfully ✓")
    else:
        ui.display_message(f"Task ID {task_id} not found", is_error=True)


def handle_toggle_complete(task_list: TaskList) -> None:
    """Handle toggling a task's completion status.

    Args:
        task_list: TaskList instance containing the task
    """
    task_id = ui.prompt_task_id()
    result = services.toggle_complete(task_list, task_id)

    if result:
        status = "complete" if result.completed else "pending"
        ui.display_message(f"Task marked as {status} ✓")
    else:
        ui.display_message(f"Task ID {task_id} not found", is_error=True)


def main() -> None:
    """Main application loop."""
    task_list = TaskList()

    try:
        while True:
            ui.display_menu()
            choice = ui.get_menu_choice()

            if choice == constants.MENU_ADD_TASK:
                handle_add_task(task_list)
            elif choice == constants.MENU_VIEW_TASKS:
                handle_view_tasks(task_list)
            elif choice == constants.MENU_UPDATE_TASK:
                handle_update_task(task_list)
            elif choice == constants.MENU_DELETE_TASK:
                handle_delete_task(task_list)
            elif choice == constants.MENU_TOGGLE_COMPLETE:
                handle_toggle_complete(task_list)
            elif choice == constants.MENU_EXIT:
                ui.display_exit_warning()
                break

    except KeyboardInterrupt:
        print("\n")
        ui.display_exit_warning()
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        ui.display_exit_warning()


if __name__ == "__main__":
    main()
