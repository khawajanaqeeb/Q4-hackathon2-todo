# Phase 3 Backend Contracts

## Overview
This document defines the API contracts for the backend services supporting chatbot authentication and integration. All endpoints must follow RESTful principles and return appropriate HTTP status codes.

## Authentication Endpoints

### POST /api/auth/login
Authenticate user and establish session

**Request:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (200):**
```json
{
  "success": true,
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string"
  },
  "message": "Login successful"
}
```

**Response (401):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

**Cookies Set:**
- `session_token`: HTTP-only, secure JWT token

### POST /api/auth/register
Register new user account

**Request:**
```json
{
  "username": "string (required, unique)",
  "email": "string (required, unique, valid email)",
  "password": "string (required, min 8 chars)"
}
```

**Response (201):**
```json
{
  "success": true,
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string"
  },
  "message": "Registration successful"
}
```

**Response (400):**
```json
{
  "success": false,
  "error": "Validation error message"
}
```

**Response (409):**
```json
{
  "success": false,
  "error": "Username or email already exists"
}
```

**Cookies Set:**
- `session_token`: HTTP-only, secure JWT token

### GET /api/auth/verify
Verify current user session

**Request Headers:**
```
Cookie: session_token=<jwt-token>
```

**Response (200):**
```json
{
  "authenticated": true,
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string"
  }
}
```

**Response (401):**
```json
{
  "authenticated": false,
  "error": "Invalid or expired session"
}
```

### POST /api/auth/logout
Terminate current user session

**Request Headers:**
```
Cookie: session_token=<jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

**Cookies Cleared:**
- `session_token`: Set to expire immediately

## Todo Management Endpoints (Authenticated)

### GET /api/todos
Retrieve user's todo items

**Request Headers:**
```
Cookie: session_token=<jwt-token>
```

**Response (200):**
```json
{
  "todos": [
    {
      "id": "integer",
      "title": "string",
      "description": "string (optional)",
      "completed": "boolean",
      "priority": "string (low|medium|high)",
      "due_date": "string (ISO 8601 format, optional)",
      "tags": "array of strings",
      "created_at": "string (ISO 8601 format)",
      "updated_at": "string (ISO 8601 format)"
    }
  ]
}
```

**Response (401):**
```json
{
  "error": "Authentication required"
}
```

### POST /api/todos
Create new todo item

**Request Headers:**
```
Cookie: session_token=<jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "priority": "string (low|medium|high, default: medium)",
  "due_date": "string (ISO 8601 format, optional)",
  "tags": "array of strings (optional)"
}
```

**Response (201):**
```json
{
  "todo": {
    "id": "integer",
    "title": "string",
    "description": "string",
    "completed": false,
    "priority": "string",
    "due_date": "string (ISO 8601 format)",
    "tags": "array of strings",
    "created_at": "string (ISO 8601 format)",
    "updated_at": "string (ISO 8601 format)"
  }
}
```

## Chatbot Endpoints

### POST /api/chat/messages
Send message to chatbot and receive response

**Request Headers:**
```
Cookie: session_token=<jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "string (required)",
  "conversation_id": "string (optional, for continuing conversations)"
}
```

**Response (200):**
```json
{
  "response": "string",
  "conversation_id": "string",
  "actions": [
    {
      "type": "string (create_todo|update_todo|delete_todo|list_todos)",
      "data": "object with action-specific data"
    }
  ]
}
```

### GET /api/chat/conversations
Get user's chat conversation history

**Request Headers:**
```
Cookie: session_token=<jwt-token>
```

**Response (200):**
```json
{
  "conversations": [
    {
      "id": "string",
      "title": "string",
      "created_at": "string (ISO 8601 format)",
      "updated_at": "string (ISO 8601 format)"
    }
  ]
}
```

## Error Responses

All error responses follow this standard format:

**Generic Error (4xx/5xx):**
```json
{
  "error": "Descriptive error message",
  "code": "error_code_string"
}
```

## Security Requirements

### Authentication
- All endpoints except `/api/auth/login`, `/api/auth/register` require valid session
- Session validation must occur before processing request
- Expired sessions must return 401 status

### Rate Limiting
- Login attempts: 5 per minute per IP
- API requests: 100 per minute per user
- Chat requests: 50 per minute per user

### CORS Policy
- Allow credentials: true
- Allowed origins: frontend domain(s) only
- Allowed methods: GET, POST, PUT, DELETE
- Allowed headers: Content-Type, Authorization, X-Requested-With

## Database Models

### User Model
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True, nullable=False))
    email: str = Field(sa_column=Column(String, unique=True, nullable=False))
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    todos: List[Todo] = Relationship(back_populates="user")
```

### Todo Model
```python
class Todo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(default="medium", sa_column=Column(String(20)))
    due_date: Optional[datetime] = None
    tags: Optional[str] = None  # JSON string of tags array
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key
    user_id: int = Field(foreign_key="user.id")

    # Relationships
    user: User = Relationship(back_populates="todos")
```

### Conversation Model
```python
class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship()
    messages: List[Message] = Relationship(back_populates="conversation")
```

### Message Model
```python
class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id")
    role: str = Field(sa_column=Column(String(20)))  # "user" or "assistant"
    content: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```