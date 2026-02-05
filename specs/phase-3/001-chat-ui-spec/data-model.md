# Data Model for Chat UI

## Core Entities

### Message
**Description**: Represents a single message in the conversation
**Fields**:
- id: string (unique identifier)
- content: string (message text content)
- sender: "user" | "ai" (determines styling and behavior)
- timestamp: Date (ISO 8601 format)
- status: "sent" | "delivered" | "failed" | "streaming" (delivery state)
- metadata: object (additional data like AI response status, tool execution info)

**Validation Rules**:
- content must be non-empty string
- sender must be either "user" or "ai"
- timestamp must be valid ISO date string
- status must be one of allowed values

**Relationships**:
- Belongs to a Conversation
- May contain references to Todo items (via MCP tool execution)

### Conversation
**Description**: Collection of related messages between user and AI
**Fields**:
- id: string (unique identifier)
- userId: string (reference to authenticated user)
- createdAt: Date (ISO 8601 format)
- updatedAt: Date (ISO 8601 format)
- isActive: boolean (whether conversation is currently active)

**Validation Rules**:
- userId must exist and be valid
- createdAt must be in past
- updatedAt must be >= createdAt
- isActive must be boolean

**Relationships**:
- Contains multiple Messages
- Associated with Todo items through MCP tools

### TodoItem (Referenced from existing system)
**Description**: Todo item that can be manipulated through chat interface
**Fields**:
- id: string (unique identifier)
- title: string (task title)
- description: string (optional description)
- completed: boolean (completion status)
- priority: "low" | "medium" | "high" (priority level)
- dueDate: Date (optional due date)
- createdAt: Date (ISO 8601 format)
- updatedAt: Date (ISO 8601 format)

**Validation Rules**:
- title must be non-empty string
- priority must be one of allowed values
- dueDate must be valid date if provided
- completed must be boolean

**Relationships**:
- Belongs to a User
- May be referenced by Messages that involve MCP tool operations

### CommandSuggestion
**Description**: Contextual command suggestion presented to user
**Fields**:
- id: string (unique identifier)
- text: string (suggested command text)
- category: string (command category for grouping)
- context: string (triggering context)
- isUsed: boolean (whether suggestion was selected)

**Validation Rules**:
- text must be non-empty string
- category must be non-empty string
- isUsed must be boolean

**Relationships**:
- Associated with Conversation context

### UIState
**Description**: Local UI state not persisted on server
**Fields**:
- inputText: string (current content of message input)
- isInputDisabled: boolean (whether input is accepting text)
- scrollPosition: number (current scroll position in message list)
- activeTheme: "light" | "dark" (current theme preference)
- isTypingIndicatorVisible: boolean (typing indicator visibility)
- commandSuggestionsVisible: boolean (command suggestions visibility)

**Validation Rules**:
- inputText can be empty string
- all boolean fields must be actual booleans
- scrollPosition must be non-negative number
- activeTheme must be one of allowed values

## State Transitions

### Message State Transitions
- "draft" → "sent" (when user submits message)
- "sent" → "delivered" (when backend confirms receipt)
- "sent" → "failed" (when sending fails)
- "delivered" → "streaming" (for AI responses being generated)
- "streaming" → "delivered" (when AI response completes)

### TodoItem State Transitions (via MCP tools)
- "active" → "completed" (when marked complete via chat)
- "active" → "updated" (when properties are modified via chat)
- "created" → "active" (when new todo is created via chat)
- "active" → "deleted" (when deleted via chat)

### UIState Transitions
- Input focus/unfocus affects isInputDisabled
- Message receipt affects scrollPosition management
- User theme preference changes affect activeTheme
- AI processing affects isTypingIndicatorVisible
- Context changes affect commandSuggestionsVisible