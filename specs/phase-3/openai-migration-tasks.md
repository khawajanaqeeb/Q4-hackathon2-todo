# Development Tasks for OpenAI Migration: Switch from Gemini to Native OpenAI Models

## Overview

This document breaks down the implementation of the OpenAI migration feature into small, testable tasks with clear acceptance criteria. Each task corresponds to elements defined in the specification documents: @specs/phase-3/spec.md, @specs/phase-3/plan.md, @specs/phase-3/data-model.md, @specs/phase-3/research.md, and @specs/phase-3/quickstart.md.

## Task Categories

### Setup Tasks

#### TASK-001: Install OpenAI Python SDK
**Description**: Install the OpenAI Python SDK as the primary dependency for the migration.

**Acceptance Criteria**:
- [ ] OpenAI SDK is installed in the project dependencies
- [ ] Version compatibility verified with Python 3.13+
- [ ] All existing dependencies remain functional
- [ ] Installation instructions updated in documentation

**Dependencies**: None
**Estimate**: 1 story point

#### TASK-002: Update Environment Configuration
**Description**: Update .env.example to remove GEMINI_API_KEY and add OPENAI_API_KEY documentation.

**Acceptance Criteria**:
- [ ] GEMINI_API_KEY removed from .env.example
- [ ] OPENAI_API_KEY entry added with proper documentation
- [ ] Format example provided (sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
- [ ] Security notes included about API key handling

**Dependencies**: None
**Estimate**: 1 story point

### Core Migration Tasks

#### TASK-003: Remove Gemini-Specific Imports and Client Initialization
**Description**: Remove all Gemini-specific AsyncOpenAI configuration from the base agent file.

**Acceptance Criteria**:
- [ ] AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/") removed
- [ ] Gemini-specific imports removed from base.py
- [ ] No compilation errors after removal
- [ ] Code passes linting checks

**Dependencies**: TASK-001
**Estimate**: 2 story points

#### TASK-004: Implement Native OpenAI Client Configuration
**Description**: Add native OpenAI AsyncOpenAI client with proper API key loading.

**Acceptance Criteria**:
- [ ] from openai import AsyncOpenAI imported correctly
- [ ] openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) implemented
- [ ] Error handling for missing API key implemented
- [ ] Client initialization verified to work with environment variable

**Dependencies**: TASK-001, TASK-003
**Estimate**: 2 story points

#### TASK-005: Update RunConfig for OpenAI Models
**Description**: Update RunConfig to use OpenAIChatCompletionsModel with native OpenAI client.

**Acceptance Criteria**:
- [ ] config = RunConfig(model=OpenAIChatCompletionsModel(model="gpt-4o", openai_client=openai_client), ...) implemented
- [ ] model_provider=openai_client configured properly
- [ ] tracing_disabled=True set as specified
- [ ] Configuration passes validation tests

**Dependencies**: TASK-004
**Estimate**: 2 story points

### Agent-Specific Migration Tasks

#### TASK-006: Update Router Agent Configuration
**Description**: Update router_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [ ] Router agent imports and uses native OpenAI client
- [ ] No Gemini-specific code remains in router agent
- [ ] Agent initializes and runs without errors
- [ ] Unit tests pass for router agent

**Dependencies**: TASK-005
**Estimate**: 2 story points

#### TASK-007: Update Add Task Agent Configuration
**Description**: Update add_task_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [ ] Add task agent imports and uses native OpenAI client
- [ ] No Gemini-specific code remains in add task agent
- [ ] Agent initializes and runs without errors
- [ ] Unit tests pass for add task agent

**Dependencies**: TASK-005
**Estimate**: 2 story points

#### TASK-008: Update List Tasks Agent Configuration
**Description**: Update list_tasks_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [ ] List tasks agent imports and uses native OpenAI client
- [ ] No Gemini-specific code remains in list tasks agent
- [ ] Agent initializes and runs without errors
- [ ] Unit tests pass for list tasks agent

**Dependencies**: TASK-005
**Estimate**: 2 story points

#### TASK-009: Update Complete Task Agent Configuration
**Description**: Update complete_task_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [ ] Complete task agent imports and uses native OpenAI client
- [ ] No Gemini-specific code remains in complete task agent
- [ ] Agent initializes and runs without errors
- [ ] Unit tests pass for complete task agent

**Dependencies**: TASK-005
**Estimate**: 2 story points

#### TASK-010: Update Update Task Agent Configuration
**Description**: Update update_task_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [ ] Update task agent imports and uses native OpenAI client
- [ ] No Gemini-specific code remains in update task agent
- [ ] Agent initializes and runs without errors
- [ ] Unit tests pass for update task agent

**Dependencies**: TASK-005
**Estimate**: 2 story points

#### TASK-011: Update Delete Task Agent Configuration
**Description**: Update delete_task_agent.py to use native OpenAI configuration.

