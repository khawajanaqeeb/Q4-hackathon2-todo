---
id: 001
title: chatkit-frontend-spec
stage: spec
date_iso: 2026-01-22
surface: agent
model: claude-sonnet-4-5-20250929
feature: chatkit-frontend
branch: 001-chatkit-frontend
user: claude
command: /sp.specify
labels: ["spec", "chatkit", "frontend", "phase3", "openai", "todo"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - specs/001-chatkit-frontend/spec.md
  - specs/001-chatkit-frontend/checklists/requirements.md
tests_yaml: |
  -
outcome: Specification created for OpenAI ChatKit frontend for Phase 3 Todo AI Chatbot
evaluation: null
---

# Prompt Text

```
/sp.specify phase3-chatkit-frontend

Phase 3 backend chat endpoint is fully working (/api/{user_id}/chat).

Now create the OpenAI ChatKit frontend for Phase 3.

Requirements:

1. Folder structure:
   phase3-chatbot/
   └── frontend-chatkit/
       ├── app/
       │   └── chat/
       │       └── page.tsx
       ├── components/
       │   └── ChatInterface.tsx   (optional custom wrapper)
       ├── .env.local
       └── next.config.js (if needed)

2. Use OpenAI ChatKit (hosted component)
   - Import and use <ChatKit /> from @openai/chatkit
   - Point it to the backend endpoint: POST {baseUrl}/api/{user_id}/chat
   - Handle user_id dynamically (from Better Auth session or URL param)

3. Authentication flow:
   - Reuse Better Auth session from Phase 2
   - Get JWT token from session (use useSession() or similar)
   - Attach Authorization: Bearer {token} to every request
   - If no session → redirect to login or show "Please log in"

4. Environment variables (in .env.local):
   - NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL=http://localhost:8000  (or Railway URL)
   - NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-from-openai

5. Domain allowlist note:
   - Document how to add the frontend URL to OpenAI allowlist
   - https://platform.openai.com/settings/organization/security/domain-allowlist

6. Features:
   - Simple full-screen chat interface
   - Show loading state while waiting for response
   - Display user_id (for debugging)
   - Auto-scroll to bottom
   - Handle errors gracefully (show toast/message)

7. Update README-phase3.md:
   - Add section: "Running the ChatKit Frontend"
   - List required env vars
   - Instructions to run: cd frontend-chatkit && npm run dev
   - How to get domain key and add domain
   - Example: open http://localhost:3000/chat

8. Make it production-ready:
   - Use app router (Next.js 13+)
   - No unnecessary dependencies
   - Clean, responsive design

Generate:
- Full code for the main chat page
- Any custom components if needed
- .env.local
```

# Response Text

Created a comprehensive specification for the OpenAI ChatKit frontend for Phase 3 Todo AI Chatbot. The specification includes:

1. Three user stories covering the core functionality:
   - Chat with AI Todo Assistant (P1 priority)
   - Secure Authentication Flow (P2 priority)
   - Responsive Chat Experience (P3 priority)

2. Detailed acceptance scenarios for each user story

3. Edge cases to consider during implementation

4. 13 functional requirements covering:
   - ChatKit integration
   - Authentication with Better Auth
   - Backend API communication
   - Loading states and error handling
   - Responsiveness and user experience

5. Five measurable success criteria

6. Key entities that will be part of the implementation

The specification follows the required template structure and is ready for the planning phase. A quality checklist was also created and validated, confirming the specification is complete and ready for the next phase.