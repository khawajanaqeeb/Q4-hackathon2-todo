# API Contract: Authentication Proxy and Task Management

## Overview
This document specifies the API contracts for the authentication proxy fix and task management functionality. The contract ensures consistency between frontend and backend implementations, particularly addressing the 422 Unprocessable Entity error and proper data validation.

## API Endpoints

### Authentication Proxy (Fixed)

#### POST /api/auth/proxy/[...path]
**Description**: Proxy route for authenticated API requests - fixes Promise resolution error in catch-all routes

**Request**:
- Method: POST
- Path: `/api/auth/proxy/{any_backend_endpoint}`
- Headers:
  - `Authorization: Bearer {jwt_token}` (required)
  - `Content-Type: application/json` (for POST/PUT/PATCH requests)
- Body: Forwarded from frontend to backend (varies by target endpoint)

**Response**:
- Success: Response from target backend endpoint (200, 201, etc.)
- `401 Unauthorized`: Invalid or expired JWT token
- `403 Forbidden`: Insufficient permissions for requested resource
- `422 Unprocessable Entity`: Validation error with proper error format:
  ```json
  {
    "detail": "Validation error message",
    "error_code": "VALIDATION_ERROR"
  }
  ```

**Fix Applied**: Properly awaits `params` Promise in Next.js App Router catch-all route:
```typescript
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  const apiPath = resolvedParams.path ? `/${resolvedParams.path.join('/')}` : '';
  // ... rest of proxy logic
}
```

#### GET /api/auth/proxy/[...path]
**Description**: Proxy route for authenticated GET requests - fixes Promise resolution error

**Request**:
- Method: GET
- Path: `/api/auth/proxy/{any_backend_endpoint}`
- Headers:
  - `Authorization: Bearer {jwt_token}` (required)

**Response**:
- Success: Response from target backend endpoint (200)
- `401 Unauthorized`: Invalid or expired JWT token
- `403 Forbidden`: Insufficient permissions for requested resource
- `422 Unprocessable Entity`: Validation error with proper format (as above)

### Task Management Endpoints

#### GET /todos
**Description**: Retrieve all user's todo items with filtering, search, and pagination

**Request**:
- Method: GET
- Path: `/todos`
- Query Parameters:
  - `skip`: number (optional, default: 0) - Pagination offset
  - `limit`: number (optional, default: 20, max: 100) - Page size
  - `completed`: boolean (optional) - Filter by completion status
  - `priority`: string (optional) - Filter by priority (low, medium, high)
  - `search`: string (optional) - Search in title/description
  - `sort_by`: string (optional, default: "created_at") - Sort field (created_at, priority, title)
  - `sort_order`: string (optional, default: "desc") - Sort direction (asc, desc)

**Response**:
- `200 OK`:
  ```json
  {
    "items": [
      {
        "id": "string",
        "title": "string (1-500 chars)",
        "description": "string (optional)",
        "completed": "boolean",
        "priority": "'low' | 'medium' | 'high'",
        "tags": "string (comma-separated, optional)",
        "user_id": "string",
        "created_at": "ISO 8601 datetime string",
        "updated_at": "ISO 8601 datetime string"
      }
    ],
    "total": "number",
    "skip": "number",
    "limit": "number"
  }
  ```
- `401 Unauthorized`: Invalid or expired JWT token

#### POST /todos
**Description**: Create a new todo item

**Request**:
- Method: POST
- Path: `/todos`
- Headers:
  - `Authorization: Bearer {jwt_token}`
  - `Content-Type: application/json`
- Body:
  ```json
  {
    "title": "string (1-500 chars)",
    "description": "string (optional, max 5000 chars)",
    "priority": "'low' | 'medium' | 'high' (optional, default: 'medium')",
    "tags": "string (comma-separated, optional, max 10 tags)",
    "completed": "boolean (optional, default: false)"
  }
  ```

**Response**:
- `201 Created`:
  ```json
  {
    "id": "string",
    "title": "string",
    "description": "string (optional)",
    "completed": "boolean",
    "priority": "'low' | 'medium' | 'high'",
    "tags": "string (optional)",
    "user_id": "string",
    "created_at": "ISO 8601 datetime string",
    "updated_at": "ISO 8601 datetime string"
  }
  ```
