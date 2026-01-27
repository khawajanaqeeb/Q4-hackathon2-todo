# Phase 3 Chatbot Data Model

## Entities

### ChatConversation
- **id**: UUID (Primary Key)
- **user_id**: UUID (Foreign Key to users table)
- **title**: VARCHAR(255) - Conversation title derived from first message or user-defined
- **created_at**: TIMESTAMP (Default: NOW())
- **updated_at**: TIMESTAMP (Default: NOW(), Updated on change)
- **status**: ENUM('active', 'archived') (Default: 'active')

**Relationships**:
- Belongs to one User (user_id → users.id)
- Has many ChatMessages (One ChatConversation to Many ChatMessages)

**Validation Rules**:
- user_id must reference existing user
- title cannot be empty
- status must be either 'active' or 'archived'

### ChatMessage
- **id**: UUID (Primary Key)
- **conversation_id**: UUID (Foreign Key to chat_conversations table)
- **sender_type**: ENUM('user', 'assistant') - Who sent the message
- **content**: TEXT - The actual message content
- **created_at**: TIMESTAMP (Default: NOW())
- **role**: VARCHAR(20) - Role in the conversation context ('user', 'assistant', 'system')

**Relationships**:
- Belongs to one ChatConversation (conversation_id → chat_conversations.id)
- Belongs to one User through ChatConversation (via user_id in chat_conversations)

**Validation Rules**:
- conversation_id must reference existing conversation
- sender_type must be 'user' or 'assistant'
- content cannot be empty
- role must be 'user', 'assistant', or 'system'

### TodoOperationLog
- **id**: UUID (Primary Key)
- **user_id**: UUID (Foreign Key to users table)
- **operation_type**: ENUM('create', 'read', 'update', 'delete') - Type of todo operation
- **todo_details**: JSONB - Details about the todo operation
- **created_at**: TIMESTAMP (Default: NOW())
- **mcp_tool_used**: VARCHAR(100) - Which MCP tool was used for this operation

**Relationships**:
- Belongs to one User (user_id → users.id)

**Validation Rules**:
- user_id must reference existing user
- operation_type must be one of the defined enum values
- todo_details must be valid JSON
- mcp_tool_used cannot be empty

## State Transitions

### ChatConversation States
- **Initial State**: 'active' when created
- **Transition to 'archived'**: When user chooses to archive conversation
- **Access Control**: Only the owning user can archive their conversations

### Data Integrity
- Foreign key constraints ensure referential integrity
- Cascading deletes: Deleting a user removes their conversations and message logs
- Conversations are soft-deleted initially (marked as archived) rather than permanently deleted