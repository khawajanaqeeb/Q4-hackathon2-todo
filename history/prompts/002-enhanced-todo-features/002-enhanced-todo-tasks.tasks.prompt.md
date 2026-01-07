---
id: 002
title: Enhanced Todo Tasks Generation
stage: tasks
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5
feature: 002-enhanced-todo-features
branch: 002-enhanced-todo-features
user: user
command: /sp.tasks
labels: ["tasks", "breakdown", "user-stories", "tdd", "parallel-execution"]
links:
  spec: specs/002-enhanced-todo-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-enhanced-todo-features/tasks.md
tests:
  - null
---

## Prompt

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (API endpoints), research.md (decisions), quickstart.md (test scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map endpoints to user stories
   - If research.md exists: Extract decisions for setup tasks
   - Generate tasks organized by user story (see Task Generation Rules below)
   - Generate dependency graph showing user story completion order
   - Create parallel execution examples per user story
   - Validate task completeness (each user story has all needed tasks, independently testable)

4. **Generate tasks.md**: Use `.specify/templates/tasks-template.md` as structure, fill with:
   - Correct feature name from plan.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories)
   - Phase 3+: One phase per user story (in priority order from spec.md)
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Phase: Polish & cross-cutting concerns
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Dependencies section showing story completion order
   - Parallel execution examples per story
   - Implementation strategy section (MVP first, incremental delivery)

5. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)

Context for task generation: $ARGUMENTS

## Response snapshot

Generated comprehensive atomic task breakdown for Enhanced Phase I - Advanced Console Todo application with 111 tasks organized across 10 phases.

**Task Organization by User Story**:

**Phase 1: Setup (7 tasks)**
- Project structure initialization
- UV project setup with Python 3.13+
- Dependencies: rich, pytest, pytest-cov
- Package markers and .gitignore

**Phase 2: Foundational (5 tasks) - CRITICAL BLOCKING PHASE**
- Priority enum with __lt__ method
- Task dataclass with 6 fields
- Task helper methods (matches_keyword, has_tag)
- TodoService class initialization

**Phase 3: User Story 1 - Add Tasks with Priority/Tags (P1) - MVP (16 tasks)**
- Tests: 7 unit tests (Task, Priority, TodoService.add_task)
- Implementation: add_task(), get_all_tasks(), CLI helpers, add_task_ui()
- Integration: 1 test for add_task_ui()

**Phase 4: User Story 2 - View in Rich Table (P1) - MVP (13 tasks)**
- Tests: 3 unit tests (display_tasks_rich, empty tasks)
- Implementation: Rich table with columns, color-coding, "Total Tasks: N", graceful fallback, view_tasks_ui()
- Integration: 1 test for view_tasks_ui()

**Phase 5: User Story 3 - Search by Keyword (P2) (9 tasks)**
- Tests: 4 unit tests (search in title/description, case-insensitive, no matches)
- Implementation: search_tasks(), search_tasks_ui()
- Integration: 1 test

**Phase 6: User Story 4 - Filter by Criteria (P2) (11 tasks)**
- Tests: 4 unit tests (filter by status/priority/tag, no matches)
- Implementation: filter_by_status/priority/tag(), filter_tasks_ui()
- Integration: 1 test

**Phase 7: User Story 5 - Sort by Criteria (P3) (11 tasks)**
- Tests: 4 unit tests (sort by priority/title/ID, empty list)
- Implementation: sort_by_priority/title/id(), sort_tasks_ui()
- Integration: 1 test

**Phase 8: User Story 6 - Update Tasks (P3) (12 tasks)**
- Tests: 4 unit tests (get_task_by_id, update_task, validation, unchanged fields)
- Implementation: get_task_by_id(), update_task(), update_task_ui()
- Integration: 1 test

**Phase 9: User Story 7 - Delete/Complete (P4) (13 tasks)**
- Tests: 4 unit tests (delete, mark_complete, invalid IDs)
- Implementation: delete_task(), mark_task_complete(), delete_task_ui(), mark_complete_ui()
- Integration: 2 tests

**Phase 10: Polish & Cross-Cutting (14 tasks)**
- Entry point (__main__.py)
- Menu headers and exit confirmation
- Full test suite run and coverage verification (80%+)
- PEP 8, type hints, docstrings validation
- Manual testing with 1000+ tasks
- README.md and CLAUDE.md documentation

**Key Design Decisions**:
1. **User Story Organization**: Each phase represents a complete, independently testable user story
2. **TDD Approach**: Tests written FIRST for each story, must FAIL before implementation
3. **Foundational Phase**: CRITICAL - blocks all user story work, must complete first
4. **Parallel Opportunities**: 40+ tasks marked [P] across all phases
5. **MVP Scope**: Phases 1-4 (42 tasks) = Add tasks with priority/tags + View in rich table
6. **Incremental Delivery**: Each user story adds value without breaking previous stories
7. **Independent Stories**: All user stories independent after Foundational phase completes

**Dependencies**:
- Setup → Foundational → All User Stories (parallel or sequential by priority)
- Within each story: Tests → Models → Services → UI
- No cross-story dependencies (enables parallel development)

**Format Compliance**:
- ✅ All 111 tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- ✅ Sequential task IDs (T001-T111)
- ✅ [P] markers for parallelizable tasks (40+)
- ✅ [Story] labels (US1-US7) for user story traceability
- ✅ Exact file paths in all task descriptions

## Outcome

- ✅ Impact: Created comprehensive atomic task breakdown with 111 tasks organized by 7 user stories, enabling independent implementation, testing, and incremental delivery of Enhanced Phase I
- 🧪 Tests: 40+ test tasks (unit + integration) targeting 80%+ coverage (90%+ models, 85%+ services, 75%+ CLI)
- 📁 Files: Created specs/002-enhanced-todo-features/tasks.md (111 tasks across 10 phases)
- 🔁 Next prompts: /sp.implement (invoke hackathon-cli-builder agent to generate code)
- 🧠 Reflection: Task breakdown successfully maps all 45 functional requirements to atomic, testable tasks. Foundational phase clearly identified as critical blocker. MVP scope (US1+US2) provides immediate value. All user stories are independent after foundation, enabling parallel development.

## Evaluation notes (flywheel)

- Failure modes observed: None - all tasks validated against spec.md requirements and plan.md architecture
- Graders run and results (PASS/FAIL): PASS - All 111 tasks have correct format (checkbox + ID + optional [P] + optional [Story] + description + file path)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Proceed with /sp.implement using hackathon-cli-builder agent to generate all three layers (models.py → services.py → cli.py) following the task sequence

