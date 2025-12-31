# Feature Specification: Phase II - Todo Full-Stack Web Application

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-01
**Status**: Draft
**Phase**: Phase II of Hackathon II Evolution
**GitHub Repository**: https://github.com/khawajanaqeeb/Q4-hackathon2-todo
**Base**: Extends Phase I (console app with basic + enhanced features) to full-stack web application

**Input**: Phase II – Full-Stack Web Application: Evolve the Todo app into a full-stack web application with persistent storage, multi-user support, authentication, and all Basic + Intermediate features. Technology Stack: Next.js (App Router), TypeScript, Tailwind CSS (frontend); FastAPI, SQLModel (backend); Neon Serverless PostgreSQL (database); Better Auth with JWT (authentication); Vercel (frontend deployment), Railway/Render (backend deployment).

---

## Overview

### Phase Goal
Transform the Phase I console-based todo application into a production-ready full-stack web application with:
- Multi-user support with authentication and user isolation
- Persistent cloud storage (Neon PostgreSQL)
- Modern responsive web interface (Next.js 16+ with App Router)
- RESTful API backend (FastAPI with async support)
- All Basic features: Add, View, Update, Delete, Mark Complete
- All Intermediate features: Priorities, Tags, Search, Filter, Sort
- Professional deployment (Vercel + Railway/Render)

### Evolution from Phase I
Phase I implemented a rich console application with:
- Interactive CLI using rich.Table for beautiful display
- Dataclass models (Task with title, description, completed, priority, tags, timestamps)
- CRUD operations via typer commands
- File-based persistence (JSON)
- Search, filter, and sort capabilities

Phase II extends this foundation by:
- Moving from single-user file storage to multi-user cloud database
- Replacing CLI with responsive web UI (accessible from any device)
- Adding authentication and user isolation (JWT with Better Auth)
- Implementing REST API for frontend-backend communication
- Enabling real-time updates and collaborative features
- Professional deployment for public access

### High-Level User Journey
1. **Registration**: User visits app → creates account with email/password → account stored in Neon PostgreSQL
2. **Login**: User enters credentials → receives JWT token → token stored in browser
3. **Dashboard**: Authenticated user sees personalized todo list (only their tasks)
4. **Manage Tasks**:
   - Add new tasks with title, description, priority, tags
   - View tasks in responsive table/card layout
   - Search by title, filter by status/priority/tags, sort by date/priority
   - Update task details inline
   - Mark tasks complete/incomplete with one click
   - Delete tasks with confirmation
5. **Logout**: User logs out → token cleared → redirected to login

### Reference to Reusable Agents/Skills
This specification enables the following agents and skills created for Phase II:

**Agents** (`.claude/agents/`):
- `hackathon-nextjs-builder.md`: Frontend component generation expert
- `hackathon-fastapi-master.md`: Backend API endpoint builder
- `hackathon-db-architect.md`: Database schema design specialist
- `hackathon-auth-specialist.md`: JWT authentication and security expert
- `hackathon-integration-tester.md`: Full-stack testing specialist

**Skills** (`.claude/skills/`):
- `nextjs-ui-generator`: Auto-triggers on "Create todo list page", "Build login UI"
- `fastapi-endpoint-builder`: Auto-triggers on "Create API endpoint", "Build CRUD routes"
- `sqlmodel-db-designer`: Auto-triggers on "Create database schema", "Define models"
- `better-auth-setup`: Auto-triggers on "Set up authentication", "Implement login"
- `fullstack-consistency-checker`: Auto-triggers on "Check consistency", "Verify API contracts"

---

## Requirements

### Functional Requirements

**AUTH - Authentication & Authorization**
- **AUTH-1**: Users must register with email (unique), password (8+ chars), and name
- **AUTH-2**: Passwords must be hashed with bcrypt (12+ rounds) before storage
- **AUTH-3**: Users must login with email + password to receive JWT token
- **AUTH-4**: JWT tokens must expire after 30 minutes (configurable)
- **AUTH-5**: All task endpoints must require valid JWT token in Authorization header
- **AUTH-6**: Frontend must store JWT in localStorage and attach to all API requests
- **AUTH-7**: Frontend must redirect to /login when token is missing or expired
- **AUTH-8**: Backend must return 401 Unauthorized for invalid/expired tokens
- **AUTH-9**: Users must be able to logout (frontend clears token)
- **AUTH-10**: Email validation must prevent invalid formats (use Pydantic EmailStr)

**TASK - Task Management Operations**
- **TASK-1**: Authenticated users must be able to create tasks with title (required, 1-500 chars)
- **TASK-2**: Tasks may include optional description (max 5000 chars)
- **TASK-3**: Tasks must have priority field: low, medium (default), or high
- **TASK-4**: Tasks may have zero or more tags (max 10 tags, each max 50 chars)
- **TASK-5**: Tasks must have completed boolean field (default: false)
- **TASK-6**: Tasks must auto-generate id, created_at, updated_at timestamps
- **TASK-7**: Users must be able to view all their tasks (paginated, 20 per page)
- **TASK-8**: Users must be able to update any field of their tasks (title, description, priority, tags, completed)
- **TASK-9**: Users must be able to delete their tasks with confirmation prompt
- **TASK-10**: Users must be able to toggle task completion status with one click
- **TASK-11**: Task titles must be trimmed of leading/trailing whitespace
- **TASK-12**: Empty or whitespace-only titles must be rejected (400 Bad Request)

