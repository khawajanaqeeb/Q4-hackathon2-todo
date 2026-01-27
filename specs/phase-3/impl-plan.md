# Phase 3 Chatbot Implementation Plan

## Technical Context

This implementation plan outlines the integration of chatbot functionality into the existing Phase 2 full-stack todo application. The primary goal is to extend Phase 2 capabilities to enable natural language todo management while preserving all existing authentication behaviors.

### Technology Stack
- Frontend: OpenAI ChatKit for chat interface
- Backend: OpenAI Agents SDK for AI processing
- MCP: Official MCP SDK for tool exposure
- Database: PostgreSQL (existing from Phase 2)
- Framework: Next.js (existing from Phase 2)
- Authentication: Preserved from Phase 2 (no changes)

### Key Constraints
- Phase 2 authentication behavior must remain unchanged
- No auth refactors or optimizations
- MCP tools must be stateless with database persistence
- Chatbot must not interfere with auth lifecycle

## Constitution Check

Based on the project constitution, this implementation must:
- Maintain backward compatibility with existing Phase 2 functionality
- Preserve all authentication behaviors from Phase 2
- Follow security-first principles for user data
- Maintain performance standards established in Phase 2
- Use minimal, testable changes

### Gate Evaluations
- [X] Authentication preservation: Plan ensures no auth changes
- [X] Backward compatibility: All Phase 2 APIs remain intact
- [X] Security compliance: MCP tools will validate existing auth tokens
- [X] Performance: Stateless design maintains Phase 2 performance

## Phase 0: Research

### Research Findings

**Decision**: Integration approach for OpenAI ChatKit
**Rationale**: OpenAI ChatKit will be integrated as a separate component that operates independently from the authentication context to prevent interference
**Alternatives considered**: Custom chat interface, third-party chat libraries

**Decision**: MCP Server implementation
**Rationale**: Official MCP SDK will be used to expose todo operations as tools for AI agents, with proper user validation through existing auth tokens
**Alternatives considered**: Custom API gateway, direct AI integration

**Decision**: Database schema for chat persistence
**Rationale**: Separate tables for chat conversations and message history, linked to existing user accounts
**Alternatives considered**: Embedding in existing todo tables, separate database

## Phase 1: Design & Contracts

### Data Model

#### ChatConversation Entity
- id: UUID (primary key)
- user_id: UUID (foreign key to users table)
- title: string (conversation title)
- created_at: datetime
- updated_at: datetime
- status: enum ('active', 'archived')

#### ChatMessage Entity
- id: UUID (primary key)
- conversation_id: UUID (foreign key to chat_conversations)
- sender_type: enum ('user', 'assistant')
- content: text
- created_at: datetime
- role: string ('user', 'assistant', 'system')

#### TodoOperationLog Entity
- id: UUID (primary key)
- user_id: UUID (foreign key to users table)
- operation_type: enum ('create', 'read', 'update', 'delete')
- todo_details: jsonb
- created_at: datetime
- mcp_tool_used: string

### API Contracts

#### Chat Endpoints (Backend - FastAPI)

```
POST /api/chat/conversations
- Create new chat conversation
- Requires auth token
- Returns conversation ID

POST /api/chat/conversations/{conversation_id}/messages
- Send message to conversation
- Requires auth token
- Returns AI response

GET /api/chat/conversations
- List user's conversations
- Requires auth token
- Returns paginated list

GET /api/chat/conversations/{conversation_id}
- Get conversation details
- Requires auth token
- Returns conversation with messages
```

#### MCP Tool Contracts

```
Tool: create_todo
- Parameters: title (string), description (string), priority (string), tags (array)
- Requires user authentication validation
- Creates todo in user's account

Tool: list_todos
- Parameters: filter (string), sort_by (string), limit (integer)
- Requires user authentication validation
- Returns user's todos

Tool: update_todo
- Parameters: todo_id (string), updates (object)
- Requires user authentication validation
- Updates user's todo

Tool: delete_todo
- Parameters: todo_id (string)
- Requires user authentication validation
- Deletes user's todo
```

### Frontend Integration Points

#### Chat Component Integration
- Mount OpenAI ChatKit in dedicated chat area
- Pass existing auth token for API calls
- Store conversation context separately from auth context
- Link chat history to authenticated user

#### Authentication Isolation
- Chat component operates with separate state from auth context
- No direct communication between chat and auth systems
- Auth token passed via props/environment, not shared state

## Phase 2: Implementation Steps

### Step 1: Backend Infrastructure
1. Set up MCP server with official SDK
2. Create database migrations for chat entities
3. Implement MCP tools with auth validation
4. Create chat API endpoints

### Step 2: Frontend Integration
1. Install and configure OpenAI ChatKit
2. Create chat container component
3. Integrate with existing auth context
4. Implement chat persistence UI

### Step 3: AI Agent Configuration
1. Configure OpenAI Agents SDK
2. Define system prompts for todo management
3. Connect agents to MCP tools
4. Implement natural language processing

### Step 4: Testing and Validation
1. Unit tests for MCP tools
2. Integration tests for chat functionality
3. Authentication preservation tests
4. Performance validation against Phase 2 baselines

## Phase 3: Deployment Preparation

### Development Environment
- Ensure local development works without memory crashes
- Validate authentication loops are prevented
- Confirm all Phase 2 functionality remains intact

### Production Considerations
- MCP server deployment strategy
- Chat data privacy and retention
- AI usage monitoring and costs