# Feature Specification: OpenAI ChatKit Frontend for Phase 3 Todo AI Chatbot

**Feature Branch**: `001-chatkit-frontend`
**Created**: 2026-01-22
**Status**: Draft
**Input**: User description: "Phase 3 backend chat endpoint is fully working (/api/{user_id}/chat). Now create the OpenAI ChatKit frontend for Phase 3. Requirements: 1. Folder structure: phase3-chatbot/ └── frontend-chatkit/ ├── app/ │ └── chat/ │ └── page.tsx ├── components/ │ └── ChatInterface.tsx ├── .env.local └── next.config.js 2. Use OpenAI ChatKit (hosted component) - Import and use <ChatKit /> from @openai/chatkit - Point it to the backend endpoint: POST {baseUrl}/api/{user_id}/chat - Handle user_id dynamically (from Better Auth session or URL param) 3. Authentication flow: - Reuse Better Auth session from Phase 2 - Get JWT token from session (use useSession() or similar) - Attach Authorization: Bearer {token} to every request - If no session → redirect to login or show "Please log in" 4. Environment variables (in .env.local): - NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL=http://localhost:8000 - NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-from-openai 5. Domain allowlist note: - Document how to add the frontend URL to OpenAI allowlist - https://platform.openai.com/settings/organization/security/domain-allowlist 6. Features: - Simple full-screen chat interface - Show loading state while waiting for response - Display user_id (for debugging) - Auto-scroll to bottom - Handle errors gracefully (show toast/message) 7. Update README-phase3.md: - Add section: "Running the ChatKit Frontend" - List required env vars - Instructions to run: cd frontend-chatkit && npm run dev - How to get domain key and add domain - Example: open http://localhost:3000/chat 8. Make it production-ready: - Use app router (Next.js 13+) - No unnecessary dependencies - Clean, responsive design"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chat with AI Todo Assistant (Priority: P1)

As a logged-in user of the Todo AI Chatbot, I want to interact with an AI assistant through a chat interface so that I can manage my tasks using natural language.

**Why this priority**: This is the core functionality of the Phase 3 Todo AI Chatbot, enabling users to manage their todos through conversational AI.

**Independent Test**: Can be fully tested by starting a chat session and sending messages to the AI assistant to verify it responds appropriately and manages tasks.

**Acceptance Scenarios**:

1. **Given** I am a logged-in user with a valid session, **When** I navigate to the chat interface, **Then** I see a functional chat interface with my user identity displayed
2. **Given** I am on the chat interface, **When** I send a message to the AI assistant, **Then** the message is sent to the backend and I receive a relevant response
3. **Given** I am interacting with the AI assistant, **When** I request to add a task, **Then** the AI processes my request and adds the task to my todo list

---

### User Story 2 - Secure Authentication Flow (Priority: P2)

As a security-conscious user, I want the chat interface to properly authenticate me using my existing Better Auth session so that my data remains protected.

**Why this priority**: Ensures that only authenticated users can access the AI chatbot and their personal todo data, maintaining security standards established in Phase 2.

**Independent Test**: Can be tested by attempting to access the chat interface without authentication and verifying that unauthorized access is prevented.

**Acceptance Scenarios**:

1. **Given** I am not logged in, **When** I try to access the chat interface, **Then** I am redirected to the login page or prompted to log in
2. **Given** I am logged in with a valid Better Auth session, **When** I access the chat interface, **Then** my authentication token is properly attached to backend requests
3. **Given** my session expires during a chat session, **When** I send a message, **Then** I am notified of the authentication issue and prompted to re-authenticate

---

### User Story 3 - Responsive Chat Experience (Priority: P3)

As a user accessing the chat from different devices, I want a responsive and user-friendly chat interface that provides feedback during interactions so that I have a smooth experience.

**Why this priority**: Enhances user experience by providing visual feedback and ensuring the interface works well across different device sizes and connection speeds.

**Independent Test**: Can be tested by accessing the chat interface on different screen sizes and observing the loading states and error handling.

**Acceptance Scenarios**:

1. **Given** I am using the chat interface, **When** I send a message while waiting for a response, **Then** I see a clear loading state indicating the AI is processing
2. **Given** I am viewing the chat interface, **When** new messages arrive, **Then** the chat automatically scrolls to show the latest content
3. **Given** I am using the chat interface on a mobile device, **When** I interact with the chat, **Then** the interface adapts to the smaller screen size appropriately

---

### Edge Cases

- What happens when the OpenAI ChatKit component fails to load?
- How does the system handle network timeouts during AI processing?
- What occurs when the backend API is temporarily unavailable?
- How does the system behave if the user's authentication token becomes invalid mid-session?
- What happens when the OpenAI domain allowlist doesn't include the current domain?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a chat interface using OpenAI ChatKit component from @openai/chatkit
- **FR-002**: System MUST authenticate users using Better Auth session from Phase 2
- **FR-003**: System MUST attach JWT token to all backend API requests as Authorization: Bearer {token}
- **FR-004**: System MUST send chat messages to POST {baseUrl}/api/{user_id}/chat endpoint
- **FR-005**: System MUST dynamically determine user_id from authenticated session or URL parameter
- **FR-006**: System MUST display a loading state while waiting for AI responses
- **FR-007**: System MUST automatically scroll to the bottom when new messages arrive
- **FR-008**: System MUST gracefully handle authentication failures and redirect to login
- **FR-009**: System MUST display user_id for debugging purposes
- **FR-010**: System MUST handle API errors gracefully with appropriate user feedback
- **FR-011**: System MUST be responsive and work on different screen sizes
- **FR-012**: System MUST be built with Next.js 13+ App Router
- **FR-013**: System MUST include proper environment variable configuration for backend endpoint and OpenAI domain key

### Key Entities

- **ChatInterface**: The main chat component that wraps or implements the OpenAI ChatKit functionality
- **Authentication Session**: The Better Auth session that provides user identity and JWT token
- **Backend Endpoint Configuration**: The configuration that determines where chat messages are sent
- **User Identity**: The authenticated user's ID that is used in API requests

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully send messages to the AI assistant and receive responses through the ChatKit interface
- **SC-002**: Authentication is properly enforced with Better Auth session integration
- **SC-003**: The chat interface is responsive and provides loading states during AI processing
- **SC-004**: The frontend can be built and deployed with proper environment configuration
- **SC-005**: Documentation is updated with clear instructions for running the ChatKit frontend