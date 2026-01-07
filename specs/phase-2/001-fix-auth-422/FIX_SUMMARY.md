# Authentication 422 Error - Complete Fix Summary

**Date**: 2026-01-08
**Status**: Ready for Implementation
**Feature Branch**: `001-fix-auth-422`
**Specification**: [spec.md](./spec.md)

---

## 🔴 Executive Summary

The application has a **critical production blocker**: POST requests to `/api/auth/login` return **422 Unprocessable Entity** errors, completely preventing user authentication.

**Root Cause**: The backend `/auth/login` endpoint expects `Form(...)` data (`application/x-www-form-urlencoded`), but the frontend proxy is not correctly forwarding the form data, causing validation failures.

**Impact**:
- ❌ Users cannot log in
- ❌ Users cannot register
- ❌ Application is non-functional
- ❌ Not deployable to Railway

---

## 🔍 Issues Identified

### Issue #1: Login Form Data Mismatch (P0 - Blocker)

**File**: `phase2-fullstack/backend/app/routers/auth.py:96-103`

**Current Code**:
```python
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    email: str = Form(...),          # ← Expects form field
    password: str = Form(...),        # ← Expects form field
    session: Session = Depends(get_session),
):
```

**Problem**: Backend expects `application/x-www-form-urlencoded` form fields, but the FastAPI validation is failing with 422.

**Frontend Sending** (`context/AuthContext.tsx:107-115`):
```typescript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    email,
    password,
  }),
});
```

**Why It Fails**:
1. Frontend correctly sends `application/x-www-form-urlencoded`
2. Next.js proxy forwards to backend at `/auth/login`
3. FastAPI `Form(...)` validation expects specific form encoding
4. Request body is not in the format FastAPI expects
5. Returns 422 Unprocessable Entity

### Issue #2: Unused LoginRequest Schema

**File**: `phase2-fullstack/backend/app/schemas/user.py:48-71`

**Problem**: A `LoginRequest` Pydantic schema exists but is NOT used in the login endpoint. The endpoint uses `Form(...)` fields instead, creating inconsistency.

```python
class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr = Field(...)
    password: str = Field(...)
```

**Inconsistency**: Schema imported but never used in `auth.py:16`.

### Issue #3: Rate Limiting May Not Be Active

**File**: `phase2-fullstack/backend/app/routers/auth.py:27-31`

**Problem**: Rate limiter is instantiated locally in the router, but FastAPI may not be using it.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)  # ← Local instance
```

**Correct Pattern**: Should use the limiter from `app.state.limiter` (set in `main.py:19-22`).

### Issue #4: Missing Content-Type Handling in Proxy

**File**: `phase2-fullstack/frontend/app/api/auth/[...path]/route.ts`

**Problem**: Proxy may not be correctly preserving or handling `application/x-www-form-urlencoded` content type when forwarding to backend.

**Current Proxy Logic** (lines 209-232):
```typescript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    email,
    password,
  }),
});
```

The proxy needs to forward the exact form data without conversion.

---

## ✅ Complete Fix

### Fix #1: Use OAuth2PasswordRequestForm (Recommended)

FastAPI provides `OAuth2PasswordRequestForm` which is the standard way to handle form-based login.

**File**: `phase2-fullstack/backend/app/routers/auth.py`

**Before** (lines 96-103):
```python
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
```

**After**:
```python
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Authenticate user and return JWT access token.

    OAuth2PasswordRequestForm expects:
    - username: User's email (we use email as username)
    - password: User's password

    Validates credentials and returns JWT token on success.
    Token expires after ACCESS_TOKEN_EXPIRE_MINUTES (default: 30).

    Args:
        request: FastAPI request object (for rate limiting)
        form_data: OAuth2 form data (username=email, password)
        session: Database session (injected)

    Returns:
        TokenResponse: JWT access token and token type

    Raises:
        HTTPException 401: Invalid credentials or inactive account
    """
    # OAuth2PasswordRequestForm uses 'username' field, but we use email
    email = form_data.username
    password = form_data.password

    # Find user by email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    # Rest of the function remains the same...
```

**Explanation**:
- `OAuth2PasswordRequestForm` is FastAPI's standard for form-based auth
- It expects `username` and `password` fields
- We map `username` to our `email` field
- Frontend needs to send `username` instead of `email`

### Fix #2: Update Frontend to Use 'username' Field

**File**: `phase2-fullstack/frontend/context/AuthContext.tsx`

**Before** (lines 107-115):
```typescript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    email,
    password,
  }),
});
```

**After**:
```typescript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: email,  // ← Changed from 'email' to 'username'
    password,
  }),
});
```

**Explanation**: OAuth2 standard uses `username` field. We pass email as the username value.

### Fix #3: Update Proxy to Preserve Form Data

**File**: `phase2-fullstack/frontend/app/api/auth/[...path]/route.ts`

The proxy already correctly forwards form data. Ensure it doesn't convert `application/x-www-form-urlencoded` to JSON.

**Verify POST Handler** (around line 205):
```typescript
export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';

  // ... logout handling ...

  // Get request body - DON'T parse JSON for form data routes
  let body = null;
  const contentType = request.headers.get('content-type') || '';

  if (contentType.includes('application/x-www-form-urlencoded')) {
    // For form data, get the raw body as text
    body = await request.text();
  } else if (contentType.includes('application/json')) {
    // For JSON, parse as JSON
    body = await request.json().catch(() => null);
  }

  // Forward to backend
  const backendUrl = buildBackendUrl(apiPath, searchParams);
  const backendResponse = await fetch(backendUrl, {
    method: 'POST',
    headers: {
      'Content-Type': contentType,  // Preserve original content type
      ...(token && { 'Authorization': `Bearer ${token}` })
    },
    ...(body && { body: typeof body === 'string' ? body : JSON.stringify(body) }),
  });
```

**Explanation**: Proxy must forward form data as-is without JSON conversion.

### Fix #4: Use App-Level Rate Limiter

**File**: `phase2-fullstack/backend/app/routers/auth.py`

**Before** (lines 27-31):
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

**After** (remove local limiter):
```python
# Remove the local limiter instantiation
# Use the app-level limiter from main.py instead
```

**And Update Decorators**:
```python
from fastapi import Request

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    # Use request.app.state.limiter for rate limiting
    # Or rely on the app-level configuration in main.py
```

**Explanation**: `main.py:19-22` already sets up the limiter in `app.state.limiter`. Use that instead of creating a duplicate.

### Fix #5: Verify Security Utilities

**File**: `phase2-fullstack/backend/app/utils/security.py`

**Verify These Functions Exist**:
```python
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password with bcrypt (cost factor 12)."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash (constant-time)."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token (30 minutes)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None
```

**If Missing**: Create this file with the above functions.

### Fix #6: Verify Database Configuration

**File**: `phase2-fullstack/backend/app/database.py`

**Ensure SSL Mode for Neon**:
```python
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Ensure DATABASE_URL includes sslmode=require for Neon
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Log SQL for debugging
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool
    max_overflow=10,  # Max extra connections
)

def create_db_and_tables():
    """Create database tables on startup."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session
