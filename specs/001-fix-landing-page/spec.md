# Feature Specification: Fix Auth Proxy Error and Create Modern Landing Page

**Feature Branch**: `001-fix-landing-page`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "i am facing this error solve all issues of frontend and backend throughly and generate modren landing page for this full stack todo app. landing page must contain welcome message and table style task display with all the fearues and wroking as descibed in my phase-2 folder in specs. first solve this issue.Error: Route "/api/auth/proxy/[...path]" used `params.path`. `params` is a Promise and must be unwrapped with `await` or `React.use()` before accessing its properties. Learn more: https://nextjs.org/docs/messages/sync-dynamic-apis
    at GET (app\api\auth\proxy\[...path]\route.ts:11:26)
   9 |   { params }: { params: { path: string[] } }
  10 | ) {
> 11 |   const apiPath = params.path ? `/${params.path.join('/')}` : '';
     |                          ^
  12 |   const url = new URL(request.url);
  13 |   const searchParams = url.search;
  14 |"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fix Authentication Proxy Error (Priority: P1)

As a user, I want the authentication proxy to work correctly so that I can securely access protected API endpoints without encountering errors. The current issue prevents the Next.js App Router from properly handling dynamic parameters in catch-all routes.

**Why this priority**: This is a critical bug that prevents the entire authentication system from functioning properly, blocking all API requests that go through the proxy.

**Independent Test**: Can be fully tested by making API requests through the proxy route and verifying that the error no longer occurs and requests are properly forwarded to the backend.

**Acceptance Scenarios**:

1. **Given** an authenticated user making API requests through the proxy, **When** they access `/api/auth/proxy/todos`, **Then** the request is properly forwarded to the backend without the Promise error.

2. **Given** an unauthenticated user attempting to access protected endpoints, **When** they make a request through the proxy, **Then** they receive proper authentication error responses.

---

### User Story 2 - Create Modern Landing Page with Welcome Message (Priority: P2)

As a visitor to the todo app, I want to see an attractive landing page with a welcome message that showcases the app's features, so I can understand the value proposition and be encouraged to sign up.

**Why this priority**: This is essential for user acquisition and first impressions, creating a professional entry point for new users.

**Independent Test**: Can be fully tested by visiting the home page and verifying that the welcome message and branding elements are displayed properly.

**Acceptance Scenarios**:

1. **Given** a visitor accessing the home page, **When** they load the page, **Then** they see a professional welcome message and call-to-action buttons.

2. **Given** a logged-in user accessing the home page, **When** they load the page, **Then** they see appropriate navigation options and can access the dashboard.

---

### User Story 3 - Display Sample Task Table on Landing Page (Priority: P3)

As a potential user, I want to see a sample task table on the landing page that demonstrates the app's core functionality, so I can understand how the todo management features work before signing up.

**Why this priority**: This provides concrete visual evidence of the app's capabilities and helps users understand the value before committing to registration.

**Independent Test**: Can be fully tested by viewing the sample task table and verifying that it displays tasks with appropriate columns and filtering capabilities.

**Acceptance Scenarios**:

1. **Given** a visitor on the landing page, **When** they view the sample task table, **Then** they see realistic sample tasks with titles, priorities, tags, and status indicators.

2. **Given** a visitor using the search functionality on the sample table, **When** they enter search terms, **Then** the table updates to show only matching tasks.

---

### User Story 4 - Implement Task Filtering and Search on Landing Page (Priority: P4)

As a visitor, I want to be able to filter and search the sample tasks on the landing page, so I can see how the filtering functionality works in the actual application.

**Why this priority**: This demonstrates the interactive capabilities of the todo management system and shows how users can organize their tasks.

**Independent Test**: Can be fully tested by using the search and filter controls on the sample task table and verifying that the results update correctly.

**Acceptance Scenarios**:

1. **Given** sample tasks displayed in the table, **When** a visitor enters search terms, **Then** the table updates to show only matching tasks.

---

### Edge Cases

- What happens when the proxy route receives malformed parameters?
- How does the system handle authentication token expiration during proxy requests?
- What happens when the sample task table has no data to display?
- How does the search functionality handle special characters or very long search terms?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST fix the Next.js App Router error where `params` is treated as a Promise in catch-all routes
- **FR-002**: System MUST properly handle dynamic parameters in `/api/auth/proxy/[...path]` routes
- **FR-003**: System MUST forward authenticated API requests from the proxy to the backend service
- **FR-004**: System MUST display a professional landing page with welcome message when users visit the home page
- **FR-005**: System MUST show sample todo tasks in a table format on the landing page
- **FR-006**: System MUST provide search and filter functionality for the sample task table
- **FR-007**: System MUST display appropriate navigation options based on user authentication status
- **FR-008**: System MUST include call-to-action buttons for registration and login on the landing page
- **FR-009**: System MUST show task details including title, description, priority, tags, and completion status
- **FR-010**: System MUST handle unauthenticated users by showing registration options

### Key Entities *(include if feature involves data)*

- **Todo**: Represents a task with title, description, priority, tags, completion status, and timestamps
- **User**: Represents an authenticated user with name, email, and authentication tokens

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authentication proxy error is resolved and API requests are successfully forwarded without Promise resolution errors
- **SC-002**: Landing page loads within 3 seconds and displays professional welcome message to visitors
- **SC-003**: Sample task table shows at least 5 realistic sample tasks with proper formatting and styling
- **SC-004**: Search functionality filters sample tasks in under 1 second for queries up to 50 characters
- **SC-005**: 100% of users can successfully navigate from landing page to registration or login
- **SC-006**: Landing page achieves at least 90% mobile responsiveness across different screen sizes