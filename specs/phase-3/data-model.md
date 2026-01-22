# Data Model: Phase 3 Enhancement

**Feature**: Phase 3 Copy and Enhancement
**Created**: 2026-01-22

## Database Schema

### Extended Task Table (from Phase 2)
- id: UUID (Primary Key) - Unique identifier for each task
- title: VARCHAR(255) - Task title/description
- description: TEXT - Detailed task description (nullable)
- completed: BOOLEAN - Whether the task is completed
- priority: VARCHAR(20) - Task priority (low, medium, high)
- tags: JSON - Array of tags associated with the task
- created_at: TIMESTAMP - When the task was created
- updated_at: TIMESTAMP - When the task was last updated
- user_id: UUID (Foreign Key) - Links to the user who owns this task
- due_date: TIMESTAMP - Optional due date for the task

### Conversation Table (new for Phase 3)
- id: UUID (Primary Key) - Unique identifier for each conversation
- user_id: UUID (Foreign Key) - Links to the user who owns this conversation
- title: VARCHAR(255) - Auto-generated title based on first message or user input
- created_at: TIMESTAMP - When the conversation was created
- updated_at: TIMESTAMP - When the conversation was last updated

### Message Table (new for Phase 3)
- id: UUID (Primary Key) - Unique identifier for each message
- conversation_id: UUID (Foreign Key) - Links to the conversation this message belongs to
- role: VARCHAR(20) - Role of the message sender (user, assistant)
- content: TEXT - The actual message content
- timestamp: TIMESTAMP - When the message was sent
- metadata: JSON - Additional data about the message (token usage, model info, etc.)

### Relationships
- Task.user_id → User.id (one-to-many relationship)
- Conversation.user_id → User.id (one-to-many relationship)  
- Message.conversation_id → Conversation.id (one-to-many relationship)

## Validation Rules

### Task Validation
- Title is required and must be 1-255 characters
- User_id is required and must reference an existing user
- Priority must be one of: 'low', 'medium', 'high'
- Completed defaults to FALSE
- Due date must be a valid future date if provided

### Conversation Validation
- User_id is required and must reference an existing user
- Title is required and must be 1-255 characters
- Created_at and updated_at are automatically managed by the database

### Message Validation
- Conversation_id is required and must reference an existing conversation
- Role must be one of: 'user', 'assistant'
- Content is required and must be 1-10000 characters
- Timestamp is automatically set to current time if not provided

## Indexes
- idx_tasks_user_id: Index on user_id for efficient user-based queries
- idx_conversations_user_id: Index on user_id for efficient user-based queries
- idx_messages_conversation_id: Index on conversation_id for efficient conversation-based queries
- idx_messages_timestamp: Index on timestamp for chronological ordering
