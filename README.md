# Phase I - Todo In-Memory Python Console App

A simple command-line todo application built with Python 3.13+ for Hackathon II: "The Evolution of Todo". This Phase I implementation focuses on basic CRUD operations with in-memory storage.

## Features

- ✅ **Add Task**: Create tasks with title and optional description
- ✅ **View Tasks**: Display all tasks in a formatted table with ID, title, description, and status
- ✅ **Update Task**: Modify task title and/or description by ID
- ✅ **Delete Task**: Remove tasks by ID (gaps allowed in ID sequence)
- ✅ **Mark Complete**: Toggle task completion status (✓ Complete / ○ Pending)

## Requirements

- Python 3.13 or higher
- UV package manager ([installation guide](https://github.com/astral-sh/uv))

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/khawajanaqeeb/hackathon-todo.git
   cd hackathon-todo/phase1-console
   ```

2. **Install dependencies with UV**:
   ```bash
   uv sync --all-extras
   ```

3. **Verify installation**:
   ```bash
   uv run pytest --version
   ```

## Usage

### Run the application

```bash
uv run todo
```

Or directly with Python:

```bash
uv run python -m todo_app.main
```

### Main Menu

When you launch the app, you'll see:

```
===== Todo App - Phase I =====

1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete/Pending
6. Exit

Enter choice (1-6):
```

### Example Workflow

1. **Add a task**:
   - Select option `1`
   - Enter title: `Buy groceries`
   - Enter description: `Milk, bread, eggs` (optional, press Enter to skip)
   - Result: `Task added successfully ✓`

2. **View all tasks**:
   - Select option `2`
   - Result:
     ```
     ID | Title              | Description        | Status
     ---|--------------------|--------------------|-------------
     1  | Buy groceries      | Milk, bread, eggs  | ○ Pending
     ```

3. **Mark task complete**:
   - Select option `5`
   - Enter task ID: `1`
   - Result: `Task marked as complete ✓`

4. **Update task**:
   - Select option `3`
   - Enter task ID: `1`
   - Enter new title (or press Enter to keep current): `Buy weekly groceries`
   - Enter new description (or press Enter to keep current): `Milk, bread, eggs, cheese`
   - Result: `Task updated successfully ✓`

5. **Delete task**:
   - Select option `4`
   - Enter task ID: `1`
   - Result: `Task deleted successfully ✓`

6. **Exit**:
   - Select option `6`
   - Warning: `⚠️  All tasks will be lost. Data is not persisted in Phase I.`

## Testing

### Run all tests

```bash
uv run pytest
```

### Run tests with coverage

```bash
uv run pytest --cov=src/todo_app --cov-report=term-missing --cov-report=html
```

View HTML coverage report:

```bash
# Open htmlcov/index.html in your browser
```

### Run specific test file

```bash
uv run pytest tests/test_services.py
uv run pytest tests/test_ui.py
uv run pytest tests/test_models.py
uv run pytest tests/test_integration.py
```

### Run type checking

```bash
uv run mypy src/todo_app
```

### Run linting

```bash
uv run ruff check src/todo_app
```

## Project Structure

```
phase1-console/
├── README.md                    # This file
├── CLAUDE.md                    # AI agent instructions
├── pyproject.toml               # UV project configuration
├── src/
│   └── todo_app/
│       ├── __init__.py          # Package initialization
│       ├── models.py            # Task and TaskList data structures
│       ├── services.py          # Business logic (CRUD operations)
│       ├── ui.py                # CLI interface (menu, display, input)
│       └── main.py              # Application entry point
└── tests/
    ├── __init__.py
    ├── test_models.py           # Unit tests for models
    ├── test_services.py         # Unit tests for services
    ├── test_ui.py               # Unit tests for UI functions
    ├── test_integration.py      # End-to-end integration tests
    └── test_edge_cases.py       # Edge case and error handling tests
```

## Architecture

Phase I follows a layered architecture:

- **Model Layer** (`models.py`): Task dataclass and TaskList for in-memory storage
- **Service Layer** (`services.py`): Pure functions for business logic (add, delete, update, toggle, get_all, find, validate)
- **UI Layer** (`ui.py`): CLI interface functions (menu, prompts, display, messages)
- **Main Entry** (`main.py`): Application orchestration and main loop

## Important Notes

⚠️ **Data is NOT persisted**: All tasks are stored in memory only. When you exit the app, all data is lost. This is expected behavior for Phase I.

✅ **Test Coverage**: Minimum 80% code coverage required (currently: check with `uv run pytest --cov`)

✅ **Type Safety**: All functions include type hints and are validated with mypy

✅ **Code Quality**: Follows PEP 8 style guidelines, enforced by ruff

## Phase I Constraints

- **No Persistence**: In-memory storage only (Python list)
- **No Authentication**: Single-user, no login required
- **No Web Interface**: CLI only
- **No AI Features**: Basic CRUD operations only
- **No Advanced Features**: No priorities, tags, due dates, search, or filtering

## Next Steps (Future Phases)

- **Phase II**: Web interface with file persistence
- **Phase III**: AI chatbot integration
- **Phase IV**: Local Kubernetes deployment
- **Phase V**: Cloud-native with full CI/CD

## Hackathon Submission

- **Repository**: https://github.com/khawajanaqeeb/hackathon-todo
- **Phase**: Phase I - In-Memory Console App
- **Submission Date**: December 7, 2025
- **Demo Video**: [Link to 90-second walkthrough]

## License

MIT License - Created for Hackathon II: "The Evolution of Todo"

## Troubleshooting

### Issue: `uv: command not found`

**Solution**: Install UV package manager:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Issue: Python version mismatch

**Solution**: UV will automatically use Python 3.13+ if available. To specify:
```bash
uv python install 3.13
uv python pin 3.13
```

### Issue: Tests failing

**Solution**: Ensure you've installed dev dependencies:
```bash
uv sync --all-extras
```

### Issue: Import errors

**Solution**: Run from the project root (phase1-console/):
```bash
cd phase1-console
uv run todo
```

## Contact

For issues or questions, create an issue at: https://github.com/khawajanaqeeb/hackathon-todo/issues
