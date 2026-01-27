# Phase 3 Chatbot Implementation Plan v2

## Technical Context

This implementation plan outlines the integration of chatbot functionality into the existing Phase 2 full-stack todo application, with emphasis on the critical dependencies and prerequisites identified during review.

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
- MCP tools and AI agents are HARD prerequisites for any complete chat functionality

### Critical Dependencies (Hard Prerequisites)
- MCP tools (T113–T119) must be fully implemented before any chat features are considered complete
- AI agent configuration (T120–T125) must be fully implemented before any chat features are considered complete
- Authentication preservation (T105–T112) must be verified before frontend integration
- [X] tasks represent structural scaffolding only, not complete implementation

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
- [X] Hard Prerequisites: MCP tools and AI agents are treated as foundational requirements

## Phase 0: Research

### Research Findings

**Decision**: MCP Tools as Foundation
**Rationale**: MCP tools must be fully implemented before any chat features can be considered complete; they serve as the core interface between AI agents and todo operations
**Alternatives considered**: Direct AI integration without MCP, custom API gateway

**Decision**: AI Agents Configuration Priority
**Rationale**: AI agents must be fully configured and connected to MCP tools before frontend integration can proceed
**Alternatives considered**: Simpler rule-based processing, delayed AI implementation

**Decision**: Authentication Verification Gate
**Rationale**: All authentication preservation must be verified before frontend integration to prevent regressions
**Alternatives considered**: Parallel development with integration testing, phased rollout

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

## Phase 2: Implementation Sequence

### Step 1: MCP Server Infrastructure (HARD PREREQUISITE)
1. Set up MCP server with official SDK
2. Create database migrations for chat entities
3. Implement MCP tools with auth validation
4. Ensure all MCP tools pass user authentication validation

### Step 2: AI Agent Configuration (HARD PREREQUISITE)
1. Configure OpenAI Agents SDK
2. Define system prompts for todo management
3. Connect agents to MCP tools
4. Implement natural language processing

### Step 3: Backend Infrastructure
1. Create chat API endpoints
2. Implement chat service layer
3. Integrate with MCP tools and AI agents

### Step 4: Authentication Verification (HARD PREREQUISITE)
1. Verify all Phase 2 authentication behaviors remain unchanged
2. Test that chat operations don't interfere with auth lifecycle
3. Validate no authentication loops occur during chat usage

### Step 5: Frontend Integration
1. Install and configure OpenAI ChatKit
2. Create chat container component
3. Integrate with existing auth context
4. Implement chat persistence UI

### Step 6: Testing and Validation
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