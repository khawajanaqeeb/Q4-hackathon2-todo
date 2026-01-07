---
description: "Task list for Fix API Proxy JSON Parsing Error implementation"
---

# Tasks: Fix API Proxy JSON Parsing Error

**Input**: Design documents from `/specs/003-fix-proxy-json-error/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), quickstart.md (complete)

**Tests**: Test tasks are included based on the comprehensive testing strategy defined in plan.md and quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. This is a focused bug fix, so setup is minimal and user stories build incrementally on the core error handling infrastructure.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **Web app** (Phase II full-stack project):
- Frontend: `phase2-fullstack/frontend/`
- Source: `phase2-fullstack/frontend/app/`, `phase2-fullstack/frontend/lib/`
- Tests: `phase2-fullstack/frontend/tests/`
- Backend: Unchanged (not modified in this fix)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Minimal setup - verify project structure and dependencies are in place

- [ ] T001 Verify Next.js project structure at phase2-fullstack/frontend/
- [ ] T002 Verify TypeScript and Jest dependencies in phase2-fullstack/frontend/package.json
- [ ] T003 Create tests/api/ directory structure at phase2-fullstack/frontend/tests/api/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core error handling utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete. This phase implements the shared utility module that all HTTP methods will use.

- [ ] T004 Create lib/api-utils.ts file at phase2-fullstack/frontend/lib/api-utils.ts
- [ ] T005 [P] Implement safeJsonParse() function in phase2-fullstack/frontend/lib/api-utils.ts
- [ ] T006 [P] Implement createErrorResponse() function in phase2-fullstack/frontend/lib/api-utils.ts
- [ ] T007 [P] Implement logBackendResponse() function in phase2-fullstack/frontend/lib/api-utils.ts
- [ ] T008 Add TypeScript type definitions for error responses in phase2-fullstack/frontend/lib/api-utils.ts
- [ ] T009 Export all utility functions from phase2-fullstack/frontend/lib/api-utils.ts

**Checkpoint**: Foundation ready - utility module complete and ready for use by all HTTP methods

---

## Phase 3: User Story 1 - Graceful Error Handling for Non-JSON Backend Responses (Priority: P1) 🎯 MVP

**Goal**: When backend returns non-JSON responses (HTML/text), proxy handles gracefully and returns meaningful error messages instead of crashing with JSON parse errors.

**Independent Test**: Simulate backend errors (stop backend service or force 500 errors) and verify frontend receives proper JSON error response without crashes.

**Why MVP**: This is the critical bug fix that prevents application crashes. Implementing US1 alone resolves the blocking production issue described in the spec.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Create test file at phase2-fullstack/frontend/tests/api/proxy-route.test.ts with Jest setup
- [ ] T011 [P] [US1] Write test T-PROXY-001: Backend returns valid JSON → Parse success in tests/api/proxy-route.test.ts
- [ ] T012 [P] [US1] Write test T-PROXY-002: Backend returns HTML error page → Standardized error in tests/api/proxy-route.test.ts
- [ ] T013 [P] [US1] Write test T-PROXY-003: Backend returns plain text → Standardized error in tests/api/proxy-route.test.ts
- [ ] T014 [P] [US1] Write test T-PROXY-004: Backend returns 200 OK with non-JSON → Error response in tests/api/proxy-route.test.ts
- [ ] T015 [P] [US1] Write test T-PROXY-005: Content-Type JSON but malformed body → Graceful handling in tests/api/proxy-route.test.ts
- [ ] T016 [P] [US1] Write test T-PROXY-006: Backend connection fails → 503 error in tests/api/proxy-route.test.ts

**Checkpoint**: Run test suite - all 6 tests should FAIL (red state) before implementation begins

### Implementation for User Story 1

**Refactor all HTTP methods to use safe JSON parsing**

- [ ] T017 [US1] Import safeJsonParse utilities in phase2-fullstack/frontend/app/api/auth/proxy/[...path]/route.ts
- [ ] T018 [P] [US1] Refactor GET method to use safeJsonParse() in route.ts (lines 56-73)
- [ ] T019 [P] [US1] Refactor POST method to use safeJsonParse() in route.ts (lines 118-139)
- [ ] T020 [P] [US1] Refactor PUT method to use safeJsonParse() in route.ts (lines 159-180)
- [ ] T021 [P] [US1] Refactor DELETE method to use safeJsonParse() in route.ts (lines 199-216)
- [ ] T022 [P] [US1] Refactor PATCH method to use safeJsonParse() in route.ts (lines 235-256)
- [ ] T023 [US1] Remove all direct .json() calls and replace with safe parsing in route.ts
- [ ] T024 [US1] Add try-catch wrappers around fetch operations in route.ts

**Checkpoint**: Run test suite - tests T-PROXY-001 through T-PROXY-006 should now PASS (green state)

### Validation for User Story 1

- [ ] T025 [US1] Run automated tests: npm test -- tests/api/proxy-route.test.ts
- [ ] T026 [US1] Manual test: Stop backend service and verify frontend error handling per quickstart.md
- [ ] T027 [US1] Verify no unhandled promise rejections in browser console
- [ ] T028 [US1] Verify acceptance criteria from spec.md User Story 1 (all 3 scenarios)

**Checkpoint**: At this point, User Story 1 should be fully functional - the critical bug is fixed and the app no longer crashes on non-JSON backend responses

---

## Phase 4: User Story 2 - Consistent Error Response Format (Priority: P2)

**Goal**: All error responses follow consistent JSON format `{ error: string, details?: string }` regardless of error source (backend, proxy, parse failures).

**Independent Test**: Trigger various error scenarios (401, 403, 500, 503, parse errors) and verify all return the standardized format.

**Dependencies**: Builds on US1's error handling infrastructure

### Tests for User Story 2

- [ ] T029 [P] [US2] Write test T-PROXY-007: All HTTP methods handle errors consistently in tests/api/proxy-route.test.ts
- [ ] T030 [P] [US2] Write test T-PROXY-010: Original status codes preserved in error responses in tests/api/proxy-route.test.ts

**Checkpoint**: Run new tests - should FAIL before implementation

### Implementation for User Story 2

**Standardize error response format across all error paths**

- [ ] T031 [US2] Update createErrorResponse() to ensure consistent format in lib/api-utils.ts
- [ ] T032 [US2] Add optional details field to error responses in lib/api-utils.ts
- [ ] T033 [P] [US2] Standardize error responses in GET method's catch block in route.ts
- [ ] T034 [P] [US2] Standardize error responses in POST method's catch block in route.ts
- [ ] T035 [P] [US2] Standardize error responses in PUT method's catch block in route.ts
- [ ] T036 [P] [US2] Standardize error responses in DELETE method's catch block in route.ts
- [ ] T037 [P] [US2] Standardize error responses in PATCH method's catch block in route.ts
- [ ] T038 [US2] Ensure all error paths preserve original HTTP status codes in route.ts
- [ ] T039 [US2] Add user-friendly error messages for common error scenarios in lib/api-utils.ts

**Checkpoint**: Run test suite - tests T-PROXY-007 and T-PROXY-010 should now PASS

### Validation for User Story 2

- [ ] T040 [US2] Verify all error responses match { error: string, details?: string } format
- [ ] T041 [US2] Test 401, 403, 500, 503 scenarios and verify consistent format
- [ ] T042 [US2] Verify acceptance criteria from spec.md User Story 2 (both scenarios)

**Checkpoint**: At this point, User Stories 1 AND 2 are complete - errors are handled gracefully AND consistently formatted

---

## Phase 5: User Story 3 - Improved Error Logging for Debugging (Priority: P3)

**Goal**: When backend responses cannot be parsed as JSON, log actual response body (truncated), Content-Type header, and status code to help developers diagnose backend issues.

**Independent Test**: Trigger non-JSON responses and verify server logs contain response content and headers (as specified in quickstart.md).

**Dependencies**: Builds on US1's error detection and US2's error formatting

### Tests for User Story 3

- [ ] T043 [P] [US3] Write test T-PROXY-008: Error logs include headers and body preview in tests/api/proxy-route.test.ts
- [ ] T044 [P] [US3] Write test T-PROXY-009: Response body truncated at 500 chars in tests/api/proxy-route.test.ts

**Checkpoint**: Run new tests - should FAIL before implementation

### Implementation for User Story 3

**Add comprehensive logging for debugging**

- [ ] T045 [US3] Implement response body truncation logic (500 char limit) in logBackendResponse()
- [ ] T046 [US3] Add Content-Type header logging in logBackendResponse()
- [ ] T047 [US3] Add HTTP status code logging in logBackendResponse()
- [ ] T048 [US3] Add request URL path logging for correlation in logBackendResponse()
- [ ] T049 [P] [US3] Integrate logBackendResponse() into GET method error path in route.ts
- [ ] T050 [P] [US3] Integrate logBackendResponse() into POST method error path in route.ts
- [ ] T051 [P] [US3] Integrate logBackendResponse() into PUT method error path in route.ts
- [ ] T052 [P] [US3] Integrate logBackendResponse() into DELETE method error path in route.ts
- [ ] T053 [P] [US3] Integrate logBackendResponse() into PATCH method error path in route.ts
- [ ] T054 [US3] Use console.error() for 5xx errors and console.warn() for 4xx errors in logBackendResponse()

**Checkpoint**: Run test suite - tests T-PROXY-008 and T-PROXY-009 should now PASS

### Validation for User Story 3

- [ ] T055 [US3] Verify logs contain Content-Type, status code, and body preview
- [ ] T056 [US3] Verify response body is truncated at 500 characters
- [ ] T057 [US3] Test manual scenario 4 from quickstart.md (logging verification)
- [ ] T058 [US3] Verify acceptance criteria from spec.md User Story 3 (both scenarios)

**Checkpoint**: All user stories (1, 2, 3) are now complete - the bug fix includes graceful handling, consistent formatting, AND comprehensive logging

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and code quality improvements

- [ ] T059 [P] Add inline code comments explaining error handling logic in lib/api-utils.ts
- [ ] T060 [P] Add inline code comments explaining safe parsing usage in route.ts
- [ ] T061 [P] Verify TypeScript strict mode compliance in all modified files
- [ ] T062 [P] Run ESLint and Prettier on lib/api-utils.ts
- [ ] T063 [P] Run ESLint and Prettier on route.ts
- [ ] T064 [P] Run ESLint and Prettier on tests/api/proxy-route.test.ts
- [ ] T065 Run complete test suite: npm test
- [ ] T066 Check test coverage: npm test -- --coverage (target: 90%+ on modified files)
- [ ] T067 Execute all quickstart.md validation scenarios (comprehensive testing checklist)
- [ ] T068 Verify all 6 success criteria from spec.md (SC-001 through SC-006)
- [ ] T069 Run performance benchmark to verify <500ms response times for errors
- [ ] T070 Test backward compatibility with existing frontend error handlers
- [ ] T071 Final review: Ensure no implementation details leaked into error messages
- [ ] T072 Update any relevant documentation referencing proxy error handling

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (T001-T003)
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories (T004-T009)
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - **US1 (Phase 3)**: Depends on Foundational (T004-T009) - No dependencies on other stories
  - **US2 (Phase 4)**: Depends on US1 completion (builds on error handling infrastructure)
  - **US3 (Phase 5)**: Depends on US1 and US2 (builds on error detection and formatting)
- **Polish (Phase 6)**: Depends on all user stories being complete (T059-T072)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ INDEPENDENT MVP
- **User Story 2 (P2)**: Depends on US1 (uses US1's error handling infrastructure) - Extends error handling to ensure consistency
- **User Story 3 (P3)**: Depends on US1 and US2 (uses US1's detection and US2's formatting) - Adds logging on top of error handling

**Note**: This feature has sequential user story dependencies because each story builds on the previous. However, within each story, many tasks can run in parallel (marked with [P]).

### Within Each User Story

- Tests (T010-T016, T029-T030, T043-T044) are written FIRST and MUST FAIL before implementation
- Foundational utilities (T004-T009) MUST complete before any HTTP method refactoring
- HTTP method refactoring tasks within a story (marked [P]) can run in parallel (different methods)
- Validation tasks run after implementation completes for that story

### Parallel Opportunities

**Phase 1 (Setup)**: All 3 tasks can run in parallel
- T001, T002, T003 (different validations/directories)

**Phase 2 (Foundational)**: Utility function implementation (T005-T007) can run in parallel
- T005 (safeJsonParse)
- T006 (createErrorResponse)
- T007 (logBackendResponse)

**Phase 3 (US1 - Tests)**: All 6 test tasks can run in parallel
- T011, T012, T013, T014, T015, T016 (different test cases in same file)

**Phase 3 (US1 - Implementation)**: All 5 HTTP method refactorings can run in parallel
- T018 (GET), T019 (POST), T020 (PUT), T021 (DELETE), T022 (PATCH)

**Phase 4 (US2 - Implementation)**: HTTP method standardization tasks can run in parallel
- T033 (GET), T034 (POST), T035 (PUT), T036 (DELETE), T037 (PATCH)

**Phase 5 (US3 - Implementation)**: Logging integration tasks can run in parallel
- T049 (GET), T050 (POST), T051 (PUT), T052 (DELETE), T053 (PATCH)

**Phase 6 (Polish)**: Many tasks can run in parallel
- T059, T060 (documentation - different files)
- T062, T063, T064 (linting - different files)

---

## Parallel Example: User Story 1 Implementation

```bash
# After foundational phase is complete and tests are written and failing:

