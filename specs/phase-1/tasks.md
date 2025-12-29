---
description: "Task list for Phase I - Todo In-Memory Python Console App implementation"
---

# Tasks: Phase I - Todo In-Memory Python Console App

**Input**: Design documents from `/specs/phase-1/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Tests**: Per spec NFR-005, minimum 80% test coverage is required with pytest. Test tasks are included throughout.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Phase I uses single project structure:
- Application code: `phase1-console/src/todo_app/`
- Tests: `phase1-console/tests/`
- Documentation: `phase1-console/` (root)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per plan.md

- [ ] T001 Create phase1-console directory structure: src/todo_app/, tests/
- [ ] T002 Initialize UV project with pyproject.toml (Python 3.13+, pytest, pytest-cov, mypy, ruff)
- [ ] T003 [P] Create .gitignore for Python (__pycache__, *.pyc, .pytest_cache, .coverage, htmlcov/)
- [ ] T004 [P] Create phase1-console/README.md with setup instructions and usage guide
- [ ] T005 [P] Create phase1-console/CLAUDE.md with AI agent instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data structures that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create Task dataclass in phase1-console/src/todo_app/models.py with fields: id (int), title (str), description (str), completed (bool)
- [ ] T007 Create TaskList class in phase1-console/src/todo_app/models.py with fields: tasks (List[Task]), next_id (int)
- [ ] T008 Add type hints and docstrings to all models per NFR-003 and NFR-004
- [ ] T009 Create tests/test_models.py with tests for Task creation and TaskList initialization
- [ ] T010 Create phase1-console/src/todo_app/__init__.py (empty, marks as package)
- [ ] T011 Create phase1-console/tests/__init__.py (empty, marks as package)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with title/description and view all tasks in a formatted list

**Independent Test**: Launch app, add 2-3 tasks with titles and optional descriptions, view task list, verify all tasks display with ID | Title | Description | Status

### Tests for User Story 1 (RED Phase - Write Failing Tests)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Create tests/test_services.py with test_add_task_success (valid title creates task with ID 1)
- [ ] T013 [P] [US1] Add test_add_task_empty_title to tests/test_services.py (empty title returns None)
- [ ] T014 [P] [US1] Add test_add_task_increments_id to tests/test_services.py (multiple adds increment IDs 1, 2, 3)
- [ ] T015 [P] [US1] Add test_get_all_tasks_empty to tests/test_services.py (empty list returns [])
- [ ] T016 [P] [US1] Add test_get_all_tasks_multiple to tests/test_services.py (returns all tasks)
- [ ] T017 [P] [US1] Create tests/test_ui.py with test_display_tasks_empty (handles empty list message)
- [ ] T018 [P] [US1] Add test_display_tasks_multiple to tests/test_ui.py (formats table correctly)
- [ ] T019 [P] [US1] Add test_display_menu to tests/test_ui.py (displays 6 menu options)

### Implementation for User Story 1 (GREEN Phase)

- [ ] T020 [P] [US1] Implement add_task function in phase1-console/src/todo_app/services.py (validate title, generate ID, create Task, append, return Task)
- [ ] T021 [P] [US1] Implement get_all_tasks function in phase1-console/src/todo_app/services.py (returns shallow copy of tasks list)
- [ ] T022 [P] [US1] Implement validate_title function in phase1-console/src/todo_app/services.py (checks non-empty after strip)
- [ ] T023 [US1] Create phase1-console/src/todo_app/ui.py with display_menu function (prints 6 numbered options)
- [ ] T024 [US1] Implement get_menu_choice function in phase1-console/src/todo_app/ui.py (validates input 1-6, loops until valid)
- [ ] T025 [US1] Implement prompt_task_details function in phase1-console/src/todo_app/ui.py (prompts for title and optional description)
- [ ] T026 [US1] Implement display_tasks function in phase1-console/src/todo_app/ui.py (formats table with ID | Title | Description | Status)
- [ ] T027 [US1] Implement display_message function in phase1-console/src/todo_app/ui.py (prints success/error messages)
- [ ] T028 [US1] Create phase1-console/src/todo_app/main.py with main function (initialize TaskList, main loop)
- [ ] T029 [US1] Implement handle_add_task function in phase1-console/src/todo_app/main.py (calls prompt_task_details, add_task, display_message)
- [ ] T030 [US1] Implement handle_view_tasks function in phase1-console/src/todo_app/main.py (calls get_all_tasks, display_tasks)
- [ ] T031 [US1] Add type hints and docstrings to all US1 functions per NFR-003 and NFR-004
- [ ] T032 [US1] Run pytest for US1 tests, verify all pass
- [ ] T033 [US1] Create tests/test_integration.py with test_add_and_view_workflow (end-to-end test)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Users can toggle task completion status and see visual indicators (✓ Complete / ○ Pending)

**Independent Test**: Add 3 tasks, mark task ID 2 complete, view list to verify status shows "✓ Complete" for ID 2 and "○ Pending" for others, toggle ID 2 again to verify back to pending

### Tests for User Story 2 (RED Phase)

- [ ] T034 [P] [US2] Add test_toggle_complete_pending_to_complete to tests/test_services.py (toggles False → True)
- [ ] T035 [P] [US2] Add test_toggle_complete_complete_to_pending to tests/test_services.py (toggles True → False)
- [ ] T036 [P] [US2] Add test_toggle_complete_not_found to tests/test_services.py (non-existent ID returns None)
- [ ] T037 [P] [US2] Add test_find_task_by_id_found to tests/test_services.py (existing ID returns Task)
- [ ] T038 [P] [US2] Add test_find_task_by_id_not_found to tests/test_services.py (non-existent ID returns None)

### Implementation for User Story 2 (GREEN Phase)

- [ ] T039 [P] [US2] Implement find_task_by_id function in phase1-console/src/todo_app/services.py (searches tasks by ID, returns Task or None)
- [ ] T040 [US2] Implement toggle_complete function in phase1-console/src/todo_app/services.py (finds task, toggles completed field, returns Task or None)
- [ ] T041 [US2] Implement prompt_task_id function in phase1-console/src/todo_app/ui.py (validates positive integer input, loops until valid)
- [ ] T042 [US2] Update display_tasks in phase1-console/src/todo_app/ui.py to show "✓ Complete" / "○ Pending" based on completed field
- [ ] T043 [US2] Implement handle_toggle_complete function in phase1-console/src/todo_app/main.py (prompts for ID, calls toggle_complete, displays result)
- [ ] T044 [US2] Add type hints and docstrings to all US2 functions
- [ ] T045 [US2] Run pytest for US2 tests, verify all pass
- [ ] T046 [US2] Add test_mark_complete_workflow to tests/test_integration.py (add → mark complete → view)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Users can modify task title and/or description by ID

**Independent Test**: Add task "Write report", update to "Write annual report" with new description, view list to verify changes persisted with same ID

### Tests for User Story 3 (RED Phase)

- [ ] T047 [P] [US3] Add test_update_task_both_fields to tests/test_services.py (updates title and description)
- [ ] T048 [P] [US3] Add test_update_task_title_only to tests/test_services.py (updates only title, description unchanged)
- [ ] T049 [P] [US3] Add test_update_task_description_only to tests/test_services.py (updates only description, title unchanged)
- [ ] T050 [P] [US3] Add test_update_task_empty_title to tests/test_services.py (empty title returns None, no changes)
- [ ] T051 [P] [US3] Add test_update_task_not_found to tests/test_services.py (non-existent ID returns None)

### Implementation for User Story 3 (GREEN Phase)

- [ ] T052 [US3] Implement update_task function in phase1-console/src/todo_app/services.py (validates title if provided, finds task, updates fields, returns Task or None)
- [ ] T053 [US3] Implement handle_update_task function in phase1-console/src/todo_app/main.py (prompts for ID, new title/description with Enter to keep current, calls update_task, displays result)
- [ ] T054 [US3] Add type hints and docstrings to all US3 functions
- [ ] T055 [US3] Run pytest for US3 tests, verify all pass
- [ ] T056 [US3] Add test_update_workflow to tests/test_integration.py (add → update → view)

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Unwanted Tasks (Priority: P4)

**Goal**: Users can remove tasks by ID, remaining tasks keep their original IDs (gaps allowed)

**Independent Test**: Add 3 tasks (IDs 1, 2, 3), delete ID 2, view list to verify only IDs 1 and 3 remain with original IDs, attempt to delete ID 99 and verify error message

### Tests for User Story 4 (RED Phase)

- [ ] T057 [P] [US4] Add test_delete_task_success to tests/test_services.py (existing ID deletes task, returns True)
- [ ] T058 [P] [US4] Add test_delete_task_not_found to tests/test_services.py (non-existent ID returns False)
- [ ] T059 [P] [US4] Add test_delete_task_preserves_ids to tests/test_services.py (delete ID 2, IDs 1 and 3 unchanged)

### Implementation for User Story 4 (GREEN Phase)

- [ ] T060 [US4] Implement delete_task function in phase1-console/src/todo_app/services.py (finds task by ID, removes from list, returns True or False)
- [ ] T061 [US4] Implement handle_delete_task function in phase1-console/src/todo_app/main.py (prompts for ID, calls delete_task, displays success or error)
- [ ] T062 [US4] Add type hints and docstrings to all US4 functions
- [ ] T063 [US4] Run pytest for US4 tests, verify all pass
- [ ] T064 [US4] Add test_delete_workflow to tests/test_integration.py (add 3 → delete 2nd → view → verify IDs)

**Checkpoint**: All 4 user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and meet all NFRs

### Error Handling & Edge Cases

- [ ] T065 [P] Create tests/test_edge_cases.py with test_empty_list_operations (view, update, delete, toggle on empty list)
- [ ] T066 [P] Add test_invalid_id_handling to tests/test_edge_cases.py (letters, negative numbers, non-existent IDs)
- [ ] T067 [P] Add test_very_long_title to tests/test_edge_cases.py (1000-char title stores correctly)
- [ ] T068 [P] Add test_unicode_characters to tests/test_edge_cases.py (emoji and special chars in title/description)
- [ ] T069 Implement display_exit_warning function in phase1-console/src/todo_app/ui.py (warns about data loss on exit)
- [ ] T070 Update main function in phase1-console/src/todo_app/main.py to display exit warning before terminating
- [ ] T071 Add KeyboardInterrupt handling in phase1-console/src/todo_app/main.py (Ctrl+C displays exit warning)
- [ ] T072 Add generic exception handling in phase1-console/src/todo_app/main.py (log to stderr, don't crash)

### Constants & Code Quality

- [ ] T073 Create constants.py in phase1-console/src/todo_app/ with all hardcoded strings (menu text, messages, status symbols)
- [ ] T074 Update all modules to use constants instead of hardcoded strings per NFR-010
- [ ] T075 Run mypy on src/todo_app/ with --strict flag, fix all type errors per NFR-003
- [ ] T076 Run ruff check src/todo_app/ --fix to enforce PEP 8 per NFR-006
- [ ] T077 Verify all functions have docstrings per NFR-004 (PEP 257)

### Test Coverage & Validation

- [ ] T078 Run pytest --cov=src/todo_app --cov-report=term-missing --cov-report=html
- [ ] T079 Verify coverage is 80% or higher per NFR-005, add tests for uncovered lines if needed
- [ ] T080 Create tests/conftest.py with fixtures: empty_task_list, task_list_with_data
- [ ] T081 Refactor tests to use fixtures for DRY code
- [ ] T082 Run full integration test with 1000 tasks to verify performance per NFR-008

### Documentation

- [ ] T083 [P] Update phase1-console/README.md with complete setup instructions (UV install, dependencies, run instructions)
- [ ] T084 [P] Add feature list and usage examples to phase1-console/README.md
- [ ] T085 [P] Add troubleshooting section to phase1-console/README.md
- [ ] T086 [P] Update phase1-console/CLAUDE.md with workflow notes and implementation decisions
- [ ] T087 Create demo script or instructions for 90-second video walkthrough

### Final Validation

- [ ] T088 Manual test: Launch app, execute all 5 features (add, view, update, delete, mark complete)
- [ ] T089 Verify exit warning displays when closing app
- [ ] T090 Verify app runs on Windows WSL 2 per NFR-002
- [ ] T091 Run complete test suite with pytest -v, verify all tests pass
- [ ] T092 Validate all 15 acceptance criteria from spec.md are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational (Phase 2) completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories (Phases 3-6) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (uses find_task_by_id helper)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2 (uses find_task_by_id helper)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3

**Key Insight**: All 4 user stories are independently implementable after Phase 2 completes!

### Within Each User Story

- Tests (RED) MUST be written and FAIL before implementation (GREEN)
- Models before services (already in Phase 2)
- Services before UI handlers
- UI helpers before main handlers
- Type hints and docstrings with implementation
- Integration test after all unit tests pass

### Parallel Opportunities

- **Setup (Phase 1)**: T003, T004, T005 can run in parallel
- **Foundational (Phase 2)**: T009 can run in parallel with T006-T008, T010-T011 can run in parallel
- **US1 Tests (T012-T019)**: All 8 test tasks can run in parallel (different test files/functions)
- **US1 Implementation (T020-T022)**: These 3 service functions can run in parallel (different functions in same file)
- **US2 Tests (T034-T038)**: All 5 test tasks can run in parallel
- **US2 Implementation (T039-T040)**: These 2 service functions can run in parallel
- **US3 Tests (T047-T051)**: All 5 test tasks can run in parallel
- **US4 Tests (T057-T059)**: All 3 test tasks can run in parallel
- **Polish - Edge Cases (T065-T068)**: All 4 edge case tests can run in parallel
- **Polish - Documentation (T083-T087)**: All 5 doc tasks can run in parallel
- **User Stories (Phases 3-6)**: Can all run in parallel by different developers after Phase 2 completes

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (RED phase):
Task T012: "Create tests/test_services.py with test_add_task_success"
Task T013: "Add test_add_task_empty_title to tests/test_services.py"
Task T014: "Add test_add_task_increments_id to tests/test_services.py"
Task T015: "Add test_get_all_tasks_empty to tests/test_services.py"
Task T016: "Add test_get_all_tasks_multiple to tests/test_services.py"
Task T017: "Create tests/test_ui.py with test_display_tasks_empty"
Task T018: "Add test_display_tasks_multiple to tests/test_ui.py"
Task T019: "Add test_display_menu to tests/test_ui.py"

# Launch all service functions for User Story 1 together (GREEN phase):
Task T020: "Implement add_task function in services.py"
Task T021: "Implement get_all_tasks function in services.py"
Task T022: "Implement validate_title function in services.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T011) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T012-T033)
4. **STOP and VALIDATE**: Test User Story 1 independently - can add and view tasks
5. Demo if ready (MVP = add + view tasks)

### Incremental Delivery (Recommended for Hackathon)

1. **Foundation** (T001-T011): Setup + Models → Foundation ready
2. **MVP** (T012-T033): Add + View → Test independently → Demo/Commit (tag: v0.1-mvp)
3. **Increment 1** (T034-T046): Mark Complete → Test independently → Demo/Commit (tag: v0.2-complete)
4. **Increment 2** (T047-T056): Update Tasks → Test independently → Demo/Commit (tag: v0.3-update)
5. **Increment 3** (T057-T064): Delete Tasks → Test independently → Demo/Commit (tag: v0.4-delete)
6. **Polish** (T065-T092): Error handling, coverage, docs → Final validation → Demo/Commit (tag: v1.0-phase1)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers (not typical for this hackathon, but possible):

1. Team completes Setup (Phase 1) + Foundational (Phase 2) together
2. Once Foundational is done:
   - Developer A: User Story 1 (T012-T033)
   - Developer B: User Story 2 (T034-T046)
   - Developer C: User Story 3 (T047-T056)
   - Developer D: User Story 4 (T057-T064)
3. Stories complete and integrate independently
4. Team converges on Polish (Phase 7) together

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks (T001-T005)
- **Phase 2 (Foundational)**: 6 tasks (T006-T011)
- **Phase 3 (US1 - Add & View)**: 22 tasks (T012-T033)
- **Phase 4 (US2 - Mark Complete)**: 13 tasks (T034-T046)
- **Phase 5 (US3 - Update)**: 10 tasks (T047-T056)
- **Phase 6 (US4 - Delete)**: 8 tasks (T057-T064)
- **Phase 7 (Polish)**: 28 tasks (T065-T092)

**Total**: 92 tasks

**Parallel Opportunities**: 35+ tasks marked [P] can run in parallel within their phase

**Critical Path**: Setup → Foundational → (US1 OR US2 OR US3 OR US4) → Polish

---

## Notes

- [P] tasks = different files or functions, no dependencies within phase
- [Story] label (US1, US2, US3, US4) maps task to specific user story for traceability
- Each user story should be independently completable and testable after Phase 2
- RED-GREEN-REFACTOR: Write failing tests, implement to pass, refactor in Polish phase
- Commit after each phase or logical group (e.g., after US1 complete)
- Stop at any checkpoint to validate story independently before proceeding
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Constitution compliance: All code AI-generated via Claude Code, no manual coding (Article II)
