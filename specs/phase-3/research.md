# Research: Phase 3 Chatbot Enhancement

## Overview
This document captures the research findings for enhancing the existing Phase 2 todo application with a conversational chatbot system.

**Iteration 1 placeholder — to be expanded during /sp.tasks and /sp.implement**

## Decision: Architecture Pattern
**Rationale**: Use logically separated components within a single FastAPI application to maintain separation of concerns while preserving existing monolithic structure for core functionality.
**Alternatives considered**:
- Monolithic expansion: Keep all functionality in existing FastAPI app
- Full service decomposition: Split into multiple services

## Decision: OpenAI Agent Configuration
**Rationale**: Use OpenAI Assistants API for advanced conversation memory and tool usage rather than basic completions API.
**Alternatives considered**:
- OpenAI Completions API: Simpler but less capable of maintaining conversation context
- Custom LLM orchestration: More flexible but violates constraint of using only OpenAI Agents SDK

## Decision: MCP Server Implementation
**Rationale**: Implement MCP server separately from main backend to maintain clean separation between AI orchestration and business logic.
**Alternatives considered**:
- Inline MCP tools: Embed directly in main FastAPI app
- Direct API calls: Call todo endpoints from agent directly

## Decision: Conversation State Management
**Rationale**: Store conversation state in database for persistence and scalability while keeping API endpoints stateless.
**Alternatives considered**:
- Client-side storage: Less secure and doesn't persist across sessions
- In-memory storage: Loses state on server restart
- External cache (Redis): Adds infrastructure complexity

## Decision: Frontend Integration
**Rationale**: Use OpenAI's ChatKit components for fastest implementation with best practices baked in.
**Alternatives considered**:
- Custom chat UI: More control but more development time
- Third-party chat libraries: Potential compatibility issues

## Decision: Authentication Flow for MCP
**Rationale**: Pass user authentication context from backend to MCP tools via secure context passing mechanism.
**Alternatives considered**:
- Separate MCP authentication: Would violate "no new auth" constraint
- Token forwarding: Security concerns with token handling

## Key Findings

### OpenAI Agents SDK Best Practices
- Use Assistants API for conversation state management
- Leverage built-in tool calling for MCP integration
- Implement proper error handling for tool failures

### MCP SDK Integration
- MCP tools must be stateless and idempotent
- Tools should validate user context passed from backend
- Error handling should be robust for network failures

### Database Schema Extension
- Need to extend existing schema with conversation and message tables
- Maintain referential integrity with existing user and todo tables
- Optimize for read-heavy conversation history access

### Security Considerations
- Ensure all user data isolation is maintained
- Validate authorization in every MCP tool call
- Sanitize all user inputs before processing

### Performance Optimization
- Implement efficient conversation history pagination
- Cache frequently accessed data where appropriate
- Optimize database queries for conversation retrieval