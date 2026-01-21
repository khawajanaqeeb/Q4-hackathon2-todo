---
id: 002
title: fix-pydantic-env-validation-spec
stage: spec
date_iso: 2026-01-22
surface: agent
model: claude-sonnet-4-5-20250929
feature: fix-pydantic-env-validation
branch: 002-fix-pydantic-env-validation
user: claude
command: /sp.specify
labels: ["spec", "pydantic", "validation", "phase3", "env"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - specs/002-fix-pydantic-env-validation/spec.md
  - specs/002-fix-pydantic-env-validation/checklists/requirements.md
tests_yaml: |
  -
outcome: Specification created successfully for fixing Pydantic validation error in Phase 3 backend
evaluation: null
---

# Prompt Text

```
/sp.specify fix-pydantic-extra-forbidden-phase3-env-pollution

We are getting this validation error when starting the Phase 3 backend:

pydantic_core._pydantic_core.ValidationError: 7 validation errors for Settings
OPENAI_API_KEY      Extra inputs are not permitted [type=extra_forbidden]
BETTER_AUTH_SECRET  Extra inputs are not permitted
JWT_SECRET_KEY      Extra inputs are not permitted
... (and PHASE2_BACKEND_PATH, JWT_ALGORITHM, etc.)

Root cause:
- Phase 3 backend imports code from Phase 2 (app.database → app.config → Settings)
- Phase 3 .env contains new keys (OPENAI_API_KEY, PHASE2_BACKEND_PATH, etc.) that Phase 2 Settings model does not know
- Settings uses strict mode (extra = "forbid") → fails on unknown env vars

Goal: Allow Phase 3 to run without changing Phase 2 code or deleting env vars.

Requirements for fix:
1. Keep .env as-is (do NOT remove OPENAI_API_KEY etc.)
2. Do NOT relax Phase 2 Settings to extra = "ignore" (preserves Phase 2 purity)
3. Preferred solutions (ranked):
   a. Create a separate Settings class for Phase 3 (phase3-chatbot/backend/config.py) that includes all needed fields + inherits or copies from Phase 2
   b. Use a different .env file for Phase 3 (e.g. .env.phase3) and load it explicitly
   c. Set os.environ only for known keys before importing Phase 2 code
   d. Patch sys.modules or monkey-patch Settings (last resort)
4. Update run command / entry point (main_phase3.py) to use Phase 3 config
5. Update README-phase3.md with correct .env usage
6. Commit all fixes to main branch of https://github.com/khawajanaqeeb/Q4-hackathon2-todo
   - Use clear commit messages
   - Push only after verification

Generate specification with:
- Problem description + root cause
- Impact (why Phase 3 fails to start)
- Proposed solutions with pros/cons
- Chosen solution + detailed steps
- Files to create/update
- Test acceptance criteria: server starts without ValidationError
- Git commit & push instructions

After spec is ready, we will proceed to plan and implementation.

Execute now.
```

# Response Text

Created specification document for fixing the Pydantic validation error in the Phase 3 backend. The specification includes:

- User stories covering the key scenarios (developer running backend, maintaining Phase 2 integrity, proper environment management)
- Functional requirements detailing what the system must do to resolve the issue
- Success criteria with measurable outcomes
- Edge cases to consider during implementation
- Key entities involved in the solution

Also created a quality checklist to validate the specification. The solution addresses the core issue where Phase 3 backend fails to start due to Pydantic validation errors when importing Phase 2 code that has strict environment variable validation. The spec ensures Phase 2 code remains unchanged while allowing Phase 3 to properly handle its extended environment variable requirements.