# Tasks: Phase 3 Chatbot Enhancement

**Input**: Design documents from `/specs/phase-3/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No explicit test requests in feature specification - tests are NOT included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths adjusted based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for Phase 3 enhancements

- [X] T001 Create project structure with MCP tools directory per implementation plan
- [X] T002 [P] Install MCP SDK dependency in backend requirements.txt
- [X] T003 [P] Install OpenAI Agents SDK dependency in backend requirements.txt
- [X] T004 [P] Install frontend ChatKit dependency in frontend package.json
- [X] T005 Set up environment variables for OpenAI and MCP server in .env files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Setup conversation database schema and migrations
- [X] T007 [P] Implement conversation models in backend/src/models/conversation.py
- [X] T008 [P] Setup MCP server integration framework in backend/src/services/mcp_integration.py
- [X] T009 Create todo tools models that all stories depend on
- [X] T010 Configure streaming response middleware for chat endpoints
- [X] T011 Setup MCP tool validation and security framework

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Todo Management Through Chatbot (Priority: P2) 🎯

**Goal**: Enable users to manage todos through natural language chat so that they can interact with their todo list more naturally

**Independent Test**: User can initiate a chat conversation, issue natural language commands (e.g., "Create a new todo called 'Buy groceries'"), and see the todo appear in both chat responses and traditional UI

### Implementation for User Story 1

- [X] T012 [P] [US3] Create Conversation model in backend/src/models/conversation.py
- [X] T013 [P] [US3] Create Message model in backend/src/models/conversation.py
- [X] T014 [US3] Implement ConversationService in backend/src/services/conversation_service.py
- [X] T015 [US3] Create TodoOperationLog model in backend/src/models/conversation.py
- [X] T016 [P] [US3] Implement chat endpoint in backend/src/api/chat.py
- [X] T017 [US3] Implement basic OpenAI Agent configuration in backend/src/services/openai_agent.py
- [X] T018 [P] [US3] Implement create_todo MCP tool in backend/src/tools/todo_tools.py
- [X] T019 [P] [US3] Implement list_todos MCP tool in backend/src/tools/todo_tools.py
- [X] T020 [P] [US3] Implement update_todo MCP tool in backend/src/tools/todo_tools.py
- [X] T021 [P] [US3] Implement delete_todo MCP tool in backend/src/tools/todo_tools.py
- [X] T022 [P] [US3] Implement complete_todo MCP tool in backend/src/tools/todo_tools.py
- [X] T023 [US3] Connect MCP tools to existing SQLModel todo models
- [X] T024 [US3] Add authentication validation to all MCP tools using existing auth dependency
- [X] T025 [US3] Integrate conversation persistence with chat endpoint
- [X] T026 [US3] Implement streaming response (SSE) for chat endpoint
- [X] T027 [US3] Test chatbot can create todos and they appear in traditional UI

**Checkpoint**: At this point, User Story 3 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Chat Interface Integration (Priority: P2)

**Goal**: Provide a complete chat UI experience that integrates seamlessly with existing authentication and shows todo management capabilities

**Independent Test**: User can navigate to chat page, authenticate using existing system, start conversations, issue todo commands, and see responses with proper context maintenance

### Implementation for User Story 2

- [X] T028 [P] [US3] Create ChatInterface component in frontend/components/ChatInterface.tsx
- [X] T029 [P] [US3] Create ChatKitInterface component in frontend/components/ChatKitInterface.tsx
- [X] T030 [US3] Implement chat API service in frontend/src/services/chatApi.js
- [X] T031 [US3] Add chat route/page in frontend/app/chat/page.tsx
- [X] T032 [US3] Integrate authentication context with chat components
- [X] T033 [US3] Connect frontend to backend chat endpoint with proper auth headers
- [X] T034 [US3] Implement conversation history display in chat UI
- [X] T035 [US3] Add conversation management (new conversation, switch conversations)
- [X] T036 [US3] Test end-to-end chatbot todo management flow with UI

**Checkpoint**: At this point, Chat Interface integration should be fully functional and testable independently

---

## Phase 5: User Story 3 - Session Management and Security for Chat (Priority: P2)

**Goal**: Ensure chat conversations are properly managed with security and maintain user data isolation

**Independent Test**: User sessions are properly maintained in chat, user data is isolated between users, API rate limiting works, and MCP server validates user identity properly

### Implementation for User Story 3

- [X] T037 [P] [US4] Implement conversation session expiration in backend/src/services/conversation_service.py
- [X] T038 [US4] Add rate limiting to chat endpoint in backend/src/api/chat.py
- [X] T039 [US4] Implement user data isolation validation in all MCP tools
- [X] T040 [US4] Add comprehensive authorization checks to MCP tools using existing auth dependency
- [X] T041 [US4] Implement proper conversation cleanup and archiving
- [X] T042 [US4] Add security audit logging for chat interactions
- [X] T043 [US4] Test user data isolation between different authenticated users
- [X] T044 [US4] Verify MCP server properly validates user identity before executing todo operations

**Checkpoint**: All chatbot security and session management should be fully functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final integration

- [X] T045 [P] Documentation updates for chatbot functionality in docs/
- [X] T046 Code cleanup and refactoring across chatbot components
- [X] T047 Performance optimization for chat streaming responses
- [X] T048 Security hardening and validation across all chat components
- [X] T049 Run quickstart.md validation for chatbot features
- [X] T050 End-to-end testing of all chatbot features with existing todo functionality

## Phase 7: Authentication Error Resolution

**Purpose**: Fix authentication issues that were identified during testing

- [X] T051 Analysis of 401/422 errors in authentication endpoints
- [X] T052 Fix HTTP-only cookie setting with proper security attributes
- [X] T053 Enhance token validation with cookie-header fallback mechanism
- [X] T054 Update registration endpoint validation to prevent 422 errors
- [X] T055 Verify authentication flow consistency across all endpoints

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P2 → P2 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (US3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (US3)**: Depends on User Story 1 (basic chat functionality)
- **User Story 3 (US4)**: Can start after Foundational but should integrate with US1/US2 components

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Create Conversation model in backend/src/models/conversation.py"
Task: "Create Message model in backend/src/models/conversation.py"

# Launch all MCP tools for User Story 1 together:
Task: "Implement create_todo MCP tool in backend/src/tools/todo_tools.py"
Task: "Implement list_todos MCP tool in backend/src/tools/todo_tools.py"
Task: "Implement update_todo MCP tool in backend/src/tools/todo_tools.py"
Task: "Implement delete_todo MCP tool in backend/src/tools/todo_tools.py"
Task: "Implement complete_todo MCP tool in backend/src/tools/todo_tools.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Basic chatbot with todo operations)
4. **STOP and VALIDATE**: Test chatbot functionality independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test chatbot todo management independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test UI integration → Deploy/Demo
4. Add User Story 3 → Test security and session management → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Backend chat & MCP tools)
   - Developer B: User Story 2 (Frontend chat UI)
   - Developer C: User Story 3 (Security & session management)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence