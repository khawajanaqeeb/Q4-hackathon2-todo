# Feature Specification: Fix Authentication 422 Errors and Security Hardening

**Feature ID**: 001-fix-auth-422
**Created**: 2026-01-08
**Status**: Draft
**Priority**: P0 (Production Blocker)

---

## Executive Summary

The full-stack todo application is experiencing critical authentication failures preventing user login and registration. POST requests to `/api/auth/login` and `/api/auth/register` return 422 Unprocessable Entity errors due to request/response validation mismatches between the FastAPI backend and Next.js frontend proxy.

This specification addresses the authentication system overhaul required to:
- Fix the 422 validation errors blocking user authentication
- Ensure secure password handling with bcrypt
- Standardize API contracts between frontend and backend
- Verify database integration with Neon PostgreSQL
- Prepare the system for production deployment on Railway

---

## Problem Statement

### Current Issues

1. **422 Validation Errors (P0 - Blocker)**
   - Backend `/auth/login` endpoint expects `Form(...)` fields (`application/x-www-form-urlencoded`)
   - Frontend proxy forwards requests with potentially mismatched content types
   - Login and registration completely non-functional

2. **Route Inconsistency**
   - Backend mounts routes at `/auth/*` (line 36 in main.py)
   - Frontend proxy adds `/auth` prefix to all requests
   - This creates correct paths BUT validation fails before routing

3. **Form Data vs JSON Mismatch**
   - Backend login uses `email: str = Form(...)` and `password: str = Form(...)`
   - Frontend sends `application/x-www-form-urlencoded` correctly
   - Proxy may be converting or corrupting the request format

4. **Security Concerns**
   - Password hashing with bcrypt is implemented but needs verification
   - Rate limiting configured but may not be active
   - JWT token generation needs security audit
   - No CSRF protection mentioned

### Impact

- **Users**: Cannot log in or register - complete authentication failure
- **Business**: Application is non-functional for end users
- **Development**: Blocking further testing and feature development
- **Production**: Not deployable to Railway in current state

---

## Success Criteria

The authentication system will be considered fixed when:

1. **Functional Requirements**
   - Users can successfully register new accounts with valid email and password
   - Users can log in with correct credentials and receive JWT tokens
   - JWT tokens are properly validated on protected endpoints
   - Invalid credentials return appropriate error messages
   - Token refresh mechanism works correctly

2. **Performance Targets**
   - Registration completes in under 2 seconds
   - Login completes in under 1 second
   - Token verification completes in under 500ms
   - System handles 100 concurrent authentication requests

3. **Security Standards**
   - Passwords hashed with bcrypt (cost factor 12)
   - JWT tokens properly signed and verified
   - Rate limiting active (5 login attempts per minute per IP)
   - No sensitive data logged (passwords, tokens)
   - HTTPS enforced in production
   - Generic error messages prevent user enumeration

4. **Quality Metrics**
   - Zero 422 validation errors in authentication flows
   - 100% test coverage for authentication endpoints
   - All authentication tests passing (registration, login, logout, refresh)
   - Database correctly stores and retrieves user data

---

## User Scenarios

### Scenario 1: New User Registration

**Actor**: New User
**Goal**: Create an account to use the todo application

**Flow**:
1. User navigates to `/register` page
2. User fills in registration form:
   - Name: "Jane Doe"
   - Email: "jane@example.com"
   - Password: "SecurePass123!"
3. User clicks "Register" button
4. Frontend sends POST request to `/api/auth/register`
5. Next.js proxy forwards to backend `/auth/register`
6. Backend validates email uniqueness
7. Backend hashes password with bcrypt
8. Backend creates user record in database
9. Backend automatically logs user in
10. Backend returns JWT access token
11. Proxy sets httpOnly cookie with token
12. User redirected to `/dashboard`

**Success Criteria**:
- User account created in database
- Password stored as bcrypt hash
- User automatically logged in
- Token set in httpOnly cookie
- User sees dashboard

