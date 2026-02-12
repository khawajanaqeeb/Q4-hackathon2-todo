# Q4 Hackathon II - Todo Application

> A multi-phase todo application evolution: from console CLI (Phase I) to full-stack web app (Phase II) to AI chatbot (Phase III).

## Project Overview

This repository contains all three phases of the Hackathon II "Evolution of Todo" project.

**Current Phase**: Phase III (AI Chatbot Integration)
**Previous Phases**: Phase I (Console CLI - Complete), Phase II (Full-Stack Web App - Complete)

---

## Quick Start (Phase I)

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

---

## Project Structure

This repository follows the official Hackathon II folder structure with clear separation between phases:

```
Q4-hackathon2-todo/
├── specs/
│   ├── phase-1/                    # Phase I specification
│   │   ├── spec.md                 # Console app requirements
│   │   ├── plan.md                 # Architecture design
│   │   └── tasks.md                # Implementation tasks
│   └── phase-2/                    # Phase II specification (CURRENT)
│       └── spec.md                 # Full-stack web app requirements
│
├── phase1-console/                 # Phase I Implementation (COMPLETE ✅)
│   ├── src/
│   │   └── todo_app/
│   │       ├── models.py           # Task dataclass with Priority enum
│   │       ├── services.py         # TodoService with CRUD operations
│   │       └── cli.py              # Interactive CLI with Rich tables
│   ├── tests/
│   │   ├── test_models.py          # 100% coverage
│   │   └── test_services.py        # 97% coverage
│   ├── pyproject.toml              # UV dependencies
│   └── README.md                   # Phase I documentation
│
├── phase2-fullstack/               # Phase II Implementation (COMPLETE ✅)
│   ├── frontend/                   # Next.js 16+ (App Router)
│   │   ├── app/                    # App Router pages
│   │   ├── components/             # React components
│   │   ├── lib/                    # API client, utilities
│   │   └── types/                  # TypeScript interfaces
│   └── backend/                    # FastAPI + SQLModel
│       ├── app/
│       │   ├── models/             # SQLModel database models
│       │   ├── routers/            # API endpoints
│       │   ├── schemas/            # Pydantic request/response schemas
│       │   └── dependencies/       # Auth, database dependencies
│       ├── alembic/                # Database migrations
│       └── tests/                  # Pytest test suite
│
├── phase3-chatbot/                 # Phase III Implementation (CURRENT)
│   ├── frontend/                   # Next.js 16.1 (App Router, Turbopack)
│   │   ├── app/                    # App Router pages + API proxies
│   │   ├── components/             # ChatInterface, Navigation
│   │   ├── context/                # Auth & Theme context
│   │   ├── lib/                    # API clients
│   │   └── types/                  # TypeScript interfaces
│   └── backend/                    # FastAPI + SQLModel + OpenAI
│       ├── src/
│       │   ├── api/                # Chat, auth, todos, MCP endpoints
│       │   ├── models/             # SQLModel database models
│       │   ├── services/           # AgentRunner, ChatService, MCP
│       │   ├── tools/              # MCP todo tools
│       │   └── dependencies/       # Auth middleware
│       ├── alembic/                # Database migrations
│       └── tests/                  # Pytest test suite
│
├── .claude/
│   ├── agents/                     # Reusable Intelligence (Phase I & II)
│   │   ├── hackathon-cli-builder.md           # Phase I agent
│   │   ├── hackathon-nextjs-builder.md        # Phase II frontend
│   │   ├── hackathon-fastapi-master.md        # Phase II backend
│   │   ├── hackathon-db-architect.md          # Phase II database
│   │   └── hackathon-auth-specialist.md       # Phase II auth
│   └── skills/                     # Auto-triggered workflows
│       ├── nextjs-ui-generator/
│       ├── fastapi-endpoint-builder/
│       ├── sqlmodel-db-designer/
│       ├── better-auth-setup/
│       └── fullstack-consistency-checker/
│
├── .specify/                       # SDD-RI templates and scripts
│   ├── memory/
│   │   └── constitution.md         # Project standards
│   ├── templates/                  # Spec, plan, task templates
│   └── scripts/                    # Automation scripts
│
├── history/                        # Development records
│   ├── prompts/                    # PHR (Prompt History Records)
│   └── adr/                        # Architectural Decision Records
│
├── Constitution.md                 # Project constitution (symlink)
├── CLAUDE.md                       # AI agent instructions
└── README.md                       # This file
```

### Phase Status

| Phase | Status | Location | Tech Stack | Features |
|-------|--------|----------|------------|----------|
| **Phase I** | ✅ Complete | `phase1-console/` | Python 3.13, Rich, UV | Console CLI with priorities, tags, search, filter, sort |
| **Phase II** | ✅ Complete | `phase2-fullstack/` | Next.js, FastAPI, SQLModel, Neon | Multi-user web app with JWT auth, REST API, PostgreSQL |
| **Phase III** | ✅ Complete | `phase3-chatbot/` | Next.js 16.1, FastAPI, OpenAI, MCP | AI chatbot, natural language task management, MCP tools |

### Key Directories

- **`specs/`** - All feature specifications and architectural plans following SDD methodology
- **`phase1-console/`** - Complete Phase I console application
- **`phase2-fullstack/`** - Complete Phase II full-stack web application
- **`phase3-chatbot/`** - Phase III AI chatbot integration (current)
- **`.claude/`** - Reusable Intelligence: agents and skills
- **`.specify/`** - SDD-RI framework templates and automation scripts

---

## Phase I: Console Application (COMPLETE ✅)

### Features

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

### Architecture - Three-Layer Design
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