**ORG - User Isolation & Data Ownership**
- **ORG-1**: Each task must be associated with exactly one user (user_id foreign key)
- **ORG-2**: Users must ONLY see their own tasks (enforce in all queries)
- **ORG-3**: Users must NOT be able to access/modify other users' tasks (403 or 404)
- **ORG-4**: API must filter all task queries by current_user.id automatically
- **ORG-5**: Database must enforce user_id foreign key constraint
- **ORG-6**: Deleting a user must not be allowed if they have tasks (or cascade delete)

**QUERY - Search, Filter, Sort**
- **QUERY-1**: Users must be able to search tasks by title (case-insensitive, partial match)
- **QUERY-2**: Users must be able to filter tasks by completion status (completed, pending, all)
- **QUERY-3**: Users must be able to filter tasks by priority (low, medium, high, all)
- **QUERY-4**: Users must be able to filter tasks by tags (any task with selected tag)
- **QUERY-5**: Users must be able to sort tasks by created_at (newest/oldest)
- **QUERY-6**: Users must be able to sort tasks by priority (high → medium → low)
- **QUERY-7**: Users must be able to sort tasks by title (A-Z, Z-A)
- **QUERY-8**: Multiple filters must be combinable (e.g., high priority + incomplete + tagged "urgent")
- **QUERY-9**: Search and filters must preserve pagination
- **QUERY-10**: Empty search/filter results must show friendly message

**DATA - Data Persistence & Integrity**
- **DATA-1**: All tasks must be stored in Neon PostgreSQL database
- **DATA-2**: Database must use connection pooling (min 5, max 20 connections)
- **DATA-3**: All database operations must be transactional (rollback on error)
- **DATA-4**: Timestamps must be stored in UTC and displayed in user's local timezone
- **DATA-5**: Database schema must be managed via Alembic migrations
- **DATA-6**: Tags must be stored as JSON array in PostgreSQL
- **DATA-7**: Indexes must exist on user_id, completed, priority, created_at for query performance
- **DATA-8**: Database connection must use SSL (required by Neon)

**UI - User Interface Requirements**
- **UI-1**: Application must be responsive (mobile 320px, tablet 768px, desktop 1024px+)
- **UI-2**: Login page must have email, password fields and submit button
- **UI-3**: Registration page must have email, password, name fields and submit button
- **UI-4**: Dashboard must display tasks in table view (desktop) and card view (mobile)
- **UI-5**: Add task form must be accessible via button/modal
- **UI-6**: Task rows must have inline edit, delete, and toggle complete buttons
- **UI-7**: Filter bar must have dropdowns for status, priority, tags and search input
- **UI-8**: UI must show loading states during API calls (spinners)
- **UI-9**: UI must display error messages for failed operations (toast notifications)
- **UI-10**: UI must display success messages for completed operations (toast notifications)
- **UI-11**: Delete action must show confirmation dialog before execution
- **UI-12**: Priority must be color-coded (high: red, medium: yellow, low: green)
- **UI-13**: Completed tasks must have strikethrough text or different styling
- **UI-14**: Tags must be displayed as colored badges/chips

### Non-Functional Requirements

**SEC - Security**
- **SEC-1**: All passwords must be hashed with bcrypt (cost factor 12+)
- **SEC-2**: JWT secret key must be stored in environment variable (min 256 bits)
- **SEC-3**: HTTPS must be enforced in production (Vercel auto-provides)
- **SEC-4**: CORS must be configured to allow only frontend origin
- **SEC-5**: SQL injection must be prevented (use SQLModel parameterized queries)
- **SEC-6**: XSS must be prevented (React auto-escapes, validate all inputs)
- **SEC-7**: Rate limiting must be applied to login endpoint (5 attempts/min per IP)
- **SEC-8**: Sensitive data (passwords, tokens) must never appear in logs
- **SEC-9**: Database credentials must be stored in environment variables only
- **SEC-10**: JWT tokens must not contain sensitive data (only user_id, email)

**PERF - Performance**
- **PERF-1**: API endpoints must respond within 200ms (p95) for list queries
- **PERF-2**: API endpoints must respond within 100ms (p95) for single-item queries
- **PERF-3**: Frontend must achieve Lighthouse score: Performance 90+, Accessibility 95+
- **PERF-4**: Database queries must use indexes (verify with EXPLAIN ANALYZE)
- **PERF-5**: Frontend must use React.memo and useMemo for expensive components
- **PERF-6**: Pagination must limit results to 20 items per page (max 100)
- **PERF-7**: Connection pool must handle 50 concurrent requests without timeout

**REL - Reliability**
- **REL-1**: Backend must handle database connection failures gracefully (retry 3x)
- **REL-2**: Frontend must handle network errors gracefully (show error, allow retry)
- **REL-3**: Application must work offline (display cached data, queue writes - future)
- **REL-4**: Database migrations must be reversible (up/down scripts)
- **REL-5**: Application must log errors to console (structured JSON format)

**USE - Usability**
- **USE-1**: Error messages must be user-friendly (not technical stack traces)
- **USE-2**: Forms must show validation errors inline (field-specific)
- **USE-3**: Required fields must be marked with asterisk (*)
- **USE-4**: Buttons must show loading state during async operations
- **USE-5**: Empty states must guide users to create first task