**Edge Cases**:
- Email already registered → "Email already registered" error
- Weak password → "Password must be at least 8 characters" error
- Invalid email format → "Invalid email address" error
- Database connection failure → "Service unavailable, try again" error

### Scenario 2: Existing User Login

**Actor**: Registered User
**Goal**: Access their todo list

**Flow**:
1. User navigates to `/login` page
2. User enters credentials:
   - Email: "jane@example.com"
   - Password: "SecurePass123!"
3. User clicks "Login" button
4. Frontend sends POST request to `/api/auth/login`
5. Next.js proxy forwards to backend `/auth/login`
6. Backend finds user by email
7. Backend verifies password against bcrypt hash
8. Backend generates JWT access and refresh tokens
9. Backend returns tokens
10. Proxy sets httpOnly cookie with access token
11. User redirected to `/dashboard`

**Success Criteria**:
- User successfully authenticated
- JWT token generated and returned
- Token set in httpOnly cookie
- User sees their dashboard

**Edge Cases**:
- Invalid email → "Invalid email or password" (generic for security)
- Invalid password → "Invalid email or password" (generic for security)
- Inactive account → "Account is inactive" error
- Rate limit exceeded → "Too many login attempts, try again later" error

### Scenario 3: Protected Resource Access

**Actor**: Logged-in User
**Goal**: Access protected todo endpoints

**Flow**:
1. User makes request to `/api/todos`
2. Frontend includes httpOnly cookie automatically
3. Next.js proxy extracts token from cookie
4. Proxy forwards request with Authorization header
5. Backend validates JWT token
6. Backend extracts user ID from token
7. Backend fetches user from database
8. Backend processes request with user context
9. Backend returns user-specific todos

**Success Criteria**:
- Token automatically included in requests
- Backend validates token successfully
- User accesses only their own data
- Request completes without re-authentication

**Edge Cases**:
- Expired token → 401 Unauthorized, redirect to login
- Invalid token → 401 Unauthorized, redirect to login
- User deleted → 401 Unauthorized, redirect to login

---

## Functional Requirements

### FR-001: Fix Login Endpoint Validation

**Description**: Correct the form data handling in the login endpoint to accept frontend requests

**Current Behavior**:
- Backend expects: `email: str = Form(...)`, `password: str = Form(...)`
- Frontend sends: `application/x-www-form-urlencoded` with URLSearchParams
- Result: 422 Unprocessable Entity

**Required Behavior**:
- Backend accepts form data from frontend proxy
- Request validation passes
- Credentials properly extracted
- User authenticated successfully

**Acceptance Criteria**:
- [ ] Login endpoint accepts `application/x-www-form-urlencoded` requests
- [ ] Email and password correctly extracted from form data
- [ ] Valid credentials return 200 OK with JWT tokens
- [ ] Invalid credentials return 401 Unauthorized with generic error
- [ ] No 422 errors in authentication flow

**Files Affected**:
- `phase2-fullstack/backend/app/routers/auth.py` (login endpoint)
- `phase2-fullstack/frontend/app/api/auth/[...path]/route.ts` (proxy forwarding)
- `phase2-fullstack/frontend/context/AuthContext.tsx` (login function)

### FR-002: Standardize Request/Response Contracts

**Description**: Ensure frontend and backend use identical data structures for all authentication operations

**Requirements**:
- Backend Pydantic schemas match frontend TypeScript types
- Request bodies use consistent field names and types
- Response structures are identical across all auth endpoints
- Error responses follow standard format

**Acceptance Criteria**:
- [ ] `UserCreate` schema matches registration form data
- [ ] `LoginRequest` schema matches login form data (or use Form fields)
- [ ] `TokenResponse` schema matches frontend token handling
- [ ] `UserResponse` schema matches frontend user state
- [ ] All field names are identical (case-sensitive)
- [ ] All validation errors return structured format

**Contracts**:

