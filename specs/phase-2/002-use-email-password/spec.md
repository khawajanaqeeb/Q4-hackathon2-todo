# Feature Specification: Use Email and Password Fields for Login

**Feature ID**: 002-use-email-password
**Created**: 2026-01-08
**Status**: Draft
**Priority**: P1 (User Experience Improvement)

---

## Executive Summary

The current authentication system uses OAuth2PasswordRequestForm which requires the `username` field, causing confusion for users and developers who expect to use `email` directly. This specification changes the login endpoint to accept `email` and `password` fields directly, making the API more intuitive and aligned with user expectations.

**Current State**: Login requires `username` field (email passed as username)
**Desired State**: Login accepts `email` field directly

This change improves developer experience, simplifies API contracts, and aligns with common authentication patterns where email is the primary login credential.

---

## Problem Statement

### Current Issues

1. **Confusing API Contract**:
   - Backend expects `username` field
   - Users actually provide their email address
   - Documentation must explain "use username field for email"
   - Creates cognitive dissonance

2. **Developer Experience**:
   - Frontend developers naturally want to send `email` field
   - OAuth2PasswordRequestForm is designed for username-based systems
   - Our application uses email-based authentication
   - Mismatch between form field names and user mental model

3. **API Clarity**:
   - API documentation shows `username` but means `email`
   - External API consumers must read documentation carefully
   - Potential for integration errors

### Impact

- **Users**: Minimal (internal change)
- **Developers**: Improved API clarity and natural field naming
- **Integration**: Clearer API contracts for external consumers
- **Documentation**: Simpler to explain and understand

---

## Success Criteria

The authentication system will meet user expectations when:

1. **API Clarity**
   - Login endpoint accepts `email` field directly
   - No need to explain "username means email"
   - API documentation accurately reflects field names

2. **Developer Experience**
   - Frontend code sends `email` field naturally
   - No mental translation required (email → username)
   - Field names match form labels

3. **Backward Compatibility**
   - Existing authentication flow continues to work
   - No breaking changes to token generation
   - Password verification unchanged

4. **Code Quality**
   - Backend validation clear and explicit
   - Pydantic schemas match actual field names
   - No confusion in codebase

---

## User Scenarios

### Scenario 1: Developer Integrating Login API

**Actor**: External Developer
**Goal**: Integrate login functionality into their application

**Current Flow**:
1. Developer reads API documentation
2. Sees login requires `username` and `password`
3. Developer confused - "Do I send username or email?"
4. Reads further documentation: "Use email as username"
5. Implements with `username=email_value`
6. Feels awkward about field naming

**Improved Flow**:
1. Developer reads API documentation
2. Sees login requires `email` and `password`
3. Developer immediately understands - matches their form fields
4. Implements with `email=email_value`
5. Natural and intuitive

**Success Criteria**:
- API documentation lists `email` and `password` fields
- No additional explanation needed
- Developer implements correctly on first try

### Scenario 2: Frontend Developer Building Login Form

**Actor**: Frontend Developer
**Goal**: Connect login form to backend API

**Current Flow**:
```typescript
// Form has email field, but must send as username
body: new URLSearchParams({
  username: email,  // ← Confusing mapping
  password,
})
```

**Improved Flow**:
```typescript
// Form fields match API fields directly
body: new URLSearchParams({
  email: email,  // ← Clear and natural
  password,
})
```

**Success Criteria**:
- Form field names match API field names
- No mental translation required
- Code is self-documenting

### Scenario 3: API Consumer Reading Error Messages

**Actor**: API Consumer
**Goal**: Debug login failures

**Current Flow**:
```json
{
  "detail": [
    {
      "loc": ["body", "username"],  // ← User sent "email" field
      "msg": "field required"
    }
  ]
}
```
User confused: "I sent email, why does it want username?"

