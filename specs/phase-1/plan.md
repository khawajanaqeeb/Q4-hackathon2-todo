# Phase I Architectural Plan: Todo In-Memory Python Console App

**Feature Branch**: `phase1-console-todo`
**Created**: 2025-12-29
**Status**: Draft
**GitHub Repository**: https://github.com/khawajanaqeeb (main branch)
**Based on**: specs/phase-1/spec.md

## Overview

### Phase Goal

Build a working command-line todo application in Python 3.13+ that allows users to perform basic CRUD operations (Create, Read, Update, Delete) on tasks stored entirely in memory. The application must be simple, testable, and demonstrate clean architecture principles while adhering to Phase I constraints (no persistence, no web, no AI).

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                │
└───────────────────────┬─────────────────────────────────────┘
                        │ CLI Commands
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    UI Layer (ui.py)                         │
│  - Display menu                                             │
│  - Capture input                                            │
│  - Format output                                            │
│  - Display messages                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │ Function calls
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Service Layer (services.py)                 │
│  - add_task()       - delete_task()                         │
│  - update_task()    - toggle_complete()                     │
│  - get_all_tasks()  - find_task_by_id()                     │
│  - validate_input()                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │ Data operations
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Model Layer (models.py)                     │
│  - Task dataclass                                           │
│  - TaskList (in-memory storage)                             │
│  - ID generator                                             │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              In-Memory Storage (Python list)                │
│  [Task(1, "Title", "Desc", False), Task(2, ...), ...]      │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Layered Architecture**: Separation of concerns into Model-Service-UI layers
   - **Rationale**: Enables independent testing, future extensibility (Phase II can swap storage layer)
   - **Tradeoff**: Slightly more files, but significantly better maintainability

2. **Dataclass for Task Model**: Use Python `@dataclass` for Task entity
   - **Rationale**: Built-in, type-safe, generates `__init__`, `__repr__`, `__eq__` automatically
   - **Alternative**: Plain dict (too loose), NamedTuple (immutable, conflicts with update operation)

3. **Pure Functions in Service Layer**: Stateless service functions accepting/returning data
   - **Rationale**: Easier to test, no hidden state, clear input/output contracts
   - **Tradeoff**: TaskList must be passed to each function (acceptable for Phase I simplicity)

4. **Sequential Integer IDs**: Auto-incrementing IDs starting from 1, gaps allowed after deletion
   - **Rationale**: Simple, predictable, human-friendly for CLI interaction
   - **Alternative**: UUIDs (overkill for single-user CLI), timestamps (not user-friendly)

5. **Standard Library Only for CLI**: No external CLI framework (typer, click, etc.)
   - **Rationale**: Meets Phase I simplicity requirement, no additional dependencies
   - **Tradeoff**: Manual input parsing (acceptable given 5 simple operations)

6. **Exit Warning Message**: Display message on exit reminding users data is not persisted
   - **Rationale**: Manages user expectations, prevents data loss confusion
   - **Risk Mitigation**: Addresses R-001 from spec (data loss surprise)

## Technology Stack

### Core Technologies

- **Language**: Python 3.13+
  - Type hints required for all functions
  - Docstrings required for all public functions (PEP 257)
  - PEP 8 style compliance

- **Package Manager**: UV
  - Modern, fast Python package manager
  - Manages dependencies and virtual environments
  - Creates `pyproject.toml` for project configuration

- **Storage**: In-memory Python list
  - List of Task dataclass instances
  - No file I/O, no database
  - Data lost on exit (expected Phase I behavior)

- **Testing Framework**: pytest
  - Unit tests for all service layer functions
  - Integration tests for complete workflows
  - Minimum 80% code coverage (measured with pytest-cov)

- **Code Generation**: Claude Code only
  - No manual coding allowed per constitution Article II
  - All code AI-generated from specifications

### Development Tools

- **Linting**: ruff (fast Python linter, PEP 8 compliance)
- **Type Checking**: mypy (static type checker for type hints)
- **Coverage**: pytest-cov (code coverage measurement)
- **Formatting**: black (automatic code formatting, optional)

### Dependencies (pyproject.toml)

```toml
[project]
name = "todo-console-app"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0"
]
```

