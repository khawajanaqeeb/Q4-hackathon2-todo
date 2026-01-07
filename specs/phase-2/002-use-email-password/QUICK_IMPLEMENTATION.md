# Quick Implementation Guide: Use Email and Password Fields

**Feature**: 002-use-email-password
**Complexity**: Low (3 simple changes)
**Time**: 10-15 minutes

---

## 🎯 Goal

Change login API from `username` field to `email` field for better developer experience.

**Before**: `username=user@example.com&password=secret`
**After**: `email=user@example.com&password=secret`

---

## 🔧 Changes Required (3 Files)

### 1. Backend: Use Form Fields Instead of OAuth2

**File**: `phase2-fullstack/backend/app/routers/auth.py`

**Find** (lines ~93-102):
```python
from fastapi import Request, Form
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
```

**Replace with**:
```python
from fastapi import Request, Form
# Remove OAuth2PasswordRequestForm import - not needed

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    email: str = Form(..., description="User's email address"),
    password: str = Form(..., description="User's password"),
    session: Session = Depends(get_session),
):
```

**Then find** (lines ~123-125):
```python
    # OAuth2PasswordRequestForm uses 'username' field, but we use email as username
    email = form_data.username
    password = form_data.password
```

**Replace with**:
```python
    # Email and password come directly from form fields
    # Normalize email to lowercase
    email = email.lower().strip()
```

**Also update docstring** (lines ~103-122):
```python
    """Authenticate user and return JWT access token.

    Accepts email and password as form fields.
    Validates credentials and returns JWT token on success.
    Token expires after ACCESS_TOKEN_EXPIRE_MINUTES (default: 30).

    Args:
        request: FastAPI request object (for rate limiting)
        email: User's email address (form field)
        password: User's password (form field)
        session: Database session (injected)

    Returns:
        TokenResponse: JWT access token and token type

    Raises:
        HTTPException 401: Invalid credentials or inactive account
    """
```

---

### 2. Frontend: Change username to email

**File**: `phase2-fullstack/frontend/context/AuthContext.tsx`

**Find** (lines ~107-117):
```typescript
      // OAuth2PasswordRequestForm expects 'username' field (we pass email as username)
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,  // OAuth2 standard uses 'username' field
          password,
        }),
      });
```

**Replace with**:
```typescript
      // Send email and password directly as form fields
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          email,     // Use email field directly
          password,
        }),
      });
```

**Find** (lines ~174-184):
```typescript
        // OAuth2PasswordRequestForm expects 'username' field (we pass email as username)
        const loginResponse = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username: email,  // OAuth2 standard uses 'username' field
            password,
          }),
        });
```

**Replace with**:
```typescript
        // Send email and password directly as form fields
        const loginResponse = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            email,     // Use email field directly
            password,
          }),
        });
```

---

### 3. Proxy: Verification Only (No Changes Needed)

**File**: `phase2-fullstack/frontend/app/api/auth/[...path]/route.ts`

✅ **Already correct** - proxy forwards form data as-is without modification.

Just verify that lines ~210-236 correctly:
- Read content-type
- For `application/x-www-form-urlencoded`, read as text
- Forward with correct content-type

---

## ✅ Testing

### 1. Backend Test
```bash
cd phase2-fullstack/backend
uvicorn app.main:app --reload

# In another terminal:
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&password=SecurePass123"

# Expected: 200 OK with tokens
```

### 2. Frontend Build Test
```bash
cd phase2-fullstack/frontend
npm run build

# Expected: ✓ Compiled successfully
```

### 3. Integration Test
1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to `http://localhost:3000/login`
4. Open DevTools → Network tab
5. Enter email and password, click Login
6. Check Network request shows `email=...` (not `username=...`)
7. Expected: Redirect to dashboard

### 4. Error Test
```bash
# Test with old 'username' field (should fail)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=SecurePass123"

# Expected: 422 Unprocessable Entity
# Error should say "email field required"
```

---

## 📋 Checklist

- [ ] Backend: Removed OAuth2PasswordRequestForm
- [ ] Backend: Added `email: str = Form(...)`
- [ ] Backend: Added `password: str = Form(...)`
- [ ] Backend: Removed `email = form_data.username` mapping
- [ ] Backend: Added `email = email.lower().strip()`
- [ ] Frontend: Changed `username: email` to `email` (login function)
- [ ] Frontend: Changed `username: email` to `email` (register auto-login)
- [ ] Backend starts without errors
- [ ] Frontend builds without errors
- [ ] Login with `email` field works
- [ ] Login with `username` field fails (422)
- [ ] Error messages reference `email` field

---

## 🚀 Deployment

```bash
# Commit changes
git add phase2-fullstack/backend/app/routers/auth.py \
        phase2-fullstack/frontend/context/AuthContext.tsx \
        specs/002-use-email-password/

git commit -m "feat: use email field directly in login (not username)

- Remove OAuth2PasswordRequestForm in favor of direct Form fields
- Frontend sends 'email' instead of 'username' for better clarity
- Improves developer experience and API clarity

Changes:
- Backend: email: str = Form(...) instead of OAuth2PasswordRequestForm
- Frontend: URLSearchParams uses 'email' field directly

🤖 Generated with Claude Code
https://claude.com/claude-code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Deploy (if using Railway)
git push railway 002-use-email-password:main
```

---

## 🎉 Benefits

After this change:

✅ **Clearer API**: `email` field instead of confusing `username`
✅ **Better DX**: Form fields match API fields
✅ **Self-Documenting**: Code explains itself
✅ **Simpler**: No OAuth2-specific concepts
✅ **Accurate Errors**: Validation messages reference `email` field

---

**Time to Implement**: 10-15 minutes
**Difficulty**: Easy (just field name changes)
**Risk**: Low (simple, well-defined change)
