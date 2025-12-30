# Enhanced Phase I - Advanced Console Todo Application

> A professional CLI todo application with priorities, tags, search, filter, and sort capabilities using Python 3.13+ and the rich library for beautiful table output.

## Features

### Basic Level (5 Core Operations)
✅ **Add Task** - Create tasks with titles and descriptions  
✅ **View All Tasks** - Display all tasks in a formatted table  
✅ **Update Task** - Modify task details by ID  
✅ **Delete Task** - Remove tasks by ID  
✅ **Mark Complete** - Toggle task completion status  

### Bonus Intermediate Level (3 Advanced Features)
✅ **Priorities** - Assign HIGH, MEDIUM, or LOW priority to tasks  
✅ **Tags/Categories** - Add multiple categorization tags per task  
✅ **Search** - Find tasks by keyword in title or description  
✅ **Filter** - Filter tasks by status, priority, or tag  
✅ **Sort** - Sort tasks by priority, title, or ID  
✅ **Rich Table Display** - Professional formatted tables with color-coding  

## Quick Start

### Prerequisites
- Python 3.13 or higher
- [UV package manager](https://docs.astral.sh/uv/)

### Installation

```bash
# Clone the repository
git clone https://github.com/khawajanaqeeb/Q4-hackathon2-todo.git
cd Q4-hackathon2-todo

# Install dependencies with UV
uv sync

# Run the application
uv run python -m src.todo_app
```

## Usage

### Main Menu
```
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Pending
6. Search Tasks
7. Filter Tasks
8. Sort Tasks
9. Exit
```

### Adding a Task
1. Select option **1** from the main menu
2. Enter task title (required)
3. Enter description (optional, press Enter to skip)
4. Select priority: **1** (High), **2** (Medium - default), or **3** (Low)
5. Enter tags separated by commas (optional, e.g., "work, urgent, backend")

### Viewing Tasks
Select option **2** to see all tasks in a beautiful rich table format:
- **Color-coded priorities**: 🔴 High (red), 🟡 Medium (yellow), 🟢 Low (green)
- **Clear status indicators**: ✓ Complete, ○ Pending
- **Task count summary**: "Total Tasks: N" at the top

### Searching Tasks
1. Select option **6**
2. Enter keyword to search in titles and descriptions
3. Results display matching tasks with count

### Filtering Tasks
1. Select option **7**
2. Choose filter type:
   - **1** - Filter by Status (Complete/Pending)
   - **2** - Filter by Priority (High/Medium/Low)
   - **3** - Filter by Tag (case-insensitive)

### Sorting Tasks
1. Select option **8**
2. Choose sort order:
   - **1** - By Priority (HIGH → MEDIUM → LOW)
   - **2** - By Title (A-Z alphabetically)
   - **3** - By ID (Creation order)

## Architecture

### Three-Layer Design
```
┌─────────────────────────────────────┐
│  CLI Layer (cli.py)                 │
│  - Interactive menu                 │
│  - Rich table display               │
│  - Input validation                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Service Layer (services.py)        │
│  - TodoService class                │
│  - CRUD operations                  │
│  - Search/Filter/Sort               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Data Layer (models.py)             │
│  - Task dataclass                   │
│  - Priority enum                    │
│  - Helper methods                   │
└─────────────────────────────────────┘
```

### File Structure
```
Q4-hackathon2-todo/
├── src/
│   └── todo_app/
│       ├── __init__.py          # Package marker
│       ├── __main__.py          # Entry point
│       ├── models.py            # Task & Priority
│       ├── services.py          # TodoService class
│       └── cli.py               # Interactive CLI
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_models.py           # Model tests (100% coverage)
│   └── test_services.py         # Service tests (97% coverage)
├── specs/
│   └── 002-enhanced-todo-features/
│       ├── spec.md              # Requirements
│       ├── plan.md              # Architecture
│       └── tasks.md             # Implementation tasks
├── .claude/
│   └── agents/
│       └── hackathon-cli-builder.md  # Reusable Intelligence
├── pyproject.toml               # UV dependencies
├── README.md                    # This file
└── CLAUDE.md                    # AI agent instructions
```

## Testing

### Run Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=src/todo_app --cov-report=html

# View HTML coverage report
# Open htmlcov/index.html in browser
```

### Test Coverage
- **models.py**: 100% coverage ✅
- **services.py**: 97% coverage ✅
- **Overall**: 80%+ coverage target achieved ✅

## Technologies

- **Python 3.13+** - Modern Python with latest features
- **UV** - Fast Python package manager
- **rich** - Beautiful terminal formatting
- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting

## Development

### Code Quality Standards
✅ **PEP 8 compliant** - All code follows Python style guidelines  
✅ **Type hints** - Comprehensive type annotations on all functions  
✅ **Google-style docstrings** - Clear documentation for all public APIs  
✅ **80%+ test coverage** - Comprehensive test suite  
✅ **Clean architecture** - Separation of concerns (Model-Service-UI)  

### Reusable Intelligence
This project demonstrates the **hackathon-cli-builder** agent, a reusable AI component that generates professional three-layer CLI applications:
- Location: `.claude/agents/hackathon-cli-builder.md`
- Capabilities: Models, Services, CLI with Rich tables
- **Bonus Points**: +200 for Reusable Intelligence

## Limitations

⚠️ **In-Memory Storage Only** - All tasks are lost when the application exits  
⚠️ **Single User** - No multi-user support or authentication  
⚠️ **No Persistence** - No database or file storage in Phase I  

These limitations are by design for Phase I and will be addressed in future phases.

## Contributing

This is a hackathon submission project. For questions or suggestions:
- GitHub: [@khawajanaqeeb](https://github.com/khawajanaqeeb)
- Repository: [Q4-hackathon2-todo](https://github.com/khawajanaqeeb/Q4-hackathon2-todo)

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with **Claude Code** by Anthropic
- Enhanced with the **hackathon-cli-builder** reusable agent
- Inspired by the SDD-RI (Spec-Driven Development with Reusable Intelligence) methodology

---

**Phase I Submission**: December 2025  
**Target**: Basic Level + Bonus Intermediate Features  
**Status**: ✅ Complete with 80%+ test coverage
