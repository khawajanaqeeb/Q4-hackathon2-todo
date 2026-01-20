# Development Tasks for Phase 3: Todo AI Chatbot

## Overview

This document breaks down the implementation plan into small, testable tasks with clear acceptance criteria. Each task corresponds to elements defined in the specification documents: @specs/phase-3/spec.md, @specs/phase-3/architecture.md, @specs/phase-3/mcp-tools.md, @specs/phase-3/database-models.md, @specs/phase-3/chat-endpoint.md, and @specs/phase-3/plan.md.

## OpenAI Migration Tasks

### Migration Setup Tasks

#### TASK-OS-001: Install OpenAI Python SDK
**Description**: Install the OpenAI Python SDK as the primary dependency for the migration from Gemini to native OpenAI models.

**Acceptance Criteria**:
- [x] OpenAI SDK is installed in the project dependencies
- [x] Version compatibility verified with Python 3.13+
- [x] All existing dependencies remain functional
- [x] Installation instructions updated in documentation

**Dependencies**: None
**Estimate**: 1 story point

#### TASK-OS-002: Update Environment Configuration
**Description**: Update .env.example to remove GEMINI_API_KEY and add OPENAI_API_KEY documentation.

**Acceptance Criteria**:
- [x] GEMINI_API_KEY removed from .env.example
- [x] OPENAI_API_KEY entry added with proper documentation
- [x] Format example provided (sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
- [x] Security notes included about API key handling

**Dependencies**: None
**Estimate**: 1 story point

### Core Migration Tasks

#### TASK-OS-003: Remove Gemini-Specific Imports and Client Initialization
**Description**: Remove all Gemini-specific AsyncOpenAI configuration from the base agent file and related files.

**Acceptance Criteria**:
- [x] AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/") removed from all agent files
- [x] Gemini-specific imports removed from base.py and other agent files
- [x] No compilation errors after removal
- [x] Code passes linting checks

**Dependencies**: TASK-OS-001
**Estimate**: 2 story points

#### TASK-OS-004: Implement Native OpenAI Client Configuration
**Description**: Add native OpenAI AsyncOpenAI client with proper API key loading in the base agent.

**Acceptance Criteria**:
- [x] from openai import AsyncOpenAI imported correctly in base.py
- [x] openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) implemented
- [x] Error handling for missing API key implemented
- [x] Client initialization verified to work with environment variable

**Dependencies**: TASK-OS-001, TASK-OS-003
**Estimate**: 2 story points

#### TASK-OS-005: Update RunConfig for OpenAI Models
**Description**: Update RunConfig to use OpenAIChatCompletionsModel with native OpenAI client.

**Acceptance Criteria**:
- [x] config = RunConfig(model=OpenAIChatCompletionsModel(model="gpt-4o", openai_client=openai_client), ...) implemented
- [x] model_provider=openai_client configured properly
- [x] tracing_disabled=True set as specified
- [x] Configuration passes validation tests

**Dependencies**: TASK-OS-004
**Estimate**: 2 story points

### Agent-Specific Migration Tasks

#### TASK-OS-006: Update Router Agent Configuration
**Description**: Update router_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [x] Router agent imports and uses native OpenAI client
- [x] No Gemini-specific code remains in router agent
- [x] Agent initializes and runs without errors
- [x] Unit tests pass for router agent

**Dependencies**: TASK-OS-005
**Estimate**: 2 story points

#### TASK-OS-007: Update Add Task Agent Configuration
**Description**: Update add_task_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [x] Add task agent imports and uses native OpenAI client
- [x] No Gemini-specific code remains in add task agent
- [x] Agent initializes and runs without errors
- [x] Unit tests pass for add task agent

**Dependencies**: TASK-OS-005
**Estimate**: 2 story points

#### TASK-OS-008: Update List Tasks Agent Configuration
**Description**: Update list_tasks_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [x] List tasks agent imports and uses native OpenAI client
- [x] No Gemini-specific code remains in list tasks agent
- [x] Agent initializes and runs without errors
- [x] Unit tests pass for list tasks agent