**Improved Flow**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],  // ← Clear: email field is required
      "msg": "field required"
    }
  ]
}
```
User understands: "Oh, I forgot to include the email field"

**Success Criteria**:
- Error messages reference correct field names
- Validation errors are immediately understandable
- No need to cross-reference documentation

---

## Functional Requirements

### FR-001: Accept Email Field in Login Request

**Description**: Modify the login endpoint to accept `email` and `password` as form fields instead of `username` and `password`

**Current Behavior**:
- Backend: `form_data: OAuth2PasswordRequestForm = Depends()`
- Expected fields: `username` (contains email), `password`
- Frontend sends: `username=user@example.com&password=secret`

**Required Behavior**:
- Backend: `email: str = Form(...)`, `password: str = Form(...)`
- Expected fields: `email`, `password`
- Frontend sends: `email=user@example.com&password=secret`

**Acceptance Criteria**:
- [ ] Login endpoint accepts `email` field as form parameter
- [ ] Login endpoint accepts `password` field as form parameter
- [ ] Email validation ensures valid email format
- [ ] Password validation ensures non-empty password
- [ ] User lookup by email functions correctly
- [ ] Authentication flow completes successfully

**Technical Details**:
```python
# Backend endpoint signature
@router.post("/login", response_model=TokenResponse)
async def login(
    email: str = Form(..., description="User's email address"),
    password: str = Form(..., description="User's password"),
    session: Session = Depends(get_session),
):
    # Validate email format
    # Find user by email
    # Verify password
    # Return tokens
```

**Files Affected**:
- `phase2-fullstack/backend/app/routers/auth.py`

### FR-002: Update Frontend to Send Email Field

**Description**: Change frontend login requests to send `email` instead of `username`

**Current Behavior**:
```typescript
body: new URLSearchParams({
  username: email,  // mapping email to username
  password,
})
```

**Required Behavior**:
```typescript
body: new URLSearchParams({
  email,     // direct email field
  password,
})
```

**Acceptance Criteria**:
- [ ] Login form sends `email` field
- [ ] Registration auto-login sends `email` field
- [ ] No references to `username` field in login flow
- [ ] Field names match form labels

**Files Affected**:
- `phase2-fullstack/frontend/context/AuthContext.tsx`

### FR-003: Update API Proxy to Preserve Email Field

**Description**: Ensure Next.js proxy correctly forwards `email` field without modification

**Current Behavior**:
- Proxy reads form data as text
- Forwards with `Content-Type: application/x-www-form-urlencoded`
- Contains `username=...` field

**Required Behavior**:
- Proxy reads form data as text (unchanged)
- Forwards with `Content-Type: application/x-www-form-urlencoded` (unchanged)
- Contains `email=...` field

**Acceptance Criteria**:
- [ ] Proxy forwards `email` field correctly
- [ ] Content-Type preserved
- [ ] No field name transformations
- [ ] Form data reaches backend unchanged

**Files Affected**:
- `phase2-fullstack/frontend/app/api/auth/[...path]/route.ts` (verification only)

### FR-004: Email Validation

**Description**: Add explicit email format validation on the backend

**Requirements**:
- Email must be valid format (contains @, domain, etc.)
- Email is case-insensitive (normalize to lowercase)
- Email must not be empty
- Email maximum length: 255 characters

**Acceptance Criteria**:
- [ ] Invalid email format returns 400 Bad Request
- [ ] Valid email format is accepted
- [ ] Email normalization (lowercase) applied consistently
- [ ] Empty email returns 400 Bad Request
- [ ] Over-length email returns 400 Bad Request

**Validation Rules**:
```python
# Pydantic EmailStr validation or manual regex
import re
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate_email(email: str) -> str:
    if not email or not email.strip():
        raise ValueError("Email is required")

    email = email.lower().strip()

    if len(email) > 255:
        raise ValueError("Email is too long")

    if not re.match(EMAIL_REGEX, email):
        raise ValueError("Invalid email format")

    return email
```

**Error Responses**:
```json
// Invalid format
{
  "error": "Invalid email format",
  "details": "Email must be a valid email address"
}

// Empty email
{
  "error": "Email is required",
  "details": "Please provide your email address"
}
```

### FR-005: Remove OAuth2PasswordRequestForm Dependency

**Description**: Replace OAuth2PasswordRequestForm with standard Form fields

**Current Dependencies**:
```python
from fastapi.security import OAuth2PasswordRequestForm

