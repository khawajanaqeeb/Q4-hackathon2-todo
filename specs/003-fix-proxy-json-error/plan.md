# Implementation Plan: Fix API Proxy JSON Parsing Error

**Branch**: `003-fix-proxy-json-error` | **Date**: 2026-01-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-fix-proxy-json-error/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix critical bug in Next.js API proxy route where JSON parsing crashes when backend returns non-JSON error responses (HTML/plain text). The proxy currently attempts to parse all backend responses as JSON without validation, causing unhandled exceptions when backends return 5xx errors as HTML pages. Solution involves implementing safe JSON parsing with Content-Type header validation, proper error wrapping, and comprehensive logging for debugging.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router)
**Primary Dependencies**: Next.js server runtime, native fetch API
**Storage**: N/A (stateless proxy layer)
**Testing**: Jest with React Testing Library for API route testing
**Target Platform**: Next.js Edge/Node.js runtime (Vercel deployment)
**Project Type**: Web application (frontend API proxy layer)
**Performance Goals**: <500ms response time for all error scenarios, minimal overhead on successful requests
**Constraints**: Must maintain backward compatibility with existing frontend API calls, preserve all HTTP status codes from backend
**Scale/Scope**: Single file modification (route.ts), affects all API proxy requests (GET, POST, PUT, DELETE, PATCH)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Alignment with Constitution Principles:

**✅ I. Spec-Driven Development (SDD) Mandate**
- Complete specification exists (spec.md) with clear requirements and acceptance criteria
- This plan documents HOW to implement WHAT was specified
- All changes traceable to functional requirements FR-001 through FR-009

**✅ II. Agentic Dev Stack Workflow**
- Following prescribed workflow: Specify → Plan (current) → Tasks → Implement
- Using `/sp.plan` command as mandated

**✅ III. Phase-Based Evolution**
- This is a Phase II bug fix within existing full-stack web application
- Does not introduce new phases or alter phase structure
- Enhances existing Phase II functionality

**✅ IV. Technology Stack Constraints**
- Uses existing Phase II stack: Next.js 16+, TypeScript
- No new technologies introduced
- Maintains immutability of Phase II stack

**✅ V. Feature Progression Discipline**
- This is a bug fix, not a new feature tier
- Ensures reliability of existing Intermediate Level features (API error handling)

**✅ VI. Code Quality & Architecture Standards**
- TypeScript strict mode compliance required
- ESLint + Prettier formatting
- Single Responsibility Principle: error handling isolated in helper function
- DRY: Extract reusable response parsing logic

**✅ VII. Security & Safety Discipline**
- Phase II security maintained: no exposure of internal errors to users
- Prevents information leakage through error messages
- Sanitizes logged response bodies (500 char limit)

**✅ VIII. Documentation Excellence**
- Implementation will include inline code comments
- Error logging with context for debugging
- Changes documented in this plan and subsequent tasks

**No violations detected. Proceeding with implementation.**

## Project Structure

### Documentation (this feature)

```text
specs/003-fix-proxy-json-error/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technical research)
├── data-model.md        # N/A (no data entities for this bug fix)
├── quickstart.md        # Phase 1 output (testing and validation guide)
├── contracts/           # N/A (no new API contracts, modifying existing proxy)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
phase2-fullstack/
├── frontend/
│   ├── app/
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── proxy/
│   │   │           └── [...path]/
│   │   │               └── route.ts          # PRIMARY FILE TO MODIFY
│   ├── lib/
│   │   └── api-utils.ts                      # NEW: Shared error handling utilities
│   └── tests/
│       └── api/
│           └── proxy-route.test.ts           # NEW: API route tests
└── backend/
    └── [unchanged - backend not modified]
```

**Structure Decision**: This is a focused bug fix within the existing Phase II web application structure. We're modifying the frontend Next.js API proxy route (`route.ts`) and creating a new utility module for reusable error handling logic. The backend is not affected as this issue is isolated to the frontend proxy layer.

## Complexity Tracking