**Dependencies**: TASK-OS-005
**Estimate**: 2 story points

#### TASK-OS-009: Update Complete Task Agent Configuration
**Description**: Update complete_task_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [x] Complete task agent imports and uses native OpenAI client
- [x] No Gemini-specific code remains in complete task agent
- [x] Agent initializes and runs without errors
- [x] Unit tests pass for complete task agent

**Dependencies**: TASK-OS-005
**Estimate**: 2 story points

#### TASK-OS-010: Update Update Task Agent Configuration
**Description**: Update update_task_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [x] Update task agent imports and uses native OpenAI client
- [x] No Gemini-specific code remains in update task agent
- [x] Agent initializes and runs without errors
- [x] Unit tests pass for update task agent

**Dependencies**: TASK-OS-005
**Estimate**: 2 story points

#### TASK-OS-011: Update Delete Task Agent Configuration
**Description**: Update delete_task_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [x] Delete task agent imports and uses native OpenAI client
- [x] No Gemini-specific code remains in delete task agent
- [x] Agent initializes and runs without errors
- [x] Unit tests pass for delete task agent

**Dependencies**: TASK-OS-005
**Estimate**: 2 story points

### Model and Configuration Updates

#### TASK-OS-012: Update Model Configuration to Use gpt-4o-mini
**Description**: Configure all agents to use gpt-4o-mini as the default model as specified in requirements.

**Acceptance Criteria**:
- [x] All agents configured to use gpt-4o-mini model
- [x] Model configuration centralized where appropriate
- [x] Configuration passes validation
- [x] Performance characteristics verified

**Dependencies**: TASK-OS-005
**Estimate**: 1 story point

### Documentation Updates

#### TASK-OS-013: Update README-phase3.md
**Description**: Update README-phase3.md to reflect OpenAI (gpt-4o) instead of Gemini and update setup instructions.

**Acceptance Criteria**:
- [x] All references to Gemini removed from README
- [x] OpenAI (gpt-4o) mentioned as the AI provider
- [x] Setup instructions updated to mention OPENAI_API_KEY
- [x] Gemini API key instructions removed
- [x] Installation and configuration steps updated

**Dependencies**: TASK-OS-002
**Estimate**: 1 story point

### Integration and Testing Tasks

#### TASK-OS-014: End-to-End Testing of OpenAI Integration
**Description**: Test the complete flow with native OpenAI models to ensure functionality is preserved.

**Acceptance Criteria**:
- [ ] All agents successfully connect to OpenAI API
- [ ] Chat functionality works end-to-end
- [ ] All existing features remain functional (agents, handoff pattern, MCP tools, DB operations, JWT auth, conversation persistence)
- [ ] Performance meets expectations
- [ ] Error handling works properly

**Dependencies**: TASK-OS-006 through TASK-OS-012
**Estimate**: 3 story points

#### TASK-OS-015: Update Quickstart Guide
**Description**: Update the quickstart guide with the new OpenAI configuration process.

**Acceptance Criteria**:
- [ ] Quickstart guide updated with OpenAI setup instructions
- [ ] Environment configuration steps updated
- [ ] Verification steps updated for OpenAI
- [ ] Troubleshooting section updated for OpenAI-specific issues

**Dependencies**: TASK-OS-013
**Estimate**: 1 story point

#### TASK-OS-016: Security Validation of OpenAI Integration
**Description**: Verify that the OpenAI integration maintains the same security standards as the previous implementation.

**Acceptance Criteria**:
- [ ] API key handling remains secure
- [ ] No sensitive information exposed in errors
- [ ] JWT authentication still enforced
- [ ] User isolation maintained
- [ ] Rate limiting and other security measures still effective

**Dependencies**: TASK-OS-014
**Estimate**: 2 story points

## Task Categories

### Database Infrastructure Tasks

#### TASK-001: Implement Conversation Model
**Description**: Create the SQLModel for Conversation entity following the specification in @specs/phase-3/database-models.md.

