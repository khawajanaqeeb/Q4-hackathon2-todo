# Feature Specification: Switch Phase 3 Backend to Native OpenAI Models

**Feature Branch**: `001-switch-openai-models`
**Created**: 2026-01-21
**Status**: Draft
**Input**: User description: "Switch the entire Phase 3 backend to use native OpenAI models instead of the Gemini compatibility layer. Use real OpenAI API key from phase3-chatbot/.env as OPENAI_API_KEY, remove all Gemini-specific code, and update configurations to use OpenAI AsyncOpenAI client with gpt-4o-mini model."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Switch Model Provider (Priority: P1)

As a developer maintaining the Phase 3 chatbot, I want to replace the Google Gemini compatibility layer with native OpenAI models so that the system uses our purchased OpenAI API key and benefits from OpenAI's advanced capabilities.

**Why this priority**: This is the foundational change that enables all other functionality to work with the new model provider. Without this change, the entire chatbot system cannot function properly.

**Independent Test**: Can be fully tested by verifying that the chatbot agents successfully connect to OpenAI API using the provided OPENAI_API_KEY and can generate responses using the gpt-4o-mini model.

**Acceptance Scenarios**:

1. **Given** the application is configured with OPENAI_API_KEY in .env, **When** an agent makes a request to the LLM, **Then** the request is sent to OpenAI API using the native AsyncOpenAI client
2. **Given** the application has removed Gemini-specific configuration, **When** the application starts up, **Then** it connects successfully to OpenAI API without any Gemini-related errors

---

### User Story 2 - Update Agent Configurations (Priority: P2)

As a system administrator, I want all agent files to be updated to use the native OpenAI configuration so that all specialized agents (router, add_task, list_tasks, complete_task, update_task, delete_task) work consistently with the new model provider.

**Why this priority**: Ensures consistent behavior across all specialized agents in the multi-agent system. Each agent needs to be properly configured to use the new OpenAI model.

**Independent Test**: Can be tested by verifying that each individual agent file correctly imports and configures the OpenAI client without any Gemini-specific code.

**Acceptance Scenarios**:

1. **Given** an agent file (e.g., router_agent.py), **When** the file is loaded, **Then** it uses native OpenAI AsyncOpenAI client instead of Gemini compatibility layer

---

### User Story 3 - Update Environment Configuration (Priority: P3)

As a developer setting up the application, I want the .env.example and README to reflect the new OpenAI requirements so that other team members can properly configure their environments.

**Why this priority**: Enables proper onboarding and deployment for other team members. Documentation is essential for maintainability.

**Independent Test**: Can be tested by reviewing the updated documentation and verifying that it guides users to set up OPENAI_API_KEY instead of GEMINI_API_KEY.

**Acceptance Scenarios**:

1. **Given** a developer reading the updated documentation, **When** they follow the setup instructions, **Then** they configure OPENAI_API_KEY in their .env file

---

### Edge Cases

- What happens when the OPENAI_API_KEY is invalid or expired?
- How does the system handle OpenAI API rate limiting or service unavailability?
- What occurs when network connectivity to OpenAI services is interrupted?
- How does the system behave if there are model availability issues with gpt-4o-mini?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST remove all Gemini-specific code including AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
- **FR-002**: System MUST remove all references to gemini-2.0-flash or similar Gemini models
- **FR-003**: System MUST remove external_client creation and passing mechanisms
- **FR-004**: System MUST import AsyncOpenAI from openai using standard client configuration
- **FR-005**: System MUST load OpenAI API key directly from environment variable OPENAI_API_KEY
- **FR-006**: System MUST configure agents to use gpt-4o-mini as the default model
- **FR-007**: System MUST update RunConfig to use OpenAIChatCompletionsModel with native OpenAI client
- **FR-008**: System MUST update all agent files (base.py, router_agent.py, add_task_agent.py, list_tasks_agent.py, complete_task_agent.py, update_task_agent.py, delete_task_agent.py) to use native OpenAI configuration
- **FR-009**: System MUST update .env.example to remove GEMINI_API_KEY and add OPENAI_API_KEY documentation
- **FR-010**: System MUST update README-phase3.md to reflect OpenAI (gpt-4o) instead of Gemini
- **FR-011**: System MUST preserve all existing functionality including agents, handoff pattern, MCP tools, DB operations, JWT auth, and conversation persistence

### Key Entities

- **OpenAI Client**: The native AsyncOpenAI client that interfaces with OpenAI API using the provided API key
- **Model Configuration**: The RunConfig settings that define which model (gpt-4o-mini) and client to use for LLM operations
- **Agent Files**: Individual Python files for each specialized agent that need to be updated to use the new OpenAI configuration

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All agent files successfully connect to OpenAI API using the native AsyncOpenAI client without any Gemini-related configuration
- **SC-002**: The system operates with gpt-4o-mini as the primary model without any fallback to Gemini models
- **SC-003**: All existing functionality remains intact after the transition (agents, handoff pattern, MCP tools, DB operations, JWT auth, conversation persistence)
- **SC-004**: Developers can successfully set up the environment using OPENAI_API_KEY instead of GEMINI_API_KEY as documented in the updated README
- **SC-005**: The application starts up successfully and all agents respond appropriately to user queries through the OpenAI API