## Project Structure

```
F:\Q4-hakathons\Q4-hackathon2-todo\
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # Project governance document
│   ├── templates/                   # Spec-Kit Plus templates
│   └── scripts/                     # Helper scripts
│
├── specs/
│   └── phase-1/
│       ├── spec.md                  # Feature specification (WHAT)
│       ├── plan.md                  # This file - architectural plan (HOW)
│       ├── tasks.md                 # Implementation tasks (TODO)
│       └── checklists/
│           └── requirements.md      # Quality validation checklist
│
├── history/
│   ├── prompts/
│   │   └── phase-1/                 # Prompt History Records for Phase I
│   └── adr/                         # Architectural Decision Records
│
├── phase1-console/
│   ├── README.md                    # Setup, usage, features documentation
│   ├── CLAUDE.md                    # AI agent instructions
│   ├── pyproject.toml               # UV project configuration
│   ├── uv.lock                      # Dependency lock file (auto-generated)
│   │
│   ├── src/
│   │   └── todo_app/
│   │       ├── __init__.py          # Package initialization
│   │       ├── models.py            # Task dataclass, TaskList
│   │       ├── services.py          # Business logic (CRUD operations)
│   │       ├── ui.py                # CLI interface (menu, I/O)
│   │       └── main.py              # Entry point, main loop
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py           # Unit tests for models
│       ├── test_services.py         # Unit tests for services
│       ├── test_ui.py               # Unit tests for UI functions
│       └── test_integration.py      # End-to-end workflow tests
│
├── .gitignore                       # Git ignore patterns
└── README.md                        # Root project README
```

## Component Architecture

### Model Layer (`models.py`)

**Responsibility**: Define data structures and in-memory storage

**Components**:

1. **Task Dataclass**
   ```python
   @dataclass
   class Task:
       id: int
       title: str
       description: str
       completed: bool = False
   ```
   - Immutable after creation except via service layer
   - Type hints for all fields
   - Default value for `completed` (False)

2. **TaskList Class**
   ```python
   class TaskList:
       tasks: List[Task]
       next_id: int
   ```
   - Encapsulates in-memory storage (list of Task objects)
   - Tracks next available ID for auto-increment
   - Provides thread-safe ID generation (not required Phase I, but good practice)

**Design Rationale**:
- Dataclass provides value equality, auto-generated methods
- Separation of Task (entity) from TaskList (collection) follows SRP
- Type hints enable static analysis and IDE autocomplete

### Service Layer (`services.py`)

**Responsibility**: Business logic and data operations

**Pure Functions** (no side effects, stateless):

1. **`add_task(task_list: TaskList, title: str, description: str = "") -> Task`**
   - Validates title is non-empty
   - Generates next sequential ID
   - Creates Task instance
   - Appends to task_list.tasks
   - Increments task_list.next_id
   - Returns created Task

2. **`delete_task(task_list: TaskList, task_id: int) -> bool`**
   - Finds task by ID
   - Removes from task_list.tasks if found
   - Returns True if deleted, False if ID not found
   - Does NOT reuse IDs (gaps allowed)

3. **`update_task(task_list: TaskList, task_id: int, title: str | None = None, description: str | None = None) -> Task | None`**
   - Validates title is non-empty if provided
   - Finds task by ID
   - Updates title and/or description (only fields provided)
   - Returns updated Task if found, None otherwise

4. **`toggle_complete(task_list: TaskList, task_id: int) -> Task | None`**
   - Finds task by ID
   - Toggles `completed` field (True ↔ False)
   - Returns updated Task if found, None otherwise

5. **`get_all_tasks(task_list: TaskList) -> List[Task]`**
   - Returns shallow copy of task_list.tasks
   - Prevents external mutation of internal list
   - Returns empty list if no tasks

6. **`find_task_by_id(task_list: TaskList, task_id: int) -> Task | None`**
   - Searches task_list.tasks for matching ID
   - Returns Task if found, None otherwise
   - Used internally by other service functions

7. **`validate_title(title: str) -> bool`**
   - Checks title is non-empty after stripping whitespace
   - Returns True if valid, False otherwise
   - Used by add_task and update_task