**Acceptance Criteria**:
- [ ] Model includes all fields specified: id, title, user_id, is_active, timestamps
- [ ] Proper foreign key relationship to User model
- [ ] Relationship to Message model is established
- [ ] Created and updated timestamp fields with proper defaults
- [ ] Model passes SQLModel validation
- [ ] Unit tests verify all model properties

**Dependencies**: None
**Estimate**: 2 story points

#### TASK-002: Implement Message Model
**Description**: Create the SQLModel for Message entity following the specification in @specs/phase-3/database-models.md.

**Acceptance Criteria**:
- [ ] Model includes all fields: id (UUID), conversation_id, role, content, status, tool info
- [ ] Proper enum types for MessageRole and MessageStatus
- [ ] Foreign key relationship to Conversation model
- [ ] JSON fields for tool_input and tool_output
- [ ] UUID primary key generation works correctly
- [ ] Unit tests verify all model properties

**Dependencies**: TASK-001
**Estimate**: 2 story points

#### TASK-003: Create Database Migrations
**Description**: Generate and test database migration scripts for Conversation and Message models.

**Acceptance Criteria**:
- [ ] Migration script creates conversation table with all required columns
- [ ] Migration script creates message table with all required columns
- [ ] Foreign key constraints are properly defined
- [ ] Indexes are created as specified in @specs/phase-3/database-models.md
- [ ] Migration can be applied and rolled back successfully
- [ ] Migration preserves existing Phase II data

**Dependencies**: TASK-001, TASK-002
**Estimate**: 1 story point

#### TASK-004: Implement Repository Classes
**Description**: Create repository classes for Conversation and Message operations.

**Acceptance Criteria**:
- [ ] Repository for Conversation with CRUD operations
- [ ] Repository for Message with CRUD operations
- [ ] Methods for loading conversation history
- [ ] Pagination support for message retrieval
- [ ] Proper error handling and validation
- [ ] Unit tests for all repository methods

**Dependencies**: TASK-001, TASK-002
**Estimate**: 3 story points

### MCP Tools Tasks

#### TASK-005: Implement add_task MCP Tool
**Description**: Create the MCP tool for adding tasks following the schema in @specs/phase-3/mcp-tools.md.

**Acceptance Criteria**:
- [ ] Tool schema matches specification exactly
- [ ] Validates input according to schema requirements
- [ ] Creates new Todo item in database
- [ ] Verifies user_id matches authenticated user
- [ ] Returns success response with task_id
- [ ] Handles all error cases with appropriate messages
- [ ] Unit tests cover all success and error paths

**Dependencies**: Database infrastructure tasks
**Estimate**: 3 story points

#### TASK-006: Implement list_tasks MCP Tool
**Description**: Create the MCP tool for listing tasks following the schema in @specs/phase-3/mcp-tools.md.

**Acceptance Criteria**:
- [ ] Tool schema matches specification exactly
- [ ] Applies all specified filters (status, priority, tags, etc.)
- [ ] Respects limit and offset parameters
- [ ] Verifies user_id matches authenticated user
- [ ] Returns properly formatted response with tasks
- [ ] Handles all error cases with appropriate messages
- [ ] Unit tests cover all filter combinations

**Dependencies**: Database infrastructure tasks
**Estimate**: 3 story points

#### TASK-007: Implement complete_task MCP Tool
**Description**: Create the MCP tool for completing tasks following the schema in @specs/phase-3/mcp-tools.md.

**Acceptance Criteria**:
- [ ] Tool schema matches specification exactly
- [ ] Validates task_id belongs to authenticated user
- [ ] Updates task completion status in database
- [ ] Returns success response with updated task info
- [ ] Handles all error cases with appropriate messages
- [ ] Unit tests cover success and error paths

**Dependencies**: Database infrastructure tasks
**Estimate**: 2 story points

#### TASK-008: Implement delete_task MCP Tool
**Description**: Create the MCP tool for deleting tasks following the schema in @specs/phase-3/mcp-tools.md.