> **No complexity violations** - This implementation maintains simplicity:
> - Single responsibility: error handling for proxy responses
> - No new architectural patterns introduced
> - Leverages existing Next.js API route structure
> - Minimal abstraction: one helper function for safe JSON parsing

---

## Phase 0: Research & Technical Discovery

### Research Tasks

#### R-001: Content-Type Header Validation Patterns
**Question**: What are the best practices for validating Content-Type headers before JSON parsing in Node.js/Next.js environments?

**Research Findings**:
- **Standard Approach**: Check `response.headers.get('content-type')` for `application/json` substring
- **Robustness**: Handle cases where Content-Type includes charset (e.g., `application/json; charset=utf-8`)
- **Edge Cases**: Some APIs return `text/json` or omit Content-Type entirely
- **Next.js Context**: Response.json() method throws on invalid JSON, requiring try-catch wrapper

**Decision**: Implement two-tier validation:
1. Check Content-Type header (warn if not JSON but attempt parse anyway for backward compatibility)
2. Wrap all `.json()` calls in try-catch to handle malformed JSON regardless of Content-Type

**Rationale**: Defensive programming - trust but verify. Headers can lie, so we validate both header and actual parsing.

#### R-002: Error Response Standardization Patterns
**Question**: What error response format should we standardize on for the API proxy?

**Research Findings**:
- **Industry Standards**: RFC 7807 (Problem Details for HTTP APIs) suggests structured error format
- **Existing Codebase**: Current code uses `{ error: "message" }` format in some places
- **Next.js Patterns**: NextResponse.json() supports arbitrary JSON structure
- **Frontend Compatibility**: Need to ensure frontend error handlers can consume format

**Decision**: Use simple, consistent format:
```typescript
{
  error: string,           // User-facing message
  details?: string,        // Optional technical details (dev mode only)
  timestamp?: string       // Optional ISO timestamp
}
```

**Rationale**: Balances simplicity with extensibility. Compatible with existing frontend error handling. Room to add fields later without breaking changes.

#### R-003: Safe Logging Practices for Response Bodies
**Question**: How to safely log response bodies without exposing sensitive data or causing log overflow?

**Research Findings**:
- **Log Size**: Large HTML error pages (50KB+) can fill logs quickly
- **Sensitive Data**: Response bodies might contain PII or auth tokens
- **Node.js Limits**: console.log truncates very long strings inconsistently
- **Best Practices**: Truncate to 500-1000 chars, sanitize known sensitive patterns