**Design Rationale**:
- Pure functions are easier to test (no mocking required)
- Explicit TaskList parameter makes data flow visible
- Return type hints (Task | None) enable clear error handling
- Single Responsibility Principle: each function does one thing

**Error Handling**:
- Service layer returns None or False for failures (no exceptions for business logic)
- UI layer interprets return values and displays appropriate messages
- Input validation (title non-empty, ID exists) happens in service layer

### UI Layer (`ui.py`)

**Responsibility**: User interaction (input/output)

**Components**:

1. **`display_menu() -> None`**
   - Prints numbered menu with 6 options:
     1. Add Task
     2. View Tasks
     3. Update Task
     4. Delete Task
     5. Mark Complete/Pending
     6. Exit
   - Clear, user-friendly formatting

2. **`get_menu_choice() -> int`**
   - Prompts user for menu selection
   - Validates input is integer 1-6
   - Loops until valid input received
   - Returns validated choice

3. **`prompt_task_details() -> tuple[str, str]`**
   - Prompts for task title (required)
   - Prompts for task description (optional, can be empty)
   - Returns (title, description) tuple

4. **`prompt_task_id() -> int`**
   - Prompts for task ID
   - Validates input is positive integer
   - Loops until valid input received
   - Returns validated ID

5. **`display_tasks(tasks: List[Task]) -> None`**
   - Formats tasks in table:
     ```
     ID | Title              | Description        | Status
     ---|--------------------|--------------------|-------------
     1  | Buy groceries      | Milk, bread, eggs  | ○ Pending
     2  | Call dentist       |                    | ✓ Complete
     ```
   - Handles empty list ("No tasks found")
   - Truncates long titles/descriptions for display (e.g., max 20 chars with "...")
   - Uses "✓ Complete" / "○ Pending" for visual clarity

6. **`display_message(message: str, is_error: bool = False) -> None`**
   - Prints success or error messages
   - Optional color coding if terminal supports (green for success, red for error)
   - Clear, actionable messages (e.g., "Task added successfully", "Task ID 99 not found")

7. **`display_exit_warning() -> None`**
   - Called before application exits
   - Warns user: "⚠️  All tasks will be lost. Data is not persisted in Phase I."

**Design Rationale**:
- Separation from service layer enables UI changes without touching business logic
- Input validation at UI level (basic type checking)
- Business validation at service level (title non-empty, ID exists)
- Table formatting improves readability over raw lists

### Main Entry (`main.py`)

**Responsibility**: Application orchestration and main loop

**Components**:

1. **`main() -> None`**
   - Initializes TaskList (empty)
   - Displays welcome message
   - Enters main loop:
     ```python
     while True:
         display_menu()
         choice = get_menu_choice()
         if choice == 1:
             handle_add_task(task_list)
         elif choice == 2:
             handle_view_tasks(task_list)
         # ... other choices
         elif choice == 6:
             display_exit_warning()
             break
     ```
   - Displays exit warning before terminating
   - Exits cleanly

2. **`handle_add_task(task_list: TaskList) -> None`**
   - Calls prompt_task_details() to get title and description
   - Calls services.add_task()
   - Displays success or error message

3. **`handle_view_tasks(task_list: TaskList) -> None`**
   - Calls services.get_all_tasks()
   - Calls display_tasks()

4. **`handle_update_task(task_list: TaskList) -> None`**
   - Prompts for task ID
   - Prompts for new title (optional, press Enter to keep current)
   - Prompts for new description (optional, press Enter to keep current)
   - Calls services.update_task()
   - Displays success or error message

5. **`handle_delete_task(task_list: TaskList) -> None`**
   - Prompts for task ID
   - Calls services.delete_task()
   - Displays success or error message

6. **`handle_toggle_complete(task_list: TaskList) -> None`**
   - Prompts for task ID
   - Calls services.toggle_complete()
   - Displays success message with new status or error

**Design Rationale**:
- Each handler function encapsulates one menu operation
- Main loop is clean and readable
- Handlers coordinate UI and service layers
- Exit warning manages user expectations (addresses spec R-001)

## Data Flow

### Example: Add Task Flow

