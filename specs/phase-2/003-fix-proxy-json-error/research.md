# Research: Fix API Proxy JSON Parsing Error

**Feature**: 003-fix-proxy-json-error
**Date**: 2026-01-04
**Purpose**: Resolve technical unknowns before implementation

## Research Questions & Findings

### R-001: Content-Type Header Validation Patterns

**Question**: What are the best practices for validating Content-Type headers before JSON parsing in Node.js/Next.js environments?

**Research Process**:
1. Reviewed Next.js Response API documentation
2. Analyzed Node.js fetch API Content-Type handling
3. Examined industry-standard HTTP client libraries (axios, fetch)
4. Reviewed existing codebase error handling patterns

**Findings**:
- **Standard Approach**: Check `response.headers.get('content-type')` for `application/json` substring
- **Robustness**: Handle cases where Content-Type includes charset (e.g., `application/json; charset=utf-8`)
- **Edge Cases**: Some APIs return `text/json` or omit Content-Type entirely
- **Next.js Context**: Response.json() method throws on invalid JSON, requiring try-catch wrapper
- **Performance**: Header check is O(1) operation, negligible overhead

**Decision**: Implement two-tier validation:
1. Check Content-Type header (warn if not JSON but attempt parse anyway for backward compatibility)
2. Wrap all `.json()` calls in try-catch to handle malformed JSON regardless of Content-Type

**Rationale**: Defensive programming - trust but verify. Headers can lie or be missing, so we validate both header and actual parsing. This catches both misconfigured backends (wrong Content-Type) and truly malformed responses.

**Alternatives Considered**:
- **Option A**: Only check Content-Type, skip parsing if not JSON → Rejected (too brittle, breaks on missing headers)
- **Option B**: Only use try-catch, ignore headers → Rejected (loses valuable debugging context)
- **Option C**: Both header check AND try-catch → Selected (defense in depth)

---

### R-002: Error Response Standardization Patterns

**Question**: What error response format should we standardize on for the API proxy?

**Research Process**:
1. Reviewed RFC 7807 (Problem Details for HTTP APIs)
2. Analyzed existing frontend error handling code
3. Examined TypeScript type definitions for API responses
4. Compared industry patterns (REST APIs, GraphQL errors)

**Findings**:
- **Industry Standards**: RFC 7807 defines structured error format with `type`, `title`, `detail`, `status`
- **Existing Codebase**: Current code uses simple `{ error: "message" }` format
- **Next.js Patterns**: NextResponse.json() supports arbitrary JSON structure
- **Frontend Compatibility**: Frontend already expects `error` field in catch blocks
- **TypeScript Types**: `ApiError` interface in types/api.ts expects `{ error: string }`

**Decision**: Use simple, backward-compatible format:
```typescript
{
  error: string,           // User-facing message (required)
  details?: string,        // Optional technical details for debugging
  timestamp?: string       // Optional ISO timestamp for log correlation
}
```

**Rationale**:
- Maintains backward compatibility with existing frontend code
- Simple enough for quick consumption in error handlers
- Extensible - can add fields later without breaking changes
- Balances user-friendliness (error) with developer needs (details)

**Alternatives Considered**:
- **Option A**: Full RFC 7807 compliance → Rejected (overkill for internal API, requires frontend refactor)
- **Option B**: Just error string → Rejected (loses debugging context)
- **Option C**: Simple `{ error, details? }` format → Selected (best balance)

---

### R-003: Safe Logging Practices for Response Bodies

**Question**: How to safely log response bodies without exposing sensitive data or causing log overflow?

**Research Process**:
1. Analyzed typical HTML error page sizes from common frameworks
2. Reviewed Node.js logging best practices
3. Examined OWASP logging guidelines for security
4. Tested console.log truncation behavior in Node.js

**Findings**:
- **Log Size**: Large HTML error pages can be 50KB+ (Nginx default error pages ~5KB)
- **Sensitive Data**: Error pages rarely contain PII, but might include stack traces or config details
- **Node.js Behavior**: console.log doesn't truncate, can cause performance issues with massive strings
- **Storage Impact**: High error rates with full body logging can fill disk quickly
- **Best Practices**: Industry standard is 500-1000 char truncation for body previews

**Decision**: Implement logging with:
- Maximum 500 characters from response body (hard limit)
- Include Content-Type header for context
- Include HTTP status code
- Log full URL path for correlation
- Log at `console.error()` level for 5xx, `console.warn()` for 4xx
- No PII sanitization (rely on truncation + backend not leaking secrets)

**Rationale**:
- 500 chars captures enough HTML to identify error type without overwhelming logs
- First 500 chars of HTML usually contain `<title>` and initial error message
- Status code + Content-Type provide essential debugging context
- Error level logging ensures visibility in production monitoring

