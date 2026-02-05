# Data Model: Phase 3 Chatbot Enhancement

## Overview
This document defines the data entities and relationships for the chatbot enhancement to the todo application.

## Entities

### Conversation
**Description**: Represents a single chat conversation session between user and AI
- **id** (UUID): Unique identifier for the conversation
- **user_id** (UUID): Foreign key to the authenticated user
- **title** (String): Auto-generated title based on first message or user-edited
- **created_at** (DateTime): Timestamp when conversation started
- **updated_at** (DateTime): Timestamp when conversation last updated
- **status** (Enum: active, archived, deleted): Current state of conversation
- **metadata** (JSON): Additional conversation context and settings

**Validation Rules**:
- user_id must reference valid user in system
- title must be 1-100 characters
- status must be one of allowed enum values

**Relationships**:
- One-to-many with Message (conversation has many messages)
- Belongs to User (conversation belongs to one user)

### Message
**Description**: Represents a single message in a conversation
- **id** (UUID): Unique identifier for the message
- **conversation_id** (UUID): Foreign key to parent conversation
- **role** (Enum: user, assistant, tool): Who sent the message
- **content** (Text): The message content
- **timestamp** (DateTime): When message was created
- **tool_calls** (JSON): For assistant messages, any tools called
- **tool_response** (JSON): For tool role messages, the result

**Validation Rules**:
- conversation_id must reference valid conversation
- role must be one of allowed enum values
- content must not exceed 10,000 characters

**Relationships**:
- Belongs to Conversation (message belongs to one conversation)
- Messages are ordered by timestamp within conversation

### TodoOperationLog
**Description**: Log of todo operations performed via chatbot
- **id** (UUID): Unique identifier for the log entry
- **conversation_id** (UUID): Foreign key to conversation where operation occurred
- **message_id** (UUID): Foreign key to the message that triggered the operation
- **operation** (Enum: create, update, delete, complete): Type of operation
- **todo_id** (UUID): ID of the affected todo item
- **previous_state** (JSON): State of todo before operation
- **new_state** (JSON): State of todo after operation
- **timestamp** (DateTime): When operation was performed

**Validation Rules**:
- conversation_id must reference valid conversation
- operation must be one of allowed enum values
- todo_id must reference valid todo in system

**Relationships**:
- Belongs to Conversation (log entry associated with conversation)
- Belongs to Message (log entry associated with triggering message)

## State Transitions

### Conversation States
- **active** → **archived**: User archives conversation or system archives after period of inactivity
- **active** → **deleted**: User deletes conversation
- **archived** → **active**: User restores conversation (if feature is supported)

### Message Relationships
- Messages in conversation ordered chronologically by timestamp
- Each conversation has exactly one starting message (earliest timestamp)
- Tool responses follow tool calls within conversation flow

## Indexing Strategy

### Primary Indexes
- Conversation: PK on id, FK index on user_id
- Message: PK on id, FK index on conversation_id, index on timestamp
- TodoOperationLog: PK on id, FK index on conversation_id and message_id

### Query Optimization
- User's conversations: Index on user_id for quick retrieval
- Conversation messages: Index on conversation_id + timestamp for chronological ordering
- Operation logs: Index on conversation_id for linking to conversation history

## Data Integrity Constraints

### Foreign Key Constraints
- All foreign key references must exist in referenced table
- Deletion cascades only in controlled scenarios (user deletion removes associated conversations)

### Business Logic Constraints
- Messages must belong to existing conversations
- Conversations must belong to existing users
- Operation logs must reference existing conversations and messages
- Todo operations must be performed by authorized users

## Extension to Existing Models

### Relationship with Existing User Model
- User model remains unchanged
- New foreign key relationships reference existing user.id field

### Relationship with Existing Todo Model
- Todo model remains unchanged
- TodoOperationLog references existing todo.id field
- Authorization checks use existing user-todo relationships