```
User
  │
  └─> Selects "1. Add Task" from menu
        │
        ▼
      ui.display_menu()
      ui.get_menu_choice() → 1
        │
        ▼
      main.handle_add_task(task_list)
        │
        ├─> ui.prompt_task_details()
        │     └─> Returns ("Buy groceries", "Milk, bread, eggs")
        │
        ├─> services.add_task(task_list, "Buy groceries", "Milk, bread, eggs")
        │     ├─> Validates title non-empty ✓
        │     ├─> Generates ID = 1 (task_list.next_id)
        │     ├─> Creates Task(1, "Buy groceries", "Milk, bread, eggs", False)
        │     ├─> Appends to task_list.tasks
        │     ├─> Increments task_list.next_id to 2
        │     └─> Returns Task(1, ...)
        │
        └─> ui.display_message("Task added successfully ✓")
              │
              ▼
            User sees confirmation
```

### Example: View Tasks Flow

```
User
  │
  └─> Selects "2. View Tasks"
        │
        ▼
      main.handle_view_tasks(task_list)
        │
        ├─> services.get_all_tasks(task_list)
        │     └─> Returns [Task(1, "Buy groceries", ..., False), Task(2, "Call dentist", ..., True)]
        │
        └─> ui.display_tasks(tasks)
              │
              └─> Prints formatted table:
                    ID | Title          | Description        | Status
                    ---|----------------|--------------------|-------------
                    1  | Buy groceries  | Milk, bread, eggs  | ○ Pending
                    2  | Call dentist   |                    | ✓ Complete
```

### Example: Error Flow (Invalid ID)

```
User
  │
  └─> Selects "4. Delete Task"
        │
        ▼
      main.handle_delete_task(task_list)
        │
        ├─> ui.prompt_task_id()
        │     └─> User enters: 99
        │     └─> Returns 99
        │
        ├─> services.delete_task(task_list, 99)
        │     ├─> Searches for Task with id=99
        │     ├─> Not found
        │     └─> Returns False
        │
        └─> ui.display_message("Task ID 99 not found ❌", is_error=True)
              │
              ▼
            User sees error, returns to menu
```

## Error Handling Strategy

### Input Validation (UI Layer)

- **Menu choice**: Loop until user enters valid integer 1-6
- **Task ID**: Loop until user enters positive integer
- **Title/Description**: Accept any string (business validation in service layer)

**Implementation**:
```python
def get_menu_choice() -> int:
    while True:
        try:
            choice = int(input("Enter choice (1-6): "))
            if 1 <= choice <= 6:
                return choice
            else:
                print("Invalid choice. Please enter 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")
```

### Business Validation (Service Layer)

- **Title non-empty**: Check `title.strip() != ""`
  - Return None or False if invalid
  - UI layer displays error message

- **Task ID exists**: Search task_list for matching ID
  - Return None or False if not found
  - UI layer displays error message

**Implementation**:
```python
def add_task(task_list: TaskList, title: str, description: str = "") -> Task | None:
    if not validate_title(title):
        return None  # UI layer handles error message
    # ... create task
    return task
```

### Exception Handling

- **Keyboard Interrupt (Ctrl+C)**: Catch in main() and display exit warning
- **Unexpected errors**: Log to stderr, display generic error, don't crash

**Implementation**:
```python
def main() -> None:
    try:
        # main loop
    except KeyboardInterrupt:
        print("\n")
        display_exit_warning()
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
```

### Error Messages

**Principle**: Clear, actionable, user-friendly

- ✅ Good: "Task ID 99 not found. Use 'View Tasks' to see valid IDs."
- ❌ Bad: "KeyError: 99"

- ✅ Good: "Title is required. Please enter a non-empty title."
- ❌ Bad: "Invalid input"

## Testing Strategy

### Test Coverage Requirements

- **Minimum**: 80% code coverage (per spec NFR-005)
- **Target**: 90%+ for critical paths (add, view, update, delete, toggle)
- **Measurement**: `pytest --cov=src/todo_app --cov-report=term-missing`

### Unit Tests

**models.py** (`test_models.py`):
- Test Task dataclass creation
- Test TaskList initialization
- Test ID generation (next_id increments correctly)

