# Chat Endpoint Specification for Phase 3 Todo AI Chatbot

## Overview

This document specifies the API contract for the chat endpoint that enables natural language interaction with the todo management system. The endpoint accepts user messages and returns AI-generated responses through the multi-agent system.

## Endpoint Definition

### POST /api/{user_id}/chat

**Purpose**: Process natural language messages from users and return AI-generated responses for todo management tasks.

#### Parameters

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| user_id | integer | Path | Yes | The ID of the authenticated user |

#### Headers

| Header | Required | Value | Description |
|--------|----------|-------|-------------|
| Authorization | Yes | Bearer {jwt_token} | JWT token for user authentication |
| Content-Type | Yes | application/json | Request body format |

#### Request Body

```json
{
  "message": "string",
  "conversation_id": "string (optional)",
  "metadata": {
    "client_type": "string (optional)",
    "timestamp": "string (ISO 8601, optional)"
  }
}
```

**Fields**:
- `message`: The natural language message from the user (required, min 1 character, max 10000 characters)
- `conversation_id`: Optional conversation identifier to continue an existing conversation (UUID format)
- `metadata`: Optional metadata about the request (free-form object)

#### Response

**Success Response (200 OK)**:

```json
{
  "response": "string",
  "conversation_id": "string",
  "routing_decision": "string | null",
  "handoff": "boolean",
  "timestamp": "string (ISO 8601)",
  "tool_calls": [
    {
      "name": "string",
      "arguments": "object",
      "result": "object (if completed)"
    }
  ]
}
```

**Fields**:
- `response`: The AI-generated response to the user's message
- `conversation_id`: The ID of the conversation (newly created or continued)
- `routing_decision`: The specialized agent that was invoked (null if direct response)
- `handoff`: Whether the request was handed off to a specialized agent
- `timestamp`: ISO 8601 timestamp of the response
- `tool_calls`: Array of tool calls made during processing (may be empty)

**Error Responses**:

| Status Code | Error Code | Description | Response Body |
|-------------|------------|-------------|---------------|
| 400 | INVALID_INPUT | Invalid request body format | `{ "detail": "string" }` |
| 401 | AUTHENTICATION_REQUIRED | Missing or invalid JWT token | `{ "detail": "string" }` |
| 403 | ACCESS_DENIED | User ID mismatch or insufficient permissions | `{ "detail": "string" }` |
| 404 | USER_NOT_FOUND | Specified user_id does not exist | `{ "detail": "string" }` |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests from user | `{ "detail": "string" }` |
| 500 | INTERNAL_ERROR | Server-side processing error | `{ "detail": "string" }` |
| 503 | SERVICE_UNAVAILABLE | AI service temporarily unavailable | `{ "detail": "string" }` |

#### Example Requests and Responses

**Example 1: Add a new task**

_Request_:
```json
{
  "message": "Add a task to buy groceries tomorrow"
}
```

_Response_:
```json
{
  "response": "I've added the task 'buy groceries' to your list.",
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "routing_decision": "add_task_agent",
  "handoff": true,
  "timestamp": "2024-01-20T10:30:00Z",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {
        "user_id": 123,
        "title": "buy groceries",
        "due_date": "2024-01-21T00:00:00Z"
      },
      "result": {
        "success": true,
        "task_id": 456,
        "message": "Task 'buy groceries' created successfully"
      }
    }
  ]
}
```

**Example 2: List pending tasks**

_Request_:
```json
{
  "message": "What tasks do I have pending?"
}
```

_Response_:
```json
{
  "response": "You have 3 pending tasks:\n1. Complete project proposal (high priority)\n2. Schedule team meeting (medium priority)\n3. Review quarterly reports (medium priority)",
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "routing_decision": "list_tasks_agent",
  "handoff": true,
  "timestamp": "2024-01-20T10:31:00Z",
  "tool_calls": [
    {
      "name": "list_tasks",
      "arguments": {
        "user_id": 123,
        "status": "pending"
      },
      "result": {
        "success": true,
        "tasks": [
          {
            "id": 123,
            "title": "Complete project proposal",
            "priority": "high",
            "completed": false
          },
          {
            "id": 124,
            "title": "Schedule team meeting",
            "priority": "medium",
            "completed": false
          },
          {
            "id": 125,
            "title": "Review quarterly reports",
            "priority": "medium",
            "completed": false
          }
        ],
        "total_count": 3
      }
    }
  ]
}
```

**Example 3: Direct response (no task intent)**

_Request_:
```json
{
  "message": "Hello! How are you today?"
}
```

_Response_:
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you manage your tasks today?",
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "routing_decision": null,
  "handoff": false,
  "timestamp": "2024-01-20T10:32:00Z",
  "tool_calls": []
}
```

## Authentication and Authorization

### JWT Token Validation
- All requests must include a valid JWT token in the Authorization header
- Token must be signed with the same secret as the Phase II authentication system
- User ID in token must match the user_id in the path parameter

### User Isolation
- Each request is processed within the context of the authenticated user
- Database queries are filtered by the authenticated user's ID
- Users cannot access data belonging to other users

## Rate Limiting

### Limits
- Per-user rate limiting: 60 requests per minute
- Per-IP rate limiting: 100 requests per minute
- Burst allowance: Up to 10 requests can exceed the limit before enforcement

### Enforcement
- Exceeded requests return 429 status code
- Response includes retry-after header with suggested wait time
- Limits reset at the beginning of each minute

## Conversation Management

### Session Handling
- If no conversation_id is provided, a new conversation is created
- If conversation_id is provided, the existing conversation is continued
- Conversation history is loaded and passed to the AI agent for context
- Updated conversation history is saved after each interaction

### Context Window
- Conversation history is limited to the last 20 exchanges to maintain performance
- Older messages are archived but remain accessible for reference
- Context is managed to stay within AI model token limits

## Error Handling

### Client-Side Errors (4xx)
- Invalid request format triggers 400 Bad Request
- Authentication failures trigger 401 Unauthorized
- Permission issues trigger 403 Forbidden
- Resource not found triggers 404 Not Found

### Server-Side Errors (5xx)
- AI service unavailability triggers 503 Service Unavailable
- Internal processing errors trigger 500 Internal Server Error
- Database connectivity issues trigger 500 Internal Server Error

### Error Response Format
All error responses follow this format:
```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_ERROR_CODE",
  "timestamp": "2024-01-20T10:30:00Z",
  "request_id": "unique identifier for the request"
}
```

## Performance Requirements

### Response Times
- 95th percentile response time: < 2 seconds
- 99th percentile response time: < 5 seconds
- Maximum response time: < 30 seconds (timeout)

### Availability
- Target uptime: 99.9%
- Planned maintenance windows communicated 48 hours in advance
- Failover mechanisms for AI service outages

## Monitoring and Logging

### Required Logs
- All requests and responses (with PII masked)
- Authentication attempts and results
- Error occurrences with stack traces
- Performance metrics per endpoint

### Metrics to Track
- Request volume per hour
- Error rates by type
- Average response time
- AI service utilization
- Database query performance