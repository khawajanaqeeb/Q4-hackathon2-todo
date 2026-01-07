# Quick Start: Testing API Proxy Error Handling

**Feature**: Fix API Proxy JSON Parsing Error
**Branch**: `003-fix-proxy-json-error`
**Last Updated**: 2026-01-04

## Overview

This guide explains how to test the API proxy error handling improvements locally and verify that all acceptance criteria are met.

## Prerequisites

- Node.js 18+ installed
- Backend service running (FastAPI) OR ability to simulate backend failures
- Frontend development server running (Next.js)
- Browser DevTools for console inspection

## Quick Test (2 minutes)

### Test 1: Normal Operation (Baseline)

**Purpose**: Verify nothing broke in the happy path

```bash
# 1. Start both backend and frontend
cd phase2-fullstack/backend
python -m uvicorn app.main:app --reload --port 8000

cd phase2-fullstack/frontend
npm run dev
```

**Actions**:
1. Open http://localhost:3000
2. Login with test credentials
3. Create a new todo item
4. View todo list

**Expected Result**: ✅ Everything works normally, no console errors

---

### Test 2: Backend Unavailable (Critical Bug Fix)

**Purpose**: Verify graceful error handling when backend returns non-JSON

```bash
# 1. Stop the backend service
# (Press Ctrl+C in backend terminal)

# 2. Frontend should still be running
```

**Actions**:
1. Try to create a new todo item
2. Try to fetch todo list
3. Open browser DevTools Console (F12)

