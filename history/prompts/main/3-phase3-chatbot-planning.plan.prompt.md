---
id: 3
title: "phase3-chatbot-planning"
stage: "plan"
date_iso: "2026-02-05"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "main"
branch: "main"
user: "NAQEEB"
command: "/sp.plan"
labels: ["chatbot", "planning", "architecture", "phase3", "mcp", "openai-agents"]
links:
  spec: "specs/phase-3/spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - specs/phase-3/plan.md
  - specs/phase-3/research.md
  - specs/phase-3/data-model.md
  - specs/phase-3/quickstart.md
  - specs/phase-3/contracts/chat-api.yaml
tests_yaml: []
prompt_text: |
  /sp.plan

  You must follow the SDD workflow strictly.
  This step is PLANNING ONLY. Do NOT implement code.

  Repository:
  https://github.com/khawajanaqeeb/Q4-hackathon2-todo

  Branch:
  - main

  Context:
  Phase 2 (fullstack todo app) is COMPLETE and WORKING.
  Authentication is FIXED and DOCUMENTED using a cookie-based model.

  Phase 3 is an ENHANCEMENT, not a rewrite.
  All Phase 2 functionality must remain intact.

  ---

  ## PHASE 3 OBJECTIVE

  Enhance the existing Phase 2 todo application by adding a chatbot system that allows users to manage todos conversationally, while preserving:
  - existing APIs
  - existing database schema
  - existing authentication contract

  ---

  ## PHASE 3 REQUIREMENTS (AUTHORITATIVE)

  1. Implement conversational interface for all Basic Level todo features
  2. Use OpenAI Agents SDK for AI logic
  3. Build MCP server using the Official MCP SDK
  4. Chat endpoint must be stateless and persist conversation state in DB
  5. AI agents must use MCP tools to manage tasks
  6. MCP tools must be stateless and store state via database
  7. Authentication must reuse existing cookie-based auth (no new auth)

  ---

  ## TECHNOLOGY CONSTRAINTS

  Frontend:
  - Next.js (App Router)
  - OpenAI ChatKit
  - Existing AuthContext and middleware remain unchanged

  Backend:
  - FastAPI
  - SQLModel
  - Existing task APIs preserved
  - New chat + MCP endpoints added incrementally

  AI:
  - OpenAI Agents SDK (authoritative for reasoning)
  - No custom LLM orchestration outside Agents SDK

  MCP:
  - Official MCP SDK only
  - MCP server must NOT introduce new auth logic

  Database:
  - Neon PostgreSQL
  - Existing tables preserved
  - New tables allowed only for conversation state

  ---

  ## PLANNING OUTPUT REQUIRED

  Produce a clear, phased implementation plan that includes:

  ### 1. Architecture Overview
  - High-level diagram (described in text) showing:
    - Frontend → ChatKit
    - Backend chat endpoint
    - OpenAI Agent
    - MCP server
    - Database
  - Explicit explanation of how auth context flows unchanged

  ---

  ### 2. Component Breakdown

  For EACH of the following, describe responsibilities and boundaries:

  - Chat UI (frontend)
  - Chat API endpoint (backend)
  - OpenAI Agent configuration
  - MCP server
  - MCP tools (task CRUD)
  - Conversation persistence layer

  ---

  ### 3. Conversation State Strategy

  Define:
  - What data is persisted (messages, tool calls, user id)
  - Where it is stored (DB tables)
  - How statelessness is preserved at API/tool level
  - How conversation resumes safely

  ---

  ### 4. MCP Tool Design

  Plan MCP tools for:
  - create_todo
  - list_todos
  - update_todo
  - delete_todo
  - complete_todo

  Each tool must:
  - Be stateless
  - Accept user context from backend
  - Use existing SQLModel models
  - Enforce authorization via existing auth dependency

  ---

  ### 5. Incremental Delivery Plan

  Break Phase 3 into ordered milestones, for example:
  - Milestone 1: Chat endpoint scaffold
  - Milestone 2: Agent setup with no tools
  - Milestone 3: MCP server + tools
  - Milestone 4: Conversation persistence
  - Milestone 5: Frontend ChatKit integration
  - Milestone 6: End-to-end verification

  Each milestone must:
response_text: |
  Successfully created comprehensive implementation plan for Phase 3 chatbot enhancement. The plan includes:

  1. Detailed architecture overview with system components and authentication flow
  2. Component breakdown defining responsibilities for Chat UI, Chat API, OpenAI Agent, MCP server, MCP tools, and conversation persistence
  3. Conversation state strategy defining data persistence, storage location, and statelessness preservation
  4. MCP tool design specifying 5 core todo operation tools (create, list, update, delete, complete)
  5. Incremental delivery plan with 6 milestones for phased implementation

  Supporting documentation created:
  - research.md: Research findings on architecture patterns and technology decisions
  - data-model.md: Entity definitions for Conversation, Message, and TodoOperationLog
  - quickstart.md: Setup instructions for the enhanced system
  - contracts/chat-api.yaml: OpenAPI specification for chat endpoints

  All Phase 2 functionality is preserved while adding new chatbot capabilities that follow the required constraints:
  - Cookie-based authentication remains unchanged
  - MCP server uses official SDK without new auth logic
  - OpenAI Agents SDK is used for AI logic
  - Existing APIs and database schema are preserved
  - New functionality is added incrementally
outcome: "Complete implementation plan for Phase 3 chatbot enhancement created"
evaluation: "Plan satisfies all requirements and constraints while preserving existing functionality"
---