form_data: OAuth2PasswordRequestForm = Depends()
email = form_data.username
password = form_data.password
```

**Required Approach**:
```python
from fastapi import Form

email: str = Form(...)
password: str = Form(...)
```

**Acceptance Criteria**:
- [ ] OAuth2PasswordRequestForm import removed
- [ ] Login endpoint uses Form(...) fields directly
- [ ] No functional changes to authentication logic
- [ ] Token generation unchanged
- [ ] Password verification unchanged

**Benefits**:
- Simpler code
- Clearer field naming
- No OAuth2-specific concepts for simple email/password auth
- Easier to understand for developers

---

## Non-Functional Requirements

### NFR-001: Backward Compatibility

- No breaking changes to token format
- Password hashing unchanged (bcrypt)
- JWT token generation unchanged
- User database schema unchanged

### NFR-002: Performance

- No performance degradation
- Email validation adds <1ms overhead
- Authentication flow remains under 1 second

### NFR-003: Security

- Email validation prevents injection
- Password handling unchanged (never logged, bcrypt hashed)
- Rate limiting remains active
- Token security unchanged

---

## Technical Constraints

1. **Backend Framework**: FastAPI - must use FastAPI Form validation
2. **Frontend Framework**: Next.js - URLSearchParams for form data
3. **Authentication**: JWT tokens - no changes to token structure
4. **Database**: Neon PostgreSQL - no schema changes required

---

## Dependencies

### Internal Dependencies

- Existing authentication system (tokens, password hashing)
- User model with email field
- Database with users table

### No External Dependencies

- No new libraries required
- Uses existing FastAPI Form validation
- Uses existing email validation (Pydantic EmailStr or regex)

---

## Out of Scope

The following are explicitly NOT included in this change:

- Support for username-based login (removing email requirement)
- Social login (OAuth2 providers)
- Magic link authentication
- Multi-factor authentication
- Password reset functionality
- Email verification
- Username field in user model
- Any database schema changes
- Token format changes
- Password hashing algorithm changes

---

## Assumptions

1. **Email as Primary Identifier**:
   - Users always log in with email (not username)
   - Email is unique in database
   - Email is the primary authentication credential

2. **Form Data Format**:
   - Frontend sends `application/x-www-form-urlencoded`
   - Backend expects form fields (not JSON)
   - Proxy preserves form data format

3. **Validation**:
   - FastAPI automatic validation is sufficient
   - Pydantic EmailStr or regex validation for email format
   - No additional validation layers needed

4. **Testing**:
   - Manual testing is sufficient for this change
   - Automated tests will be added in separate effort

---

## Data Model

No changes to data model. User entity remains:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Unique user identifier |
| email | String(255) | Unique, Not Null | User's email (login credential) |
| name | String(255) | Not Null | User's display name |
| hashed_password | String(255) | Not Null | Bcrypt hash of password |
| is_active | Boolean | Not Null | Account status |
| created_at | DateTime | Not Null | Account creation timestamp |
| updated_at | DateTime | Not Null | Last update timestamp |

**No schema migration required** - email field already exists and is properly indexed.

---

## Risk Assessment

### Low Risk

1. **Breaking Change**: Field name change from `username` to `email`
   - **Mitigation**: This is a new implementation, no existing external consumers
   - **Impact**: Low - internal application only

2. **Frontend/Backend Mismatch**: Temporary inconsistency during deployment
   - **Mitigation**: Deploy backend and frontend together in same session
   - **Impact**: Low - can be tested locally before deploying

3. **Validation Differences**: Email validation may reject previously valid usernames
   - **Mitigation**: We've always used email, no actual usernames exist
   - **Impact**: None - all existing users have valid email addresses

---

## Testing Strategy

### Manual Testing Checklist

1. **Backend API Testing**:
   - [ ] POST /auth/login with `email` and `password` → 200 OK + tokens
   - [ ] POST /auth/login with `username` and `password` → 422 (field not recognized)
   - [ ] POST /auth/login with invalid email format → 400 Bad Request
   - [ ] POST /auth/login with missing email → 422 Validation Error
   - [ ] POST /auth/login with missing password → 422 Validation Error
   - [ ] POST /auth/login with correct email, wrong password → 401 Unauthorized
   - [ ] POST /auth/login with non-existent email → 401 Unauthorized

2. **Frontend Testing**:
   - [ ] Login form sends `email` field (check Network tab)
   - [ ] Login with valid credentials → success
   - [ ] Login with invalid credentials → error message
   - [ ] Register → auto-login → success

3. **Integration Testing**:
   - [ ] Complete registration flow → dashboard
   - [ ] Complete login flow → dashboard
   - [ ] Logout → login again → success
   - [ ] Protected routes require authentication

4. **Error Message Testing**:
   - [ ] Invalid email format → clear error message
   - [ ] Missing email → clear error message
   - [ ] Validation errors reference `email` field (not `username`)

### Test Commands

```bash
# Test backend directly
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&password=SecurePass123"