**Expected Results**:
- ✅ Frontend displays: "Service temporarily unavailable. Please try again later."
- ✅ No unhandled promise rejection errors in console
- ✅ No "SyntaxError: Unexpected token" errors
- ✅ App remains functional (doesn't crash)

**Before Fix** (what used to happen):
- ❌ Console shows: `SyntaxError: Unexpected token 'I', "Internal S"... is not valid JSON`
- ❌ Unhandled promise rejection crashes the request
- ❌ User sees generic error or blank screen

---

### Test 3: Backend Returns HTML Error Page

**Purpose**: Verify proper handling of HTML error responses (common in production)

**Setup**: Modify backend to return HTML error (temporary test change):

```python
# In backend/app/api/endpoints/todos.py (temporary!)
@router.post("/")
async def create_todo(...):
    # Add this at the top of the function for testing
    return HTMLResponse("<html><body>Internal Server Error</body></html>", status_code=500)
```

**Actions**:
1. Try to create a todo item
2. Check browser console and network tab

**Expected Results**:
- ✅ Frontend receives JSON error: `{ error: "API service error" }`
- ✅ Server logs show: "Content-Type: text/html" and HTML preview
- ✅ HTTP status 500 preserved from backend
- ✅ No JSON parse crashes

**Cleanup**: Remove the test HTML response from backend code

---

## Comprehensive Testing Checklist

### Unit Tests (Automated)

Run the test suite:

```bash
cd phase2-fullstack/frontend
npm test -- tests/api/proxy-route.test.ts
```

**Expected Output**:
```
 PASS  tests/api/proxy-route.test.ts
  ✓ T-PROXY-001: Backend returns valid JSON → Parse success
  ✓ T-PROXY-002: Backend returns HTML error page → Standardized error
  ✓ T-PROXY-003: Backend returns plain text → Standardized error
  ✓ T-PROXY-004: Backend returns 200 OK with non-JSON → Error response
  ✓ T-PROXY-005: Content-Type JSON but malformed body → Graceful handling
  ✓ T-PROXY-006: Backend connection fails → 503 error
  ✓ T-PROXY-007: All HTTP methods handle errors consistently
  ✓ T-PROXY-008: Logs include headers and body preview
  ✓ T-PROXY-009: Response body truncated at 500 chars
  ✓ T-PROXY-010: Original status codes preserved

Test Suites: 1 passed, 1 total
Tests:       10 passed, 10 total
```

---

### Manual Integration Tests

#### Scenario 1: Backend Service Down

**Steps**:
1. Stop backend: `Ctrl+C` in backend terminal
2. Frontend: Try all CRUD operations (Create, Read, Update, Delete)
3. Observe error messages in UI
4. Check browser console for errors

**Pass Criteria**:
- [ ] All operations show "Service temporarily unavailable"
- [ ] No unhandled exceptions in console
- [ ] App remains responsive (can navigate, logout, etc.)

---

#### Scenario 2: Backend Timeout (Slow Response)

**Steps**:
1. Modify backend to add artificial delay:
   ```python
   import asyncio
   await asyncio.sleep(30)  # 30 second delay
   ```
2. Try to create a todo item
3. Wait for timeout (should be <30 seconds based on fetch timeout)

**Pass Criteria**:
- [ ] Request times out with appropriate error
- [ ] Error message is user-friendly
- [ ] Timeout doesn't crash the app

---

#### Scenario 3: Backend Returns Mixed Content Types

**Steps**:
1. Create todo (expect JSON) ✓
2. Trigger 404 error (expect HTML error page)
3. Trigger 500 error (expect HTML error page)
4. Check network tab in DevTools

**Pass Criteria**:
- [ ] Valid JSON responses pass through unchanged
- [ ] HTML error responses wrapped in `{ error: "..." }` format
- [ ] Status codes preserved (404 stays 404, 500 stays 500)
- [ ] All responses are valid JSON to frontend

---

#### Scenario 4: Logging Verification

**Steps**:
1. Stop backend
2. Trigger multiple error scenarios
3. Check terminal logs (frontend dev server output)

**Pass Criteria**:
- [ ] Logs contain "API proxy error: ..." messages
- [ ] Logs show Content-Type header
- [ ] Logs show HTTP status code
- [ ] Response body preview is truncated to ~500 chars
- [ ] Logs are readable and useful for debugging

---

## Success Criteria Validation

**From spec.md - verify each criterion:**

### SC-001: Zero Unhandled JSON Parsing Exceptions
**Test**: Run all manual scenarios above
**Validation**:
- [ ] No "Unexpected token" errors in console
- [ ] No unhandled promise rejections
- [ ] All errors caught and wrapped properly

### SC-002: 100% of Non-JSON Responses Return Valid JSON
**Test**: Scenarios 2 and 3 above
**Validation**:
- [ ] All API responses are valid JSON
- [ ] HTML/text responses wrapped in `{ error: "..." }`
- [ ] Network tab shows "Content-Type: application/json" from proxy

### SC-003: Error Responses Return Within 500ms
**Test**: Measure response times in Network tab
**Validation**:
- [ ] Error responses complete in <500ms
- [ ] No noticeable delay vs. normal requests
- [ ] Performance overhead is minimal

### SC-004: Error Logs Include Sufficient Debugging Info
**Test**: Review logs from Scenario 4
**Validation**:
- [ ] Logs contain all necessary context (status, headers, body)
- [ ] Can diagnose backend issues from logs alone
- [ ] No need to add additional logging

### SC-005: Users See Meaningful Error Messages
**Test**: All UI error scenarios
**Validation**:
- [ ] No stack traces shown to users
- [ ] Messages are clear: "Service temporarily unavailable"
- [ ] No technical jargon (JSON, parsing, etc.)

### SC-006: Graceful Backend Outage Handling
**Test**: Scenario 1 (backend service down)
**Validation**:
- [ ] App doesn't crash
- [ ] All operations show appropriate errors
- [ ] Users can recover without page refresh

---

## Troubleshooting

### Issue: Tests fail with "Cannot find module 'api-utils'"

**Solution**: Ensure `lib/api-utils.ts` exists and is properly exported:
```bash
ls -la phase2-fullstack/frontend/lib/api-utils.ts
```

### Issue: Frontend still shows old error behavior

**Solution**: Clear Next.js cache and rebuild:
```bash
rm -rf .next
npm run dev
```

### Issue: Backend logs not showing in test

**Solution**: Check backend is running with `--reload` flag:
```bash
uvicorn app.main:app --reload --port 8000
```

---

## Performance Benchmarking

Optional: Measure performance impact of error handling

```bash
# Use Apache Bench to test response times
ab -n 1000 -c 10 http://localhost:3000/api/auth/proxy/todos

# Compare before/after fix
# Target: <5ms overhead per request
```

---

## Next Steps After Validation

Once all tests pass:

1. Run full test suite: `npm test`
2. Check code coverage: `npm test -- --coverage`
3. Review PR checklist in tasks.md
4. Create commit with changes
5. Open pull request for review

---

## Emergency Rollback

If critical issues found after deployment:

```bash
# Revert the proxy route changes
git revert <commit-hash>

# Or restore from backup
git checkout main -- phase2-fullstack/frontend/app/api/auth/proxy/[...path]/route.ts
```

---

**Testing Status**: ⏳ Pending implementation
**Last Validated**: [To be filled after implementation]
**Validated By**: [Your name]
