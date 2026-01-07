# Database Models Documentation

This directory contains SQLModel database models for the Phase II Full-Stack Todo Application.

**Spec Reference**: `specs/001-fullstack-web-app/data-model.md`

---

## Models Overview

### 1. User Model (`user.py`)

Handles user authentication and account management.

**Table**: `users`

**Fields**:
- `id` (int, PK): Auto-increment primary key
- `email` (str, unique, indexed): Login identifier (max 255 chars)
- `hashed_password` (str): Bcrypt hash (60 chars)
- `name` (str): Display name (max 255 chars)
- `is_active` (bool): Account status (default: True)
- `created_at` (datetime): Registration timestamp
- `updated_at` (datetime): Last update timestamp

**Constraints**:
- Unique constraint on `email`
- All fields NOT NULL except `id` (auto-generated)

**Indexes**:
- Primary key on `id`
- Unique index on `email`

**Usage Example**:
```python
from app.models import User
from app.database import Session, engine

# Create new user
user = User(
    email="user@example.com",
    hashed_password="$2b$12$...",  # bcrypt hash
    name="John Doe"
)

with Session(engine) as session:
    session.add(user)
    session.commit()
    session.refresh(user)
    print(f"Created user: {user.id}")
```

---

### 2. Todo Model (`todo.py`)

Manages task items with user isolation.

**Table**: `todos`

**Fields**:
- `id` (int, PK): Auto-increment primary key
- `user_id` (int, FK, indexed): Owner reference (users.id)
- `title` (str, indexed): Task title (1-500 chars, required)
- `description` (str, optional): Detailed description (max 5000 chars)
- `completed` (bool, indexed): Completion status (default: False)
- `priority` (Priority enum, indexed): low/medium/high (default: medium)
- `tags` (List[str], JSON): Tag array (max 10 tags, 50 chars each)
- `created_at` (datetime, indexed): Creation timestamp
- `updated_at` (datetime): Last modification timestamp

**Constraints**:
- Foreign key to `users.id` with CASCADE delete
- CHECK constraint on `priority` enum values
- Title cannot be empty/whitespace-only
- Maximum 10 tags, 50 chars per tag

**Indexes**:
- Primary key on `id`
- Single indexes: `user_id`, `completed`, `priority`, `created_at`, `title`
- Composite indexes: `(user_id, completed)`, `(user_id, priority)`

**Usage Example**:
```python
from app.models import Todo, Priority
from app.database import Session, engine

# Create new todo
todo = Todo(
    user_id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    priority=Priority.HIGH,
    tags=["shopping", "urgent"]
)

with Session(engine) as session:
    session.add(todo)
    session.commit()
    session.refresh(todo)
    print(f"Created todo: {todo.id}")
```

**Validation**:
```python
# Title validation (auto-trimmed, cannot be empty)
todo = Todo(title="  Valid Title  ", user_id=1)
# todo.title == "Valid Title"

# Tags validation (max 10, auto-deduplicated)
todo = Todo(
    title="Task",
    user_id=1,
    tags=["tag1", "tag2", "tag1"]  # Duplicate removed
)
# todo.tags == ["tag1", "tag2"]
```

---

### 3. Priority Enum (`todo.py`)

Defines priority levels for todos.

**Values**:
- `Priority.LOW = "low"`
- `Priority.MEDIUM = "medium"` (default)
- `Priority.HIGH = "high"`

**Usage**:
```python
from app.models import Priority

todo = Todo(title="Urgent task", priority=Priority.HIGH, user_id=1)
```

---

## Entity Relationship Diagram

```
┌──────────────────────┐
│ User                 │
├──────────────────────┤
│ id (PK)              │◄──┐
│ email (UNIQUE)       │   │
│ hashed_password      │   │
│ name                 │   │
│ is_active            │   │
│ created_at           │   │
│ updated_at           │   │
└──────────────────────┘   │
         1                 │
         │                 │
         │ has many        │
         │                 │
         ▼ *               │
┌──────────────────────┐   │
│ Todo                 │   │
├──────────────────────┤   │
│ id (PK)              │   │
│ user_id (FK) ────────┼───┘ ON DELETE CASCADE
│ title                │
│ description          │
│ completed            │
│ priority             │
│ tags (JSON)          │
│ created_at           │
│ updated_at           │
└──────────────────────┘
```

**Relationship**: User (1) ←→ (*) Todo
- One user can have many todos
- Each todo belongs to exactly one user
- Deleting a user cascades to delete all their todos

---

## Database Migrations

### Running Migrations

**Prerequisites**:
1. Create `.env` file from `.env.example`
2. Set `DATABASE_URL` to your Neon PostgreSQL connection string
3. Install dependencies: `pip install -r requirements.txt`

**Apply Migration**:
```bash
# Navigate to backend directory
cd phase2-fullstack/backend

# Run migration to create tables
alembic upgrade head
```

**Check Current Version**:
```bash
alembic current
```

**Rollback Migration**:
```bash
alembic downgrade -1
```

**View Migration History**:
```bash
alembic history --verbose
```

---

### Migration File Structure

**Location**: `alembic/versions/001_create_users_and_todos_tables.py`

