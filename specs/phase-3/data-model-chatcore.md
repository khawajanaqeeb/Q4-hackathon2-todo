# Data Model: Phase 3 – Chat Core

## Entities

### Conversation
- **id**: UUID (primary key, default: gen_random_uuid())
- **user_id**: UUID (foreign key to users table)
- **title**: VARCHAR(255), nullable (auto-generated from first message)
- **created_at**: TIMESTAMP (default: current_timestamp)
- **updated_at**: TIMESTAMP (default: current_timestamp, on update: current_timestamp)
- **is_active**: BOOLEAN (default: true)

### Message
- **id**: UUID (primary key, default: gen_random_uuid())
- **conversation_id**: UUID (foreign key to conversations table)
- **role**: VARCHAR(20) (constraint: in ['user', 'assistant', 'system'])
- **content**: TEXT (not null)
- **timestamp**: TIMESTAMP (default: current_timestamp)
- **metadata**: JSONB (nullable, for tokens used, AI response details)

### Task (Extended from existing model)
- **id**: UUID (primary key, default: gen_random_uuid())
- **user_id**: UUID (foreign key to users table)
- **title**: VARCHAR(255) (not null)
- **description**: TEXT (nullable)
- **priority**: VARCHAR(20) (constraint: in ['low', 'medium', 'high'], default: 'medium')
- **due_date**: TIMESTAMP (nullable)
- **completed**: BOOLEAN (default: false)
- **tags**: JSONB (nullable, array of strings)
- **created_at**: TIMESTAMP (default: current_timestamp)
- **updated_at**: TIMESTAMP (default: current_timestamp, on update: current_timestamp)

## Relationships

### Conversation ↔ Message
- One Conversation has many Messages
- Foreign Key: messages.conversation_id → conversations.id
- Cascade delete: When conversation is deleted, messages are also deleted

### User ↔ Conversation
- One User has many Conversations
- Foreign Key: conversations.user_id → users.id

### User ↔ Task
- One User has many Tasks
- Foreign Key: tasks.user_id → users.id

## Validation Rules

### Conversation
- Must belong to a valid user
- Title length must be ≤ 255 characters if provided
- Cannot have more than 10,000 messages (prevent excessively large conversations)

### Message
- Role must be one of 'user', 'assistant', or 'system'
- Content must be provided (length > 0)
- Must belong to a valid conversation
- Content length must be ≤ 10,000 characters (prevent abuse)

### Task
- Title must be provided (length > 0)
- Title length must be ≤ 255 characters
- Priority must be one of 'low', 'medium', 'high'
- Due date cannot be in the past if provided
- User can only access their own tasks

## State Transitions

### Task States
- Created → Active (default state when created)
- Active → Completed (when marked as complete)
- Completed → Active (when unmarked as complete)
- Any state → Archived (soft deletion)

### Conversation States
- Active → Inactive (archived by user or system)
- Inactive → Active (restored by user)
- Any state → Deleted (permanent deletion after confirmation)