**Acceptance Criteria**:
- [ ] Delete task agent imports and uses native OpenAI client
- [ ] No Gemini-specific code remains in delete task agent
- [ ] Agent initializes and runs without errors
- [ ] Unit tests pass for delete task agent

**Dependencies**: TASK-005
**Estimate**: 2 story points

### Model and Configuration Updates

#### TASK-012: Update Model Configuration to Use gpt-4o-mini
**Description**: Configure all agents to use gpt-4o-mini as the default model as specified in requirements.

**Acceptance Criteria**:
- [ ] All agents configured to use gpt-4o-mini model
- [ ] Model configuration centralized where appropriate
- [ ] Configuration passes validation
- [ ] Performance characteristics verified

**Dependencies**: TASK-005
**Estimate**: 1 story point

### Documentation Updates

#### TASK-013: Update README-phase3.md
**Description**: Update README-phase3.md to reflect OpenAI (gpt-4o) instead of Gemini and update setup instructions.

**Acceptance Criteria**:
- [ ] All references to Gemini removed from README
- [ ] OpenAI (gpt-4o) mentioned as the AI provider
- [ ] Setup instructions updated to mention OPENAI_API_KEY
- [ ] Gemini API key instructions removed
- [ ] Installation and configuration steps updated

**Dependencies**: TASK-002
**Estimate**: 1 story point

### Integration and Testing Tasks

#### TASK-014: End-to-End Testing of OpenAI Integration
**Description**: Test the complete flow with native OpenAI models to ensure functionality is preserved.

**Acceptance Criteria**:
- [ ] All agents successfully connect to OpenAI API
- [ ] Chat functionality works end-to-end
- [ ] All existing features remain functional (agents, handoff pattern, MCP tools, DB operations, JWT auth, conversation persistence)
- [ ] Performance meets expectations
- [ ] Error handling works properly

**Dependencies**: TASK-006 through TASK-012
**Estimate**: 3 story points

#### TASK-015: Update Quickstart Guide
**Description**: Update the quickstart guide with the new OpenAI configuration process.

**Acceptance Criteria**:
- [ ] Quickstart guide updated with OpenAI setup instructions
- [ ] Environment configuration steps updated
- [ ] Verification steps updated for OpenAI
- [ ] Troubleshooting section updated for OpenAI-specific issues

**Dependencies**: TASK-013
**Estimate**: 1 story point

#### TASK-016: Security Validation of OpenAI Integration
**Description**: Verify that the OpenAI integration maintains the same security standards as the previous implementation.

**Acceptance Criteria**:
- [ ] API key handling remains secure
- [ ] No sensitive information exposed in errors
- [ ] JWT authentication still enforced
- [ ] User isolation maintained
- [ ] Rate limiting and other security measures still effective

**Dependencies**: TASK-014
**Estimate**: 2 story points

## Task Dependencies Summary

```
TASK-001 ──┬── TASK-003
           └── TASK-004
TASK-002 ──┴── TASK-013
TASK-003 ──┬── TASK-005
           └── TASK-004
TASK-004 ──┴── TASK-005
TASK-005 ──┬── TASK-006
           ├── TASK-007
           ├── TASK-008
           ├── TASK-009
           ├── TASK-010
           ├── TASK-011
           └── TASK-012
TASK-006 ──┬── TASK-014
           └── TASK-007
TASK-007 ──┬── TASK-014
           └── TASK-008
TASK-008 ──┬── TASK-014
           └── TASK-009
TASK-009 ──┬── TASK-014
           └── TASK-010
TASK-010 ──┬── TASK-014
           └── TASK-011
TASK-011 ──┴── TASK-014
TASK-012 ──┬── TASK-014
           └── TASK-015
TASK-013 ──┴── TASK-015
TASK-014 ──┬── TASK-016
           └── TASK-015
TASK-015 ──┴── TASK-016
```

## Sprint Planning

### Sprint 1 (Week 1)
- TASK-001: Install OpenAI Python SDK
- TASK-002: Update Environment Configuration
- TASK-003: Remove Gemini-Specific Imports and Client Initialization
- TASK-004: Implement Native OpenAI Client Configuration
- TASK-005: Update RunConfig for OpenAI Models

### Sprint 2 (Week 2)
- TASK-006: Update Router Agent Configuration
- TASK-007: Update Add Task Agent Configuration
- TASK-008: Update List Tasks Agent Configuration
- TASK-009: Update Complete Task Agent Configuration
- TASK-010: Update Update Task Agent Configuration
- TASK-011: Update Delete Task Agent Configuration
- TASK-012: Update Model Configuration to Use gpt-4o-mini

### Sprint 3 (Week 3)
- TASK-013: Update README-phase3.md
- TASK-014: End-to-End Testing of OpenAI Integration
- TASK-015: Update Quickstart Guide
- TASK-016: Security Validation of OpenAI Integration