```typescript
// Registration Request
{
  "name": "string",      // 1-255 characters
  "email": "string",     // Valid email format
  "password": "string"   // 8-255 characters
}

// Registration Response (HTTP 201)
{
  "id": number,
  "email": "string",
  "name": "string",
  "is_active": boolean,
  "created_at": "ISO 8601 string",
  "updated_at": "ISO 8601 string"
}

// Login Request (application/x-www-form-urlencoded)
email=user@example.com&password=SecurePass123

// Login Response (HTTP 200)
{
  "access_token": "string (JWT)",
  "refresh_token": "string (JWT)",
  "token_type": "bearer"
}

// Verify Request (GET with Authorization header)
Authorization: Bearer <access_token>

// Verify Response (HTTP 200)
{
  "id": number,
  "email": "string",
  "name": "string",
  "is_active": boolean,
  "created_at": "ISO 8601 string",
  "updated_at": "ISO 8601 string"
}

// Error Response (HTTP 4xx/5xx)
{
  "error": "string (user-facing message)",
  "details": "string (optional technical details)"
}
```

### FR-003: Secure Password Handling

**Description**: Verify and document password hashing, storage, and verification

**Requirements**:
- Passwords hashed with bcrypt (cost factor 12)
- Plain text passwords never stored or logged
- Password verification resistant to timing attacks
- Password strength validation enforced

**Acceptance Criteria**:
- [ ] `hash_password()` uses bcrypt with cost factor 12
- [ ] `verify_password()` uses constant-time comparison
- [ ] Password strength validation enforces:
  - Minimum 8 characters
  - Maximum 255 characters
  - At least one uppercase letter (recommended)
  - At least one number (recommended)
  - At least one special character (recommended)
- [ ] Plain text passwords never logged
- [ ] Database stores only bcrypt hashes

**Security Notes**:
- Bcrypt is intentionally slow (prevents brute force)
- Cost factor 12 provides good balance (≈200ms per hash)
- Salt is automatically handled by bcrypt
- Rainbow table attacks prevented

### FR-004: JWT Token Security

**Description**: Ensure JWT tokens are properly generated, signed, and validated

**Requirements**:
- Access tokens expire after 30 minutes
- Refresh tokens expire after 7 days
- Tokens signed with secure SECRET_KEY
- Token payload includes user ID and email
- Token validation checks signature and expiration

**Acceptance Criteria**:
- [ ] `create_access_token()` generates valid JWT with 30min expiry
- [ ] `create_refresh_token()` generates valid JWT with 7 day expiry
- [ ] `decode_access_token()` validates signature and expiration
- [ ] `decode_refresh_token()` validates signature and expiration
- [ ] SECRET_KEY is loaded from environment variable
- [ ] SECRET_KEY is minimum 32 characters (256 bits)
- [ ] Token payload includes:
  - `sub`: User ID (as string)
  - `email`: User email
  - `exp`: Expiration timestamp
  - `iat`: Issued at timestamp

**Token Structure**:
```json
{
  "sub": "123",
  "email": "user@example.com",
  "iat": 1704153600,
  "exp": 1704155400
}
```

### FR-005: Rate Limiting

**Description**: Protect authentication endpoints from brute force attacks

**Requirements**:
- Login endpoint: 5 attempts per minute per IP
- Registration endpoint: 3 attempts per minute per IP
- Refresh endpoint: 10 attempts per minute per IP
- Rate limit state stored in memory (or Redis for production)

**Acceptance Criteria**:
- [ ] `@limiter.limit("5/minute")` decorator on login endpoint
- [ ] `@limiter.limit("3/minute")` decorator on register endpoint
- [ ] `@limiter.limit("10/minute")` decorator on refresh endpoint
- [ ] Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp
- [ ] 429 Too Many Requests returned when limit exceeded
- [ ] Rate limit bypass available for testing

### FR-006: Error Handling and Logging

**Description**: Provide clear error messages without exposing sensitive information

