# Phase II Architectural Plan: Todo Full-Stack Web Application

**Feature**: Full-Stack Web Application
**Phase**: Phase II of Hackathon II Evolution
**Created**: 2026-01-01
**Status**: Planning Complete
**Branch**: `001-fullstack-web-app`
**Repository**: https://github.com/khawajanaqeeb/Q4-hackathon2-todo

---

## Overview

### Phase II Goals

Phase II transforms the Phase I console application into a production-ready full-stack web application with:

**Evolution from Phase I**:
- **Storage**: In-memory Python lists → Persistent PostgreSQL database (Neon)
- **Interface**: CLI console → Responsive web UI (Next.js)
- **Users**: Single-user → Multi-user with authentication (JWT)
- **Deployment**: Local only → Cloud deployment (Vercel + Railway + Neon)
- **Features**: All Basic + Intermediate features (Add, View, Update, Delete, Mark Complete, Priorities, Tags, Search, Filter, Sort)

**Key Objectives**:
1. Implement multi-user authentication and user isolation
2. Migrate from in-memory storage to PostgreSQL with SQLModel ORM
3. Build responsive web UI using Next.js 16+ App Router
4. Create RESTful API with FastAPI
5. Deploy to production (Vercel, Railway/Render, Neon)
6. Achieve 80%+ backend coverage, 70%+ frontend coverage

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  USER BROWSER                                               │
│  - Mobile (320px+), Tablet (768px+), Desktop (1024px+)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (Vercel)                                          │
│  Next.js 16+ App Router                                     │
│  - /login, /register pages (public)                         │
│  - /dashboard page (protected, JWT required)                │
│  - React components (TaskTable, AddTaskForm, FilterBar)     │
│  - Tailwind CSS styling                                     │
│  - TypeScript strict mode                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API calls
                       │ Authorization: Bearer <JWT>
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND API (Railway/Render)                               │
│  FastAPI + SQLModel                                         │
│  - /auth/register, /auth/login (no auth)                    │
│  - /todos/* endpoints (JWT required)                        │
│  - JWT authentication middleware                            │
│  - Dependency injection (get_current_user, get_session)     │
│  - Pydantic validation                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │ PostgreSQL (SSL required)
                       │ Connection pooling
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  DATABASE (Neon PostgreSQL)                                 │
│  - users table (id, email, hashed_password, name)           │
│  - todos table (id, user_id FK, title, description, ...)    │
│  - Indexes on user_id, completed, priority, created_at      │
│  - User isolation enforced via foreign key + queries        │
│  - Alembic migrations for schema management                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

**1. Monorepo with Phase Separation**:
- Use `phase2-fullstack/` directory for all Phase II code
- Separate `frontend/` and `backend/` subdirectories
- Keeps Phase I code intact in `phase1-console/` (no modifications)

**Rationale**: Enables independent evolution of phases, maintains clear history, allows running both phases simultaneously for comparison.

**2. User Isolation via Database Foreign Keys**:
- Every task has `user_id` foreign key to `users.id`
- All task queries filter by `current_user.id` automatically
- Backend enforces isolation; frontend trusts backend

**Rationale**: Security at database level prevents data leaks, simplifies frontend logic, enables future multi-tenancy.

**3. JWT Authentication (Better Auth)**:
- Stateless tokens (no server-side session storage)
- 30-minute expiry with refresh capability
- Tokens stored in localStorage (frontend)
- Bcrypt password hashing (cost factor 12)

**Rationale**: Scalable (stateless), industry-standard, works with serverless deployment, supports future mobile apps.

**4. SQLModel ORM**:
- Combines SQLAlchemy (ORM) + Pydantic (validation)
- Single model definition for database + API schemas
- Type-safe queries with Python type hints

**Rationale**: Reduces code duplication, leverages Pydantic for FastAPI, maintains type safety from database to API.

**5. Next.js App Router (not Pages Router)**:
- Server Components by default
- Client Components only when needed (forms, interactivity)
- File-based routing in `app/` directory

**Rationale**: Latest Next.js pattern, better performance with Server Components, simpler data fetching, future-proof.

**6. Neon Serverless PostgreSQL**:
- Auto-scaling compute (suspend when idle)
- Branch-based development (Git-like)
- Built-in connection pooling

**Rationale**: Free tier sufficient for development, serverless cost model, integrates with Railway/Vercel, production-ready.

---

## Technology Stack & Dependencies

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16+ | React framework with App Router |
| **React** | 19+ | UI library (Server + Client Components) |
| **TypeScript** | 5.3+ | Type-safe JavaScript |
| **Tailwind CSS** | 4+ | Utility-first styling |
| **React Hook Form** | 7+ | Form state management |
| **Zod** | 3+ | Schema validation |
| **React Hot Toast** | 2+ | Toast notifications |
| **Heroicons** | 2+ | Icon library |
| **Jest** | 29+ | Testing framework |
| **React Testing Library** | 14+ | Component testing |
| **Playwright** | 1.40+ | E2E testing |

**Frontend Dependencies (`package.json`)**:
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^4.0.0",
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.0",
    "react-hot-toast": "^2.4.1",
    "@heroicons/react": "^2.1.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.1.0",
    "@playwright/test": "^1.40.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0"
  }
}
```

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.100+ | Async web framework |
| **SQLModel** | 0.0.14+ | ORM (SQLAlchemy + Pydantic) |
| **Pydantic** | 2.5+ | Data validation |
| **Uvicorn** | 0.25+ | ASGI server |
| **Alembic** | 1.13+ | Database migrations |
| **python-jose** | 3.3+ | JWT tokens |
| **passlib** | 1.7+ | Password hashing (bcrypt) |
| **psycopg2-binary** | 2.9+ | PostgreSQL driver |
| **pytest** | 7.4+ | Testing framework |
| **pytest-asyncio** | 0.23+ | Async test support |
| **pytest-cov** | 4.1+ | Coverage reporting |

**Backend Dependencies (`requirements.txt`)**:
```
fastapi==0.100.0
sqlmodel==0.0.14
pydantic==2.5.0
uvicorn[standard]==0.25.0
alembic==1.13.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
psycopg2-binary==2.9.9
pytest==7.4.3
pytest-asyncio==0.23.0
pytest-cov==4.1.0
httpx==0.26.0
```

### Database

| Component | Details |
|-----------|---------|
| **Database** | Neon Serverless PostgreSQL |
| **Version** | PostgreSQL 16+ |
| **Connection** | SSL required, connection pooling |
| **Features** | Auto-scaling, branching, point-in-time recovery |

### Deployment

| Service | Purpose | URL Format |
|---------|---------|-----------|
| **Vercel** | Frontend hosting | `https://your-app.vercel.app` |
| **Railway** or **Render** | Backend API hosting | `https://your-api.railway.app` |
| **Neon** | PostgreSQL database | `postgresql://user:pass@ep-xxx.neon.tech/db` |

### Environment Variables

**Frontend (`.env.local`)**:
```bash
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

**Backend (`.env`)**:
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require
SECRET_KEY=<256-bit-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
CORS_ORIGINS=https://your-app.vercel.app
```

---

## Project Structure

```
Q4-hackathon2-todo/
├── specs/
│   ├── phase-1/                           # Phase I specifications (unchanged)
│   │   ├── spec.md
│   │   ├── plan.md
│   │   └── tasks.md
│   └── phase-2/                           # Phase II specifications (current)
│       ├── spec.md                        # Requirements (1,526 lines, 96 requirements)
│       ├── plan.md                        # This file
│       └── tasks.md                       # Generated by /sp.tasks
│
├── phase1-console/                        # Phase I implementation (unchanged)
│   ├── src/todo_app/
│   ├── tests/
│   └── pyproject.toml
│
├── phase2-fullstack/                      # Phase II implementation (NEW)
│   ├── frontend/                          # Next.js application
│   │   ├── app/
│   │   │   ├── layout.tsx                 # Root layout
│   │   │   ├── page.tsx                   # Home (redirects to /dashboard or /login)
│   │   │   ├── login/
│   │   │   │   └── page.tsx               # Login page
│   │   │   ├── register/
│   │   │   │   └── page.tsx               # Registration page
│   │   │   └── dashboard/
│   │   │       ├── layout.tsx             # Dashboard layout (protected)
│   │   │       └── page.tsx               # Todo list page
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx          # Login form component
│   │   │   │   └── RegisterForm.tsx       # Registration form component
│   │   │   ├── todos/
│   │   │   │   ├── TodoTable.tsx          # Desktop table view
│   │   │   │   ├── TodoCard.tsx           # Mobile card view
│   │   │   │   ├── AddTaskForm.tsx        # Add task modal/form
│   │   │   │   ├── EditTaskForm.tsx       # Edit task form
│   │   │   │   ├── FilterBar.tsx          # Search/filter controls
│   │   │   │   └── TodoRow.tsx            # Single todo row
│   │   │   └── ui/
│   │   │       ├── Button.tsx             # Reusable button
│   │   │       ├── Input.tsx              # Reusable input
│   │   │       ├── Modal.tsx              # Modal component
│   │   │       ├── Toast.tsx              # Toast notification
│   │   │       └── Spinner.tsx            # Loading spinner
│   │   ├── lib/
│   │   │   ├── api.ts                     # API client functions
│   │   │   ├── auth.ts                    # Auth utilities (getToken, logout)
│   │   │   └── utils.ts                   # Helper functions (cn, formatDate)
│   │   ├── types/
│   │   │   ├── user.ts                    # User TypeScript interfaces
│   │   │   └── todo.ts                    # Todo TypeScript interfaces
│   │   ├── context/
│   │   │   └── AuthContext.tsx            # Global auth state
│   │   ├── middleware.ts                  # Route protection middleware
│   │   ├── tailwind.config.ts             # Tailwind configuration
│   │   ├── next.config.js                 # Next.js configuration
│   │   ├── package.json                   # NPM dependencies
│   │   ├── tsconfig.json                  # TypeScript configuration
│   │   └── .env.local                     # Environment variables
│   │
│   └── backend/                           # FastAPI application
│       ├── app/
│       │   ├── main.py                    # FastAPI app entry point
│       │   ├── config.py                  # Settings (DATABASE_URL, SECRET_KEY)
│       │   ├── database.py                # Engine, session, create_db_and_tables
│       │   ├── models/
│       │   │   ├── __init__.py
│       │   │   ├── user.py                # User SQLModel
│       │   │   └── todo.py                # Todo SQLModel
│       │   ├── schemas/
│       │   │   ├── __init__.py
│       │   │   ├── user.py                # UserCreate, UserResponse Pydantic
│       │   │   └── todo.py                # TodoCreate, TodoUpdate, TodoResponse
│       │   ├── routers/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py                # /auth/register, /auth/login
│       │   │   └── todos.py               # /todos CRUD endpoints
│       │   ├── dependencies/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py                # get_current_user dependency
│       │   │   └── database.py            # get_session dependency
│       │   └── utils/
│       │       └── security.py            # hash_password, verify_password, create_token
│       ├── alembic/
│       │   ├── env.py                     # Alembic configuration
│       │   └── versions/
│       │       └── 001_create_tables.py   # Initial migration
│       ├── tests/
│       │   ├── conftest.py                # Pytest fixtures
│       │   ├── test_auth.py               # Authentication tests
│       │   └── test_todos.py              # Todo CRUD tests
│       ├── scripts/
│       │   └── seed.py                    # Seed database script
│       ├── requirements.txt               # Python dependencies
│       ├── .env                           # Environment variables
│       └── alembic.ini                    # Alembic config file
│
├── .claude/
│   ├── agents/                            # Reusable Intelligence
│   │   ├── hackathon-cli-builder.md       # Phase I agent
│   │   ├── hackathon-nextjs-builder.md    # Phase II frontend agent
│   │   ├── hackathon-fastapi-master.md    # Phase II backend agent
│   │   ├── hackathon-db-architect.md      # Phase II database agent
│   │   └── hackathon-auth-specialist.md   # Phase II auth agent
│   └── skills/                            # Auto-triggered workflows
│       ├── nextjs-ui-generator/
│       ├── fastapi-endpoint-builder/
│       ├── sqlmodel-db-designer/
│       ├── better-auth-setup/
│       └── fullstack-consistency-checker/
│
├── .specify/                              # SDD-RI framework
│   ├── memory/
│   │   └── constitution.md                # Project standards
│   ├── templates/                         # Spec, plan, task templates
│   └── scripts/                           # Automation scripts
│
├── history/
│   ├── prompts/                           # Prompt History Records
│   └── adr/                               # Architectural Decision Records
│
├── Constitution.md                        # Project constitution (symlink)
├── CLAUDE.md                              # AI agent instructions
└── README.md                              # Project README
```

---

## Component Architecture

### Frontend (Next.js 16+ App Router)

#### App Router Structure

**Pages (Routes)**:
```
app/
├── layout.tsx                             # Root layout (metadata, providers)
├── page.tsx                               # Home page (redirects)
├── login/
│   └── page.tsx                           # Public: Login page
├── register/
│   └── page.tsx                           # Public: Registration page
└── dashboard/
    ├── layout.tsx                         # Protected: Dashboard layout
    └── page.tsx                           # Protected: Todo list page
```

**Middleware (`middleware.ts`)**:
- Protects `/dashboard` routes (requires JWT in cookies)
- Redirects authenticated users away from `/login`, `/register`
- Reads token from `access_token` cookie

**Component Hierarchy**:
```
app/
├── layout.tsx
│   └── AuthContext.Provider              # Global auth state
│       └── Toaster                        # Toast notifications
│
├── login/page.tsx
│   └── LoginForm                          # Form with email/password
│       ├── Input (email)
│       ├── Input (password)
│       └── Button (submit)
│
├── register/page.tsx
│   └── RegisterForm                       # Form with name/email/password
│       ├── Input (name)
│       ├── Input (email)
│       ├── Input (password)
│       ├── Input (confirm password)
│       └── Button (submit)
│
└── dashboard/page.tsx
    ├── Button (Add Task)                  # Opens AddTaskForm modal
    ├── FilterBar                          # Search + filters
    │   ├── Input (search)
    │   ├── Select (status: all/completed/pending)
    │   ├── Select (priority: all/low/medium/high)
    │   └── Button (clear filters)
    ├── TodoTable (desktop)                # Conditional: hidden on mobile
    │   └── TodoRow (for each task)
    │       ├── Checkbox (toggle complete)
    │       ├── Text (title, description, priority, tags)
    │       ├── Button (edit) → EditTaskForm
    │       └── Button (delete) → Confirmation modal
    ├── TodoCard[] (mobile)                # Conditional: hidden on desktop
    │   └── Similar to TodoRow but stacked
    ├── Pagination                         # Next/Prev buttons
    └── Modal (AddTaskForm, EditTaskForm, Delete Confirmation)
```

#### Key Components

**1. LoginForm.tsx**
- **Props**: `{ onSubmit: (data: LoginFormData) => Promise<void> }`
- **State**: `email`, `password`, `error`, `loading`
- **Validation**: React Hook Form + Zod schema
- **Actions**: Call `/auth/login` → Store token → Redirect to `/dashboard`

**2. RegisterForm.tsx**
- **Props**: `{ onSubmit: (data: RegisterFormData) => Promise<void> }`
- **State**: `name`, `email`, `password`, `confirmPassword`, `error`, `loading`
- **Validation**: Passwords match, email format, min 8 chars
- **Actions**: Call `/auth/register` → Redirect to `/login`

**3. TodoTable.tsx**
- **Props**: `{ todos: Todo[], onEdit, onDelete, onToggle }`
- **Renders**: HTML `<table>` with responsive columns
- **Columns**: Checkbox, Title, Description (truncated), Priority (color-coded), Tags (chips), Actions
- **Mobile**: Hidden via `hidden md:block` Tailwind class

**4. TodoCard.tsx**
- **Props**: `{ todo: Todo, onEdit, onDelete, onToggle }`
- **Renders**: Card layout with stacked fields
- **Desktop**: Hidden via `block md:hidden` Tailwind class

**5. AddTaskForm.tsx**
- **Props**: `{ isOpen: boolean, onClose: () => void, onSubmit: (data: TodoFormData) => Promise<void> }`
- **Fields**: Title (required), Description (optional), Priority (dropdown), Tags (comma-separated input)
- **Validation**: Zod schema (title 1-500 chars, description max 5000 chars, max 10 tags)

**6. FilterBar.tsx**
- **Props**: `{ onSearchChange, onStatusChange, onPriorityChange, onTagsChange }`
- **State**: `search`, `status`, `priority`, `tags`
- **Debounce**: Search input debounced 300ms
- **URL Sync**: Updates URL query params for shareable links

#### State Management Strategy

**Global State (React Context)**:
- **AuthContext**: `{ user, token, login, logout, register }`
- Provides user info to all components
- Handles token storage in localStorage

**Local State (React hooks)**:
- **Forms**: React Hook Form for form state + validation
- **Lists**: `useState` for todos array, filters, pagination
- **Modals**: `useState` for modal open/close state

**Server State (API calls)**:
- **Fetching**: `useEffect` with loading/error states
- **Mutations**: Optimistic updates (update UI immediately, revert on error)

#### Responsive Design

**Breakpoints (Tailwind)**:
- **Mobile**: `< 768px` (default)
- **Tablet**: `md:` (768px - 1023px)
- **Desktop**: `lg:` (1024px+)

**Adaptive Components**:
- **TodoTable**: Desktop only (`hidden md:block`)
- **TodoCard**: Mobile/Tablet only (`block md:hidden`)
- **FilterBar**: Hamburger menu on mobile, sidebar on desktop

---

### Backend (FastAPI + SQLModel)

#### Application Structure

**Main Entry Point (`main.py`)**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, todos
from app.database import create_db_and_tables

app = FastAPI(
    title="Todo API",
    version="2.0.0",
    description="Phase II Full-Stack Todo Application API"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(todos.router, prefix="/todos", tags=["todos"])

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Todo API v2.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

#### Routers

**1. Auth Router (`routers/auth.py`)**:
```python
router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    # Check if email exists
    # Hash password with bcrypt
    # Create user in database
    # Return user data (no password)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # Find user by email
    # Verify password with bcrypt
    # Generate JWT token
    # Return access_token and token_type
```

**2. Todos Router (`routers/todos.py`)**:
```python
router = APIRouter()

@router.post("/", response_model=TodoResponse, status_code=201)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Create todo with user_id = current_user.id
    # Save to database
    # Return todo

@router.get("/", response_model=List[TodoResponse])
async def get_todos(
    skip: int = 0,
    limit: int = 20,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Query todos WHERE user_id = current_user.id
    # Apply filters (completed, priority, search)
    # Apply pagination (skip, limit)
    # Return list of todos

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get todo by id
    # Verify user_id == current_user.id (404 if not)
    # Return todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get todo by id
    # Verify ownership
    # Update fields (only provided fields)
    # Update updated_at timestamp
    # Return updated todo

@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get todo by id
    # Verify ownership
    # Delete from database
    # Return 204 No Content

@router.post("/{todo_id}/toggle", response_model=TodoResponse)
async def toggle_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get todo by id
    # Verify ownership
    # Toggle completed field
    # Update updated_at timestamp
    # Return updated todo
```

#### Dependency Injection

**Authentication Dependency (`dependencies/auth.py`)**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.utils.security import decode_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

**Database Session Dependency (`dependencies/database.py`)**:
```python
from sqlmodel import Session
from app.database import engine

def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
```

---

### Database Layer

#### SQLModel Models

**User Model (`models/user.py`)**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=60)
    name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Todo Model (`models/todo.py`)**:
```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)  # User isolation
    title: str = Field(max_length=500, index=True)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False, index=True)
    priority: Priority = Field(default=Priority.MEDIUM, index=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Database Connection (`database.py`)

```python
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,        # Verify connections before use
    pool_size=10,              # Connection pool size
    max_overflow=20,           # Max connections beyond pool_size
    pool_recycle=3600,         # Recycle connections after 1 hour
    connect_args={
        "sslmode": "require",  # Required for Neon
        "connect_timeout": 10,
    },
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

#### Alembic Migrations

**Initial Migration (`alembic/versions/001_create_tables.py`)**:
```python
def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=60), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=5000), nullable=True),
        sa.Column('completed', sa.Boolean(), server_default='false'),
        sa.Column('priority', sa.String(length=10), server_default='medium'),
        sa.Column('tags', postgresql.JSON(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    # Indexes for performance
    op.create_index('ix_todos_user_id', 'todos', ['user_id'])
    op.create_index('ix_todos_completed', 'todos', ['completed'])
    op.create_index('ix_todos_priority', 'todos', ['priority'])
    op.create_index('ix_todos_created_at', 'todos', ['created_at'])
    op.create_index('ix_todos_title', 'todos', ['title'])

def downgrade():
    op.drop_table('todos')
    op.drop_table('users')
```

---

## Data Flow & API Contracts

### Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  1. USER ACTION                                             │
│  User clicks "Add Task" button on /dashboard               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. FRONTEND (Next.js)                                      │
│  - AddTaskForm.tsx component opens                          │
│  - User fills: title, description, priority, tags           │
│  - Form validation with Zod                                 │
│  - On submit: calls lib/api.ts → createTodo(data)           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST /todos
                       │ Headers: {
                       │   Authorization: "Bearer <JWT>",
                       │   Content-Type: "application/json"
                       │ }
                       │ Body: {
                       │   title: "Buy groceries",
                       │   description: "Milk, eggs, bread",
                       │   priority: "high",
                       │   tags: ["shopping", "urgent"]
                       │ }
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. BACKEND API (FastAPI)                                   │
│  - Request hits @router.post("/todos")                      │
│  - Dependencies injected:                                   │
│    * get_current_user → validates JWT → extracts user_id    │
│    * get_session → provides database session                │
│  - Pydantic validates request body → TodoCreate schema      │
│  - Creates Todo object with user_id = current_user.id       │
│  - session.add(todo), session.commit(), session.refresh()   │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQL: INSERT INTO todos (user_id, title, ...)
                       │      VALUES (1, 'Buy groceries', ...)
                       │      RETURNING *;
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. DATABASE (Neon PostgreSQL)                              │
│  - Validates foreign key (user_id exists in users table)    │
│  - Inserts row into todos table                             │
│  - Returns inserted row with auto-generated id, timestamps  │
└──────────────────────┬──────────────────────────────────────┘
                       │ Result: {
                       │   id: 42,
                       │   user_id: 1,
                       │   title: "Buy groceries",
                       │   description: "Milk, eggs, bread",
                       │   completed: false,
                       │   priority: "high",
                       │   tags: ["shopping", "urgent"],
                       │   created_at: "2026-01-01T12:00:00Z",
                       │   updated_at: "2026-01-01T12:00:00Z"
                       │ }
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  5. BACKEND RESPONSE                                        │
│  - SQLModel object converted to Pydantic TodoResponse       │
│  - Serialized to JSON                                       │
│  - HTTP 201 Created response                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP 201 Created
                       │ Body: { id: 42, title: "Buy groceries", ... }
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  6. FRONTEND UPDATE                                         │
│  - lib/api.ts receives response                             │
│  - Updates local state (adds new todo to todos array)       │
│  - Closes AddTaskForm modal                                 │
│  - TodoTable/TodoCard re-renders with new task              │
│  - Shows success toast: "Task added successfully"           │
└─────────────────────────────────────────────────────────────┘
```

### API Endpoints Contract

| Method | Endpoint | Auth Required | Request Body | Response | Status Codes |
|--------|----------|---------------|--------------|----------|--------------|
| **POST** | `/auth/register` | No | `{ email, password, name }` | `{ id, email, name, created_at }` | 201, 400 (email exists) |
| **POST** | `/auth/login` | No | `{ email, password }` | `{ access_token, token_type }` | 200, 401 (invalid creds) |
| **GET** | `/todos` | Yes | Query: `skip, limit, completed, priority, search, sort_by, sort_order` | `[ { id, title, ... }, ... ]` | 200, 401 |
| **POST** | `/todos` | Yes | `{ title, description?, priority?, tags? }` | `{ id, title, ..., user_id }` | 201, 400, 401 |
| **GET** | `/todos/{id}` | Yes | - | `{ id, title, ..., user_id }` | 200, 404, 401 |
| **PUT** | `/todos/{id}` | Yes | `{ title?, description?, priority?, tags?, completed? }` | `{ id, title, ..., updated_at }` | 200, 404, 400, 401 |
| **DELETE** | `/todos/{id}` | Yes | - | `null` | 204, 404, 401 |
| **POST** | `/todos/{id}/toggle` | Yes | - | `{ id, completed, ... }` | 200, 404, 401 |

### Pydantic Schemas

**Request Schemas**:
```python
# schemas/user.py
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(max_length=255)

# schemas/todo.py
class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    tags: list[str] = Field(default_factory=list, max_items=10)

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    tags: Optional[list[str]] = Field(None, max_items=10)
    completed: Optional[bool] = None
```

**Response Schemas**:
```python
# schemas/user.py
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# schemas/todo.py
class TodoResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## Authentication Strategy

### Better Auth with JWT

**JWT Token Structure**:
```json
{
  "sub": 123,                   // user_id (subject)
  "email": "user@example.com",
  "exp": 1704153600,            // Expiry timestamp (30 min from iat)
  "iat": 1704150000             // Issued at timestamp
}
```

**Token Generation (`utils/security.py`)**:
```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # Bcrypt with cost factor 12

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```

### Authentication Flow

**1. Registration Flow**:
```
User → /register page
      → Fills form (name, email, password)
      → Frontend validates (email format, password length)
      → POST /auth/register
            → Backend checks if email exists (400 if duplicate)
            → Hashes password with bcrypt
            → Creates user in database
            → Returns user data (no password)
      → Redirects to /login with success message
```

**2. Login Flow**:
```
User → /login page
      → Fills form (email, password)
      → POST /auth/login
            → Backend finds user by email (401 if not found)
            → Verifies password with bcrypt (401 if wrong)
            → Generates JWT token with user_id
            → Returns { access_token, token_type: "bearer" }
      → Frontend stores token in localStorage
      → Sets cookie for middleware (optional)
      → Redirects to /dashboard
```

**3. Protected Request Flow**:
```
User → /dashboard (protected route)
      → Middleware checks for token in cookies
      → If no token → redirect to /login
      → If token exists → allow access
      → Page loads → fetches todos via API

GET /todos
      → Frontend includes: Authorization: Bearer <token>
      → Backend extracts token from header
      → Validates token (signature, expiry)
      → Extracts user_id from payload
      → Queries User table (401 if not found/inactive)
      → Returns current_user to endpoint handler
      → Endpoint queries todos WHERE user_id = current_user.id
```

**4. Logout Flow**:
```
User → Clicks "Logout" button
      → Frontend clears localStorage (token)
      → Clears cookies
      → Redirects to /login
```

### Protected Routes

**Frontend Middleware (`middleware.ts`)**:
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');

  // Protected routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // Auth routes (redirect if already logged in)
  if (['/login', '/register'].includes(request.nextUrl.pathname)) {
    if (token) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/register'],
};
```

**Backend Protected Endpoints**:
```python
# All /todos/* endpoints require authentication
@router.get("/todos")
async def get_todos(
    current_user: User = Depends(get_current_user),  # JWT required
    session: Session = Depends(get_session)
):
    # User is authenticated if we reach here
    # current_user.id is available for queries
    query = select(Todo).where(Todo.user_id == current_user.id)
    return session.exec(query).all()
```

---

## Reusable Intelligence Integration

### Phase II Agents

The following agents are available in `.claude/agents/` and will be used during `/sp.implement`:

**1. hackathon-nextjs-builder.md** (Frontend Expert):
- **Triggers**: "Create login page", "Build dashboard UI", "Add task form"
- **Capabilities**: Next.js App Router, React components, Tailwind CSS, TypeScript
- **Output**: Complete page/component files with proper imports, types, and styling

**2. hackathon-fastapi-master.md** (Backend Expert):
- **Triggers**: "Create auth endpoints", "Build todo CRUD API", "Add search filter"
- **Capabilities**: FastAPI routers, SQLModel queries, dependency injection, JWT auth
- **Output**: Complete router files with Pydantic schemas, error handling, user isolation

**3. hackathon-db-architect.md** (Database Expert):
- **Triggers**: "Design database schema", "Create migrations", "Add indexes"
- **Capabilities**: SQLModel models, Alembic migrations, Neon connection setup
- **Output**: Model files, migration scripts, database.py with connection pooling

**4. hackathon-auth-specialist.md** (Security Expert):
- **Triggers**: "Implement JWT authentication", "Add password hashing", "Protect routes"
- **Capabilities**: Better Auth integration, bcrypt hashing, token generation/validation
- **Output**: auth.py router, security.py utilities, middleware, protected endpoints

**5. hackathon-integration-tester.md** (Testing Expert):
- **Triggers**: "Write tests for auth", "Test user isolation", "Add E2E tests"
- **Capabilities**: pytest (backend), Jest (frontend), Playwright (E2E), coverage reporting
- **Output**: Test files with fixtures, mocks, assertions, coverage >80%/70%

### Phase II Skills (Auto-Triggered)

The following skills in `.claude/skills/` will auto-trigger during implementation:

**1. nextjs-ui-generator**:
- **Auto-triggers**: When task mentions "Create page", "Build component", "Add form"
- **Actions**: Reads design requirements → Generates React component with Tailwind

**2. fastapi-endpoint-builder**:
- **Auto-triggers**: When task mentions "Create endpoint", "Add route", "Implement API"
- **Actions**: Reads API spec → Generates FastAPI router with validation + error handling

**3. sqlmodel-db-designer**:
- **Auto-triggers**: When task mentions "Create model", "Define schema", "Add migration"
- **Actions**: Reads data model → Generates SQLModel class + Alembic migration

**4. better-auth-setup**:
- **Auto-triggers**: When task mentions "Add authentication", "Implement login", "Protect route"
- **Actions**: Reads auth requirements → Generates JWT utils + protected endpoints

**5. fullstack-consistency-checker**:
- **Auto-triggers**: After code generation for frontend + backend
- **Actions**: Validates frontend API calls match backend endpoints, types align

### Example Delegation During /sp.implement

**Task**: "Implement user registration feature"

```
1. Task Parser identifies components needed:
   - Frontend: RegisterForm component
   - Backend: /auth/register endpoint
   - Database: users table (already exists)

2. Delegate to hackathon-nextjs-builder:
   Input: "Create RegisterForm component in components/auth/RegisterForm.tsx
          - Fields: name, email, password, confirmPassword
          - Validation: Zod schema (email format, password min 8 chars, passwords match)
          - On submit: call /auth/register API
          - Show errors and success messages"
   Output: Complete RegisterForm.tsx file

3. Delegate to hackathon-fastapi-master:
   Input: "Create /auth/register endpoint in routers/auth.py
          - Schema: UserCreate (email, password, name)
          - Check if email exists (400 if duplicate)
          - Hash password with bcrypt
          - Create user in database
          - Return UserResponse (no password)"
   Output: auth.py router with register endpoint

4. Delegate to hackathon-integration-tester:
   Input: "Write tests for user registration
          - Test successful registration
          - Test duplicate email (400)
          - Test weak password (400)
          - Test frontend component rendering and submission"
   Output: test_auth.py (backend) and RegisterForm.test.tsx (frontend)

5. Auto-trigger fullstack-consistency-checker:
   - Verifies RegisterForm API call matches backend endpoint
   - Checks UserCreate schema matches frontend form data
   - Reports any type mismatches
```

---

## Deployment Plan

### Vercel (Frontend)

**Setup Steps**:
1. Connect GitHub repository to Vercel
2. Configure project settings:
   - **Framework**: Next.js
   - **Root Directory**: `phase2-fullstack/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`
3. Add environment variables:
   - `NEXT_PUBLIC_API_URL` = `https://your-api.railway.app`
4. Deploy from `001-fullstack-web-app` branch
5. Domain: `https://your-app.vercel.app` (free subdomain)

**Automatic Deployments**:
- Every push to `001-fullstack-web-app` triggers new deployment
- Preview deployments for pull requests
- Instant rollback to previous deployments

---

### Railway or Render (Backend)

**Railway Setup Steps**:
1. Connect GitHub repository to Railway
2. Create new project → select `phase2-fullstack/backend` directory
3. Configure build settings:
   - **Builder**: Nixpacks (auto-detects Python)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `DATABASE_URL` = Neon connection string
   - `SECRET_KEY` = Generate with `openssl rand -hex 32`
   - `ALGORITHM` = `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` = `30`
   - `DEBUG` = `false`
   - `CORS_ORIGINS` = `https://your-app.vercel.app`
5. Deploy from `001-fullstack-web-app` branch
6. Domain: `https://your-api.railway.app` (auto-generated)

**Health Check**:
- Railway pings `GET /health` endpoint
- Expects `{ "status": "healthy" }` response
- Restarts container if health check fails

**Render Setup Steps** (Alternative):
1. Create new Web Service
2. Connect GitHub repository
3. Configure:
   - **Root Directory**: `phase2-fullstack/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (same as Railway)
5. Deploy

---

### Neon (Database)

**Setup Steps**:
1. Create Neon account at https://neon.tech
2. Create new project:
   - **Name**: `q4-hackathon-todo`
   - **Region**: Auto (closest to backend)
   - **PostgreSQL Version**: 16
3. Copy connection string:
   - Format: `postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require`
4. Create development branch (optional):
   - Use for testing without affecting production
   - Git-like branching for databases
5. Run migrations:
   ```bash
   # From backend directory
   alembic upgrade head
   ```

**Database Features**:
- **Auto-scaling**: Compute scales to zero when idle (free tier)
- **Branching**: Create database branches for development/staging
- **Backups**: Automatic daily backups (7-day retention on free tier)
- **SSL Required**: All connections must use `sslmode=require`

---

### Environment Variables Summary

**Frontend (`.env.local` → Vercel Environment Variables)**:
```bash
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

**Backend (`.env` → Railway/Render Environment Variables)**:
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require
SECRET_KEY=<256-bit-secret-generated-with-openssl>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
CORS_ORIGINS=https://your-app.vercel.app
```

---

### Local Development Setup

**Option 1: Docker Compose** (Recommended):

Create `docker-compose.yml` in repo root:
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./phase2-fullstack/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./phase2-fullstack/frontend:/app
      - /app/node_modules

  backend:
    build:
      context: ./phase2-fullstack/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/todoapp
      - SECRET_KEY=local-dev-secret-key-not-for-production
      - DEBUG=true
    volumes:
      - ./phase2-fullstack/backend:/app
    depends_on:
      - db

  db:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=todoapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Run Commands**:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

**Option 2: Manual Setup** (without Docker):

**Frontend**:
```bash
cd phase2-fullstack/frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
# Runs on http://localhost:3000
```

**Backend**:
```bash
cd phase2-fullstack/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env with DATABASE_URL (use Neon or local PostgreSQL)
alembic upgrade head  # Run migrations
uvicorn app.main:app --reload --port 8000
# Runs on http://localhost:8000
```

---

## Testing Strategy

### Backend Testing (pytest)

**Target Coverage**: 80%+

**Test Structure** (`tests/`):
```
tests/
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication tests
├── test_todos.py            # Todo CRUD tests
└── test_user_isolation.py   # Security tests
```

**Key Fixtures (`conftest.py`)**:
```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from app.main import app
from app.database import get_session

@pytest.fixture
def client():
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    })
    return response.json()

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

**Example Tests**:
```python
# test_auth.py
def test_register_user(client):
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "securepass123",
        "name": "New User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "hashed_password" not in data  # Never return password

def test_login_valid_credentials(client, test_user):
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# test_todos.py
def test_create_todo_requires_auth(client):
    response = client.post("/todos", json={"title": "Test"})
    assert response.status_code == 401

def test_user_isolation(client, auth_headers, test_user):
    # Create todo for test_user
    response = client.post("/todos", json={"title": "User 1 task"}, headers=auth_headers)
    task_id = response.json()["id"]

    # Create second user
    client.post("/auth/register", json={"email": "user2@example.com", "password": "pass", "name": "User 2"})
    login = client.post("/auth/login", data={"username": "user2@example.com", "password": "pass"})
    user2_token = login.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 tries to access User 1's task
    response = client.get(f"/todos/{task_id}", headers=user2_headers)
    assert response.status_code == 404  # Not found (user isolation)
```

**Run Tests**:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

---

### Frontend Testing (Jest + React Testing Library)

**Target Coverage**: 70%+

**Test Structure**:
```
frontend/
├── __tests__/
│   ├── components/
│   │   ├── LoginForm.test.tsx
│   │   ├── TodoTable.test.tsx
│   │   └── AddTaskForm.test.tsx
│   └── lib/
│       └── api.test.ts
├── jest.config.js
└── jest.setup.js
```

**Example Tests**:
```typescript
// __tests__/components/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginForm from '@/components/auth/LoginForm';

describe('LoginForm', () => {
  it('renders email and password fields', () => {
    render(<LoginForm onSubmit={jest.fn()} />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('validates email format', async () => {
    render(<LoginForm onSubmit={jest.fn()} />);
    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);

    await waitFor(() => {
      expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
    });
  });

  it('calls onSubmit with valid data', async () => {
    const onSubmit = jest.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    fireEvent.click(screen.getByRole('button', { name: /log in/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });
});
```

**Run Tests**:
```bash
# Run all tests
npm run test

# Run with coverage
npm run test -- --coverage

# Watch mode
npm run test -- --watch
```

---

### E2E Testing (Playwright)

**Critical Flows**:
1. User registration and login
2. Create todo → view → edit → mark complete → delete
3. Search and filter todos
4. Responsive behavior (mobile, tablet, desktop)

**Example Test**:
```typescript
// e2e/auth-flow.spec.ts
import { test, expect } from '@playwright/test';

test('complete authentication and todo flow', async ({ page }) => {
  // Register
  await page.goto('http://localhost:3000/register');
  await page.fill('[name="name"]', 'Test User');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123');
  await page.fill('[name="confirmPassword"]', 'SecurePass123');
  await page.click('button[type="submit"]');

  // Should redirect to login
  await expect(page).toHaveURL('http://localhost:3000/login');

  // Login
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123');
  await page.click('button[type="submit"]');

  // Should redirect to dashboard
  await expect(page).toHaveURL('http://localhost:3000/dashboard');

  // Create todo
  await page.click('text=Add Task');
  await page.fill('[name="title"]', 'Buy groceries');
  await page.selectOption('[name="priority"]', 'high');
  await page.click('text=Save');

  // Verify todo appears
  await expect(page.locator('text=Buy groceries')).toBeVisible();

  // Mark complete
  await page.click('[aria-label="Mark complete"]');
  await expect(page.locator('text=Buy groceries')).toHaveClass(/line-through/);

  // Delete
  await page.click('[aria-label="Delete task"]');
  await page.click('text=Confirm');
  await expect(page.locator('text=Buy groceries')).not.toBeVisible();
});
```

**Run E2E Tests**:
```bash
# Install Playwright
npx playwright install

# Run tests
npx playwright test

# Run in UI mode
npx playwright test --ui

# Run specific browser
npx playwright test --project=chromium
```

---

## Implementation Phases

### Phase 0: Setup & Infrastructure (Estimated: 1 day)

**Tasks**:
1. Initialize frontend (Next.js) and backend (FastAPI) projects
2. Configure Neon PostgreSQL database
3. Set up local development environment (docker-compose)
4. Create `.env` files with environment variables
5. Verify build and run locally

**Acceptance Criteria**:
- Frontend runs on http://localhost:3000
- Backend runs on http://localhost:8000
- Database connection successful
- Health check endpoint returns 200

---

### Phase 1: Database & Models (Estimated: 1 day)

**Tasks**:
1. Create SQLModel models (User, Todo)
2. Set up Alembic migrations
3. Run initial migration to create tables
4. Verify schema in Neon dashboard
5. Create seed script for test data

**Acceptance Criteria**:
- `users` and `todos` tables exist in database
- Foreign key relationship enforced
- Indexes created on user_id, completed, priority, created_at
- Seed script populates test data

---

### Phase 2: Backend API (Estimated: 2-3 days)

**Tasks**:
1. Implement `/auth/register` endpoint
2. Implement `/auth/login` endpoint
3. Implement JWT authentication middleware (`get_current_user`)
4. Implement `/todos` CRUD endpoints (create, read, update, delete)
5. Implement `/todos/{id}/toggle` endpoint
6. Add query parameters for search, filter, sort
7. Write backend tests (80%+ coverage)

**Acceptance Criteria**:
- All endpoints return correct responses
- User isolation enforced (users cannot access other users' todos)
- Input validation with Pydantic
- Error handling with proper HTTP status codes
- Tests pass with 80%+ coverage

---

### Phase 3: Frontend UI (Estimated: 3-4 days)

**Tasks**:
1. Create login and registration pages
2. Implement authentication flow (JWT storage, middleware)
3. Create dashboard layout with header
4. Implement TodoTable and TodoCard components
5. Implement AddTaskForm and EditTaskForm components
6. Implement FilterBar with search, status, priority filters
7. Add responsive design (mobile, tablet, desktop)
8. Write frontend tests (70%+ coverage)

**Acceptance Criteria**:
- All pages render correctly
- Forms validate input
- API calls work correctly
- Responsive design works on all screen sizes
- Tests pass with 70%+ coverage

---

### Phase 4: Integration & E2E (Estimated: 1-2 days)

**Tasks**:
1. Test full authentication flow (register → login → dashboard)
2. Test full todo lifecycle (create → edit → mark complete → delete)
3. Test search and filter functionality
4. Test user isolation (multiple users)
5. Write Playwright E2E tests
6. Fix bugs found during testing

**Acceptance Criteria**:
- All E2E tests pass
- No console errors in browser
- User isolation verified
- All features work end-to-end

---

### Phase 5: Deployment (Estimated: 1 day)

**Tasks**:
1. Deploy frontend to Vercel
2. Deploy backend to Railway/Render
3. Configure environment variables
4. Run database migrations on Neon
5. Test production deployment
6. Set up custom domain (optional)

**Acceptance Criteria**:
- Frontend accessible at Vercel URL
- Backend accessible at Railway/Render URL
- Database migrations applied successfully
- All features work in production
- HTTPS enabled

---

## Risk Analysis

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Neon connection timeout** | High | Use connection pooling, pool_pre_ping, retry logic |
| **JWT token expiry UX** | Medium | Implement token refresh, show expiry warning |
| **CORS issues** | Medium | Properly configure CORS_ORIGINS, test cross-origin requests |
| **Database migration conflicts** | Medium | Use Alembic's auto-merge, version control migrations |
| **Vercel/Railway cold starts** | Low | Use health checks, keep-alive pings, serverless optimizations |

### Implementation Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **User isolation bugs** | Critical | Write comprehensive tests for user isolation, code review |
| **Password security** | Critical | Use bcrypt with cost factor 12+, never log passwords |
| **SQL injection** | Critical | Use SQLModel parameterized queries, never raw SQL |
| **XSS attacks** | High | Use React's auto-escaping, validate all inputs |
| **Type mismatches (frontend/backend)** | Medium | Use fullstack-consistency-checker skill, TypeScript strict mode |

---

## Success Criteria

### Technical Metrics

- ✅ Backend test coverage: 80%+
- ✅ Frontend test coverage: 70%+
- ✅ E2E tests: 100% of critical flows
- ✅ API response time: <200ms (p95)
- ✅ Lighthouse performance: 90+
- ✅ Lighthouse accessibility: 95+
- ✅ Zero critical security vulnerabilities

### Functional Metrics

- ✅ All 10 features implemented (registration, login, add, view, search, filter, sort, update, delete, mark complete)
- ✅ User isolation verified (users cannot access other users' data)
- ✅ Responsive design works on mobile, tablet, desktop
- ✅ Production deployment successful (Vercel + Railway + Neon)
- ✅ All acceptance criteria met for each feature

### User Experience Metrics

- ✅ User can register, login, and create first task in <2 minutes
- ✅ Task CRUD operations complete in <3 clicks
- ✅ No blocking bugs in critical flows
- ✅ Error messages clear and actionable
- ✅ Loading states visible during async operations

---

## Next Steps

After this plan is approved:

1. **Run `/sp.tasks`**: Generate atomic, testable task breakdown from this plan
2. **Review and refine tasks**: Ensure all tasks are clear and independently verifiable
3. **Run `/sp.implement`**: Execute tasks using Phase II agents and skills
4. **Iterate**: Test, validate, and fix issues as they arise
5. **Deploy**: Deploy to production (Vercel + Railway + Neon)
6. **Document**: Update README.md with Phase II deployment instructions

---

**Plan Status**: Complete and Ready for Task Breakdown
**Next Command**: `/sp.tasks`
**Created**: 2026-01-01
**Last Updated**: 2026-01-01
