# Implementation Plan: Phase 3 Chatbot Enhancement

**Branch**: `main` | **Date**: 2026-02-05 | **Spec**: specs/phase-3/spec.md
**Input**: Feature specification from `/specs/phase-3/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the existing Phase 2 todo application by adding a conversational chatbot system that allows users to manage todos through natural language, while preserving existing APIs, database schema, and authentication contract. The system will use OpenAI Agents SDK with an MCP server to provide stateless task management tools that integrate seamlessly with the existing todo functionality.

## Technical Context

**Language/Version**: Python 3.11, TypeScript/JavaScript (Next.js 16.1.1)
**Primary Dependencies**: FastAPI, Next.js (App Router), OpenAI Agents SDK, SQLModel, MCP SDK
**Storage**: Neon PostgreSQL database with existing tables preserved
**Testing**: pytest for backend, Jest for frontend
**Target Platform**: Web application with SSR and CSR support
**Project Type**: Web application with frontend and backend components
**Performance Goals**: <500ms response time for chat interactions, 60fps UI responsiveness
**Constraints**: Preserve existing Phase 2 functionality, maintain cookie-based auth, stateless API endpoints
**Scale/Scope**: Individual user chat sessions, concurrent multi-user support, persistent conversation history

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ All Phase 2 functionality remains intact (no breaking changes)
- ✅ Existing authentication contract preserved (cookie-based model)
- ✅ Statelessness maintained at API level with DB persistence
- ✅ Incremental enhancement approach (not rewrite)
- ✅ Technology stack alignment (FastAPI, Next.js, SQLModel, Neon PG)

## HARD GUARDRAILS

- **MCP Server**: Runs in-process within the main FastAPI application
- **Deployment**: No separate deployment required for MCP server
- **Authentication**: No new auth, tokens, or middleware - reuse existing cookie-based auth
- **Frontend Access**: No direct frontend → MCP access - all MCP interactions via backend

## Project Structure

### Documentation (this feature)

```text
specs/phase-3/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── chat.py      # Chat endpoint
│   │   ├── mcp.py       # MCP endpoints
│   │   └── auth.py      # Auth endpoints (preserved)
│   ├── models/
│   │   ├── user.py      # User model (preserved)
│   │   ├── todo.py      # Todo model (preserved)
│   │   └── conversation.py  # New conversation model
│   ├── tools/
│   │   └── todo_tools.py    # MCP todo operation tools
│   ├── services/
│   │   ├── mcp_integration.py  # MCP server integration
│   │   └── conversation_service.py  # Conversation persistence
│   ├── dependencies/
│   │   └── auth.py      # Auth dependency (preserved)
│   ├── database.py      # DB connection (preserved)
│   └── main.py          # App entry point
└── tests/

frontend/
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...path]/route.ts  # Auth proxy (preserved)
│   ├── chat/            # Chat UI page
│   └── middleware.ts    # Auth middleware (preserved)
├── components/
│   ├── ChatInterface.tsx  # Chat UI component
│   └── ChatKitInterface.tsx  # OpenAI ChatKit integration
├── context/
│   └── AuthContext.tsx  # Auth context (preserved)
└── src/
    └── services/
        ├── api.js       # API service (preserved)
        └── auth.js      # Auth service (preserved)
```

**Structure Decision**: Web application structure chosen to match existing architecture with clear separation of concerns between frontend and backend. All Phase 2 components preserved with new chatbot functionality added incrementally.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None] | [All checks passed] | [No violations identified] |

## 1. Architecture Overview

### System Architecture Diagram (Text Description)

```
┌─────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   Frontend  │ ────────────────▶│    Backend      │
│             │                  │                 │
│ ChatKit UI  │ ◀─────────────── │ Chat Endpoint   │
│             │   SSE/WebSocket  │                 │
└─────────────┘                  ├─────────────────┤
                                 │   OpenAI Agent  │
                                 │                 │
                                 ├─────────────────┤
                                 │   MCP Server    │
                                 │                 │
                                 ├─────────────────┤
                                 │  Neon PostgreSQL│
 │                              │                 │
 │                              └─────────────────┘
 │                                         │
 │            ┌─────────────────────────────┘
 │            ▼
 │    ┌─────────────────┐
 │    │   MCP Tools     │
 │    │ (Todo CRUD ops) │
 │    └─────────────────┘
 │            │
 │            ▼
 │    ┌─────────────────┐
 │    │  Existing Todo  │
 │    │  API Endpoints  │
 │    └─────────────────┘
 │            │
 │            ▼
 └───► ┌─────────────────┐
       │  SQLModel ORM   │
       │  (PostgreSQL)   │
       └─────────────────┘
