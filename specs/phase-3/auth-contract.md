# Canonical Authentication Contract for Phase 2/3

## Overview
This document defines the authoritative authentication contract between frontend and backend that must be preserved across Phase 2 and Phase 3 implementations. The system uses a cookie-based authentication model where JWT access and refresh tokens are stored in HttpOnly cookies, with the backend as the single source of truth.

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
  - Sets HttpOnly cookies containing JWT tokens
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
- **Success Response**: 201 with user data and HttpOnly cookie containing JWT token
- **Failure Response**: 400/409 with error details

### Verify Endpoint
- **Frontend Request**: `GET /api/auth/verify` (via proxy)
- **Backend Receives**: `GET /auth/verify`
- **Method**: GET
- **Authentication**: HttpOnly cookie automatically included by browser
- **Success Response**: 200 with user data
- **Failure Response**: 401 with error details

### Refresh Endpoint
- **Frontend Request**: `POST /api/auth/refresh`
- **Backend Receives**: `POST /auth/refresh`
- **Method**: POST
- **Authentication**: HttpOnly cookie automatically included by browser or form data
- **Success Response**: 200 with new tokens set in HttpOnly cookies
- **Failure Response**: 401 with error details

## Authentication Flow

### Cookie Management
- **Cookie Name**: `auth_token`
- **HttpOnly**: true
- **Secure**: true in production, false in development
- **SameSite**: none in production, lax in development
- **Max Age**: 30 minutes (1800 seconds)

### Token Propagation
1. Backend issues JWT token as HttpOnly cookie upon successful login
2. Browser automatically stores and manages HttpOnly cookie
3. Browser automatically includes cookie in all subsequent requests to same origin
4. Backend extracts token from cookie for authentication verification

## Backend Implementation Requirements

### Route Structure
Backend must expose auth endpoints at `/auth/{operation}`:
- `/auth/login`
- `/auth/register`
- `/auth/verify` (GET method)
- `/auth/refresh`

### Authentication Method
- **Token Type**: JWT Bearer tokens stored in HttpOnly cookies
- **Algorithm**: HS256 (recommended)
- **Payload**: Must include `sub` (user identifier), `exp` (expiration)
- **User Identifier**: Should use UUID string format for consistency

## Frontend Implementation Requirements

### Proxy Behavior
- **Public Routes**: `/login`, `/register` (no auth cookie required)
- **Protected Routes**: `/verify`, `/refresh`, `/logout` (require auth cookie)
- **URL Mapping**: Frontend `/api/auth/{path}` → Backend `/auth/{path}`
- **Cookie Handling**: Frontend NEVER reads, parses, or forwards tokens manually; relies on browser to include HttpOnly cookies automatically

### Error Handling
- 401 responses from backend should trigger logout/redirect to login
- Network errors should show appropriate user feedback
- Token expiration should trigger refresh attempts

## Key Differences Between Phase 2 and Phase 3

### Phase 2 Backend
- Routes: `/auth/login`, `/auth/register`, `/auth/verify` (GET), `/auth/refresh`
- Token storage: JWT with integer user IDs in HttpOnly cookies
- Dependencies: FastAPI with SQLModel, custom auth utils

### Phase 3 Backend
- Routes: `/auth/login`, `/auth/register`, `/auth/verify` (GET), `/auth/refresh` (same as Phase 2)
- Token storage: JWT with UUID user IDs in HttpOnly cookies
- Dependencies: FastAPI with SQLModel, auth dependencies in src/dependencies

### Critical Difference
The token storage mechanism remains consistent between phases:
1. Phase 3 backend maintains the same cookie-based authentication model as Phase 2
2. Phase 3 frontend proxy maintains the same behavior of letting browser handle HttpOnly cookies
3. User ID format change: int (Phase 2) → UUID string (Phase 3) while preserving cookie-based flow

## Expected Verification Results

Upon proper implementation of the authentication contract:
- POST /api/auth/login should return 200 and set authentication cookies
- GET /api/auth/verify should return 200 with user data for valid cookie sessions
- All subsequent protected API calls should succeed with valid authentication via browser-included cookies
- Phase 2 functionality should remain intact
- Phase 3 chatbot functionality should work with authenticated user context