**Acceptance Criteria**:
- [ ] Tool schema matches specification exactly
- [ ] Validates task_id belongs to authenticated user
- [ ] Deletes task from database
- [ ] Returns success response with confirmation
- [ ] Handles all error cases with appropriate messages
- [ ] Unit tests cover success and error paths

**Dependencies**: Database infrastructure tasks
**Estimate**: 2 story points

#### TASK-009: Implement update_task MCP Tool
**Description**: Create the MCP tool for updating tasks following the schema in @specs/phase-3/mcp-tools.md.

**Acceptance Criteria**:
- [ ] Tool schema matches specification exactly
- [ ] Validates task_id belongs to authenticated user
- [ ] Updates specified fields in database
- [ ] Returns success response with updated task info
- [ ] Handles all error cases with appropriate messages
- [ ] Unit tests cover all field update combinations

**Dependencies**: Database infrastructure tasks
**Estimate**: 3 story points

#### TASK-010: Implement MCP Tools Error Handling
**Description**: Create consistent error handling across all MCP tools.

**Acceptance Criteria**:
- [ ] All tools return errors in the format specified in @specs/phase-3/mcp-tools.md
- [ ] Common error codes are properly implemented
- [ ] Error messages are descriptive and helpful
- [ ] Authentication failures are handled consistently
- [ ] Database errors are wrapped appropriately
- [ ] Unit tests verify error responses

**Dependencies**: TASK-005 through TASK-009
**Estimate**: 2 story points

### Agent Infrastructure Tasks

#### TASK-011: Implement Base Agent Utilities
**Description**: Create shared utilities for agents including JWT handling and history loading.

**Acceptance Criteria**:
- [ ] Function to extract user_id from JWT token
- [ ] Function to load conversation history from database
- [ ] Function to format messages for AI consumption
- [ ] Proper error handling for JWT validation
- [ ] Unit tests for all utility functions
- [ ] Integration with existing Phase II auth system

**Dependencies**: Database infrastructure tasks
**Estimate**: 2 story points

#### TASK-012: Implement Router Agent
**Description**: Create the router agent that analyzes intent and routes to specialized agents.

**Acceptance Criteria**:
- [ ] Agent follows the system prompt in @specs/phase-3/architecture.md
- [ ] Correctly identifies all 5 intent types (add, list, complete, delete, update)
- [ ] Generates appropriate tool calls to specialized agents
- [ ] Handles non-task messages with direct responses
- [ ] Integrates with MCP tools schemas
- [ ] Unit tests for intent classification
- [ ] Integration tests for routing functionality

**Dependencies**: TASK-005 through TASK-010, TASK-011
**Estimate**: 4 story points

#### TASK-013: Implement Specialized Agents
**Description**: Create the 5 specialized agents for specific task operations.

**Acceptance Criteria**:
- [ ] add_task_agent connects to add_task MCP tool
- [ ] list_tasks_agent connects to list_tasks MCP tool
- [ ] complete_task_agent connects to complete_task MCP tool
- [ ] delete_task_agent connects to delete_task MCP tool
- [ ] update_task_agent connects to update_task MCP tool
- [ ] All agents validate user permissions
- [ ] All agents handle errors gracefully
- [ ] Unit tests for each specialized agent

**Dependencies**: TASK-005 through TASK-010, TASK-011
**Estimate**: 5 story points

### Chat Endpoint Tasks

#### TASK-014: Implement Chat Endpoint
**Description**: Create the main chat endpoint following @specs/phase-3/chat-endpoint.md.

**Acceptance Criteria**:
- [ ] Endpoint accepts POST requests at `/api/{user_id}/chat`
- [ ] Validates JWT token and verifies user_id match
- [ ] Loads conversation history from database
- [ ] Passes message to router agent
- [ ] Stores conversation history after processing
- [ ] Returns response in specified format
- [ ] Handles all error cases appropriately
- [ ] Unit tests for endpoint functionality