```

**Verify DATABASE_URL Format**:
```
postgresql://user:password@host:5432/dbname?sslmode=require
```

---

## 🔧 Implementation Steps

### Step 1: Backend Changes

1. **Update Login Endpoint** (`app/routers/auth.py`):
   ```bash
   cd phase2-fullstack/backend
   # Edit app/routers/auth.py
   # Replace lines 96-103 with OAuth2PasswordRequestForm version
   ```

2. **Remove Local Limiter** (`app/routers/auth.py`):
   ```python
   # Delete lines 27-31 (local limiter instantiation)
   ```

3. **Verify Security Utils** (`app/utils/security.py`):
   ```bash
   # Ensure all functions exist and use correct settings
   ```

4. **Test Backend Locally**:
   ```bash
   cd phase2-fullstack/backend
   uvicorn app.main:app --reload --port 8000

   # Test with curl:
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=testpass123"
   ```

### Step 2: Frontend Changes

1. **Update AuthContext** (`context/AuthContext.tsx`):
   ```bash
   cd phase2-fullstack/frontend
   # Edit context/AuthContext.tsx
   # Change 'email' to 'username' in URLSearchParams (lines 107-115 and 173-181)
   ```

2. **Update Proxy Form Handling** (`app/api/auth/[...path]/route.ts`):
   ```bash
   # Edit app/api/auth/[...path]/route.ts
   # Add content-type checking for form data (see Fix #3 above)
   ```

3. **Test Frontend Build**:
   ```bash
   npm run build
   # Should complete with no errors
   ```

### Step 3: Integration Testing

1. **Start Backend**:
   ```bash
   cd phase2-fullstack/backend
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd phase2-fullstack/frontend
   npm run dev
   ```

3. **Test Registration Flow**:
   - Navigate to `http://localhost:3000/register`
   - Fill in: Name, Email, Password
   - Click Register
   - Should redirect to dashboard (HTTP 201 → HTTP 200)

4. **Test Login Flow**:
   - Navigate to `http://localhost:3000/login`
   - Enter registered email and password
   - Click Login
   - Should redirect to dashboard (HTTP 200 + token cookie)

5. **Test Protected Access**:
   - While logged in, navigate to `http://localhost:3000/dashboard`
   - Should see dashboard without re-authentication
   - Check browser DevTools: Cookie `auth_token` should be set