```

### Auth Context Flow Explanation

1. User authenticates through existing cookie-based system
2. HttpOnly auth cookie is set and automatically included by browser
3. Frontend makes requests to chat endpoint with auth cookie
4. Backend validates auth using existing dependency
5. MCP server receives user context from validated backend
6. MCP tools enforce authorization using existing auth dependency
7. All operations are restricted to authenticated user's data only

### Chat Transport Choice

- **Selected Approach**: HTTP streaming (Server-Sent Events)
- **Rationale**: Simpler implementation with good browser support
- **Out of Scope**: WebSockets (Phase 3 constraint)

## 2. Component Breakdown

### Chat UI (frontend)
- **Responsibility**: User-facing conversational interface using OpenAI ChatKit
- **Boundaries**:
  - Accepts user input and displays AI responses
  - Handles conversation history and state management
  - Integrates with existing AuthContext for authentication
  - Makes requests to backend chat endpoint
- **Preserves**: Existing Next.js structure and authentication context

### Chat API endpoint (backend)
- **Responsibility**: Handle chat requests and orchestrate with OpenAI Agent
- **Boundaries**:
  - Validates user authentication using existing auth dependency
  - Manages conversation state in database
  - Coordinates with OpenAI Agent and MCP tools
  - Returns streaming responses to frontend
- **Preserves**: Existing authentication contract and FastAPI structure

### OpenAI Agent configuration
- **Responsibility**: AI reasoning and conversation management
- **Boundaries**:
  - Uses OpenAI Agents SDK for AI logic
  - Interacts with MCP tools for todo operations
  - Maintains conversation context
  - Follows security guidelines for API usage
- **Preserves**: No custom LLM orchestration outside Agents SDK

### MCP server
- **Responsibility**: Expose todo operations as standardized tools
- **Boundaries**:
  - Uses Official MCP SDK only
  - Accepts user context from backend, not frontend
  - Stateless operation with database persistence
  - No new authentication logic
- **Preserves**: Existing FastAPI structure with new endpoints

### MCP tools (task CRUD)
- **Responsibility**: Execute todo operations through standardized interfaces
- **Boundaries**:
  - Implement create_todo, list_todos, update_todo, delete_todo, complete_todo
  - Use existing SQLModel models and database
  - Enforce authorization via existing auth dependency
  - Stateless with database persistence
- **Preserves**: Existing todo model and database schema

### Conversation persistence layer
- **Responsibility**: Store and retrieve conversation state
- **Boundaries**:
  - Manages chat message history
  - Tracks conversation context
  - Links conversations to authenticated users
  - Maintains data isolation between users
- **Preserves**: Existing database schema with new conversation table

## 3. Conversation State Strategy

### Data to be Persisted
- **Conversation ID**: Unique identifier for each conversation
- **Message History**: Complete history of user and AI messages
- **Tool Calls**: Record of MCP tool invocations and results
- **User ID**: Associated authenticated user (foreign key reference)
- **Timestamps**: Created and updated timestamps for each message
- **Conversation Metadata**: Title, status, and context information

### Storage Location
- **Database Table**: `conversations` table in existing Neon PostgreSQL database
- **Schema**: Follow existing SQLModel patterns with relations to user table
- **Indexing**: Index on user_id for efficient retrieval of user's conversations

### Statelessness Preservation
- **API Level**: Chat endpoint remains stateless by retrieving state from DB
- **MCP Tools**: Tools remain stateless by accessing DB directly for operations
- **User Context**: Maintained via existing auth dependency on each request

### Conversation Resume Strategy
- **History Retrieval**: Fetch conversation history by ID when resuming
- **Context Restoration**: Rebuild AI agent context with message history
- **Active Session**: Establish new connection with restored context

## 4. MCP Tool Design

### create_todo Tool
- **Function**: Create new todo item for authenticated user
- **Parameters**: title (string), description (string, optional), priority (enum), due_date (string, optional)
- **Authorization**: Validates user context via existing auth dependency
- **Implementation**: Uses existing Todo model and SQLModel for DB operations
- **Returns**: Created todo object with ID and confirmation

### list_todos Tool
- **Function**: Retrieve todos for authenticated user with filters
- **Parameters**: status (enum, optional), priority (enum, optional), limit (int, optional), offset (int, optional)
- **Authorization**: Validates user context via existing auth dependency
- **Implementation**: Queries existing Todo table with user_id filter
- **Returns**: Array of todo objects matching criteria

### update_todo Tool
- **Function**: Update specific todo item for authenticated user
- **Parameters**: todo_id (string), title (string, optional), description (string, optional), priority (enum, optional), status (enum, optional), due_date (string, optional)
- **Authorization**: Validates user owns the todo via existing auth dependency
- **Implementation**: Updates existing Todo object in database
- **Returns**: Updated todo object

### delete_todo Tool
- **Function**: Delete specific todo item for authenticated user
- **Parameters**: todo_id (string)
- **Authorization**: Validates user owns the todo via existing auth dependency
- **Implementation**: Removes Todo object from database
- **Returns**: Confirmation of deletion

### complete_todo Tool
- **Function**: Mark specific todo item as complete/incomplete for authenticated user
- **Parameters**: todo_id (string), completed (boolean)
- **Authorization**: Validates user owns the todo via existing auth dependency
- **Implementation**: Updates completed status of Todo object
- **Returns**: Updated todo object with completion status

## 5. Incremental Delivery Plan

### Milestone 1: Chat endpoint scaffold
- Create basic chat endpoint in backend
- Integrate with existing authentication
- Implement conversation model in database
- Set up basic response structure

### Milestone 2: OpenAI Agent setup
- Configure OpenAI Agent SDK
- Set up basic agent without tools
- Implement message streaming
- Connect to chat endpoint

### Milestone 3: MCP server + tools
- Build MCP server using Official MCP SDK
- Implement stateless MCP tools for todo operations
- Connect tools to existing database models
- Test tools with dummy agent

### Milestone 4: Conversation persistence
- Implement conversation history storage
- Add message persistence to database
- Implement resume functionality
- Test conversation continuity

### Milestone 5: Frontend ChatKit integration
- Integrate OpenAI ChatKit in frontend
- Connect to backend chat endpoint
- Implement conversation UI
- Add authentication integration

### Milestone 6: End-to-end verification
- Test complete chatbot workflow
- Verify all todo operations work via chat
- Confirm authentication preservation
- Validate Phase 2 functionality remains intact