# Expected: 200 OK with tokens

# Test with invalid email
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=notanemail&password=SecurePass123"

# Expected: 400 Bad Request with email validation error
```

---

## Implementation Notes

### Backend Changes

**File**: `phase2-fullstack/backend/app/routers/auth.py`

**Changes Required**:
1. Remove `from fastapi.security import OAuth2PasswordRequestForm`
2. Change login function signature:
   ```python
   async def login(
       request: Request,
       email: str = Form(..., description="User's email address"),
       password: str = Form(..., description="User's password"),
       session: Session = Depends(get_session),
   ):
   ```
3. Remove `email = form_data.username` mapping
4. Add email validation (optional - FastAPI handles basic validation)

### Frontend Changes

**File**: `phase2-fullstack/frontend/context/AuthContext.tsx`

**Changes Required**:
1. Change login function URLSearchParams:
   ```typescript
   body: new URLSearchParams({
     email,     // ← Changed from 'username: email'
     password,
   })
   ```
2. Change register auto-login URLSearchParams (same change)
3. Update comments referencing OAuth2/username

### Proxy Verification

**File**: `phase2-fullstack/frontend/app/api/auth/[...path]/route.ts`

**Verification Only** - No changes needed, already handles form data correctly.

---

## Deployment Checklist

### Pre-Deployment

- [ ] Local testing complete (all manual tests passing)
- [ ] Frontend build succeeds
- [ ] Backend starts without errors
- [ ] No 422 validation errors
- [ ] Error messages reference `email` field

### Deployment

- [ ] Commit changes to branch `002-use-email-password`
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel (or local)
- [ ] Test production login flow
- [ ] Verify error messages in production

### Post-Deployment

- [ ] Monitor logs for errors
- [ ] Verify users can log in successfully
- [ ] Check that new registrations work
- [ ] Confirm no 422 errors in production

---

## Success Validation

The feature is successfully implemented when:

1. **API Contract Clear**:
   - Login endpoint documentation shows `email` and `password` fields
   - No mention of `username` field in login API
   - Validation errors reference `email` field

2. **Developer Experience Improved**:
   - Frontend code directly sends `email` field
   - No mental mapping required (email → username)
   - Code is self-explanatory

3. **Functionality Maintained**:
   - Login flow works correctly
   - Registration and auto-login work
   - Token generation unchanged
   - Password verification unchanged

4. **Error Messages Clear**:
   - Missing email → "email field required"
   - Invalid email → "invalid email format"
   - No references to `username` field

---

## Appendix

### API Contract Before and After

**Before** (OAuth2PasswordRequestForm):
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secret

Response:
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**After** (Direct Email Field):
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=secret

Response:
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### Code Examples

**Backend Endpoint**:
```python
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    email: str = Form(..., description="User's email address"),
    password: str = Form(..., description="User's password"),
    session: Session = Depends(get_session),
):
    """Authenticate user with email and password."""
    # Normalize email
    email = email.lower().strip()

    # Find user
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Generate tokens and return
    ...
```

**Frontend Login**:
```typescript
const login = async (email: string, password: string) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      email,      // Clear and direct
      password,
    }),
  });
  // ... handle response
}
```

---

**Document Version**: 1.0
**Last Updated**: 2026-01-08
**Approved By**: Pending Review