**Dependencies**: TASK-011 through TASK-013
**Estimate**: 4 story points

#### TASK-015: Implement Authentication Middleware
**Description**: Add authentication and authorization to the chat endpoint.

**Acceptance Criteria**:
- [ ] JWT token validation occurs for every request
- [ ] User ID in path matches authenticated user
- [ ] Appropriate error responses for auth failures
- [ ] Integration with existing Phase II auth system
- [ ] Unit tests for authentication logic
- [ ] Security testing for auth bypass attempts

**Dependencies**: TASK-014
**Estimate**: 2 story points

#### TASK-016: Implement Rate Limiting
**Description**: Add rate limiting to prevent abuse of the chat endpoint.

**Acceptance Criteria**:
- [ ] Per-user rate limiting (60 requests/minute)
- [ ] Per-IP rate limiting (100 requests/minute)
- [ ] Proper 429 responses when limits exceeded
- [ ] Retry-after header included in responses
- [ ] Configuration for rate limit values
- [ ] Unit tests for rate limiting logic

**Dependencies**: TASK-014
**Estimate**: 2 story points

### Integration and Testing Tasks

#### TASK-017: End-to-End Integration Tests
**Description**: Create comprehensive tests for the complete system flow.

**Acceptance Criteria**:
- [ ] Test complete flow: user message → router → specialized agent → MCP tool → response
- [ ] Verify conversation history is properly stored and retrieved
- [ ] Test all 5 agent types with various inputs
- [ ] Test error handling throughout the flow
- [ ] Test user isolation (users can't access others' data)
- [ ] Performance tests meet requirements

**Dependencies**: All previous tasks
**Estimate**: 4 story points

#### TASK-018: Security Validation
**Description**: Conduct security validation of the complete system.

**Acceptance Criteria**:
- [ ] Penetration testing for auth bypass
- [ ] SQL injection prevention verified
- [ ] Input sanitization confirmed
- [ ] User isolation verified through testing
- [ ] JWT token validation thoroughly tested
- [ ] Security scan results reviewed and addressed

**Dependencies**: All previous tasks
**Estimate**: 3 story points

#### TASK-019: Performance Optimization
**Description**: Optimize system performance to meet requirements.

**Acceptance Criteria**:
- [ ] 95th percentile response time < 2 seconds
- [ ] System handles 100 concurrent users
- [ ] Database queries optimized (< 100ms for common operations)
- [ ] AI token usage minimized
- [ ] Caching implemented where appropriate
- [ ] Load testing confirms performance targets

**Dependencies**: TASK-017
**Estimate**: 3 story points

#### TASK-020: Documentation and Deployment
**Description**: Complete documentation and prepare for deployment.

**Acceptance Criteria**:
- [ ] API documentation matches @specs/phase-3/chat-endpoint.md
- [ ] Installation and setup guide created
- [ ] Deployment scripts created
- [ ] Monitoring and alerting configured
- [ ] Runbooks created for operational tasks
- [ ] Code review completed by team

**Dependencies**: All previous tasks
**Estimate**: 2 story points

## Task Dependencies Summary

