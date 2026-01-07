# Tasks: Fix Frontend Tags Validation

**Input**: Design documents from `/specs/001-fix-frontend-tags-validation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Verify project structure and locate app/dashboard/page.tsx file
- [ ] T002 [P] Set up development environment for Next.js frontend

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Review current handleAddTask implementation in app/dashboard/page.tsx
- [ ] T004 [P] Analyze existing task creation patterns in the codebase
- [ ] T005 Create backup of original app/dashboard/page.tsx file for safety

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Proper Tags Array Submission (Priority: P1) 🎯 MVP

**Goal**: Implement proper tag formatting to send tags as arrays instead of strings to the backend API

**Independent Test**: Can be fully tested by creating a task with tags and verifying the API request succeeds without validation errors.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US1] Create unit test for tag formatting in tests/unit/test_tag_formatting.ts

### Implementation for User Story 1

- [ ] T007 [P] [US1] Update handleAddTask function in phase2-fullstack/frontend/app/dashboard/page.tsx to format tags as arrays
- [ ] T008 [US1] Implement formatTags utility function to handle different input types in page.tsx
- [ ] T009 [US1] Update request body construction to use properly formatted tags array
- [ ] T010 [US1] Test task creation with single tag to verify API success

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Consistent Tags Handling (Priority: P2)

**Goal**: Ensure all tag-related API calls consistently send tags as arrays for proper backend validation

**Independent Test**: Can be tested by examining all API calls that involve tags and verifying they send arrays instead of strings.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T011 [P] [US2] Create integration test for consistent tag handling in tests/integration/test_tag_consistency.ts

### Implementation for User Story 2

- [ ] T012 [P] [US2] Review other task-related functions in page.tsx for tag handling consistency
- [ ] T013 [US2] Update any other functions that handle tags to use the same formatting approach
- [ ] T014 [US2] Test multiple API endpoints with tags to verify consistency

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Robust Tags Processing (Priority: P3)

**Goal**: Implement robust tag processing that handles various input formats (comma-separated, empty) properly

**Independent Test**: Can be tested by entering different tag formats and verifying they are properly converted to arrays before API submission.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T015 [P] [US3] Create end-to-end test for various tag input formats in tests/e2e/test_tag_formats.ts

### Implementation for User Story 3

- [ ] T016 [P] [US3] Enhance formatTags function to handle comma-separated inputs in page.tsx
- [ ] T017 [US3] Add validation to handle empty tags and special characters properly
- [ ] T018 [US3] Test various input scenarios: comma-separated, single tag, empty, special chars

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T019 [P] Update documentation to reflect new tag handling approach
- [ ] T020 Code cleanup and refactoring if needed
- [ ] T021 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Create unit test for tag formatting in tests/unit/test_tag_formatting.ts"

# Launch all implementation tasks for User Story 1 together:
Task: "Update handleAddTask function in phase2-fullstack/frontend/app/dashboard/page.tsx to format tags as arrays"
Task: "Implement formatTags utility function to handle different input types in page.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence