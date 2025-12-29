---
id: 002
title: Phase I Architectural Plan
stage: plan
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5
feature: phase1-console-todo
branch: master
user: khawajanaqeeb
command: /sp.plan
labels: ["phase-1", "architecture", "planning", "design", "layered-architecture"]
links:
  spec: specs/phase-1/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phase-1/plan.md
tests:
  - Architecture validates against constitution (all articles compliant)
  - Design supports all 15 functional requirements from spec
---

## Prompt

**Phase**: Phase I – Todo In-Memory Python Console App
**Objective**: Generate a detailed architectural plan document (plan.md) for Phase I based strictly on the constitution and the approved spec.md. This plan describes HOW the system will be built (architecture, components, data flow, file structure, etc.) without including any code or implementation details.

**Core References** (must strictly align with these):
- Hackathon document (pages 1–9): Phase I requirements, deliverables, technology stack, submission guidelines
- Constitution.md: All articles, especially Article II (Agentic Dev Stack Workflow - Plan phase = HOW), Article III (Phase-Based Evolution), Article IV (Technology Stack Constraints), Article VI (Code Quality & Architecture Standards), Article VII (Security Discipline), Article VIII (Documentation Excellence), Article IX (Submission & Presentation Standards)
- specs/phase-1/spec.md (the approved specification from /sp.specify)

**GitHub Repository Requirement**:
- All artifacts must be committed to the main branch of the public repository: https://github.com/khawajanaqeeb
- Repository name: hackathon-todo or todo-evolution-hackathon-ii (public, initialized with README.md)
- Commit plan.md with message like: "Add Phase I architectural plan"
- Tag phase completion later: git tag v1.0-phase1 && git push --tags

**Output Requirements**:
Create a single Markdown file content for `specs/phase-1/plan.md` with comprehensive sections covering overview, technology stack, project structure, component architecture (Model/Service/UI layers), data flow diagrams, error handling strategy, testing strategy, constitution compliance check, risks & mitigations, and next steps.

## Response snapshot

Successfully created comprehensive Phase I architectural plan with the following design:

**Architecture Pattern**: Layered architecture with 3 distinct layers
- **Model Layer** (models.py): Task dataclass + TaskList (in-memory storage)
- **Service Layer** (services.py): Pure functions for business logic (add, delete, update, toggle, get_all, find_by_id, validate)
- **UI Layer** (ui.py): CLI interface (menu, prompts, display, messages)
- **Main Entry** (main.py): Application orchestration and main loop

**Key Design Decisions**:
1. **Dataclass for Task**: Type-safe, auto-generates methods, value equality
2. **Pure Functions in Services**: Stateless, easier to test, explicit data flow
3. **Sequential Integer IDs**: Human-friendly for CLI, gaps allowed after deletion
4. **Standard Library for CLI**: No external frameworks (typer/click), meets Phase I simplicity
5. **Exit Warning**: Manages user expectations about data loss (mitigates spec R-001)

**Technology Stack**:
- Python 3.13+ with type hints and docstrings (PEP 257)
- UV package manager with pyproject.toml
- In-memory Python list storage (no persistence)
- pytest + pytest-cov + mypy + ruff for testing and quality
- Claude Code for all code generation (no manual coding)

**Project Structure**:
```
phase1-console/
  src/todo_app/
    models.py    # Task dataclass, TaskList class
    services.py  # 7 pure functions for CRUD operations
    ui.py        # 7 UI functions for display/input
    main.py      # Main loop + 5 handler functions
  tests/
    test_models.py
    test_services.py
    test_ui.py
    test_integration.py
```

**Data Flow Examples**:
- Add Task: User → UI prompt → Service validation → Model creation → UI confirmation
- View Tasks: User → Service get_all → UI table display
- Error Flow: Invalid ID → Service returns None → UI displays error message

**Error Handling Strategy**:
- **UI Layer**: Input validation (type checking, range checking, loops until valid)
- **Service Layer**: Business validation (title non-empty, ID exists), returns None/False on failure
- **Exception Handling**: KeyboardInterrupt caught, generic errors logged, no crashes

**Testing Strategy**:
- **Unit Tests**: 20+ tests for models, services, UI (mocked I/O)
- **Integration Tests**: Full workflows (add → view → update → delete)
- **Coverage Target**: 80% minimum, 90% for critical paths
- **Test Fixtures**: empty_task_list, task_list_with_data

**Constitution Compliance**: ✅ All 6 articles validated
- Article II: Spec-driven, plan follows spec ✅
- Article III: Phase I constraints respected ✅
- Article IV: Python 3.13+, UV, in-memory, CLI, pytest ✅
- Article VI: Modular, SRP, clean architecture, type hints, docstrings ✅
- Article VII: Input validation, no code injection, error handling ✅
- Article VIII: README, CLAUDE.md, spec, plan, tasks, PHRs ✅
- Article IX: Public GitHub, main branch, git tags ✅

**Risks Identified & Mitigated**:
- R-T01: Test coverage <80% → TDD approach, frequent coverage checks
- R-T02: Incomplete type hints → mypy strict mode
- R-T03: PEP 8 violations → ruff auto-fix
- R-UX01: Data loss confusion → Exit warning message
- R-UX02: Long text display → Truncate display, store full text
- R-UX03: Invalid input crash → Comprehensive validation, try-except
- R-P01: Performance with 1000+ tasks → Efficient data structures, tested

## Outcome

- ✅ Impact: Created comprehensive architectural plan ready for task breakdown. Layered architecture enables testing, future extensibility (Phase II storage swap). All 15 functional requirements mappable to components.
- 🧪 Tests: Testing strategy defined with 80% coverage target, 20+ unit tests planned, integration tests for workflows, pytest fixtures for reusable test data
- 📁 Files: Created specs/phase-1/plan.md (comprehensive architectural plan with ASCII diagrams, data flows, component descriptions)
- 🔁 Next prompts: `/sp.tasks` to break down into testable implementation tasks (create tasks.md), `/sp.implement` to generate code from tasks
- 🧠 Reflection: Architecture balances simplicity (Phase I constraint) with extensibility (future phases). Pure functions in service layer maximize testability. Constitution compliance validated across all articles. Ready for task breakdown.

## Evaluation notes (flywheel)

- Failure modes observed: None. Architecture designed to support all spec requirements (15 FR, 10 NFR) and constitution mandates.
- Graders run and results (PASS/FAIL): Constitution compliance check - PASS (all 6 articles validated). Design supports all 5 CRUD features from spec.
- Prompt variant (if applicable): Standard /sp.plan workflow with layered architecture pattern (Model-Service-UI)
- Next experiment (smallest change to try): Proceed to /sp.tasks to validate whether architectural plan provides sufficient detail for task breakdown. Monitor if any design decisions need refinement during implementation.
