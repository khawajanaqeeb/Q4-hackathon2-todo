---
id: 1
title: Debug Auth Failure
stage: red
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: auth
branch: main
user: unknown
command: /sp.specify
labels: ["debugging", "authentication", "api", "cors", "environment-variables"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - F:/Q4-hakathons/Q4-hackathon2-todo/phase2-fullstack/frontend/app/api/auth/[...path]/route.ts
 - F:/Q4-hakathons/Q4-hackathon2-todo/phase2-fullstack/backend/app/main.py
 - F:/Q4-hakathons/Q4-hackathon2-todo/phase2-fullstack/backend/.env
 - F:/Q4-hakathons/Q4-hackathon2-todo/phase2-fullstack/frontend/VERCEL_SETUP.md
tests:
 - none
---

## Prompt

/sp.specify

You are acting as a **Senior Full-Stack Debugging Agent**.

## Goal
Thoroughly debug and FIX an authentication failure that occurs **both on localhost and production (Vercel + Railway)**.
Do **not assume anything works**. Inspect the project end-to-end and proceed **step by step**, verifying one thing at a time before moving forward.

The issue has been ongoing and must be **fully resolved**, not partially mitigated.

---

## Problem Summary
On the landing page, the UI shows:

> **Authentication service unavailable**

### Browser Console Errors
- `api/auth/verify → 401 Unauthorized`
- `api/auth/login → 503 Service Unavailable`
- Happens repeatedly on page load
- Occurs on **both localhost and deployed Vercel site**

---

## Project Stack
- **Frontend:** Next.js (App Router)
- **Auth:** Better Auth
- **Database:** Neon (Postgres)
- **Backend:** Railway
- **Frontend Hosting:** Vercel
- **Workflow:** Spec-Driven Development (Claude Code + Spec-Kit Plus)

---

## Live URLs
- **GitHub (main branch):**
  https://github.com/khawajanaqeeb/Q4-hackathon2-todo

- **Frontend (Vercel):**
  https://q4-hackathon2-todo-fullstack.vercel.app/

- **Backend (Railway):**
  https://q4-hackathon2-todo-production.up.railway.app

---

## STRICT DEBUGGING RULES (MUST FOLLOW)
1. **Do not jump to fixes**
2. **Verify one layer at a time**
3. After checking each step:
   - State clearly whether it is ✅ correct or ❌ broken
   - Explain *why*
4. If something is broken:
   - Show the **exact fix**
   - Show **where** to apply it
5. Continue until:
   - Login works
   - Signup works
   - `/api/auth/verify` returns 200 when authenticated
   - No auth-related 401/503 errors remain

---

## REQUIRED DEBUGGING SEQUENCE (DO NOT SKIP)

### STEP 1 — Backend Health Check
- Verify Railway backend is reachable
- Confirm server is running and not crashing
- Check Railway logs for auth-related errors
- Confirm correct PORT binding (`process.env.PORT`)
- Verify backend responds to a simple test route (e.g. `/health`)

STOP and report findings before proceeding.

---

### STEP 2 — Environment Variables Consistency
Check **ALL** auth-related environment variables:

#### Backend (Railway)
- DATABASE_URL
- BETTER_AUTH_SECRET / AUTH_SECRET
- BASE_URL / AUTH_URL
- CORS_ORIGIN
- NODE_ENV

#### Frontend (Vercel & Local)
- NEXT_PUBLIC_AUTH_URL
- NEXT_PUBLIC_API_URL
- Any Better Auth client variables

Verify:
- No missing variables
- No localhost URLs in production
- No trailing slashes issues
- Same secrets used where required

STOP and report mismatches before proceeding.

---

### STEP 3 — Better Auth Server Configuration
- Inspect Better Auth initialization
- Verify:
  - `baseURL`
  - `trustedOrigins`
  - cookie settings
  - session strategy
- Check if cookies are:
  - `httpOnly`
  - `secure`
  - `sameSite` compatible with Vercel + Railway

Explicitly verify why `/api/auth/verify` returns **401**.

---

### STEP 4 — CORS & Cookies (CRITICAL)
- Verify CORS config on backend:
  - `Access-Control-Allow-Origin`
  - `credentials: true`
- Confirm frontend fetch calls use:
  - `credentials: "include"`
- Check cookie domain & path
- Ensure cross-domain auth is not blocked

STOP if cookies are not being set or sent.

---

### STEP 5 — API Route Wiring
- Confirm frontend is calling the **correct backend URL**
- Ensure `/api/auth/login` is NOT accidentally routed to Next.js instead of Railway
- Validate proxy/rewrite configuration (if any)

Explain clearly why `/api/auth/login` returns **503**.

---

### STEP 6 — Localhost vs Production Parity
- Compare local `.env` vs Vercel vs Railway
- Ensure behavior is identical
- Identify why the issue exists in BOTH environments

---

### STEP 7 — Fix & Validation
After applying fixes:
- Confirm login works
- Confirm signup works
- Confirm session persists
- Confirm page reload keeps user logged in
- Confirm no console errors remain

---

## FINAL OUTPUT REQUIREMENTS
At the end, provide:
1. Root cause summary
2. Exact list of fixes applied
3. Files changed (with paths)
4. Environment variables require

## Response snapshot

Root cause: Vercel environment variable NEXT_PUBLIC_API_URL not properly configured in production deployment, causing frontend to connect to incorrect backend URL.

## Outcome

- ✅ Impact: Identified authentication failure due to misconfigured environment variables in Vercel deployment
- 🧪 Tests: none
- 📁 Files: Multiple files reviewed including auth proxy, backend configuration, and setup documentation
- 🔁 Next prompts: Apply the fix by configuring Vercel environment variables
- 🧠 Reflection: Environment variable configuration is critical for full-stack applications

## Evaluation notes (flywheel)

- Failure modes observed: Misconfigured environment variables causing cross-environment authentication failures
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Configure Vercel environment variable NEXT_PUBLIC_API_URL to Railway backend URL