**services.py** (`test_services.py`):
- **test_add_task_success**: Valid title and description creates task with ID 1
- **test_add_task_empty_title**: Empty title returns None
- **test_add_task_increments_id**: Multiple adds increment IDs (1, 2, 3)
- **test_delete_task_success**: Existing ID deletes task, returns True
- **test_delete_task_not_found**: Non-existent ID returns False
- **test_update_task_both_fields**: Update title and description
- **test_update_task_title_only**: Update only title, description unchanged
- **test_update_task_empty_title**: Empty title returns None
- **test_update_task_not_found**: Non-existent ID returns None
- **test_toggle_complete_pending_to_complete**: Toggles False → True
- **test_toggle_complete_complete_to_pending**: Toggles True → False
- **test_toggle_complete_not_found**: Non-existent ID returns None
- **test_get_all_tasks_empty**: Empty list returns []
- **test_get_all_tasks_multiple**: Returns all tasks
- **test_find_task_by_id_found**: Existing ID returns Task
- **test_find_task_by_id_not_found**: Non-existent ID returns None

**ui.py** (`test_ui.py`):
- Test display_tasks() formats correctly (mock print)
- Test display_tasks() handles empty list
- Test display_message() output (mock print)
- Test prompt functions with mocked input (using pytest monkeypatch)

### Integration Tests (`test_integration.py`)

- **test_full_workflow**: Add → View → Update → Mark Complete → Delete → View
- **test_multiple_tasks**: Add 5 tasks, verify IDs 1-5, delete ID 3, verify gap
- **test_edge_case_very_long_title**: Add task with 1000-char title, verify storage and display
- **test_edge_case_unicode**: Add task with emoji and special chars, verify storage

### Test Fixtures (conftest.py)

```python
@pytest.fixture
def empty_task_list() -> TaskList:
    return TaskList(tasks=[], next_id=1)

@pytest.fixture
def task_list_with_data() -> TaskList:
    tl = TaskList(tasks=[], next_id=1)
    add_task(tl, "Task 1", "Description 1")
    add_task(tl, "Task 2", "Description 2")
    return tl
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/todo_app --cov-report=term-missing --cov-report=html

# Run specific test file
uv run pytest tests/test_services.py

# Run specific test
uv run pytest tests/test_services.py::test_add_task_success
```

## Constitution Compliance Check

### Article II: Spec-Driven Development Mandate ✅

- ✅ All code generated by Claude Code from this architectural plan
- ✅ No manual coding permitted
- ✅ Plan phase (HOW) follows spec phase (WHAT)
- ✅ Next: Tasks phase will break down into testable implementation steps

### Article III: Phase-Based Evolution ✅

- ✅ Phase I constraints respected:
  - In-memory storage only (no persistence)
  - CLI interface only (no web)
  - Basic CRUD features only (no advanced features)
- ✅ Phase II preparation: Layered architecture allows storage layer swap

### Article IV: Technology Stack Constraints ✅

- ✅ Python 3.13+ (specified in pyproject.toml)
- ✅ UV package manager (pyproject.toml, uv.lock)
- ✅ In-memory storage (Python list in TaskList)
- ✅ CLI interface (ui.py, no web dependencies)
- ✅ pytest testing framework (dev dependencies)

### Article VI: Code Quality & Architecture Standards ✅

- ✅ **Modularity**: Separate files for models, services, ui, main
- ✅ **Single Responsibility Principle**: Each module has one clear purpose
- ✅ **Clean Architecture**: Layered (Model → Service → UI)
- ✅ **Type Hints**: All function signatures include type hints
- ✅ **Docstrings**: Required for all public functions (PEP 257)
- ✅ **PEP 8**: Style compliance enforced by ruff

### Article VII: Security & Safety Discipline ✅

- ✅ **Input Validation**: Title non-empty, ID positive integer
- ✅ **No Code Injection**: No eval(), exec(), or dynamic imports
- ✅ **Error Handling**: Try-except blocks, graceful degradation
- ✅ **Phase I Rules**: No authentication required (single-user CLI)

### Article VIII: Documentation Excellence ✅