**TEST - Testing**
- **TEST-1**: Backend must achieve 80%+ code coverage (pytest)
- **TEST-2**: Frontend must achieve 70%+ code coverage (Jest + React Testing Library)
- **TEST-3**: E2E tests must cover critical flows: register, login, CRUD (Playwright)
- **TEST-4**: All API endpoints must have unit tests for success and error cases
- **TEST-5**: Authentication middleware must have security-focused tests
- **TEST-6**: User isolation must be tested (user A cannot access user B's tasks)

**SCALE - Scalability**
- **SCALE-1**: Application must support 100 concurrent users (Phase II target)
- **SCALE-2**: Database must support 10,000 tasks per user
- **SCALE-3**: API must support 1,000 requests/min (rate limit above this)

### Key Entities

**User**
- `id`: Integer (auto-increment primary key)
- `email`: String (unique, indexed, max 255 chars)
- `hashed_password`: String (bcrypt hash, 60 chars)
- `name`: String (max 255 chars)
- `is_active`: Boolean (default true)
- `created_at`: DateTime (UTC, auto-generated)
- `updated_at`: DateTime (UTC, auto-updated)

**Task**
- `id`: Integer (auto-increment primary key)
- `user_id`: Integer (foreign key to users.id, indexed, NOT NULL)
- `title`: String (required, 1-500 chars, indexed for search)
- `description`: String (optional, max 5000 chars)
- `completed`: Boolean (default false, indexed for filtering)
- `priority`: Enum('low', 'medium', 'high') (default 'medium', indexed)
- `tags`: JSON array of strings (default [], max 10 tags)
- `created_at`: DateTime (UTC, auto-generated, indexed for sorting)
- `updated_at`: DateTime (UTC, auto-updated)

---

## Data Model

### Database Schema (PostgreSQL via Neon)

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(60) NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Todos table
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    tags JSON DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_completed ON todos(completed);
CREATE INDEX idx_todos_priority ON todos(priority);
CREATE INDEX idx_todos_created_at ON todos(created_at);
CREATE INDEX idx_todos_title ON todos(title);

-- Composite indexes for common queries
CREATE INDEX idx_todos_user_completed ON todos(user_id, completed);
CREATE INDEX idx_todos_user_priority ON todos(user_id, priority);
```

### SQLModel Models (Backend)

```python
# app/models/user.py
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

```python
# app/models/todo.py
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
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=500, index=True)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False, index=True)
    priority: Priority = Field(default=Priority.MEDIUM, index=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### TypeScript Interfaces (Frontend)

```typescript
// types/user.ts
export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// types/todo.ts
export interface Todo {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface TodoFormData {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  tags?: string[];
}
```

---

## Authentication & Security

### Better Auth with JWT Integration

**Flow Overview**:
1. User registers → Backend hashes password with bcrypt → Store in DB
2. User logs in → Backend verifies password → Generate JWT token → Return to frontend
3. Frontend stores JWT in localStorage
4. Frontend includes JWT in Authorization header for all API requests
5. Backend validates JWT on protected routes → Extract user_id → Use for queries

### JWT Token Structure

```json
{
  "sub": "user_id_here",
  "email": "user@example.com",
  "exp": 1704153600,
  "iat": 1704150000
}
```

### Backend Authentication Flow

```python
# app/utils/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

```python
# app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.utils.security import decode_token
from app.models.user import User
from sqlmodel import Session, select

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

### Protected Routes (Backend)

All `/todos/*` endpoints require authentication:

```python
@router.get("/todos", response_model=List[TodoResponse])
async def get_todos(
    current_user: User = Depends(get_current_user),  # JWT required
    session: Session = Depends(get_session)
):
    # User isolation enforced automatically
    query = select(Todo).where(Todo.user_id == current_user.id)
    return session.exec(query).all()
```

### Protected Routes (Frontend)

```typescript
// middleware.ts (Next.js App Router)
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

---

## Frontend Architecture

### Technology Stack
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS 4+
- **State Management**: React Context API + useState/useReducer
- **HTTP Client**: fetch API with custom wrapper
- **Forms**: React Hook Form + Zod validation
- **UI Components**: Headless UI (dialogs, dropdowns)
- **Icons**: Heroicons or Lucide React
- **Notifications**: react-hot-toast

### Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home (redirects to /dashboard or /login)
│   ├── login/
│   │   └── page.tsx            # Login page
│   ├── register/
│   │   └── page.tsx            # Registration page
│   └── dashboard/
│       ├── layout.tsx          # Dashboard layout (protected)
│       └── page.tsx            # Main todo list
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── todos/
│   │   ├── TodoTable.tsx       # Desktop table view
│   │   ├── TodoCard.tsx        # Mobile card view
│   │   ├── AddTaskForm.tsx     # Modal form for adding tasks
│   │   ├── EditTaskForm.tsx    # Inline/modal edit form
│   │   ├── FilterBar.tsx       # Search + filter controls
│   │   └── TodoRow.tsx         # Single todo row with actions
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Modal.tsx
│       ├── Toast.tsx
│       └── Spinner.tsx
├── lib/
│   ├── api.ts                  # API client functions
│   ├── auth.ts                 # Auth utilities (getToken, logout)
│   └── utils.ts                # Helpers (cn, formatDate)
├── types/
│   ├── user.ts
│   └── todo.ts
├── context/
│   └── AuthContext.tsx         # Global auth state
└── middleware.ts               # Route protection
```

### Key Pages

**1. Login Page (`/login`)**
- Email input (type="email", required)
- Password input (type="password", required, min 8 chars)
- Submit button
- Link to registration page
- Error display for invalid credentials

**2. Registration Page (`/register`)**
- Name input (required, max 255 chars)
- Email input (type="email", required, unique)
- Password input (type="password", required, min 8 chars, show strength)
- Confirm password input
- Submit button
- Link to login page
- Error display for duplicate email or validation failures

**3. Dashboard Page (`/dashboard`)**
- Header with user name and logout button
- Add Task button (opens modal)
- Filter bar (search, status dropdown, priority dropdown, tags filter)
- Task table (desktop) / Task cards (mobile)
- Pagination controls (if >20 tasks)
- Empty state (when no tasks)

### Key Components

**TodoTable.tsx**
```tsx
interface TodoTableProps {
  todos: Todo[];
  onEdit: (id: number, data: Partial<Todo>) => void;
  onDelete: (id: number) => void;
  onToggle: (id: number) => void;
}
```

**AddTaskForm.tsx**
```tsx
interface AddTaskFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: TodoFormData) => Promise<void>;
}
```

**FilterBar.tsx**
```tsx
interface FilterBarProps {
  onSearchChange: (search: string) => void;
  onStatusChange: (status: 'all' | 'completed' | 'pending') => void;
  onPriorityChange: (priority: 'all' | 'low' | 'medium' | 'high') => void;
  onTagsChange: (tags: string[]) => void;
}
```

### Responsive Design

**Mobile (320px - 767px)**:
- Card layout for todos
- Hamburger menu for filters
- Full-width forms
- Single column

**Tablet (768px - 1023px)**:
- Table layout with horizontal scroll
- Sidebar filters
- Two-column forms

**Desktop (1024px+)**:
- Full table layout
- Fixed sidebar filters
- Modal forms
- Multi-column layout

---

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.11+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT (python-jose) + bcrypt (passlib)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **ASGI Server**: Uvicorn

### Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app + CORS
│   ├── config.py               # Settings (DATABASE_URL, SECRET_KEY)
│   ├── database.py             # Engine, session, create_db_and_tables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── todo.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # UserCreate, UserResponse
│   │   └── todo.py             # TodoCreate, TodoUpdate, TodoResponse
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             # /auth/register, /auth/login
│   │   └── todos.py            # /todos CRUD
│   ├── dependencies/
│   │   ├── auth.py             # get_current_user
│   │   └── database.py         # get_session
│   └── utils/
│       └── security.py         # hash_password, verify_password, create_token
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── test_auth.py
│   ├── test_todos.py
│   └── conftest.py
├── .env
├── requirements.txt
└── alembic.ini
```

### Database Connection

```python
# app/database.py
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"sslmode": "require"}
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### Dependency Injection

All routes use FastAPI dependencies:
- `session: Session = Depends(get_session)` - Database session
- `current_user: User = Depends(get_current_user)` - Authenticated user

---

## API Endpoints

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com` (Railway/Render)

### Endpoints Table

| Method | Endpoint | Auth | Description | Request Body | Response | Status Codes |
|--------|----------|------|-------------|--------------|----------|--------------|
| POST | `/auth/register` | No | Create new user | `{email, password, name}` | `{id, email, name, created_at}` | 201, 400 (duplicate email) |
| POST | `/auth/login` | No | Login user | `{email, password}` | `{access_token, token_type}` | 200, 401 (invalid creds) |
| GET | `/todos` | Yes | Get all user's todos | Query params: `skip`, `limit`, `completed`, `priority`, `search`, `sort_by`, `sort_order` | `[{id, title, ...}]` | 200, 401 |
| POST | `/todos` | Yes | Create new todo | `{title, description?, priority?, tags?}` | `{id, title, ..., user_id}` | 201, 400 (validation), 401 |
| GET | `/todos/{id}` | Yes | Get single todo | - | `{id, title, ..., user_id}` | 200, 404 (not found or not owned), 401 |
| PUT | `/todos/{id}` | Yes | Update todo | `{title?, description?, priority?, tags?, completed?}` | `{id, title, ..., updated_at}` | 200, 404, 400, 401 |
| DELETE | `/todos/{id}` | Yes | Delete todo | - | `null` | 204, 404, 401 |
| POST | `/todos/{id}/toggle` | Yes | Toggle completed | - | `{id, completed, ...}` | 200, 404, 401 |

### Query Parameters (GET /todos)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 20 | Max results (max 100) |
| `completed` | bool | null | Filter by completion status |
| `priority` | str | null | Filter by priority (low/medium/high) |
| `search` | str | null | Search in title (case-insensitive) |
| `sort_by` | str | created_at | Sort field (created_at, priority, title) |
| `sort_order` | str | desc | Sort direction (asc/desc) |

### Example Requests

**Register**
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Login**
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Create Todo**
```bash
POST /todos
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "tags": ["shopping", "urgent"]
}
```

**Get Todos with Filters**
```bash
GET /todos?completed=false&priority=high&search=grocery&sort_by=created_at&sort_order=desc
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## Feature Specifications

### Feature 1: User Registration

**User Story**: As a new user, I want to create an account so that I can manage my personal todo list.

**UI Description**:
- Page route: `/register`
- Form fields:
  - Name (text input, required, max 255 chars)
  - Email (email input, required, validation for format)
  - Password (password input, required, min 8 chars, show strength indicator)
  - Confirm Password (password input, must match password)
  - Submit button (disabled until valid)
- Link to login page: "Already have an account? Log in"
- Error messages displayed inline and as toast

**Inputs**:
- `name`: string (1-255 chars, no leading/trailing whitespace)
- `email`: string (valid email format, unique in database)
- `password`: string (8+ chars, must include letter and number)
- `confirm_password`: string (must match password)

**Outputs**:
- Success: Redirect to `/login` with success message "Account created! Please log in."
- Error: Display error message (e.g., "Email already registered")

**Edge Cases**:
1. Email already exists → 400 Bad Request, message: "Email already registered"
2. Password too weak → Frontend validation prevents submit
3. Passwords don't match → Frontend validation prevents submit
4. Empty fields → Frontend validation prevents submit
5. Network error → Show error toast, allow retry

**Acceptance Criteria**:
- [ ] User can submit valid registration form
- [ ] Email uniqueness enforced (backend returns 400 for duplicates)
- [ ] Password hashed with bcrypt before storage (never stored in plain text)
- [ ] User redirected to login after successful registration
- [ ] Error messages clear and actionable
- [ ] Form accessible (keyboard navigation, screen reader labels)

---

### Feature 2: User Login

**User Story**: As a registered user, I want to log in so that I can access my todo list.

**UI Description**:
- Page route: `/login`
- Form fields:
  - Email (email input, required)
  - Password (password input, required)
  - Submit button
- Link to registration: "Don't have an account? Sign up"
- Error message displayed for invalid credentials

**Inputs**:
- `email`: string
- `password`: string

**Outputs**:
- Success: JWT token stored in localStorage, redirect to `/dashboard`
- Error: "Invalid email or password" (don't reveal which is wrong)

**Edge Cases**:
1. User doesn't exist → 401 Unauthorized
2. Wrong password → 401 Unauthorized
3. Account inactive (is_active=false) → 401 Unauthorized
4. Rate limit exceeded (5 attempts/min) → 429 Too Many Requests
5. Token storage fails → Show error, allow retry

**Acceptance Criteria**:
- [ ] User can login with valid credentials
- [ ] JWT token stored in localStorage/cookies
- [ ] Token included in Authorization header for all API requests
- [ ] Invalid credentials return generic error (no user enumeration)
- [ ] Rate limiting prevents brute force attacks
- [ ] Token expiry handled (redirect to login when expired)

---

### Feature 3: Add New Task

**User Story**: As an authenticated user, I want to add a new task so that I can track things I need to do.

**UI Description**:
- Trigger: "Add Task" button on dashboard
- Modal/form with fields:
  - Title (text input, required, max 500 chars)
  - Description (textarea, optional, max 5000 chars)
  - Priority (dropdown: Low, Medium, High, default: Medium)
  - Tags (multi-select or comma-separated input, max 10 tags)
- Save and Cancel buttons
- Loading state on submit

**Inputs**:
- `title`: string (1-500 chars, trimmed)
- `description`: string (optional, max 5000 chars)
- `priority`: enum ('low', 'medium', 'high')
- `tags`: array of strings (max 10, each max 50 chars)

**Outputs**:
- Success: New todo appears in list, modal closes, success toast
- Error: Error toast with message

**Edge Cases**:
1. Empty title → Frontend prevents submit
2. Whitespace-only title → Backend returns 400 "Title cannot be empty"
3. Title too long (>500 chars) → Frontend prevents submit, backend validates
4. More than 10 tags → Frontend prevents adding more
5. Network error during submit → Show error, keep modal open with data

**Acceptance Criteria**:
- [ ] Task created with all fields
- [ ] Task auto-assigned to current user (user_id set from JWT)
- [ ] Title trimmed and validated
- [ ] Priority defaults to 'medium'
- [ ] Tags deduplicated
- [ ] Timestamps auto-generated (created_at, updated_at)
- [ ] New task appears in list immediately (optimistic update or refetch)

---

### Feature 4: View Task List

**User Story**: As an authenticated user, I want to view all my tasks so that I can see what I need to do.

**UI Description**:
- Desktop: Table with columns (Checkbox, Title, Description, Priority, Tags, Actions)
- Mobile: Card layout with all info stacked
- Priority color-coded (high: red, medium: yellow, low: green)
- Completed tasks have strikethrough or faded text
- Tags displayed as colored chips
- Actions: Edit (pencil icon), Delete (trash icon), Toggle (checkbox)
- Pagination controls at bottom (showing "1-20 of 45 tasks")

**Inputs**:
- Query params from FilterBar (search, completed, priority, tags)
- Pagination params (skip, limit)
- Sort params (sort_by, sort_order)

**Outputs**:
- List of tasks matching filters
- Total count for pagination
- Empty state if no tasks

**Edge Cases**:
1. No tasks → Show empty state with "Add your first task" CTA
2. All tasks filtered out → Show "No tasks match your filters"
3. Loading state → Show skeleton/spinner
4. Error fetching → Show error message with retry button
5. Very long title/description → Truncate with "..." and show full in modal on click

**Acceptance Criteria**:
- [ ] Only current user's tasks displayed (user isolation)
- [ ] Tasks sorted by created_at descending by default
- [ ] Responsive layout (table on desktop, cards on mobile)
- [ ] Pagination works (next/prev buttons, page numbers)
- [ ] Loading and error states handled
- [ ] Empty state guides user to create first task

---

### Feature 5: Search and Filter Tasks

**User Story**: As a user with many tasks, I want to search and filter so that I can find specific tasks quickly.

**UI Description**:
- Filter bar above task list with:
  - Search input (placeholder: "Search tasks...")
  - Status dropdown (All, Completed, Pending)
  - Priority dropdown (All, Low, Medium, High)
  - Tags multi-select dropdown (shows all unique tags from user's tasks)
  - Clear filters button
- Filters applied on change (debounced search)
- Filter count badge (e.g., "3 filters active")

**Inputs**:
- `search`: string (searches in title, case-insensitive, partial match)
- `completed`: boolean | null (null = all, true = completed, false = pending)
- `priority`: 'low' | 'medium' | 'high' | null (null = all)
- `tags`: array of strings (tasks with ANY of these tags)

**Outputs**:
- Filtered list of tasks
- Message if no results: "No tasks match your search"

**Edge Cases**:
1. No results → Show empty state with suggestion to clear filters
2. Multiple filters active → Combine with AND logic
3. Search term with special chars → Escape properly to prevent SQL injection
4. Very fast typing → Debounce search (300ms delay)
5. Tags filter with no tasks → Show "No tasks with these tags"

**Acceptance Criteria**:
- [ ] Search filters by title (case-insensitive, partial match)
- [ ] Status filter works (all/completed/pending)
- [ ] Priority filter works (all/low/medium/high)
- [ ] Tags filter works (OR logic: task has ANY selected tag)
- [ ] Multiple filters combine with AND logic
- [ ] Clear filters resets all filters
- [ ] URL params updated (shareable filtered view)
- [ ] Filters persist on page refresh (read from URL)

---

### Feature 6: Update Task

**User Story**: As a user, I want to edit a task so that I can update details or fix mistakes.

**UI Description**:
- Trigger: Click edit icon on task row
- Inline edit (desktop) or modal (mobile)
- Form pre-filled with current values
- All fields editable (title, description, priority, tags, completed)
- Save and Cancel buttons

**Inputs**:
- `title`: string (optional, 1-500 chars)
- `description`: string (optional, max 5000 chars)
- `priority`: enum (optional)
- `tags`: array of strings (optional)
- `completed`: boolean (optional)

**Outputs**:
- Success: Task updated in list, form closes, success toast
- Error: Error toast with message

**Edge Cases**:
1. No changes made → Save button disabled or shows "No changes"
2. Another user's task → 404 Not Found (user isolation)
3. Task deleted by another session → 404 Not Found, remove from list
4. Empty title submitted → Validation error
5. Network error → Show error, keep form open with unsaved changes

**Acceptance Criteria**:
- [ ] User can edit any field
- [ ] Only changed fields sent to backend (PATCH behavior)
- [ ] User isolation enforced (cannot edit other users' tasks)
- [ ] updated_at timestamp refreshed
- [ ] Validation same as create (title required, max lengths)
- [ ] Optimistic update in UI (revert on error)

---

### Feature 7: Delete Task

**User Story**: As a user, I want to delete a task so that I can remove tasks I no longer need.

**UI Description**:
- Trigger: Click delete icon on task row
- Confirmation dialog: "Are you sure you want to delete this task? This cannot be undone."
- Confirm and Cancel buttons
- Loading state on confirm
- Success toast after deletion

**Inputs**:
- `task_id`: integer

**Outputs**:
- Success: Task removed from list, success toast "Task deleted"
- Error: Error toast with message

**Edge Cases**:
1. Another user's task → 404 Not Found (user isolation)
2. Task already deleted → 404 Not Found, remove from UI
3. User cancels confirmation → Dialog closes, no action
4. Network error during delete → Show error, task remains in list

**Acceptance Criteria**:
- [ ] Confirmation dialog prevents accidental deletion
- [ ] Task deleted from database (hard delete)
- [ ] User isolation enforced
- [ ] Task removed from UI immediately after confirmation
- [ ] Undo functionality (optional, requires soft delete)

---

### Feature 8: Mark Task Complete/Incomplete

**User Story**: As a user, I want to mark tasks as complete so that I can track my progress.

**UI Description**:
- Trigger: Click checkbox next to task title
- Checkbox checked = completed, unchecked = pending
- Completed tasks styled differently (strikethrough, faded)
- Toggle instant (optimistic update)
- Undo toast shown briefly after toggle (optional)

**Inputs**:
- `task_id`: integer
- No body needed (endpoint toggles current state)

**Outputs**:
- Success: Task completion status flipped, UI updated
- Error: Revert to previous state, error toast

**Edge Cases**:
1. Rapid clicking → Debounce or disable during request
2. Another user's task → 404 Not Found
3. Network error → Revert optimistic update, show error
4. Task deleted during toggle → 404, remove from UI

**Acceptance Criteria**:
- [ ] Checkbox toggles completed state
- [ ] Backend endpoint: POST /todos/{id}/toggle
- [ ] Optimistic update in UI (instant feedback)
- [ ] Revert on error
- [ ] updated_at timestamp refreshed
- [ ] Visual distinction for completed tasks (strikethrough)

---

### Feature 9: Sort Tasks

**User Story**: As a user, I want to sort my tasks so that I can view them in my preferred order.

**UI Description**:
- Sort dropdown or column headers (table view)
- Options:
  - Newest first (default)
  - Oldest first
  - Priority (High → Low)
  - Title (A-Z, Z-A)
- Icon indicates current sort (arrow up/down)
- Sort persists in URL params

**Inputs**:
- `sort_by`: 'created_at' | 'priority' | 'title'
- `sort_order`: 'asc' | 'desc'

**Outputs**:
- Tasks reordered in list

**Edge Cases**:
1. Sort + filter combination → Both applied
2. Invalid sort field → Backend returns 400 or ignores
3. No tasks to sort → Empty state shown

**Acceptance Criteria**:
- [ ] Sort by created_at (newest/oldest)
- [ ] Sort by priority (high → medium → low)
- [ ] Sort by title (alphabetical A-Z, Z-A)
- [ ] Sort works with filters (combined)
- [ ] Sort persists on page refresh (URL params)
- [ ] Default sort: created_at descending

---

### Feature 10: Responsive Design

**User Story**: As a user on any device, I want the app to work well so that I can manage tasks anywhere.

**UI Description**:
- Mobile (320px - 767px):
  - Card layout for tasks
  - Full-width forms
  - Hamburger menu for filters
  - Bottom tab navigation (if multi-page)
- Tablet (768px - 1023px):
  - Table layout with horizontal scroll
  - Sidebar filters
  - Touch-friendly buttons
- Desktop (1024px+):
  - Full table layout
  - Fixed sidebar filters
  - Hover states on buttons
  - Keyboard shortcuts (optional)

**Acceptance Criteria**:
- [ ] App usable on mobile (320px width)
- [ ] Layout adapts at breakpoints (320, 768, 1024px)
- [ ] Touch targets min 44x44px (mobile)
- [ ] No horizontal scroll on mobile
- [ ] Forms full-width on mobile, centered on desktop
- [ ] Lighthouse accessibility score 95+

---

## Deployment & Environment

### Deployment Targets

**Frontend (Vercel)**:
- Framework: Next.js (auto-detected)
- Build command: `npm run build`
- Output directory: `.next`
- Environment variables:
  - `NEXT_PUBLIC_API_URL`: Backend API URL (Railway/Render)
- Domain: `your-app.vercel.app` (custom domain optional)

**Backend (Railway or Render)**:
- Runtime: Python 3.11
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `DATABASE_URL`: Neon PostgreSQL connection string
  - `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
  - `ALGORITHM`: HS256
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: 30
  - `DEBUG`: false (production)
- Health check: `GET /health`

**Database (Neon)**:
- Region: Auto (closest to backend)
- Connection string format: `postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require`
- Compute: Auto-scale (suspend after inactivity)
- Storage: 3GB free tier
- Backups: Automatic daily

### Environment Variables

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**Backend (.env)**:
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require
SECRET_KEY=your-256-bit-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
CORS_ORIGINS=https://your-app.vercel.app
```

### Deployment Steps

**1. Deploy Database (Neon)**:
```bash
# Create Neon project at neon.tech
# Copy connection string
# Run migrations
alembic upgrade head
```

**2. Deploy Backend (Railway)**:
```bash
# Connect GitHub repo to Railway
# Add environment variables
# Deploy from main branch
# Verify health check: https://your-backend.railway.app/health
```

**3. Deploy Frontend (Vercel)**:
```bash
# Connect GitHub repo to Vercel
# Add NEXT_PUBLIC_API_URL environment variable
# Deploy from main branch
# Verify app loads: https://your-app.vercel.app
```

---

## Testing Requirements

### Backend Testing (pytest)

**Target Coverage**: 80%+

**Test Categories**:
1. **Unit Tests** (`tests/test_models.py`, `tests/test_utils.py`):
   - Model validation (Pydantic schemas)
   - Password hashing/verification
   - JWT token creation/decoding

2. **API Tests** (`tests/test_auth.py`, `tests/test_todos.py`):
   - Registration (valid, duplicate email, weak password)
   - Login (valid, invalid credentials, rate limiting)
   - CRUD operations (create, read, update, delete)
   - User isolation (user A cannot access user B's tasks)
   - Filtering, searching, sorting
   - Edge cases (invalid IDs, unauthorized access)

3. **Integration Tests**:
   - Full flow: register → login → create task → update → delete
   - Database transactions (rollback on error)

**Example Test**:
```python
def test_create_todo_requires_auth(client):
    response = client.post("/todos", json={"title": "Test"})
    assert response.status_code == 401

def test_user_isolation(client, auth_headers_user1, auth_headers_user2):
    # User 1 creates task
    response = client.post("/todos", json={"title": "User 1 task"}, headers=auth_headers_user1)
    task_id = response.json()["id"]

    # User 2 tries to access it
    response = client.get(f"/todos/{task_id}", headers=auth_headers_user2)
    assert response.status_code == 404  # Not found (user isolation)
```

**Run Tests**:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Testing (Jest + React Testing Library)

**Target Coverage**: 70%+

**Test Categories**:
1. **Component Tests**:
   - LoginForm renders and submits
   - TodoTable displays tasks
   - FilterBar updates filters
   - AddTaskForm validation

2. **Integration Tests**:
   - Full flow: login → view tasks → add task → edit → delete
   - Filter + sort combinations

**Example Test**:
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '@/components/auth/LoginForm';

test('login form submits with valid data', async () => {
  const onSubmit = jest.fn();
  render(<LoginForm onSubmit={onSubmit} />);

  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' }
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password123' }
  });
  fireEvent.click(screen.getByRole('button', { name: /log in/i }));

  expect(onSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123'
  });
});
```

**Run Tests**:
```bash
npm run test -- --coverage
```

### E2E Testing (Playwright)

**Critical Flows**:
1. User registration and login
2. Create task → view in list → edit → mark complete → delete
3. Search and filter tasks
4. Responsive behavior (mobile, tablet, desktop)

**Example Test**:
```typescript
import { test, expect } from '@playwright/test';

test('full task CRUD flow', async ({ page }) => {
  // Register
  await page.goto('/register');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123');
  await page.fill('[name="name"]', 'Test User');
  await page.click('button[type="submit"]');

  // Login
  await expect(page).toHaveURL('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123');
  await page.click('button[type="submit"]');

  // Dashboard
  await expect(page).toHaveURL('/dashboard');

  // Create task
  await page.click('text=Add Task');
  await page.fill('[name="title"]', 'Buy groceries');
  await page.selectOption('[name="priority"]', 'high');
  await page.click('text=Save');

  // Verify in list
  await expect(page.locator('text=Buy groceries')).toBeVisible();

  // Edit task
  await page.click('[aria-label="Edit task"]');
  await page.fill('[name="title"]', 'Buy groceries and cook dinner');
  await page.click('text=Save');

  // Mark complete
  await page.click('[aria-label="Mark complete"]');
  await expect(page.locator('text=Buy groceries and cook dinner')).toHaveClass(/line-through/);

  // Delete task
  await page.click('[aria-label="Delete task"]');
  await page.click('text=Confirm');
  await expect(page.locator('text=Buy groceries')).not.toBeVisible();
});
```

**Run E2E Tests**:
```bash
npx playwright test
```

---

## Setup & Running Locally

### Prerequisites
- **Node.js**: 18+ (for Next.js frontend)
- **Python**: 3.11+ (for FastAPI backend)
- **PostgreSQL**: Neon account (or local PostgreSQL for development)
- **Git**: For version control

### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/khawajanaqeeb/Q4-hackathon2-todo.git
cd Q4-hackathon2-todo/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost/todoapp
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
EOF

# 5. Run migrations
alembic upgrade head

# 6. (Optional) Seed database
python scripts/seed.py

# 7. Start server
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
# 1. Navigate to frontend
cd ../frontend

# 2. Install dependencies
npm install

# 3. Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# 4. Start development server
npm run dev
```

Frontend runs at `http://localhost:3000`

### Verify Setup

1. Open `http://localhost:3000`
2. Click "Sign up" → Create account
3. Login with credentials
4. Add a test task
5. Verify task appears in list
6. Test search, filter, and sort
7. Mark task complete and delete

---

## Assumptions

1. **Users have unique email addresses** (enforced by database constraint)
2. **Tasks belong to exactly one user** (no shared/collaborative tasks in Phase II)
3. **Tags are simple strings** (no tag management UI, users type tags manually)
4. **No task due dates** (future enhancement)
5. **No task priorities beyond low/medium/high** (no custom priorities)
6. **No file attachments** (Phase II focuses on text-based tasks)
7. **No real-time collaboration** (no WebSockets, users see their own data only)
8. **No offline support** (requires internet connection, future enhancement)
9. **No email verification** (users can register and login immediately)
10. **No password reset** (future enhancement)
11. **No user profile editing** (name/email fixed after registration)
12. **No task archiving** (tasks are either active or deleted)
13. **No notifications** (no email/push notifications for task updates)
14. **No recurring tasks** (each task is one-time)
15. **Frontend assumes modern browsers** (ES2020+, no IE11 support)

---

## Success Metrics

**Technical Metrics**:
- Backend test coverage: 80%+
- Frontend test coverage: 70%+
- API response time: <200ms (p95)
- Lighthouse performance: 90+
- Lighthouse accessibility: 95+
- Zero critical security vulnerabilities (OWASP Top 10)

**Functional Metrics**:
- All 10 features implemented and tested
- User isolation verified (security testing)
- Responsive on 3 device sizes (mobile, tablet, desktop)
- Deployment successful (Vercel + Railway + Neon)
- API documentation complete (FastAPI auto-docs)

**User Experience Metrics**:
- User can register, login, and create first task in <2 minutes
- Task CRUD operations complete in <3 clicks
- No blocking bugs in critical flows
- Error messages clear and actionable

---

## Next Steps (Post Phase II)

Future enhancements for Phase III or beyond:
- Task due dates and reminders
- Recurring tasks (daily, weekly, monthly)
- Task categories/projects
- Collaboration (shared tasks, team workspaces)
- File attachments
- Calendar view
- Mobile apps (React Native)
- Offline support (Service Workers, sync)
- Email notifications
- Password reset flow
- User profile editing
- Dark mode
- Keyboard shortcuts
- Task templates
- Time tracking
- Analytics dashboard (task completion rates, productivity trends)

---

**End of Specification**

This specification provides a comprehensive blueprint for implementing Phase II of the todo application. All agents and skills referenced are available in `.claude/agents/` and `.claude/skills/` directories.