**Requirements**:
- User-facing errors are generic (prevent enumeration)
- Technical details logged server-side
- Authentication attempts logged (without passwords)
- Failed login attempts tracked

**Acceptance Criteria**:
- [ ] Invalid credentials → "Invalid email or password" (generic)
- [ ] Inactive account → "Account is inactive" (specific)
- [ ] Rate limit exceeded → "Too many requests, try again later"
- [ ] Server errors → "Service unavailable, please try again"
- [ ] Login attempts logged with:
  - Timestamp
  - Email (NOT password)
  - IP address
  - Success/failure status
  - Error type (if failed)
- [ ] Passwords NEVER appear in logs

**Logging Examples**:
```
INFO: Login attempt - email=user@example.com, ip=192.168.1.1, status=success
INFO: Login attempt - email=user@example.com, ip=192.168.1.1, status=failed, error=invalid_credentials
INFO: Registration - email=new@example.com, ip=192.168.1.1, status=success
```

### FR-007: Database Integration Verification

**Description**: Ensure SQLAlchemy models work correctly with Neon PostgreSQL

**Requirements**:
- User model correctly defined with all fields
- Database connection uses environment variable
- Sessions properly managed (created and closed)
- Alembic migrations applied
- Connection pooling configured

**Acceptance Criteria**:
- [ ] `User` model includes:
  - `id`: Integer primary key (auto-increment)
  - `email`: String (unique, indexed)
  - `name`: String
  - `hashed_password`: String
  - `is_active`: Boolean (default True)
  - `created_at`: DateTime (auto-set)
  - `updated_at`: DateTime (auto-update)
- [ ] `DATABASE_URL` loaded from environment
- [ ] SSL mode enabled for Neon (`sslmode=require`)
- [ ] Connection pool configured:
  - Pool size: 5
  - Max overflow: 10
  - Pool timeout: 30 seconds
- [ ] Database tables created on startup
- [ ] Migrations tracked with Alembic

