# Implementation Plan: Switch Phase 3 Backend to Native OpenAI Models

**Branch**: `001-switch-openai-models` | **Date**: 2026-01-21 | **Spec**: [specs/phase-3/spec.md](./spec.md)
**Input**: Feature specification from `/specs/phase-3/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan outlines the migration of the Phase 3 chatbot backend from Google Gemini compatibility layer to native OpenAI models. The primary requirement is to replace all Gemini-specific configurations with native OpenAI AsyncOpenAI client using the purchased OpenAI API key. This involves updating all agent files, configuration, and documentation while preserving all existing functionality including agents, handoff pattern, MCP tools, DB operations, JWT auth, and conversation persistence.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: OpenAI Python SDK, FastAPI, SQLModel, Better Auth
**Storage**: Neon Serverless PostgreSQL (via SQLModel ORM)
**Testing**: pytest
**Target Platform**: Linux server (cloud deployment)
**Project Type**: Web application (backend API services)
**Performance Goals**: Maintain current response times with improved reliability via native OpenAI integration
**Constraints**: Must preserve all existing functionality, maintain backward compatibility with current agent patterns, ensure secure API key handling
**Scale/Scope**: Support current user base and anticipated growth with OpenAI's reliable infrastructure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **SDD Mandate**: ✓ Plan follows Spec-Driven Development by building on the existing spec.md
2. **Workflow Compliance**: ✓ Following Phase III technology stack requirements (OpenAI Agents SDK, MCP tools)
3. **Phase Constraints**: ✓ Working within Phase III scope (AI-powered chatbot with OpenAI integration)
4. **Security Requirements**: ✓ Maintaining Better Auth JWT user isolation and secure API key handling
5. **Code Quality**: ✓ Will maintain PEP 8 compliance and type hints as specified in constitution
6. **Feature Progression**: ✓ Building on existing Phase III features without removing functionality

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
phase3-chatbot/
├── backend/
│   ├── agents/
│   │   ├── base.py
│   │   ├── router_agent.py
│   │   ├── add_task_agent.py
│   │   ├── list_tasks_agent.py
│   │   ├── complete_task_agent.py
│   │   ├── update_task_agent.py
│   │   └── delete_task_agent.py
│   ├── api/
│   ├── models/
│   ├── database/
│   ├── auth/
│   ├── mcp_tools/
│   └── main.py
├── frontend/
├── .env
├── .env.example
└── README-phase3.md
```

**Structure Decision**: The migration affects the backend agent files in phase3-chatbot/backend/agents/ and related configuration files. The structure maintains the existing Phase III architecture while updating the LLM integration layer.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None] | [N/A] | [N/A] |