**Decision**: Implement logging with:
- Maximum 500 characters from response body
- Include Content-Type header for context
- Include HTTP status code
- Log at error level for 5xx, warn level for 4xx
- No sanitization (assume backend doesn't leak secrets in error pages, but truncation limits exposure)

**Rationale**: 500 chars captures enough HTML to identify error page type without overwhelming logs. Status code and Content-Type provide essential debugging context.

#### R-004: Backward Compatibility with Existing Frontend Code
**Question**: Will changing error response format break existing frontend error handlers?

**Research Findings**:
- **Current Frontend**: Uses `.catch()` blocks expecting `error` field in response
- **TypeScript Types**: Frontend has `ApiError` type expecting `{ error: string }`
- **Breaking Change Risk**: If we change structure, frontend displays might break
- **Migration Effort**: Would require updating all API call sites

**Decision**: Maintain existing `{ error: string }` as base format, add optional fields:
```typescript
{ error: string, details?: string }
```

**Rationale**: Minimizes frontend changes. Existing code continues working. New code can optionally consume `details` field for enhanced error reporting.

#### R-005: Testing Strategy for Non-JSON Backend Responses
**Question**: How to test proxy behavior with various backend response types without modifying backend?

**Research Findings**:
- **Jest Mocking**: Can mock `fetch()` to return custom responses
- **MSW (Mock Service Worker)**: Popular for mocking HTTP requests in tests
- **Next.js Testing**: API routes can be tested directly with request/response mocks
- **Response Types to Test**: HTML error pages, plain text, empty body, malformed JSON, valid JSON

**Decision**: Use Jest with manual fetch mocking:
```typescript
global.fetch = jest.fn(() => Promise.resolve({
  ok: false,
  status: 500,
  headers: new Headers({ 'content-type': 'text/html' }),
  text: () => Promise.resolve('<html>Internal Server Error</html>'),
  json: () => Promise.reject(new Error('invalid json'))
}))
```

**Rationale**: Lightweight, no additional dependencies. Provides full control over response simulation. Easy to test edge cases.

### Research Summary

All technical unknowns resolved. Key decisions documented:
1. **Validation Strategy**: Two-tier (Content-Type + try-catch)
2. **Error Format**: `{ error: string, details?: string }` (backward compatible)
3. **Logging**: Truncate to 500 chars, include headers and status
4. **Testing**: Jest with fetch mocking
5. **Compatibility**: Maintain existing error structure

---

## Phase 1: Design & Implementation Architecture

### Component Architecture

#### Modified Component: API Proxy Route Handler

**File**: `phase2-fullstack/frontend/app/api/auth/proxy/[...path]/route.ts`

**Current Issues**:
- Lines 67, 133, 174, 210, 250: Direct `.json()` calls without error handling
- No Content-Type validation before parsing
- Inconsistent error responses across HTTP methods

**Proposed Changes**:
1. Extract safe JSON parsing into helper function
2. Add Content-Type header validation
3. Wrap all backend response processing in try-catch
4. Standardize error response format
5. Add comprehensive logging for debugging

#### New Component: API Utilities Module

**File**: `phase2-fullstack/frontend/lib/api-utils.ts` (NEW)

**Purpose**: Centralize response parsing and error handling logic

**Exports**:
```typescript
// Safe JSON parsing with error handling
export async function safeJsonParse(response: Response): Promise<any>

// Create standardized error response
export function createErrorResponse(
  message: string,
  statusCode: number,
  details?: string
): NextResponse

// Log backend response details for debugging
export function logBackendResponse(
  response: Response,
  bodyPreview: string
): void
```

**Rationale**: DRY principle - avoid duplicating error handling across all HTTP methods (GET, POST, PUT, DELETE, PATCH). Single source of truth for error response format.

### Data Flow Architecture

**Current Flow (Buggy)**:
```
Frontend Request → Next.js Proxy Route → Backend API
                                            ↓
                                      Response (any content-type)
                                            ↓
                                      .json() parse (CRASHES if not JSON)
                                            ↓
                                      Return to Frontend
```

**New Flow (Fixed)**:
```
Frontend Request → Next.js Proxy Route → Backend API
                                            ↓
                                      Response (any content-type)
                                            ↓
                                      Check Content-Type header
                                            ↓
                                      safeJsonParse() with try-catch
                                            ↓
                         ┌─────────────────┴─────────────────┐
                         ↓                                   ↓
                   Parse Success                       Parse Failure
                         ↓                                   ↓
                   Return JSON data                    Log error details
                         ↓                                   ↓
                   Status from backend              Return { error: "..." }
                                                            ↓
                                                      Status 503 (or original)
```

### Error Handling Strategy

#### Error Categories and Responses

**Category 1: Network/Connection Errors**
- Trigger: Backend unreachable, timeout, connection refused
- Response: `{ error: "API service unavailable", details: "Connection failed" }`
- Status: 503 Service Unavailable
- Logging: Error level with exception details

**Category 2: Non-JSON Content-Type**
- Trigger: Backend returns HTML/text with non-JSON Content-Type
- Response: `{ error: "API service error", details: "Invalid response format" }`
- Status: Original backend status code (or 503 if 2xx with non-JSON)
- Logging: Warning level with Content-Type and body preview

**Category 3: Malformed JSON**
- Trigger: Content-Type says JSON but parsing fails
- Response: `{ error: "API service error", details: "Malformed response" }`
- Status: Original backend status code
- Logging: Warning level with parse error and body preview

**Category 4: Valid JSON**
- Trigger: Successful parse
- Response: Pass through backend JSON
- Status: Original backend status code
- Logging: None (success case)

### Implementation Pattern for All HTTP Methods

**Template to apply to GET, POST, PUT, DELETE, PATCH**:

```typescript
export async function METHOD(request: NextRequest, context: Context) {
  // ... existing auth and path handling ...

  try {
    // Fetch from backend (existing code)
    const backendResponse = await fetch(backendUrl, { /* options */ });

    // NEW: Safe JSON parsing
    const data = await safeJsonParse(backendResponse);
    return NextResponse.json(data, { status: backendResponse.status });

  } catch (error) {
    // NEW: Enhanced error handling
    console.error('API proxy error:', error);
    return createErrorResponse(
      'API service unavailable',
      503,
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
}
```

### Testing Strategy

#### Unit Tests (New File: `tests/api/proxy-route.test.ts`)

**Test Cases**:

1. **T-PROXY-001**: Backend returns valid JSON → Parse success, return data
2. **T-PROXY-002**: Backend returns HTML error page → Return standardized error
3. **T-PROXY-003**: Backend returns plain text → Return standardized error
4. **T-PROXY-004**: Backend returns 200 OK with non-JSON → Treat as error
5. **T-PROXY-005**: Content-Type is JSON but body is malformed → Handle gracefully
6. **T-PROXY-006**: Backend connection fails → Return 503 with appropriate message
7. **T-PROXY-007**: All HTTP methods (GET/POST/PUT/DELETE/PATCH) handle errors consistently
8. **T-PROXY-008**: Error logs include response headers and body preview
9. **T-PROXY-009**: Response body logging truncates at 500 characters
10. **T-PROXY-010**: Original backend status codes preserved in error responses

**Coverage Target**: 100% of new error handling code paths

#### Integration Test Scenarios

**Manual Testing Checklist** (documented in quickstart.md):

1. Stop backend service → Verify frontend shows "Service unavailable" message
2. Force backend 500 error → Verify HTML error page is caught and wrapped
3. Check browser console logs → Verify no unhandled promise rejections
4. Test all CRUD operations with backend down → Verify consistent error messaging
5. Restart backend → Verify normal operations resume without refresh

---

## Phase 2: Task Breakdown Preview

**Note**: Detailed tasks generated by `/sp.tasks` command. High-level breakdown:

### Atomic Tasks (Implementation Order):

**Task Group 1: Foundation (Utility Functions)**
- T-001: Create `lib/api-utils.ts` with `safeJsonParse()` function
- T-002: Implement `createErrorResponse()` helper
- T-003: Implement `logBackendResponse()` helper
- T-004: Write unit tests for utility functions

**Task Group 2: Route Modification**
- T-005: Refactor GET method in route.ts to use safe parsing
- T-006: Refactor POST method in route.ts to use safe parsing
- T-007: Refactor PUT method in route.ts to use safe parsing
- T-008: Refactor DELETE method in route.ts to use safe parsing
- T-009: Refactor PATCH method in route.ts to use safe parsing

**Task Group 3: Testing & Validation**
- T-010: Create API route test file with mock responses
- T-011: Implement test cases T-PROXY-001 through T-PROXY-010
- T-012: Manual integration testing with backend service toggling
- T-013: Verify all success criteria from spec.md (SC-001 through SC-006)

**Task Group 4: Documentation**
- T-014: Add inline code comments explaining error handling logic
- T-015: Create quickstart.md with testing instructions
- T-016: Update any relevant documentation referencing error handling

---

## Architectural Decisions

### AD-001: Why Create Separate Utility Module vs. Inline Error Handling?

**Decision**: Extract error handling to `lib/api-utils.ts`

**Alternatives Considered**:
1. Inline error handling in each HTTP method (copy-paste)
2. Internal helper function within route.ts file
3. Shared utility module (chosen)

**Rationale**:
- **DRY Principle**: Five HTTP methods would duplicate identical logic
- **Maintainability**: Single source of truth for error format changes
- **Testability**: Utilities can be unit tested independently
- **Reusability**: Other API routes can use same error handling

**Trade-offs Accepted**: Adds one new file, increases coupling between route and utils

### AD-002: Why Preserve Backend Status Codes vs. Normalize to 503?

**Decision**: Preserve original backend status codes when possible

**Alternatives Considered**:
1. Always return 503 for any backend error
2. Map backend errors to frontend-appropriate codes
3. Preserve original codes (chosen)

**Rationale**:
- **Debugging**: Original status helps diagnose backend issues
- **Semantics**: 401 vs 500 have different meanings, shouldn't be conflated
- **Client Logic**: Frontend may have different handling for 401 (redirect) vs 500 (retry)

**Exception**: When backend returns 2xx with non-JSON, override to 503 (malformed success is a server error)

### AD-003: Why Two-Tier Validation (Header + Try-Catch) vs. Header Only?

**Decision**: Check Content-Type AND wrap parsing in try-catch

**Alternatives Considered**:
1. Only check Content-Type header, skip if not JSON
2. Only use try-catch, ignore headers
3. Both (chosen)

**Rationale**:
- **Defense in Depth**: Headers can be incorrect or missing
- **Backward Compatibility**: Some backends might omit Content-Type
- **Edge Cases**: Handles "Content-Type: application/json" with invalid JSON body
- **Cost**: Minimal performance overhead, max safety

**Trade-offs Accepted**: Slight redundancy, but eliminates entire class of bugs

---

## Risk Assessment

### High-Priority Risks

**RISK-001: Breaking Existing Frontend Error Handlers**
- **Likelihood**: Medium
- **Impact**: High (entire frontend error handling could break)
- **Mitigation**: Maintain exact `{ error: string }` format, add optional fields only
- **Validation**: Test all existing API call sites before deployment

**RISK-002: Performance Regression on Success Path**
- **Likelihood**: Low
- **Impact**: Medium (slower API responses)
- **Mitigation**: Minimize overhead - only add try-catch (negligible cost in V8)
- **Validation**: Benchmark response times before/after (target: <5ms overhead)

### Medium-Priority Risks

**RISK-003: Logging Overhead with High Error Rates**
- **Likelihood**: Low (should only occur during outages)
- **Impact**: Medium (log storage costs, performance)
- **Mitigation**: 500 char truncation, rate limiting if needed
- **Monitoring**: Track log volume, add sampling if excessive

**RISK-004: Incomplete Test Coverage**
- **Likelihood**: Medium
- **Impact**: Medium (bugs slip through)
- **Mitigation**: Comprehensive test suite with edge cases
- **Validation**: Minimum 90% coverage on modified files

---

## Success Validation Checklist

**From Specification (spec.md) Success Criteria**:

- [ ] **SC-001**: Zero unhandled JSON parsing exceptions after deployment
  - Validation: Test suite has 100% coverage of parse paths
  - Validation: No uncaught promise rejections in browser console

- [ ] **SC-002**: 100% of non-JSON responses return valid JSON errors
  - Validation: All test cases pass (T-PROXY-002, T-PROXY-003, T-PROXY-004)
  - Validation: Manual testing with HTML/text backend responses

- [ ] **SC-003**: Error responses return within 500ms
  - Validation: Benchmark tests show <500ms p95
  - Validation: No noticeable delay in error scenarios

- [ ] **SC-004**: Error logs include sufficient debugging information
  - Validation: Logs contain Content-Type, status code, body preview
  - Validation: 95% of simulated errors diagnosable from logs alone

- [ ] **SC-005**: Users see meaningful error messages (not stack traces)
  - Validation: Frontend displays user-friendly messages
  - Validation: No technical jargon exposed to end users

- [ ] **SC-006**: System handles backend outages gracefully
  - Validation: Manual testing with backend service stopped
  - Validation: All CRUD operations show appropriate error messages

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to create detailed task breakdown
2. **Implementation**: Execute tasks in order via Claude Code
3. **Testing**: Validate all acceptance criteria and success criteria
4. **Review**: Ensure constitution compliance maintained throughout
5. **Documentation**: Complete quickstart.md and inline comments
6. **Deployment**: Merge to main after all tests pass

---

**Plan Status**: ✅ Complete - Ready for `/sp.tasks` command
**Phase 0 Research**: ✅ Complete - All unknowns resolved
**Phase 1 Design**: ✅ Complete - Architecture documented
**Constitution Check**: ✅ Passed - No violations