**Database Schema**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_users_email ON users(email);
```

### FR-008: Frontend Proxy Configuration

**Description**: Ensure Next.js authentication proxy correctly forwards requests

**Requirements**:
- Proxy routes all `/api/auth/*` requests to backend
- Content-Type headers preserved
- Form data properly forwarded
- Cookies set on successful authentication
- Errors handled gracefully

**Acceptance Criteria**:
- [ ] `/api/auth/login` forwards to `${BACKEND_URL}/auth/login`
- [ ] `/api/auth/register` forwards to `${BACKEND_URL}/auth/register`
- [ ] `/api/auth/verify` forwards to `${BACKEND_URL}/auth/verify`
- [ ] `/api/auth/refresh` forwards to `${BACKEND_URL}/auth/refresh`
- [ ] `/api/auth/logout` clears cookies locally (no backend call)
- [ ] Content-Type headers preserved in forwarding
- [ ] Form data sent as `application/x-www-form-urlencoded`
- [ ] JSON responses properly parsed
- [ ] httpOnly cookies set on login/register success
- [ ] Cookies include:
  - `auth_token`: JWT access token
  - `httpOnly`: true
  - `secure`: true (production only)
  - `sameSite`: 'strict'
  - `maxAge`: 1800 seconds (30 minutes)
  - `path`: '/'

---

## Non-Functional Requirements

### NFR-001: Performance

- Authentication endpoints respond within 2 seconds (95th percentile)
- Token verification completes within 500ms
- Database queries optimized with indexes
- No N+1 query problems

### NFR-002: Security

- HTTPS enforced in production (Railway)
- CORS configured for frontend origin only
- JWT tokens properly signed and validated
- Passwords never exposed in responses or logs
- Rate limiting active and tested
- SQL injection prevented (SQLAlchemy parameterized queries)
- XSS prevention (React escaping, CSP headers)

### NFR-003: Observability

- Authentication attempts logged
- Failed login attempts tracked
- Error rates monitored
- Token generation/validation logged
- Database connection health checked

### NFR-004: Reliability

- Database connection retries configured
- Graceful degradation on service failures
- Transaction rollback on errors
- Connection pool prevents resource exhaustion

---

## Technical Constraints

1. **Backend Framework**: FastAPI (Python) - no changes allowed
2. **Frontend Framework**: Next.js 13+ App Router - no changes allowed
3. **Database**: Neon PostgreSQL - no changes allowed
4. **Deployment**: Railway.app - must be compatible
5. **Authentication**: JWT tokens with bcrypt - established pattern
6. **Rate Limiting**: slowapi library - already integrated

---

## Dependencies

### External Services

- **Neon PostgreSQL**: Database hosting (required)
- **Railway.app**: Backend hosting (required)
- **Vercel**: Frontend hosting (or local dev)

### Environment Variables Required

**Backend** (`phase2-fullstack/backend/.env`):
```
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
SECRET_KEY=<minimum 32 character secret>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
ALGORITHM=HS256
```

**Frontend** (`phase2-fullstack/frontend/.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
# or in production:
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Out of Scope

The following are explicitly NOT included in this fix:

- OAuth2 / social login integration
- Multi-factor authentication (MFA)
- Password reset functionality
- Email verification
- Account deletion
- User profile updates
- Permission/role system beyond is_active flag
- Session management beyond JWT tokens
- Frontend UI/UX improvements
- Database migration tools (Alembic setup exists)
- Performance monitoring beyond basic logging
- Automated security scanning
- Load testing

---

## Assumptions

1. **Environment Setup**:
   - Database (Neon) is provisioned and accessible
   - Railway backend service is configured
   - Environment variables are set correctly

2. **Security**:
   - HTTPS is terminated at Railway/Vercel level
   - CORS is sufficient (no additional auth middleware needed)
   - JWT tokens in httpOnly cookies are acceptable security

3. **Performance**:
   - Single database instance is sufficient for current scale
   - In-memory rate limiting is acceptable (no Redis required yet)
   - No caching layer needed for auth operations

4. **Testing**:
   - Manual testing is sufficient for this fix
   - Automated tests will be added in separate effort

---

## Data Model

### User Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique user identifier |
| email | String(255) | Unique, Not Null, Indexed | User's email address (login credential) |
| name | String(255) | Not Null | User's display name |
| hashed_password | String(255) | Not Null | Bcrypt hash of password |
| is_active | Boolean | Not Null, Default: True | Account activation status |
| created_at | DateTime | Not Null, Auto-set | Account creation timestamp (UTC) |
| updated_at | DateTime | Not Null, Auto-update | Last modification timestamp (UTC) |

**Relationships**:
- User has many Todos (one-to-many)

**Indexes**:
- Primary key index on `id`
- Unique index on `email`

---

## Risk Assessment

### High Risk

1. **Data Loss**: Incorrect password hashing could lock out all users
   - **Mitigation**: Test with dummy accounts first, backup database

2. **Security Breach**: Weak JWT secret or SQL injection
   - **Mitigation**: Use strong secrets (32+ chars), SQLAlchemy prevents injection

### Medium Risk

3. **Breaking Changes**: Schema changes could break existing users
   - **Mitigation**: Use Alembic migrations, test on staging first

4. **Rate Limiting**: Too aggressive limits could block legitimate users
   - **Mitigation**: Start with lenient limits, monitor and adjust

### Low Risk

5. **Performance**: Bcrypt slowness could impact response times
   - **Mitigation**: Cost factor 12 is industry standard, acceptable for auth

---

## Testing Strategy

### Unit Tests

- Password hashing and verification
- JWT token generation and validation
- User model validation
- Schema validation

### Integration Tests

- Registration endpoint with valid/invalid data
- Login endpoint with correct/incorrect credentials
- Token verification with valid/expired tokens
- Database operations (create, read, update)

### End-to-End Tests

- Complete registration flow (frontend → proxy → backend → database)
- Complete login flow (frontend → proxy → backend → cookie)
- Protected resource access (cookie → proxy → backend → response)
- Logout flow (cookie clearing)

### Manual Testing Checklist

- [ ] Register new user → success (201 Created)
- [ ] Register duplicate email → error (400 Bad Request)
- [ ] Login with valid credentials → success (200 OK + token)
- [ ] Login with invalid email → error (401 Unauthorized)
- [ ] Login with invalid password → error (401 Unauthorized)
- [ ] Access protected endpoint with valid token → success
- [ ] Access protected endpoint without token → error (401)
- [ ] Access protected endpoint with expired token → error (401)
- [ ] Refresh token with valid refresh token → success
- [ ] Refresh token with invalid refresh token → error (401)
- [ ] Rate limit enforcement (6 login attempts) → error (429)
- [ ] Database contains correct user data
- [ ] Password is bcrypt hash (not plain text)
- [ ] No 422 errors in any authentication flow

---

## Deployment Checklist

### Railway Backend

- [ ] Environment variables set (DATABASE_URL, SECRET_KEY, etc.)
- [ ] Database migrations applied
- [ ] Health check endpoint responding
- [ ] CORS configured for frontend domain
- [ ] Logs show successful startup
- [ ] Test authentication endpoints via curl

### Vercel Frontend (or local)

- [ ] Environment variables set (NEXT_PUBLIC_API_URL)
- [ ] Build completes without errors
- [ ] Authentication proxy routes configured
- [ ] Cookies working correctly
- [ ] Test registration and login via UI

### Neon Database

- [ ] Connection string includes `sslmode=require`
- [ ] User table created with correct schema
- [ ] Indexes created
- [ ] Test database connection from Railway

---

## Success Validation

The authentication system is production-ready when:

1. **All Manual Tests Pass**: Complete checklist above with zero failures
2. **No 422 Errors**: All authentication requests process correctly
3. **Database Verification**: Users stored correctly with bcrypt hashes
4. **Token Flow Works**: Login → cookie set → protected access → logout → access denied
5. **Error Handling Works**: Invalid inputs return appropriate errors
6. **Security Verified**: Rate limiting active, passwords hashed, tokens valid
7. **Railway Deployment**: Backend responding and authenticating correctly
8. **Frontend Integration**: UI successfully communicates with backend

---

## Appendix

### Key Files

**Backend**:
- `phase2-fullstack/backend/app/main.py` - FastAPI app and router mounting
- `phase2-fullstack/backend/app/routers/auth.py` - Authentication endpoints
- `phase2-fullstack/backend/app/schemas/user.py` - Pydantic request/response schemas
- `phase2-fullstack/backend/app/models/user.py` - SQLAlchemy User model
- `phase2-fullstack/backend/app/utils/security.py` - Password/JWT utilities
- `phase2-fullstack/backend/app/database.py` - Database connection
- `phase2-fullstack/backend/app/config.py` - Settings and environment variables

**Frontend**:
- `phase2-fullstack/frontend/app/api/auth/[...path]/route.ts` - Unified auth proxy
- `phase2-fullstack/frontend/context/AuthContext.tsx` - Authentication state management
- `phase2-fullstack/frontend/app/login/page.tsx` - Login UI
- `phase2-fullstack/frontend/app/register/page.tsx` - Registration UI
- `phase2-fullstack/frontend/lib/api-utils.ts` - API helper functions

### Reference Documentation

- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- JWT Tokens: https://jwt.io/introduction
- Bcrypt: https://github.com/pyca/bcrypt
- Next.js API Routes: https://nextjs.org/docs/app/building-your-application/routing/route-handlers
- Neon PostgreSQL: https://neon.tech/docs
- Railway Deployment: https://docs.railway.app/

---

**Document Version**: 1.0
**Last Updated**: 2026-01-08
**Approved By**: Pending Review
