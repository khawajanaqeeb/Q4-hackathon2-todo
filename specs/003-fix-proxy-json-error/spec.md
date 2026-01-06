# Feature Specification: Fix API Proxy JSON Parsing Error

**Feature Branch**: `003-fix-proxy-json-error`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "solve this error it is occuring repaetedly API proxy error: SyntaxError: Unexpected token 'I', "Internal S"... is not valid JSON at JSON.parse (<anonymous>) at async POST (app\api\auth\proxy\[...path]\route.ts:133:20)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Graceful Error Handling for Non-JSON Backend Responses (Priority: P1)

When the backend service returns an error response (such as 5xx errors) in HTML or plain text format instead of JSON, the API proxy should handle this gracefully and return a meaningful error message to the frontend rather than crashing with a JSON parsing error.

**Why this priority**: This is critical for application stability. Currently, the application crashes with an unhandled exception whenever the backend returns non-JSON error responses, breaking the user experience completely. Users see cryptic error messages and cannot complete their tasks.

**Independent Test**: Can be fully tested by simulating backend errors (shutting down backend service or forcing 500 errors) and verifying that frontend receives a proper JSON error response instead of crashing.

**Acceptance Scenarios**:

1. **Given** the backend service is unavailable, **When** a user attempts to create a new todo item, **Then** the frontend displays "Service temporarily unavailable. Please try again later." instead of showing a JSON parsing error.
2. **Given** the backend returns an HTML 500 error page, **When** the API proxy attempts to forward the request, **Then** the proxy catches the JSON parsing error and returns a standardized JSON error response with status 503.
3. **Given** the backend returns a plain text error message, **When** any API request is made through the proxy, **Then** the proxy detects the non-JSON response and wraps it in a proper error structure.

---

### User Story 2 - Consistent Error Response Format (Priority: P2)

All error responses from the API proxy should follow a consistent JSON format regardless of whether the error originated from the backend service, the proxy itself, or from malformed responses.

**Why this priority**: Consistent error formats allow the frontend to handle errors uniformly, reducing code complexity and improving the user experience. This is secondary to P1 as it's an enhancement rather than a critical bug fix.

**Independent Test**: Can be tested independently by triggering various error scenarios (authentication failures, backend timeouts, malformed responses) and verifying all errors follow the same response structure.

**Acceptance Scenarios**:

1. **Given** various error conditions (401, 403, 500, 503, JSON parse errors), **When** errors occur at any stage of request processing, **Then** all errors return the format `{ error: "message", details: "optional details" }`.
2. **Given** a backend service timeout, **When** the timeout occurs, **Then** the error response includes both a user-friendly message and technical details for debugging.

---

### User Story 3 - Improved Error Logging for Debugging (Priority: P3)

When backend responses cannot be parsed as JSON, the system should log the actual response body (truncated if necessary) to help developers diagnose backend issues.

**Why this priority**: This improves developer experience and reduces time to diagnose issues. It's not critical for end users but valuable for maintenance and debugging.

**Independent Test**: Can be tested by triggering non-JSON responses and verifying that server logs contain the actual response content and response headers.

**Acceptance Scenarios**:

1. **Given** a non-JSON backend response, **When** the parsing error occurs, **Then** server logs include the Content-Type header and first 500 characters of the response body.
2. **Given** repeated parsing errors from the same endpoint, **When** reviewing logs, **Then** developers can identify patterns in backend failures from the logged response data.

---

### Edge Cases

- What happens when the backend returns a valid JSON response but with a non-standard structure?
- How does the system handle responses with Content-Type: application/json but invalid JSON content?
- What happens when the backend returns a 200 OK status but with an HTML error page (common in reverse proxy setups)?
- How does the system handle extremely large error responses (multiple MB of HTML error pages)?
- What happens when the backend response is partially transmitted (connection dropped mid-response)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect when backend responses are not valid JSON before attempting to parse them
- **FR-002**: System MUST return a standardized JSON error response when backend responses cannot be parsed as JSON
- **FR-003**: System MUST check the Content-Type header of backend responses to verify JSON format before parsing
- **FR-004**: System MUST preserve the original HTTP status code from the backend when wrapping error responses, unless the status code indicates success (2xx) with non-JSON content
- **FR-005**: System MUST handle all HTTP methods (GET, POST, PUT, DELETE, PATCH) consistently when dealing with non-JSON responses
- **FR-006**: System MUST log sufficient information about parsing failures to enable debugging (response headers, status code, response preview)
- **FR-007**: Error responses MUST include both a user-friendly message field and an optional details field for technical information
- **FR-008**: System MUST limit the size of response bodies logged to prevent log overflow (maximum 500 characters of response content)
- **FR-009**: System MUST differentiate between network errors, timeout errors, and content parsing errors in error responses

### Key Entities

- **Backend Response**: The HTTP response received from the backend service, which may contain JSON or non-JSON content
  - Attributes: status code, headers (especially Content-Type), body content
  - Relationships: Processed by the API proxy before being returned to the frontend

- **Error Response**: Standardized JSON object returned when errors occur
  - Attributes: error message (user-friendly), details (technical), HTTP status code
  - Relationships: Generated by proxy when backend responses fail or cannot be parsed

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero unhandled JSON parsing exceptions in the API proxy after implementation
- **SC-002**: 100% of non-JSON backend responses result in valid JSON error responses to the frontend
- **SC-003**: All error scenarios (network, timeout, parse errors) return responses within 500ms
- **SC-004**: Error logs include sufficient information to diagnose 95% of backend issues without additional debugging
- **SC-005**: Users receive meaningful error messages instead of technical stack traces in 100% of error cases
- **SC-006**: System handles backend service outages gracefully with appropriate user-facing error messages
