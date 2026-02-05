# Canonical Authentication Contract for Phase 2/3

## Overview
This document defines the authoritative authentication contract between frontend and backend that must be preserved across Phase 2 and Phase 3 implementations.

## Frontend → Backend Authentication Routes

### Login Endpoint
- **Frontend Request**: `POST /api/auth/login`
- **Backend Receives**: `POST /auth/login`
- **Method**: POST
- **Expected Content-Type**: `application/x-www-form-urlencoded` (OAuth2PasswordRequestForm)
- **Parameters**:
  - `username` (string): User's email or username
  - `password` (string): User's password
- **Success Response**:
  - Status: 200
  - Body: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`
- **Failure Response**: 401 with error details

### Register Endpoint
- **Frontend Request**: `POST /api/auth/register`
- **Backend Receives**: `POST /auth/register`
- **Method**: POST
- **Expected Content-Type**: `application/x-www-form-urlencoded`
- **Parameters**:
  - `email` (string): User's email
  - `password` (string): User's password
  - `username` (string): User's username
- **Success Response**: 201 with user data
- **Failure Response**: 400/409 with error details

### Verify Endpoint
- **Frontend Request**: `POST /api/auth/verify` (via proxy)
- **Backend Receives**: `POST /auth/verify`
- **Method**: POST
- **Headers**: `Authorization: Bearer {token}`
- **Success Response**: 200 with user data
- **Failure Response**: 401 with error details

### Refresh Endpoint
- **Frontend Request**: `POST /api/auth/refresh`
- **Backend Receives**: `POST /auth/refresh`
- **Method**: POST
- **Headers**: `Authorization: Bearer {refresh_token}` or form data
- **Success Response**: 200 with new tokens
- **Failure Response**: 401 with error details

## Authentication Flow

### Cookie Management
- **Cookie Name**: `auth_token`
- **HttpOnly**: true
- **Secure**: true in production, false in development
- **SameSite**: none in production, lax in development
- **Max Age**: 30 minutes (1800 seconds)

### Token Propagation
1. Frontend receives JWT token from backend login
2. Token is stored in HttpOnly cookie via `setAuthCookie()`
3. Subsequent requests include token in `Authorization: Bearer {token}` header
4. Frontend proxy extracts token from cookie and adds to backend requests

## Backend Implementation Requirements

### Route Structure
Backend must expose auth endpoints at `/auth/{operation}`:
- `/auth/login`
- `/auth/register`
- `/auth/verify`
- `/auth/refresh`

### Authentication Method
- **Token Type**: JWT Bearer tokens
- **Algorithm**: HS256 (recommended)
- **Payload**: Must include `sub` (user identifier), `exp` (expiration)
- **User Identifier**: Should use UUID string format for consistency

## Frontend Implementation Requirements

### Proxy Behavior
- **Public Routes**: `/login`, `/register` (no auth token required)
- **Protected Routes**: `/verify`, `/refresh`, `/logout` (require auth token)
- **URL Mapping**: Frontend `/api/auth/{path}` → Backend `/auth/{path}`

### Error Handling
- 401 responses from backend should trigger logout/redirect to login
- Network errors should show appropriate user feedback
- Token expiration should trigger refresh attempts

## Key Differences Between Phase 2 and Phase 3

### Phase 2 Backend
- Routes: `/auth/login`, `/auth/register`, `/auth/verify`, `/auth/refresh`
- Token storage: Traditional JWT with integer user IDs
- Dependencies: FastAPI with SQLModel, custom auth utils

### Phase 3 Backend
- Routes: `/auth/login`, `/auth/register`, `/auth/verify`, `/auth/refresh` (same as Phase 2)
- Token storage: JWT with UUID user IDs
- Dependencies: FastAPI with SQLModel, auth dependencies in src/dependencies

### Current Issue
The authentication contract mismatch occurs because:
1. Phase 3 backend has `/auth/` routes (same as Phase 2)
2. Phase 3 frontend proxy maps `/api/auth/` to `/auth/` (same as Phase 2)
3. But there might be differences in:
   - Token format/storage between implementations
   - User ID format (int vs UUID)
   - Token validation logic
   - Cookie handling between frontend and backend

## Expected Verification Results

Upon fixing the authentication contract:
- POST /api/auth/login should return 200 with token
- GET /api/auth/verify should return 200 with user data for valid sessions
- All subsequent protected API calls should succeed with valid authentication
- Phase 2 functionality should remain intact
- Phase 3 chatbot functionality should work with authenticated user context