See the [Project Structure](#project-structure) section above for complete directory layout.

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

---

## Phase II: Full-Stack Web Application (COMPLETE ✅)

### Overview

Phase II evolves the console application into a production-ready full-stack web application with:
- **Multi-user support** with JWT authentication
- **Persistent storage** using Neon Serverless PostgreSQL
- **Modern web UI** with Next.js 16+ (App Router)
- **RESTful API** with FastAPI and SQLModel
- **Professional deployment** on Vercel (frontend) and Railway/Render (backend)

### Technology Stack

**Frontend**:
- Next.js 16+ (App Router)
- TypeScript (strict mode)
- Tailwind CSS 4+
- React Hook Form + Zod validation
- React Testing Library + Jest

**Backend**:
- FastAPI 0.100+
- SQLModel (SQLAlchemy + Pydantic)
- Python 3.11+
- Pytest with 80%+ coverage
- Alembic migrations

**Database**:
- Neon Serverless PostgreSQL
- SSL-required connections
- Auto-scaling compute
- Daily backups

**Authentication**:
- Better Auth with JWT
- Bcrypt password hashing (12+ rounds)
- Token-based sessions (30-min expiry)
- User isolation enforced at database level

### Features (All Basic + Intermediate)

**Authentication** (Phase II New):
- ✅ User registration with email/password
- ✅ JWT-based login with rate limiting
- ✅ Protected routes (frontend + backend)
- ✅ Token refresh handling

**Task Management** (Enhanced from Phase I):
- ✅ Add tasks (with title, description, priority, tags)
- ✅ View tasks (responsive table/card layout)
- ✅ Update tasks (inline editing)
- ✅ Delete tasks (with confirmation)
- ✅ Mark complete/incomplete (toggle)
- ✅ Search (by title, case-insensitive)
- ✅ Filter (by status, priority, tags)
- ✅ Sort (by date, priority, title)
- ✅ Pagination (20 items per page)

**Multi-User Features** (Phase II New):
- ✅ User isolation (users see only their tasks)
- ✅ Concurrent user support (100+ users)
- ✅ Per-user task limits (10,000 tasks)

### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Create new user account |
| POST | `/auth/login` | No | Login and receive JWT token |
| GET | `/todos` | Yes | Get user's todos (with filters) |
| POST | `/todos` | Yes | Create new todo |
| GET | `/todos/{id}` | Yes | Get single todo by ID |
| PUT | `/todos/{id}` | Yes | Update todo |
| DELETE | `/todos/{id}` | Yes | Delete todo |
| POST | `/todos/{id}/toggle` | Yes | Toggle completion status |

### Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│  Frontend (Vercel)                                  │
│  - Next.js App Router                               │
│  - Static + Server Components                       │
│  - Responsive UI (320px - 1920px+)                  │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS (JWT in Authorization header)
┌────────────────────▼────────────────────────────────┐
│  Backend API (Railway/Render)                       │
│  - FastAPI REST endpoints                           │
│  - JWT authentication middleware                    │
│  - SQLModel ORM                                     │
└────────────────────┬────────────────────────────────┘
                     │ PostgreSQL (SSL required)
┌────────────────────▼────────────────────────────────┐
│  Database (Neon PostgreSQL)                         │
│  - User isolation with foreign keys                 │
│  - Indexed queries for performance                  │
│  - Auto-scaling serverless compute                  │
└─────────────────────────────────────────────────────┘
```

See `phase2-fullstack/README.md` for detailed documentation.

---

## Phase III: AI Chatbot Integration (COMPLETE ✅)

### Overview

Phase III adds an AI-powered chatbot that lets users manage todos through natural language commands, built on OpenAI Chat Completions API with function calling and MCP tool orchestration.

### Technology Stack

**Frontend**: Next.js 16.1 (App Router, Turbopack), TypeScript, Tailwind CSS
**Backend**: FastAPI, SQLModel, OpenAI Chat Completions API, MCP
**Database**: PostgreSQL (Neon Serverless)
**Auth**: JWT with httpOnly cookies via Next.js API proxy

### Features

- Natural language task management (create, list, complete, update, delete)
- Instant greeting/help detection (zero latency, no API call)
- OpenAI function calling for intent parsing (single API call)
- Keyword-based fallback when OpenAI is unavailable
- Conversation history with context
- 7 MCP tools for task operations
- Cookie-based authentication via Next.js API proxy
- Audit logging for all operations

### Chat Commands

| Command | Example |
|---------|---------|
| Create task | "Add a task to buy groceries" |
| List tasks | "Show my tasks" |
| Complete task | "Mark task 3 as done" |
| Update task | "Update task 5 title to Review PR" |
| Delete task | "Delete task 2" |
| Help | "What can you do?" |

See `phase3-chatbot/README.md` for detailed documentation.

---

## Contributing

This is a hackathon submission project. For questions or suggestions:
- GitHub: [@khawajanaqeeb](https://github.com/khawajanaqeeb)
- Repository: [Q4-hackathon2-todo](https://github.com/khawajanaqeeb/Q4-hackathon2-todo)

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with **Claude Code** by Anthropic
- Powered by **SDD-RI** (Spec-Driven Development with Reusable Intelligence) methodology
- Phase I: **hackathon-cli-builder** agent
- Phase II: 5 specialized agents (Next.js, FastAPI, Database, Auth, Testing)
- Phase II: 5 auto-triggered skills (UI Generator, Endpoint Builder, DB Designer, Auth Setup, Consistency Checker)

---

## Project Timeline

| Phase | Submission | Target | Status |
|-------|------------|--------|--------|
| **Phase I** | December 2025 | Basic + Intermediate Features | ✅ Complete |
| **Phase II** | January 2026 | Full-Stack Web Application | ✅ Complete |
| **Phase III** | February 2026 | AI Chatbot Integration | ✅ Complete |

**Repository**: https://github.com/khawajanaqeeb/Q4-hackathon2-todo
