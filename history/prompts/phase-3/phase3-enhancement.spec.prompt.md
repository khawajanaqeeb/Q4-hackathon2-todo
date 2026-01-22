---
id: 1
title: "Phase 3 Copy and Enhancement Spec"
stage: spec
date_iso: "2026-01-22"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "phase-3-enhancement"
branch: "phase-3-enhancement"
user: "NAQEEB"
command: "/sp.specify phase3-copy-then-enhance-from-phase2"
labels: ["specification", "phase3", "enhancement", "ai-chatbot"]
link_spec: "specs/phase-3/spec.md"
link_ticket: null
link_adr: null
link_pr: null
files_yaml:
  - "specs/phase-3/spec.md"
tests_yaml: []
---

# Phase 3 Copy and Enhancement Spec

## Prompt Text

```
/sp.specify phase3-copy-then-enhance-from-phase2

Important rule: DO NOT modify, delete or touch ANY file in phase2-fullstack/ — keep it 100% untouched as the original Phase 2.

New approach for Phase 3:
1. Copy the entire Phase 2 backend and frontend into phase3-chatbot/
2. Then enhance only the copied files/folders to add all Phase 3 requirements

Exact copy plan:

A. Copy backend:
   From: phase2-fullstack/backend/
   To:   phase3-chatbot/backend/

B. Copy frontend:
   From: phase2-fullstack/frontend/   (or wherever the Next.js code is)
   To:   phase3-chatbot/frontend/

After copying:
- All original Phase 2 code is now duplicated in phase3-chatbot/
- We will only modify files inside phase3-chatbot/ going forward

Phase 3 enhancements (apply only to the copied code in phase3-chatbot/):

Backend enhancements:
1. Add OPENAI_API_KEY field to config.py Settings class (or subclass it)
2. Add agents/ folder (copy from previous phase3-chatbot/backend/agents/)
3. Add mcp/ folder (copy from previous phase3-chatbot/backend/mcp/)
4. Add chat_router.py to routers/ (copy or create from previous phase3-chatbot/backend/routers/chat_router.py)
5. Update main.py (or create main_phase3.py) to include chat_router
6. Fix any pydantic extra fields issues by adjusting Settings or loading env selectively
7. Keep running on port 8000 (no conflict anymore)

Frontend enhancements:
1. Add /chat page (app/chat/page.tsx or similar) with OpenAI ChatKit component
2. Reuse existing Better Auth session/login for JWT
3. Add .env.local with:
   NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL=http://localhost:8000
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=...
4. Make sure ChatKit sends requests to /api/{user_id}/chat with Bearer token

Other requirements:
- Update README-phase3.md with new structure and run instructions
- Add gitignore entries if needed (do not commit node_modules, .env, etc.)
- Acceptance criteria:
  - phase2-fullstack/ remains completely unchanged
  - phase3-chatbot/backend starts on 8000 without errors
  - phase3-chatbot/frontend runs on 3000
```

## Response Text

Created a comprehensive specification for the Phase 3 copy and enhancement feature. The specification includes:

- User scenarios and testing requirements with priorities (P1-P3)
- Functional requirements (FR-001 through FR-013) covering the copy operation, MCP tools, authentication, and UI requirements
- Key entities (Conversation, Message, Task, User)
- Success criteria with measurable outcomes (SC-001 through SC-007)
- Edge cases for error handling and security considerations

The specification ensures that Phase 2 remains untouched while creating a new Phase 3 structure with enhanced chatbot capabilities using OpenAI Agents SDK and MCP tools.

## Outcome

Successfully created feature specification document at specs/1-phase3-copy-enhance/spec.md with accompanying quality checklist at specs/1-phase3-copy-enhance/checklists/requirements.md. The specification is ready for the planning phase.