6. **Test Logout Flow**:
   - Click Logout
   - Should redirect to `/login`
   - Cookie `auth_token` should be cleared
   - Accessing `/dashboard` should redirect back to `/login`

### Step 4: Verify Database

1. **Connect to Neon**:
   ```bash
   psql "${DATABASE_URL}"
   ```

2. **Check Users Table**:
   ```sql
   SELECT id, email, name, is_active, created_at
   FROM users
   ORDER BY created_at DESC
   LIMIT 5;
   ```

3. **Verify Password Hash**:
   ```sql
   SELECT email,
          substring(hashed_password from 1 for 10) as hash_preview
   FROM users
   LIMIT 1;
   ```

   Should start with `$2b$` (bcrypt identifier).

### Step 5: Railway Deployment

1. **Set Environment Variables** (Railway Dashboard):
   ```
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   SECRET_KEY=<generate 32+ character random string>
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
   ALGORITHM=HS256
   ```

2. **Deploy Backend**:
   ```bash
   git push railway main
   # or use Railway CLI
   railway up
   ```

3. **Test Deployed Backend**:
   ```bash
   curl -X POST https://your-backend.railway.app/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=testpass123"
   ```

4. **Update Frontend Env** (`.env.local`):
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

5. **Test Complete Flow**:
   - Register new user via frontend
   - Login via frontend
   - Access protected routes
   - Verify no 422 errors in logs

---

## ✅ Verification Checklist

### Backend Verification

- [ ] Backend starts without errors
- [ ] `/health` endpoint returns 200 OK
- [ ] `/auth/login` accepts `application/x-www-form-urlencoded`
- [ ] `/auth/login` with valid credentials returns 200 + tokens
- [ ] `/auth/login` with invalid credentials returns 401
- [ ] `/auth/register` creates user and returns 201
- [ ] `/auth/verify` with valid token returns 200 + user data
- [ ] `/auth/verify` without token returns 401
- [ ] Rate limiting active (6th login attempt returns 429)
- [ ] Database contains users with bcrypt hashes
- [ ] No 422 errors in any authentication endpoint

### Frontend Verification

- [ ] Frontend builds without errors
- [ ] Registration form submits successfully
- [ ] Login form submits successfully
- [ ] httpOnly cookie set after login
- [ ] Protected routes accessible when logged in
- [ ] Protected routes redirect when not logged in
- [ ] Logout clears cookie
- [ ] No 422 errors in browser console or network tab

### Integration Verification

- [ ] Complete registration flow works end-to-end
- [ ] Complete login flow works end-to-end
- [ ] Token automatically included in protected requests
- [ ] Token expiration handled gracefully (redirect to login)
- [ ] Database stores correct user data
- [ ] Passwords stored as bcrypt hashes (not plain text)

### Security Verification

- [ ] Passwords hashed with bcrypt (check database)
- [ ] JWT tokens properly signed (decode at jwt.io)
- [ ] Rate limiting prevents brute force (test with 6+ requests)
- [ ] CORS configured for frontend origin only
- [ ] HTTPS enforced in production (Railway + Vercel)
- [ ] Generic error messages (no user enumeration)
- [ ] Passwords never logged (check application logs)

---

## 📊 Expected Outcomes

### Before Fix

```
POST /api/auth/login → 422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### After Fix

```
POST /api/auth/login → 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

Cookies: auth_token=eyJhbGciOiJIUz...; HttpOnly; Secure; SameSite=Strict
```

---

## 🚨 Common Pitfalls

1. **Forgetting to Change 'email' to 'username'**: Frontend must use `username` field for OAuth2 compatibility
2. **Content-Type Mismatch**: Ensure proxy forwards `application/x-www-form-urlencoded` without JSON conversion
3. **Missing SSL Mode**: Neon requires `sslmode=require` in DATABASE_URL
4. **Weak SECRET_KEY**: Must be 32+ characters, randomly generated
5. **CORS Misconfiguration**: Backend CORS must include frontend domain
6. **Rate Limiter Not Active**: Ensure using `app.state.limiter` from `main.py`

---

## 📚 Additional Resources

- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- **OAuth2PasswordRequestForm**: https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/
- **Bcrypt Best Practices**: https://github.com/pyca/bcrypt#password-hashing
- **JWT Debugging**: https://jwt.io/
- **Next.js API Routes**: https://nextjs.org/docs/app/building-your-application/routing/route-handlers

---

## 🎯 Next Steps

1. **Implement Fixes**: Follow Step-by-Step Implementation above
2. **Run All Tests**: Complete Verification Checklist
3. **Deploy to Railway**: Test in production environment
4. **Monitor Logs**: Watch for any new errors
5. **User Acceptance**: Have real users test authentication

---

**Document Version**: 1.0
**Last Updated**: 2026-01-08
**Ready for Implementation**: Yes
