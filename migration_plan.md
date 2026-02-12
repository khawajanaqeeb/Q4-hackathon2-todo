# Database Migration Plan: Legacy to Canonical Tables

## Current State Analysis

### Legacy Tables (app/models)
- `users` table: Integer ID, `name` field, no `username`
- `todos` table: Integer ID, `user_id` pointing to users.id

### Canonical Tables (src/models)
- `user` table: UUID ID, `username` field, no `name`
- `task` table: UUID ID, `user_id` pointing to user.id
- `conversation` table: UUID ID, `user_id` pointing to user.id
- `message` table: UUID ID, `conversation_id` pointing to conversation.id

## Migration Steps

### Phase 1: User Migration
1. Copy users from `users` table to `user` table
2. Convert `name` to `username` where possible
3. Maintain UUID integrity for new user records

### Phase 2: Todo/Task Migration
1. Copy todos from `todos` table to `task` table
2. Map `user_id` from integer to corresponding UUID in user table
3. Convert `tags` from JSON array to string format

### Phase 3: Chat Data Migration
1. Migrate any legacy chat data if it exists
2. Update foreign key references to use UUIDs

### Phase 4: Model and Code Updates
1. Update SQLModel definitions
2. Update FastAPI endpoints
3. Update MCP tools and chat endpoints
4. Update frontend API calls

## Migration Script

```sql
-- Backup original tables
CREATE TABLE users_backup AS SELECT * FROM users;
CREATE TABLE todos_backup AS SELECT * FROM todos;

-- Migrate users from legacy to canonical
INSERT INTO user (id, username, email, hashed_password, is_active, is_superuser, created_at, updated_at)
SELECT
    gen_random_uuid(),  -- Generate new UUID
    COALESCE(u.name, 'user_' || u.id::text),  -- Convert name to username
    u.email,
    u.hashed_password,
    u.is_active,
    FALSE,  -- Default superuser status
    u.created_at,
    u.updated_at
FROM users u;

-- Create a mapping table to convert legacy IDs to new UUIDs
CREATE TEMP TABLE user_id_mapping AS
SELECT
    u.id as legacy_id,
    nu.id as new_uuid
FROM users u
JOIN user nu ON nu.email = u.email;  -- Match by email as the stable identifier

-- Migrate todos to tasks with proper UUID mapping
INSERT INTO task (id, user_id, title, description, priority, due_date, completed, tags, created_at, updated_at)
SELECT
    gen_random_uuid(),  -- Generate new UUID for task
    mapping.new_uuid,   -- Map legacy user_id to new UUID
    t.title,
    t.description,
    CASE
        WHEN t.priority = 'low' THEN 'low'
        WHEN t.priority = 'high' THEN 'high'
        ELSE 'medium'  -- Default to medium
    END,
    NULL,  -- No due_date in legacy
    t.completed,
    CASE
        WHEN t.tags IS NOT NULL THEN t.tags::text  -- Convert JSON to string
        ELSE NULL
    END,
    t.created_at,
    t.updated_at
FROM todos t
JOIN user_id_mapping mapping ON mapping.legacy_id = t.user_id;

-- Verify migration counts
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'user' as table_name, COUNT(*) as count FROM user
UNION ALL
SELECT 'todos' as table_name, COUNT(*) as count FROM todos
UNION ALL
SELECT 'task' as table_name, COUNT(*) as count FROM task;

-- Clean up temporary mapping table
DROP TABLE IF EXISTS user_id_mapping;
```

## Code Updates Required

### 1. Update User Model (src/models/user.py)
```python
# Already correct - uses UUID primary key and username field
```

### 2. Update Task Model (src/models/task.py)
```python
# Ensure it properly references the user table
user_id: uuid.UUID = Field(foreign_key="user.id")
```

### 3. Update Todo API (src/api/todos.py)
```python
# Update to use Task model instead of legacy Todo model
# Update foreign key references to use UUIDs
```

### 4. Update Authentication Dependencies (src/dependencies/auth.py)
```python
# Ensure get_current_user properly handles UUID-based users
```

## Verification Steps

1. Run the migration script on a test database
2. Verify data integrity and foreign key relationships
3. Test all application functionality:
   - Authentication (login/register)
   - Todo operations (CRUD)
   - Chat functionality
4. Run integration tests

## Rollback Plan

If issues occur, restore from backups:
```sql
TRUNCATE TABLE user, task, conversation, message RESTART IDENTITY;
INSERT INTO user SELECT * FROM user_backup;
INSERT INTO task SELECT * FROM task_backup;
-- Restore other tables as needed
```

## Final Cleanup

Once verified, optionally remove backup tables:
```sql
DROP TABLE users_backup, todos_backup;
```