- `400 Bad Request`: Validation error (improper format)
- `401 Unauthorized`: Invalid or expired JWT token
- `422 Unprocessable Entity`: Validation error with proper format (as above)

#### PUT /todos/{id}
**Description**: Update an existing todo item

**Request**:
- Method: PUT
- Path: `/todos/{id}`
- Headers:
  - `Authorization: Bearer {jwt_token}`
  - `Content-Type: application/json`
- Body (partial update):
  ```json
  {
    "title": "string (1-500 chars) (optional)",
    "description": "string (optional)",
    "priority": "'low' | 'medium' | 'high' (optional)",
    "tags": "string (comma-separated, optional)",
    "completed": "boolean (optional)"
  }
  ```

**Response**:
- `200 OK`:
  ```json
  {
    "id": "string",
    "title": "string",
    "description": "string (optional)",
    "completed": "boolean",
    "priority": "'low' | 'medium' | 'high'",
    "tags": "string (optional)",
    "user_id": "string",
    "created_at": "ISO 8601 datetime string",
    "updated_at": "ISO 8601 datetime string"
  }
  ```
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Invalid or expired JWT token
- `404 Not Found`: Todo item not found
- `422 Unprocessable Entity`: Validation error with proper format

#### DELETE /todos/{id}
**Description**: Delete a todo item

**Request**:
- Method: DELETE
- Path: `/todos/{id}`
- Headers:
  - `Authorization: Bearer {jwt_token}`

**Response**:
- `204 No Content`: Successfully deleted
- `401 Unauthorized`: Invalid or expired JWT token
- `404 Not Found`: Todo item not found

#### POST /todos/{id}/toggle
**Description**: Toggle the completion status of a todo item

**Request**:
- Method: POST
- Path: `/todos/{id}/toggle`
- Headers:
  - `Authorization: Bearer {jwt_token}`

**Response**:
- `200 OK`:
  ```json
  {
    "id": "string",
    "completed": "boolean",
    "updated_at": "ISO 8601 datetime string"
  }
  ```
- `401 Unauthorized`: Invalid or expired JWT token
- `404 Not Found`: Todo item not found

## Error Response Format

All error responses follow a consistent format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_ERROR_CODE"
}
```

### Specific Error Codes
- `TOKEN_EXPIRED`: JWT token has expired
- `INVALID_CREDENTIALS`: Authentication credentials are invalid
- `VALIDATION_ERROR`: Request body validation failed
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `PERMISSION_DENIED`: Insufficient permissions to access resource
- `SERVER_ERROR`: Internal server error occurred

## Authentication

### JWT Token Format
- Algorithm: HS256
- Expiration: 30 minutes (configurable)
- Claims:
  - `sub`: User ID (string)
  - `email`: User email (string)
  - `exp`: Expiration timestamp (number)
  - `iat`: Issued at timestamp (number)

### Token Storage
- Frontend: Stored in localStorage (with secure options) or httpOnly cookies
- Included in requests as: `Authorization: Bearer {token}`

## Data Validation

### Todo Item Validation
- `title`: Required, 1-500 characters
- `description`: Optional, max 5000 characters
- `priority`: Enum of 'low', 'medium', 'high'
- `completed`: Boolean (true/false)
- `tags`: Optional, comma-separated string, max 10 tags
- `user_id`: String, references authenticated user

### User Validation
- `email`: Required, valid email format, unique
- `password`: Required, minimum 8 characters
- `name`: Required, 1-255 characters

## Security Considerations

### Input Sanitization
- All user inputs are validated against defined schemas
- SQL injection prevention through parameterized queries
- XSS prevention through framework auto-escaping
- Rate limiting on authentication endpoints (5 attempts per minute per IP)

### Authentication Flow
1. User registers with email, password, and name
2. Password is hashed using bcrypt (12+ rounds)
3. User receives JWT token on successful login
4. JWT token is required for all protected endpoints
5. Token is validated on each protected request
6. User can only access their own resources (user isolation enforced)

## API Versioning
- Current version: 1.0.0
- Version specified in FastAPI app definition
- Breaking changes will increment major version
- Backwards-compatible changes increment minor version