**What it creates**:
1. `users` table with all constraints
2. `todos` table with foreign key to users
3. All performance indexes (single and composite)
4. CHECK constraint for priority enum
5. CASCADE delete behavior

**Reversibility**:
- `upgrade()`: Creates all tables and indexes
- `downgrade()`: Drops all tables (cascade)

---

## Query Examples

### User Queries

**Find user by email (login)**:
```python
from sqlmodel import select
from app.models import User

with Session(engine) as session:
    statement = select(User).where(User.email == "user@example.com")
    user = session.exec(statement).first()
```

**Check if user is active**:
```python
statement = select(User).where(
    User.email == "user@example.com",
    User.is_active == True
)
user = session.exec(statement).first()
```

---

### Todo Queries

**Get all todos for a user** (with user isolation):
```python
from sqlmodel import select
from app.models import Todo

with Session(engine) as session:
    statement = select(Todo).where(Todo.user_id == current_user.id)
    todos = session.exec(statement).all()
```

**Filter by completion status**:
```python
statement = select(Todo).where(
    Todo.user_id == current_user.id,
    Todo.completed == False
)
pending_todos = session.exec(statement).all()
```

**Filter by priority**:
```python
from app.models import Priority

statement = select(Todo).where(
    Todo.user_id == current_user.id,
    Todo.priority == Priority.HIGH
)
high_priority = session.exec(statement).all()
```

**Search by title**:
```python
search_term = "groceries"
statement = select(Todo).where(
    Todo.user_id == current_user.id,
    Todo.title.contains(search_term)
)
results = session.exec(statement).all()
```

**Sort by creation date (newest first)**:
```python
statement = select(Todo).where(
    Todo.user_id == current_user.id
).order_by(Todo.created_at.desc())
todos = session.exec(statement).all()
```

**Pagination**:
```python
page = 1
page_size = 20
skip = (page - 1) * page_size

statement = select(Todo).where(
    Todo.user_id == current_user.id
).offset(skip).limit(page_size)
todos = session.exec(statement).all()
```

---

## Security Considerations

### User Isolation (CRITICAL)

**ALWAYS filter by `current_user.id`** when querying todos:

```python
# GOOD: User isolation enforced
todos = session.exec(
    select(Todo).where(Todo.user_id == current_user.id)
).all()

# BAD: Returns ALL users' todos (security breach!)
todos = session.exec(select(Todo)).all()  # NEVER DO THIS
```

### Password Security

**Never store plain passwords**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password before storing
hashed = pwd_context.hash("user_password")
user = User(email="...", hashed_password=hashed, name="...")

# Verify password during login
is_valid = pwd_context.verify("user_password", user.hashed_password)
```

---

## Performance Best Practices

### 1. Use Indexes for Filtering

Queries automatically benefit from indexes:
```python
# Fast (uses idx_todos_completed)
select(Todo).where(Todo.completed == False)

# Fast (uses idx_todos_user_completed composite)
select(Todo).where(Todo.user_id == 1, Todo.completed == False)
```

### 2. Avoid N+1 Query Problem

```python
# BAD: N+1 queries (1 for todos, N for users)
todos = session.exec(select(Todo)).all()
for todo in todos:
    print(todo.user.email)  # Each triggers a query

# GOOD: Eager loading (single query with JOIN)
from sqlalchemy.orm import selectinload

statement = select(Todo).options(selectinload(Todo.user))
todos = session.exec(statement).all()
```

### 3. Use Pagination

```python
# Always limit query results
statement = select(Todo).limit(100)  # Max 100 results
todos = session.exec(statement).all()
```

---

## Testing Models

### Unit Tests Example

```python
import pytest
from app.models import User, Todo, Priority

def test_user_creation():
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$...",
        name="Test User"
    )
    assert user.email == "test@example.com"
    assert user.is_active is True

def test_todo_title_validation():
    with pytest.raises(ValueError):
        Todo(title="   ", user_id=1)  # Empty title

def test_todo_tags_deduplication():
    todo = Todo(
        title="Task",
        user_id=1,
        tags=["work", "urgent", "work"]
    )
    assert todo.tags == ["work", "urgent"]
```

---

## Troubleshooting

### Issue: Migration fails with "relation already exists"

**Solution**: Database already has tables. Either:
1. Drop existing tables: `alembic downgrade base`
2. Or stamp current state: `alembic stamp head`

### Issue: "Could not parse SQLAlchemy URL"

**Solution**: Check `.env` file has valid `DATABASE_URL`:
```bash
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

### Issue: Foreign key constraint violation

**Cause**: Trying to create todo with non-existent user_id

**Solution**: Ensure user exists before creating todo:
```python
user = session.exec(select(User).where(User.id == user_id)).first()
if not user:
    raise ValueError("User not found")
```

---

## Additional Resources

- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **Neon Postgres**: https://neon.tech/docs
- **Data Model Spec**: `specs/001-fullstack-web-app/data-model.md`
- **Constitution**: `.specify/memory/constitution.md`

---

**Last Updated**: 2026-01-02
**Phase**: II (Full-Stack Web Application)
**Schema Version**: 001 (Initial)