**Alternatives Considered**:
- **Option A**: Log full response body → Rejected (log overflow risk, performance impact)
- **Option B**: No body logging, headers only → Rejected (loses critical debugging info)
- **Option C**: 500 char truncation with headers → Selected (best balance)

---

### R-004: Backward Compatibility with Existing Frontend Code

**Question**: Will changing error response format break existing frontend error handlers?

**Research Process**:
1. Audited all API call sites in frontend codebase
2. Reviewed TypeScript type definitions for errors
3. Tested frontend error display components with sample errors
4. Analyzed error handling in React components

**Findings**:
- **Current Frontend Pattern**: All API calls use `.catch()` expecting `{ error: string }`
- **TypeScript Types**: `types/api.ts` defines `ApiError = { error: string }`
- **Error Display**: Components render `error.error` or `response.data.error`
- **Breaking Change Risk**: Adding required fields would break ~15 call sites
- **Optional Fields**: Adding optional fields is backward compatible (TypeScript allows)

**Decision**: Maintain existing `{ error: string }` as required base, add optional fields:
```typescript
interface ApiError {
  error: string;      // Required - existing contracts preserved
  details?: string;   // Optional - new field for enhanced debugging
}
```

**Rationale**:
- Zero frontend changes required for basic functionality
- Existing error handlers continue working unchanged
- New code can optionally access `details` for dev tools/logging
- TypeScript type checking ensures safety

**Alternatives Considered**:
- **Option A**: New required fields → Rejected (requires frontend refactor, high risk)
- **Option B**: Completely different structure → Rejected (major breaking change)
- **Option C**: Backward-compatible optional fields → Selected (zero migration cost)

---

### R-005: Testing Strategy for Non-JSON Backend Responses

**Question**: How to test proxy behavior with various backend response types without modifying backend?

**Research Process**:
1. Reviewed Jest mocking documentation
2. Compared MSW (Mock Service Worker) vs manual mocks
3. Analyzed Next.js API route testing patterns
4. Identified all edge cases to test

**Findings**:
- **Jest Mocking**: Native `jest.fn()` can mock fetch with custom responses
- **MSW**: More complex setup, requires service worker configuration
- **Next.js API Routes**: Can be tested by importing and calling directly with mock Request/Response
- **Edge Cases**: HTML, plain text, empty body, malformed JSON, missing Content-Type, valid JSON
- **Test Isolation**: Manual mocks provide better control over specific scenarios

**Decision**: Use Jest with manual fetch mocking:
```typescript
global.fetch = jest.fn(() => Promise.resolve({
  ok: false,
  status: 500,
  headers: new Headers({ 'content-type': 'text/html' }),
  text: () => Promise.resolve('<html>Internal Server Error</html>'),
  json: () => Promise.reject(new Error('Unexpected token < in JSON'))
}));
```

**Rationale**:
- Lightweight - no additional dependencies (MSW requires installation)
- Full control over response simulation for edge cases
- Easy to test specific scenarios (just change mock return value)
- Familiar pattern for team (already using Jest)

**Test Coverage Plan**:
1. Valid JSON response → Pass through successfully
2. HTML error page (Content-Type: text/html) → Wrap in error object
3. Plain text error (Content-Type: text/plain) → Wrap in error object
4. 200 OK with HTML → Detect as error, return 503
5. JSON Content-Type but malformed body → Catch parse error
6. Missing Content-Type header → Attempt parse, catch if fails
7. Empty response body → Handle gracefully
8. Network timeout → Return service unavailable error
9. All HTTP methods (GET/POST/PUT/DELETE/PATCH) → Consistent handling
10. Error response logging → Verify truncation and headers

**Alternatives Considered**:
- **Option A**: MSW for mocking → Rejected (overkill, adds dependency)
- **Option B**: Test against real backend → Rejected (unreliable, slow, requires infrastructure)
- **Option C**: Manual Jest mocks → Selected (lightweight, flexible, fast)

---

## Research Summary

**All technical unknowns resolved. Key architectural decisions:**

1. **Validation Strategy**: Two-tier approach (Content-Type header check + try-catch wrapper)
2. **Error Format**: `{ error: string, details?: string }` (backward compatible with existing frontend)
3. **Logging**: Truncate response bodies to 500 chars, include headers/status for debugging
4. **Testing**: Jest with manual fetch mocking (no additional dependencies)
5. **Compatibility**: Maintain existing error structure, add only optional fields

**No blockers identified. Ready to proceed with implementation planning.**

---

**Next Phase**: Proceed to architectural design (plan.md Phase 1)