```
TASK-OS-001 ──┬── TASK-OS-003
              └── TASK-OS-004
TASK-OS-002 ──┴── TASK-OS-013
TASK-OS-003 ──┬── TASK-OS-005
              └── TASK-OS-004
TASK-OS-004 ──┴── TASK-OS-005
TASK-OS-005 ──┬── TASK-OS-006
              ├── TASK-OS-007
              ├── TASK-OS-008
              ├── TASK-OS-009
              ├── TASK-OS-010
              ├── TASK-OS-011
              └── TASK-OS-012
TASK-OS-006 ──┬── TASK-OS-014
              └── TASK-OS-007
TASK-OS-007 ──┬── TASK-OS-014
              └── TASK-OS-008
TASK-OS-008 ──┬── TASK-OS-014
              └── TASK-OS-009
TASK-OS-009 ──┬── TASK-OS-014
              └── TASK-OS-010
TASK-OS-010 ──┬── TASK-OS-014
              └── TASK-OS-011
TASK-OS-011 ──┴── TASK-OS-014
TASK-OS-012 ──┬── TASK-OS-014
              └── TASK-OS-015
TASK-OS-013 ──┴── TASK-OS-015
TASK-OS-014 ──┬── TASK-OS-016
              └── TASK-OS-015
TASK-OS-015 ──┴── TASK-OS-016
TASK-001 ──┬── TASK-003
           └── TASK-004
TASK-002 ──┬── TASK-003
           └── TASK-004
TASK-004 ──┬── TASK-005
           ├── TASK-006
           ├── TASK-007
           ├── TASK-008
           └── TASK-009
TASK-005 ──┬── TASK-010
           ├── TASK-012
           └── TASK-013
TASK-006 ──┬── TASK-010
           ├── TASK-012
           └── TASK-013
TASK-007 ──┬── TASK-010
           ├── TASK-012
           └── TASK-013
TASK-008 ──┬── TASK-010
           ├── TASK-012
           └── TASK-013
TASK-009 ──┬── TASK-010
           ├── TASK-012
           └── TASK-013
TASK-011 ──┬── TASK-012
           ├── TASK-013
           └── TASK-014
TASK-010 ──┬── TASK-012
           └── TASK-013
TASK-012 ──┬── TASK-014
           └── TASK-017
TASK-013 ──┬── TASK-014
           └── TASK-017
TASK-014 ──┬── TASK-015
           ├── TASK-016
           └── TASK-017
TASK-017 ──┬── TASK-018
           └── TASK-019
TASK-019 ──┴── TASK-020
```

## Sprint Planning

### Sprint 0 (Preparation)
- TASK-OS-001: Install OpenAI Python SDK
- TASK-OS-002: Update Environment Configuration

### Sprint 1 (Migration)
- TASK-OS-003: Remove Gemini-Specific Imports and Client Initialization
- TASK-OS-004: Implement Native OpenAI Client Configuration
- TASK-OS-005: Update RunConfig for OpenAI Models

### Sprint 2 (Agent Updates)
- TASK-OS-006: Update Router Agent Configuration
- TASK-OS-007: Update Add Task Agent Configuration
- TASK-OS-008: Update List Tasks Agent Configuration
- TASK-OS-009: Update Complete Task Agent Configuration
- TASK-OS-010: Update Update Task Agent Configuration
- TASK-OS-011: Update Delete Task Agent Configuration
- TASK-OS-012: Update Model Configuration to Use gpt-4o-mini

### Sprint 3 (Integration and Documentation)
- TASK-OS-013: Update README-phase3.md
- TASK-OS-014: End-to-End Testing of OpenAI Integration
- TASK-OS-015: Update Quickstart Guide
- TASK-OS-016: Security Validation of OpenAI Integration

### Sprint 4 (Core Phase 3 Implementation)
- TASK-001: Implement Conversation Model
- TASK-002: Implement Message Model
- TASK-003: Create Database Migrations
- TASK-004: Implement Repository Classes

### Sprint 5 (MCP Tools)
- TASK-005: Implement add_task MCP Tool
- TASK-006: Implement list_tasks MCP Tool
- TASK-007: Implement complete_task MCP Tool
- TASK-008: Implement delete_task MCP Tool
- TASK-009: Implement update_task MCP Tool
- TASK-010: Implement MCP Tools Error Handling

### Sprint 6 (Agent Infrastructure)
- TASK-011: Implement Base Agent Utilities
- TASK-012: Implement Router Agent
- TASK-013: Implement Specialized Agents
- TASK-014: Implement Chat Endpoint

### Sprint 7 (Final Integration)
- TASK-015: Implement Authentication Middleware
- TASK-016: Implement Rate Limiting
- TASK-017: End-to-End Integration Tests
- TASK-018: Security Validation
- TASK-019: Performance Optimization
- TASK-020: Documentation and Deployment