- ✅ **README.md**: Setup instructions, usage guide, features list
- ✅ **CLAUDE.md**: AI agent instructions, workflow documentation
- ✅ **Spec.md**: Feature specification (WHAT)
- ✅ **Plan.md**: This architectural plan (HOW)
- ✅ **Tasks.md**: Implementation breakdown (TODO, next step)
- ✅ **PHRs**: Prompt History Records in history/prompts/phase-1/

### Article IX: Submission & Presentation Standards ✅

- ✅ **Public GitHub Repository**: https://github.com/khawajanaqeeb
- ✅ **Main Branch**: All artifacts on main branch
- ✅ **Git Tags**: v1.0-phase1 (to be created after implementation)
- ✅ **Demo Video**: 90-second walkthrough (to be created after implementation)
- ✅ **Submission Form**: To be completed with repo link

## Risks & Mitigations

### Technical Risks

**R-T01: Test Coverage Below 80%**
- **Impact**: High (fails acceptance criteria AC-006)
- **Likelihood**: Medium
- **Mitigation**: Write tests before implementation (TDD), run coverage checks frequently
- **Acceptance Test**: `pytest --cov=src/todo_app --cov-fail-under=80`

**R-T02: Type Hint Coverage Incomplete**
- **Impact**: Medium (fails NFR-003)
- **Likelihood**: Low (mypy catches this)
- **Mitigation**: Run `mypy src/todo_app` before each commit
- **Acceptance Test**: `mypy src/todo_app --strict` passes with 0 errors

**R-T03: PEP 8 Violations**
- **Impact**: Medium (fails NFR-006)
- **Likelihood**: Low (ruff auto-fixes most issues)
- **Mitigation**: Run `ruff check src/todo_app --fix` before commit
- **Acceptance Test**: `ruff check src/todo_app` passes with 0 errors

### User Experience Risks

**R-UX01: Data Loss Confusion**
- **Impact**: High (user frustration, spec R-001)
- **Likelihood**: High (expected behavior misunderstood)
- **Mitigation**: Display exit warning message: "⚠️ All tasks will be lost. Data is not persisted in Phase I."
- **Acceptance Test**: Manual - verify warning displays on exit

**R-UX02: Long Titles/Descriptions Display Issues**
- **Impact**: Low (spec R-002 - may cause formatting problems)
- **Likelihood**: Medium
- **Mitigation**: Truncate display to 50 chars with "...", store full text
- **Acceptance Test**: Add task with 1000-char title, verify display truncates but full text stored

**R-UX03: Invalid Input Causes Crash**
- **Impact**: High (spec R-003 - poor user experience)
- **Likelihood**: Low (comprehensive input validation)
- **Mitigation**: Try-except blocks, input validation loops, never call `int()` without try-except
- **Acceptance Test**: Fuzz test with random inputs, verify no crashes

### Performance Risks

**R-P01: Performance Degradation with 1000+ Tasks**
- **Impact**: Medium (spec R-005, NFR-008 requires 1000 tasks without degradation)
- **Likelihood**: Low (Python lists are efficient up to 10,000+ items)
- **Mitigation**: Use list comprehensions, avoid nested loops, use dict for ID lookups if needed
- **Acceptance Test**: Create 1000 tasks, measure operations complete in <1 second

## Next Steps

### Immediate Actions

1. **Create tasks.md**: Break down this plan into testable implementation tasks using `/sp.tasks`
2. **Implement via Claude Code**: Execute tasks using `/sp.implement` (NO manual coding)
3. **Run Tests**: Verify 80%+ coverage after implementation
4. **Create README.md**: Document setup, usage, features
5. **Create Demo Video**: Record 90-second walkthrough of all 5 features
6. **Git Commit & Tag**: Commit all files, create v1.0-phase1 tag
7. **Submit Form**: Complete hackathon submission form with repo link

### Success Criteria (from spec.md)

Implementation complete when:
- ✅ All 5 CRUD features functional
- ✅ All 15 functional requirements implemented
- ✅ All 10 non-functional requirements met
- ✅ 80%+ test coverage
- ✅ All tests pass
- ✅ PEP 8 compliance
- ✅ Type hints and docstrings complete
- ✅ README.md with instructions
- ✅ Demo video created
- ✅ Git tag v1.0-phase1 pushed
- ✅ Submission form completed

---

**Ready for**: `/sp.tasks` to break down into implementation tasks
