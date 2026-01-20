# Database Models Specification for Phase 3 Todo AI Chatbot

## Overview

This document defines the SQLModel database models required for the AI Todo Chatbot system. It extends the existing Phase II models with new entities for managing conversation history while maintaining compatibility with the existing Todo and User models.

## Entity Relationships

```
User (1) -----> (Many) Todo
User (1) -----> (Many) Conversation
Conversation (1) -----> (Many) Message
```

## Model Definitions

### 1. Conversation Model

**Purpose**: Represents a conversation session between a user and the AI chatbot.

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime

class ConversationBase(SQLModel):
    """Base model for conversation with common fields"""
    title: str = Field(default="New Conversation", max_length=200)
    user_id: int = Field(foreign_key="user.id")
    is_active: bool = Field(default=True)


class Conversation(ConversationBase, table=True):
    """SQLModel for Conversation entity"""
    id: int = Field(default=None, primary_key=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationRead(ConversationBase):
    """Response model for reading conversations"""
    id: int
    created_at: datetime
    updated_at: datetime
    message_count: int


class ConversationCreate(ConversationBase):
    """Request model for creating conversations"""
    title: str = Field(default="New Conversation", max_length=200)
    # user_id will be extracted from JWT token, not from request body


class ConversationUpdate(SQLModel):
    """Request model for updating conversations"""
    title: str | None = Field(default=None, max_length=200)
    is_active: bool | None = Field(default=None)
```

### 2. Message Model

**Purpose**: Represents individual messages within a conversation.

```python
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime
import uuid

class MessageRole(str, Enum):
    """Enumeration for message roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageStatus(str, Enum):
    """Enumeration for message processing status"""
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"


class MessageBase(SQLModel):
    """Base model for message with common fields"""
    conversation_id: int = Field(foreign_key="conversation.id")
    role: MessageRole
    content: str = Field(sa_column_kwargs={"server_default": ""})
    status: MessageStatus = Field(default=MessageStatus.PROCESSED)

    # Optional fields for tool interactions
    tool_name: str | None = Field(default=None, max_length=100)
    tool_input: dict | None = Field(default=None, sa_column_kwargs={"server_default": "'{}'::jsonb"})
    tool_output: dict | None = Field(default=None, sa_column_kwargs={"server_default": "'{}'::jsonb"})


class Message(MessageBase, table=True):
    """SQLModel for Message entity"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")


class MessageRead(MessageBase):
    """Response model for reading messages"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    processing_time_ms: int | None = None


class MessageCreate(MessageBase):
    """Request model for creating messages"""
    role: MessageRole
    content: str
    # conversation_id will be determined by the system based on the chat session


class MessageUpdate(SQLModel):
    """Request model for updating messages"""
    content: str | None = Field(default=None)
    status: MessageStatus | None = Field(default=None)
    tool_output: dict | None = Field(default=None)
```

## Integration with Existing Models

### User Model Reference
The new models maintain compatibility with the existing User model from Phase II:
- `user_id` foreign key in Conversation references `user.id`
- User authentication and permissions continue to work as in Phase II

### Todo Model Reference
The system integrates with the existing Todo model for task operations:
- All specialized agents will query and modify the existing Todo table
- User isolation is maintained through the existing `user_id` foreign key in the Todo model

## Indexes and Performance

### Required Database Indexes

```sql
-- Conversation indexes
CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_created_at ON conversation(created_at DESC);
CREATE INDEX idx_conversation_is_active ON conversation(is_active);

-- Message indexes
CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_role ON message(role);
CREATE INDEX idx_message_created_at ON message(created_at DESC);
CREATE INDEX idx_message_status ON message(status);
```

## Data Integrity Constraints

### Foreign Key Constraints
- `conversation.user_id` references `user.id` (CASCADE DELETE on user removal)
- `message.conversation_id` references `conversation.id` (CASCADE DELETE on conversation removal)

### Check Constraints
- Message content length: maximum 10,000 characters
- Conversation title length: maximum 200 characters
- User ID must be positive integer

## Migration Strategy

### New Database Schema
The following tables will be added to the existing Phase II schema:

1. `conversation` table - stores conversation metadata
2. `message` table - stores individual conversation messages

### Backward Compatibility
- All existing Phase II functionality remains unchanged
- Existing Todo and User models continue to work as before
- No breaking changes to existing API endpoints

## Privacy and Security Considerations

### Data Isolation
- All conversation data is isolated by user_id
- Users can only access their own conversations and messages
- JWT authentication required for all access

### Data Retention
- Conversations are retained for 2 years by default
- Messages are automatically deleted when parent conversation is deleted
- Administrative tools available for data cleanup

### Audit Trail
- Created and updated timestamps on all records
- Message status tracking for monitoring processing
- Tool interaction logging for debugging purposes