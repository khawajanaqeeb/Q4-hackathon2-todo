---
description: "Atomic task breakdown for Enhanced Phase I - Advanced Console Todo"
---

# Tasks: Enhanced Phase I - Advanced Console Todo

**Input**: Design documents from `/specs/002-enhanced-todo-features/`
**Prerequisites**: plan.md, spec.md

**Tests**: Tests are included with 80%+ coverage target as specified in requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure:
- Source: `src/todo_app/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per plan.md

- [x] T001 Create project directory structure: src/todo_app/, tests/, .claude/agents/
- [x] T002 Initialize UV project with Python 3.13+ in pyproject.toml
- [x] T003 [P] Add rich library dependency (>=13.0.0) to pyproject.toml via UV
- [x] T004 [P] Add pytest and pytest-cov dependencies to pyproject.toml via UV
- [x] T005 [P] Create package markers: src/todo_app/__init__.py and tests/__init__.py
- [x] T006 [P] Create .gitignore for Python project (.venv/, __pycache__/, .pytest_cache/, htmlcov/)
- [x] T007 [P] Verify hackathon-cli-builder.md agent is committed in .claude/agents/

**Checkpoint**: Project structure and dependencies ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 [P] Create Priority enum (HIGH/MEDIUM/LOW) with __lt__ method in src/todo_app/models.py per FR-019
- [x] T009 [P] Create Task dataclass with 6 fields (id, title, description, completed, priority, tags) in src/todo_app/models.py per FR-001, FR-011
- [x] T010 Add matches_keyword(keyword: str) -> bool helper method to Task class per FR-028, FR-029
- [x] T011 Add has_tag(tag: str) -> bool helper method to Task class per FR-027, FR-034
- [x] T012 Create TodoService class with __init__ (empty _tasks list, _next_id=1) in src/todo_app/services.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tasks with Priority and Tags (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with priority levels (HIGH/MEDIUM/LOW) and multiple tags for organization

**Independent Test**: Launch app, add tasks with different priorities (high/medium/low) and tags (e.g., "work, urgent"), view list, verify priorities display with color-coding and tags show correctly

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Unit test Task dataclass creation with all fields in tests/test_models.py
- [ ] T014 [P] [US1] Unit test Priority enum comparison (HIGH < MEDIUM < LOW) in tests/test_models.py
- [ ] T015 [P] [US1] Unit test Task.matches_keyword() case-insensitive in tests/test_models.py
- [ ] T016 [P] [US1] Unit test Task.has_tag() case-insensitive matching in tests/test_models.py
- [ ] T017 [P] [US1] Unit test TodoService.add_task() with title, description, priority, tags in tests/test_services.py per FR-001
- [ ] T018 [P] [US1] Unit test TodoService.add_task() validates non-empty title in tests/test_services.py per FR-007
- [ ] T019 [P] [US1] Unit test TodoService.add_task() defaults to MEDIUM priority in tests/test_services.py per FR-020

### Implementation for User Story 1

- [ ] T020 [US1] Implement TodoService.add_task(title, description="", priority=MEDIUM, tags=[]) in src/todo_app/services.py per FR-001, FR-007
- [ ] T021 [US1] Implement TodoService.get_all_tasks() returning copy of _tasks list in src/todo_app/services.py per FR-003
- [ ] T022 [US1] Create cli.py with main() function and menu loop (options 1-9) in src/todo_app/cli.py per FR-010, FR-045
- [ ] T023 [US1] Implement get_priority_input() helper validating 1-3 input with MEDIUM default in src/todo_app/cli.py per FR-021
- [ ] T024 [US1] Implement get_tags_input() helper parsing comma-separated tags in src/todo_app/cli.py per FR-024
- [ ] T025 [US1] Implement get_non_empty_string(prompt) helper with validation loop in src/todo_app/cli.py per FR-007
- [ ] T026 [US1] Implement add_task_ui(service) function with interactive prompts for title, description, priority, tags in src/todo_app/cli.py per FR-001
- [ ] T027 [US1] Add success message "✅ Task added successfully! (ID: N)" in add_task_ui() per acceptance scenario
- [ ] T028 [P] [US1] Integration test add_task_ui() with mocked input in tests/test_cli.py

**Checkpoint**: User Story 1 complete - users can add tasks with priority and tags

---

## Phase 4: User Story 2 - View Tasks in Beautiful Table Format (Priority: P1) 🎯 MVP

**Goal**: Users see all tasks in professionally formatted table with "Total Tasks: N" summary at top

**Independent Test**: Add multiple tasks with various priorities and tags, view list, verify rich table displays with proper headers, color-coded priorities, and task count summary

### Tests for User Story 2

- [ ] T029 [P] [US2] Unit test display_tasks_rich() creates table with correct columns in tests/test_cli.py per FR-003
- [ ] T030 [P] [US2] Unit test display_tasks_rich() shows "Total Tasks: N" header in tests/test_cli.py per FR-043
- [ ] T031 [P] [US2] Unit test display empty tasks shows friendly message in tests/test_cli.py

### Implementation for User Story 2

- [ ] T032 [US2] Implement display_tasks_rich(tasks) function with rich.Table in src/todo_app/cli.py per FR-003, FR-041
- [ ] T033 [US2] Add table columns: ID | Title | Description | Priority | Tags | Status in display_tasks_rich() per FR-003
- [ ] T034 [US2] Add "Total Tasks: N" header using rich.Console.print() in display_tasks_rich() per FR-043
- [ ] T035 [US2] Add color-coding: HIGH=red, MEDIUM=yellow, LOW=green in display_tasks_rich() per FR-022
- [ ] T036 [US2] Add graceful fallback to basic print() if rich not available in display_tasks_rich() per FR-042
- [ ] T037 [US2] Display tags as comma-separated or "-" if empty in display_tasks_rich() per FR-026
- [ ] T038 [US2] Display status as "✓ Complete" (green) or "○ Pending" (yellow) in display_tasks_rich() per FR-015
- [ ] T039 [US2] Implement view_tasks_ui(service) calling get_all_tasks() and display_tasks_rich() in src/todo_app/cli.py
- [ ] T040 [US2] Add empty list message "📋 No tasks found. Add your first task to get started!" in view_tasks_ui() per acceptance scenario
- [ ] T041 [P] [US2] Integration test view_tasks_ui() displays table correctly in tests/test_cli.py

**Checkpoint**: User Story 2 complete - users can view tasks in beautiful rich table format with color-coding

---

## Phase 5: User Story 3 - Search Tasks by Keyword (Priority: P2)

**Goal**: Users can quickly find tasks by searching for keywords in titles or descriptions

**Independent Test**: Create tasks with various titles and descriptions, search for specific keywords (case-insensitive), verify only matching tasks appear with match count

### Tests for User Story 3

- [ ] T042 [P] [US3] Unit test TodoService.search_tasks() finds matches in title in tests/test_services.py per FR-028
- [ ] T043 [P] [US3] Unit test TodoService.search_tasks() finds matches in description in tests/test_services.py per FR-028
- [ ] T044 [P] [US3] Unit test TodoService.search_tasks() case-insensitive matching in tests/test_services.py per FR-029
- [ ] T045 [P] [US3] Unit test search returns empty list when no matches in tests/test_services.py

### Implementation for User Story 3

- [ ] T046 [US3] Implement TodoService.search_tasks(keyword) using Task.matches_keyword() in src/todo_app/services.py per FR-028, FR-029
- [ ] T047 [US3] Implement search_tasks_ui(service) with keyword input prompt in src/todo_app/cli.py per FR-030
- [ ] T048 [US3] Display search results with "✅ Found N task(s) matching 'keyword'" message in search_tasks_ui() per FR-030
- [ ] T049 [US3] Display "📋 No tasks found matching 'keyword'" when no matches in search_tasks_ui() per FR-031
- [ ] T050 [P] [US3] Integration test search_tasks_ui() with mocked input in tests/test_cli.py

**Checkpoint**: User Story 3 complete - users can search tasks by keyword with match count display

---

## Phase 6: User Story 4 - Filter Tasks by Criteria (Priority: P2)

**Goal**: Users can filter tasks by completion status, priority level, or tags to focus on specific subsets

**Independent Test**: Create tasks with various statuses, priorities, and tags, filter by each criterion, verify only matching tasks appear with appropriate counts

### Tests for User Story 4

- [ ] T051 [P] [US4] Unit test TodoService.filter_by_status(completed=True/False) in tests/test_services.py per FR-032
- [ ] T052 [P] [US4] Unit test TodoService.filter_by_priority(priority) in tests/test_services.py per FR-033
- [ ] T053 [P] [US4] Unit test TodoService.filter_by_tag(tag) case-insensitive in tests/test_services.py per FR-034, FR-027
- [ ] T054 [P] [US4] Unit test filter methods return empty list when no matches in tests/test_services.py

### Implementation for User Story 4

- [ ] T055 [P] [US4] Implement TodoService.filter_by_status(completed: bool) in src/todo_app/services.py per FR-032
- [ ] T056 [P] [US4] Implement TodoService.filter_by_priority(priority: Priority) in src/todo_app/services.py per FR-033
- [ ] T057 [US4] Implement TodoService.filter_by_tag(tag: str) using Task.has_tag() in src/todo_app/services.py per FR-034
- [ ] T058 [US4] Implement filter_tasks_ui(service) with filter menu (status/priority/tag) in src/todo_app/cli.py per FR-035
- [ ] T059 [US4] Display filtered results with "✅ Showing [filter type]:" message in filter_tasks_ui() per FR-035
- [ ] T060 [US4] Display "📌 No tasks match the selected filter." when no matches in filter_tasks_ui() per FR-036
- [ ] T061 [P] [US4] Integration test filter_tasks_ui() with mocked input in tests/test_cli.py

**Checkpoint**: User Story 4 complete - users can filter tasks by status, priority, or tags with descriptive messages

---

## Phase 7: User Story 5 - Sort Tasks by Multiple Criteria (Priority: P3)

**Goal**: Users can sort tasks by priority (high to low), alphabetically by title, or by creation order (ID)

**Independent Test**: Create tasks in random order with various priorities and titles, sort by each criterion, verify correct sort order displayed

### Tests for User Story 5

- [ ] T062 [P] [US5] Unit test TodoService.sort_by_priority() returns HIGH→MEDIUM→LOW order in tests/test_services.py per FR-037
- [ ] T063 [P] [US5] Unit test TodoService.sort_by_title() returns A-Z case-insensitive in tests/test_services.py per FR-038
- [ ] T064 [P] [US5] Unit test TodoService.sort_by_id() returns ascending ID order in tests/test_services.py per FR-039
- [ ] T065 [P] [US5] Unit test sort methods handle empty list in tests/test_services.py

### Implementation for User Story 5

- [ ] T066 [P] [US5] Implement TodoService.sort_by_priority(tasks) using Priority.__lt__ in src/todo_app/services.py per FR-037
- [ ] T067 [P] [US5] Implement TodoService.sort_by_title(tasks) case-insensitive in src/todo_app/services.py per FR-038
- [ ] T068 [P] [US5] Implement TodoService.sort_by_id(tasks) ascending order in src/todo_app/services.py per FR-039
- [ ] T069 [US5] Implement sort_tasks_ui(service) with sort menu (priority/title/id) in src/todo_app/cli.py per FR-040
- [ ] T070 [US5] Display sorted results with "✅ Tasks sorted by [criterion]:" message in sort_tasks_ui() per FR-040
- [ ] T071 [US5] Display "📌 No tasks to sort." for empty list in sort_tasks_ui()
- [ ] T072 [P] [US5] Integration test sort_tasks_ui() with mocked input in tests/test_cli.py

**Checkpoint**: User Story 5 complete - users can sort tasks by priority, title, or ID with descriptive messages

---

## Phase 8: User Story 6 - Update Tasks with New Features (Priority: P3)

**Goal**: Users can modify task priorities and tags in addition to title and description

**Independent Test**: Create tasks, update priorities and tags, view to verify changes persisted, confirm other attributes unchanged

### Tests for User Story 6

- [ ] T073 [P] [US6] Unit test TodoService.get_task_by_id(id) returns task or None in tests/test_services.py per FR-008
- [ ] T074 [P] [US6] Unit test TodoService.update_task(id, **kwargs) updates specified fields in tests/test_services.py per FR-005
- [ ] T075 [P] [US6] Unit test update_task() validates non-empty title in tests/test_services.py per FR-007
- [ ] T076 [P] [US6] Unit test update_task() keeps unchanged fields as-is in tests/test_services.py

### Implementation for User Story 6

- [ ] T077 [P] [US6] Implement TodoService.get_task_by_id(task_id: int) in src/todo_app/services.py per FR-008
- [ ] T078 [US6] Implement TodoService.update_task(task_id, title=None, description=None, priority=None, tags=None) in src/todo_app/services.py per FR-005
- [ ] T079 [US6] Implement get_task_id() helper validating positive integer with error loop in src/todo_app/cli.py per FR-008
- [ ] T080 [US6] Implement update_task_ui(service) with prompts for all updatable fields in src/todo_app/cli.py per FR-005
- [ ] T081 [US6] Allow Enter to skip field updates (keep existing values) in update_task_ui() per acceptance scenario
- [ ] T082 [US6] Display "Task updated successfully!" success message in update_task_ui()
- [ ] T083 [US6] Display "❌ Error: Task ID [N] not found" for invalid IDs in update_task_ui() per FR-009
- [ ] T084 [P] [US6] Integration test update_task_ui() with mocked input in tests/test_cli.py

**Checkpoint**: User Story 6 complete - users can update all task attributes including priority and tags

---

## Phase 9: User Story 7 - Delete and Mark Complete with Enhanced Display (Priority: P4)

**Goal**: Users perform basic delete and mark complete operations with enhanced table display

**Independent Test**: Perform delete and mark complete operations, verify enhanced table shows updated states with color-coding and formatting

### Tests for User Story 7

- [ ] T085 [P] [US7] Unit test TodoService.delete_task(id) removes task from list in tests/test_services.py per FR-004
- [ ] T086 [P] [US7] Unit test TodoService.delete_task(id) returns False for invalid ID in tests/test_services.py per FR-008
- [ ] T087 [P] [US7] Unit test TodoService.mark_task_complete(id) toggles completed status in tests/test_services.py per FR-006
- [ ] T088 [P] [US7] Unit test mark_task_complete(id) returns False for invalid ID in tests/test_services.py per FR-008

### Implementation for User Story 7

- [ ] T089 [P] [US7] Implement TodoService.delete_task(task_id: int) -> bool in src/todo_app/services.py per FR-004
- [ ] T090 [P] [US7] Implement TodoService.mark_task_complete(task_id: int) -> bool in src/todo_app/services.py per FR-006
- [ ] T091 [US7] Implement delete_task_ui(service) with ID prompt and confirmation in src/todo_app/cli.py per FR-004
- [ ] T092 [US7] Display "Task ID [N] deleted successfully!" in delete_task_ui() with updated table per acceptance scenario
- [ ] T093 [US7] Display "❌ Error: Task ID [N] not found" for invalid IDs in delete_task_ui() per FR-009
- [ ] T094 [US7] Implement mark_complete_ui(service) with ID prompt and status toggle in src/todo_app/cli.py per FR-006
- [ ] T095 [US7] Display task status change confirmation with updated table in mark_complete_ui()
- [ ] T096 [P] [US7] Integration test delete_task_ui() with mocked input in tests/test_cli.py
- [ ] T097 [P] [US7] Integration test mark_complete_ui() with mocked input in tests/test_cli.py

**Checkpoint**: All 7 user stories complete - full enhanced Phase I functionality implemented

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final deliverables

- [ ] T098 [P] Create __main__.py entry point calling cli.main() in src/todo_app/__main__.py
- [ ] T099 [P] Add menu section headers (Task Management, Advanced Features, Exit) in cli.py per FR-044
- [ ] T100 [P] Add exit confirmation message "👋 Goodbye! Your tasks are in-memory only (not saved)." in cli.py per FR-014
- [ ] T101 Run full test suite with pytest --cov=src/todo_app --cov-report=html
- [ ] T102 Verify 80%+ test coverage across all files per NFR-005
- [ ] T103 Fix any failing tests or coverage gaps
- [ ] T104 [P] Verify PEP 8 compliance with ruff check per NFR-006
- [ ] T105 [P] Verify all functions have type hints per NFR-003
- [ ] T106 [P] Verify all functions have Google-style docstrings per NFR-004
- [ ] T107 Manual testing of all 9 menu options with edge cases
- [ ] T108 Test with 1000+ tasks to verify performance <1 second per NFR-001, NFR-008
- [ ] T109 [P] Create README.md with setup instructions (UV install, usage guide, features list)
- [ ] T110 [P] Update CLAUDE.md with hackathon-cli-builder agent usage documentation
- [ ] T111 [P] Add code comments linking to spec sections (FR-XXX references)

**Checkpoint**: Enhanced Phase I complete, fully tested, documented, ready for demo and submission

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User Story 1 (P1): Add Tasks with Priority and Tags - FOUNDATIONAL FOR MVP
  - User Story 2 (P1): View Tasks in Beautiful Table - FOUNDATIONAL FOR MVP
  - User Story 3 (P2): Search Tasks - Independent, can run after Foundational
  - User Story 4 (P2): Filter Tasks - Independent, can run after Foundational
  - User Story 5 (P3): Sort Tasks - Independent, can run after Foundational
  - User Story 6 (P3): Update Tasks - Independent, can run after Foundational
  - User Story 7 (P4): Delete and Mark Complete - Independent, can run after Foundational
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends ONLY on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends ONLY on Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Depends ONLY on Foundational (Phase 2) - Independent from other stories
- **User Story 4 (P2)**: Depends ONLY on Foundational (Phase 2) - Independent from other stories
- **User Story 5 (P3)**: Depends ONLY on Foundational (Phase 2) - Independent from other stories
- **User Story 6 (P3)**: Depends ONLY on Foundational (Phase 2) - Independent from other stories
- **User Story 7 (P4)**: Depends ONLY on Foundational (Phase 2) - Independent from other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Models before services (Task and Priority must exist before TodoService methods)
- Services before UI (TodoService methods must exist before CLI functions)
- Core implementation before integration tests
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T003, T004, T005, T006, T007 can all run in parallel

**Phase 2 (Foundational)**: Tasks T008, T009 can run in parallel; T010, T011 after T009; T012 after T009

**Within Each User Story**:
- All unit tests marked [P] can run in parallel within that story
- Models marked [P] can run in parallel
- Service methods marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members AFTER Foundational phase completes

**Phase 10 (Polish)**: Tasks T098, T099, T100, T104, T105, T106, T109, T110, T111 can run in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational Phase 2 completes, launch all User Story 1 tests together:
Task T013: "Unit test Task dataclass creation with all fields"
Task T014: "Unit test Priority enum comparison (HIGH < MEDIUM < LOW)"
Task T015: "Unit test Task.matches_keyword() case-insensitive"
Task T016: "Unit test Task.has_tag() case-insensitive matching"
Task T017: "Unit test TodoService.add_task() with title, description, priority, tags"
Task T018: "Unit test TodoService.add_task() validates non-empty title"
Task T019: "Unit test TodoService.add_task() defaults to MEDIUM priority"

# Then launch implementation tasks sequentially (dependencies exist):
Task T020: "Implement TodoService.add_task(...)" (depends on T008, T009)
Task T021: "Implement TodoService.get_all_tasks()" (depends on T012)
Task T022: "Create cli.py with main() and menu loop"
Task T023-T025: "Implement input helpers" (can run in parallel)
Task T026-T027: "Implement add_task_ui() with prompts and success message"
Task T028: "Integration test add_task_ui()"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T012) - CRITICAL BLOCKING PHASE
3. Complete Phase 3: User Story 1 (T013-T028) - Add tasks with priority and tags
4. Complete Phase 4: User Story 2 (T029-T041) - View tasks in beautiful table
5. **STOP and VALIDATE**: Test User Stories 1 and 2 independently
6. Deploy/demo MVP with enhanced add and view capabilities

**MVP Delivers**: Users can add tasks with priorities and tags, and view them in a professionally formatted rich table with color-coding

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T012)
2. Add User Story 1 + 2 → Test independently → Deploy/Demo (MVP!) (T013-T041)
3. Add User Story 3 → Test independently → Deploy/Demo (Search) (T042-T050)
4. Add User Story 4 → Test independently → Deploy/Demo (Filter) (T051-T061)
5. Add User Story 5 → Test independently → Deploy/Demo (Sort) (T062-T072)
6. Add User Story 6 → Test independently → Deploy/Demo (Update) (T073-T084)
7. Add User Story 7 → Test independently → Deploy/Demo (Delete/Complete) (T085-T097)
8. Polish and finalize → Complete implementation (T098-T111)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (Phase 1) together (T001-T007)
2. Team completes Foundational (Phase 2) together (T008-T012) - MUST FINISH FIRST
3. Once Foundational is done, parallel story development:
   - Developer A: User Story 1 + 2 (MVP core) (T013-T041)
   - Developer B: User Story 3 + 4 (Search & Filter) (T042-T061)
   - Developer C: User Story 5 + 6 (Sort & Update) (T062-T084)
   - Developer D: User Story 7 (Delete & Complete) (T085-T097)
4. Team completes Polish (Phase 10) together (T098-T111)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US1-US7) maps task to specific user story for traceability
- Each user story is independently completable and testable
- TDD approach: Write tests first, verify they FAIL, then implement
- Foundational Phase 2 is CRITICAL - blocks all user story work
- All user stories are independent after Foundational phase completes
- 80%+ test coverage target: 90%+ models, 85%+ services, 75%+ CLI
- Commit after each task or logical group
- Stop at checkpoints to validate story independently
- MVP = User Stories 1 + 2 (add tasks with priority/tags, view in rich table)

---

**Total Tasks**: 111
**Task Distribution**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1 - Add with Priority/Tags): 16 tasks
- Phase 4 (US2 - View in Rich Table): 13 tasks
- Phase 5 (US3 - Search): 9 tasks
- Phase 6 (US4 - Filter): 11 tasks
- Phase 7 (US5 - Sort): 11 tasks
- Phase 8 (US6 - Update): 12 tasks
- Phase 9 (US7 - Delete/Complete): 13 tasks
- Phase 10 (Polish): 14 tasks

**Parallel Opportunities**: 40+ tasks marked [P] across all phases

**MVP Scope**: Phases 1-4 (42 tasks) deliver core enhanced functionality

**Independent Test Criteria**:
- US1: Add tasks with priorities and tags, verify in list
- US2: View tasks in rich table with color-coding and count
- US3: Search by keyword, verify only matches appear
- US4: Filter by status/priority/tag, verify only matches appear
- US5: Sort by priority/title/ID, verify correct order
- US6: Update priorities and tags, verify changes persist
- US7: Delete and mark complete, verify table updates

---

**Status**: ✅ Ready for `/sp.implement` with `hackathon-cli-builder` agent