# Launch all HTTP method refactorings together (different methods, same concepts):
Task: "Refactor GET method to use safeJsonParse() in route.ts"
Task: "Refactor POST method to use safeJsonParse() in route.ts"
Task: "Refactor PUT method to use safeJsonParse() in route.ts"
Task: "Refactor DELETE method to use safeJsonParse() in route.ts"
Task: "Refactor PATCH method to use safeJsonParse() in route.ts"

# After completion, run sequential cleanup:
Task: "Remove all direct .json() calls and replace with safe parsing in route.ts"
Task: "Add try-catch wrappers around fetch operations in route.ts"

# Then run all validation tasks:
Task: "Run automated tests: npm test -- tests/api/proxy-route.test.ts"
Task: "Manual test: Stop backend service and verify frontend error handling"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - RECOMMENDED

**Why**: US1 fixes the critical production bug (JSON parse crashes). This alone delivers immense value.

1. Complete Phase 1: Setup (T001-T003) - 5 minutes
2. Complete Phase 2: Foundational (T004-T009) - 30 minutes (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (T010-T028) - 2 hours
   - Write tests first (T010-T016) - 30 minutes
   - Implement error handling (T017-T024) - 60 minutes
   - Validate (T025-T028) - 30 minutes
4. **STOP and VALIDATE**: Test User Story 1 independently
5. **Deploy if ready** - the critical bug is now fixed

**Estimated Time for MVP**: ~3 hours
**Value Delivered**: Application no longer crashes on backend errors (resolves production incident)

### Incremental Delivery (All User Stories)

1. **Foundation** (Phases 1-2): Setup + Foundational → T001-T009 (45 minutes)
2. **MVP** (Phase 3): US1 → T010-T028 → Test independently → Deploy (2 hours) ✅ **Critical bug fixed**
3. **Enhancement 1** (Phase 4): US2 → T029-T042 → Test independently (1.5 hours) ✅ **Consistent errors**
4. **Enhancement 2** (Phase 5): US3 → T043-T058 → Test independently (1.5 hours) ✅ **Better debugging**
5. **Finalize** (Phase 6): Polish → T059-T072 → Final validation (1 hour)

**Total Estimated Time**: ~6.5 hours for complete implementation
**Each story adds value without breaking previous stories**

### Sequential Strategy (Single Developer)

1. Complete Setup (T001-T003)
2. Complete Foundational (T004-T009) - MUST finish before proceeding
3. Implement User Story 1 (T010-T028) - Test and validate before moving on
4. Implement User Story 2 (T029-T042) - Test and validate before moving on
5. Implement User Story 3 (T043-T058) - Test and validate before moving on
6. Polish and final validation (T059-T072)

**Advantage**: Clear checkpoints, thorough testing at each stage
**Disadvantage**: Longer time to first deployment

### Parallel Team Strategy (If Multiple Developers)

**Not applicable for this feature** - sequential dependencies between user stories mean they must be completed in order (US1 → US2 → US3). However, within each story, tasks can be parallelized:

**Within US1** (after T004-T009 complete):
- Developer A: Write tests (T010-T016)
- Developer B: Refactor GET, POST, PUT (T018-T020)
- Developer C: Refactor DELETE, PATCH (T021-T022)
- All: Come together for cleanup (T023-T024) and validation (T025-T028)

**Within US2** (after US1 complete):
- Developer A: Update utilities and tests (T029-T032)
- Developer B: Standardize GET, POST, PUT errors (T033-T035)
- Developer C: Standardize DELETE, PATCH errors (T036-T037)
- Developer A: Final standardization and validation (T038-T042)

**Within US3** (after US2 complete):
- Developer A: Implement logging functions and tests (T043-T048)
- Developer B: Integrate logging into GET, POST, PUT (T049-T051)
- Developer C: Integrate logging into DELETE, PATCH (T052-T053)
- All: Validation together (T055-T058)

---

## Notes

- **[P] tasks** = different files or different methods, no dependencies within that group
- **[Story] label** maps task to specific user story for traceability (US1, US2, US3)
- **Sequential user stories**: US2 builds on US1, US3 builds on US2 - this is intentional architecture
- **Tests first**: All test tasks (T010-T016, T029-T030, T043-T044) MUST be written and FAIL before implementation
- **Checkpoints**: Stop at each checkpoint to validate story independently before proceeding
- **File paths**: All paths are absolute from repository root (phase2-fullstack/frontend/...)
- **Commit strategy**: Commit after completing each user story phase (after validation)
- **Backward compatibility**: Maintained throughout - existing frontend code requires no changes

---

## Task Summary

**Total Tasks**: 72 tasks
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 6 tasks (BLOCKING)
- Phase 3 (US1 - P1): 19 tasks (6 tests + 8 implementation + 5 validation) 🎯 MVP
- Phase 4 (US2 - P2): 14 tasks (2 tests + 9 implementation + 3 validation)
- Phase 5 (US3 - P3): 16 tasks (2 tests + 10 implementation + 4 validation)
- Phase 6 (Polish): 14 tasks (documentation, linting, final validation)

**Parallel Opportunities**: 42 tasks marked [P] can run concurrently within their phase
**User Story Distribution**:
- US1: 19 tasks (critical bug fix)
- US2: 14 tasks (consistency enhancement)
- US3: 16 tasks (debugging improvement)

**Estimated Effort**:
- MVP (US1 only): ~3 hours
- Full implementation (all stories): ~6.5 hours
- Per user story average: ~2 hours

**Test Coverage**: 10 automated tests (T-PROXY-001 through T-PROXY-010) across all user stories

---

## Success Criteria Validation Map

Each success criterion from spec.md maps to specific validation tasks:

- **SC-001** (Zero unhandled exceptions): Validated by T025, T027, T065, T067
- **SC-002** (100% non-JSON → JSON): Validated by T025, T026, T040, T067
- **SC-003** (Error responses <500ms): Validated by T069
- **SC-004** (Logs include debugging info): Validated by T055, T056, T057
- **SC-005** (Meaningful user messages): Validated by T027, T028, T071
- **SC-006** (Graceful backend outages): Validated by T026, T027, T067

All validation tasks are in Phase 6 (Polish) or within each user story's validation section.
