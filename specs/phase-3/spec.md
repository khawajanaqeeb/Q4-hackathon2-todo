# Phase 3: Chatbot Authentication & Integration Specification

## Overview
This specification defines the requirements for integrating chatbot functionality with authentication in the todo application. The system will enable users to manage their todos through natural language interactions while maintaining secure authentication. This builds upon the Phase 2 foundation and preserves all existing functionality.

## Canonical Authentication Contract

### Frontend → Backend Authentication Routes

#### Login Endpoint
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

#### Register Endpoint
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

#### Verify Endpoint
- **Frontend Request**: `POST /api/auth/verify` (via proxy)
- **Backend Receives**: `POST /auth/verify`
- **Method**: POST
- **Headers**: `Authorization: Bearer {token}`
- **Success Response**: 200 with user data
- **Failure Response**: 401 with error details

#### Refresh Endpoint
- **Frontend Request**: `POST /api/auth/refresh`
- **Backend Receives**: `POST /auth/refresh`
- **Method**: POST
- **Headers**: `Authorization: Bearer {refresh_token}` or form data
- **Success Response**: 200 with new tokens
- **Failure Response**: 401 with error details

### Authentication Flow

#### Cookie Management
- **Cookie Name**: `auth_token`
- **HttpOnly**: true
- **Secure**: true in production, false in development
- **SameSite**: none in production, lax in development
- **Max Age**: 30 minutes (1800 seconds)

#### Token Propagation
1. Frontend receives JWT token from backend login
2. Token is stored in HttpOnly cookie via `setAuthCookie()`
3. Subsequent requests include token in `Authorization: Bearer {token}` header
4. Frontend proxy extracts token from cookie and adds to backend requests

### Backend Implementation Requirements

#### Route Structure
Backend must expose auth endpoints at `/auth/{operation}`:
- `/auth/login`
- `/auth/register`
- `/auth/verify`
- `/auth/refresh`

#### Authentication Method
- **Token Type**: JWT Bearer tokens
- **Algorithm**: HS256 (recommended)
- **Payload**: Must include `sub` (user identifier), `exp` (expiration)
- **User Identifier**: Should use UUID string format for consistency

### Frontend Implementation Requirements

#### Proxy Behavior
- **Public Routes**: `/login`, `/register` (no auth token required)
- **Protected Routes**: `/verify`, `/refresh`, `/logout` (require auth token)
- **URL Mapping**: Frontend `/api/auth/{path}` → Backend `/auth/{path}`

#### Error Handling
- 401 responses from backend should trigger logout/redirect to login
- Network errors should show appropriate user feedback
- Token expiration should trigger refresh attempts

## User Stories

### US1: User Registration and Authentication (P1 - High Priority)
As a new user, I want to register for an account and log in securely so that I can access my todo list and chatbot functionality.

**Acceptance Criteria**:
- User can register with username, email, and password
- User can log in with registered credentials
- Sessions are maintained securely using JWT tokens in HTTP-only cookies
- Invalid credentials return appropriate error messages
- POST /api/auth/login returns 200 with token
- GET /api/auth/verify returns 200 with user data for valid sessions

### US2: Todo Management Through Traditional UI (P1 - High Priority)
As an authenticated user, I want to manage my todos through the traditional UI so that I can create, update, complete, and delete todo items.

**Acceptance Criteria**:
- User can create todos with title, description, priority, due date, and tags
- User can mark todos as complete/incomplete
- User can update todo details
- User can delete todos
- User can view all their todos in a list
- All Phase 2 functionality remains intact without regression

### US3: Todo Management Through Chatbot (P2 - Medium Priority)
As an authenticated user, I want to manage my todos through natural language chat so that I can interact with my todo list more naturally.

**Acceptance Criteria**:
- Chatbot understands natural language commands for todo operations
- Chatbot can create, update, delete, and list user's todos
- Chatbot maintains context during conversations
- Actions taken via chat are reflected in the traditional UI
- Chat endpoint works with authenticated user context
- MCP tool invocation succeeds with same auth context

### US4: Session Management and Security (P1 - High Priority)
As a user, I want my session to be managed securely so that my data remains protected and my login state is maintained appropriately.

**Acceptance Criteria**:
- Sessions expire after defined inactivity period
- User is redirected to login when session expires
- User data is isolated and not accessible to other users
- API requests are rate-limited to prevent abuse
- MCP server validates user identity from frontend context before executing any todo operations

## Business Objectives
- Enable natural language interaction for todo management
- Maintain secure user authentication across all features
- Provide seamless integration between traditional UI and chatbot
- Support AI-powered assistance for task management
- Preserve all Phase 2 functionality while adding Phase 3 features
- Ensure consistent authentication contract between frontend and backend