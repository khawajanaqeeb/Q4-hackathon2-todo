# API Contracts: OpenAI ChatKit Frontend for Phase 3 Todo AI Chatbot

## Overview
This document defines the API contracts for the frontend components that interact with the Phase 3 backend API.

## Backend API Endpoints

### Chat Endpoint
The primary endpoint for chat interactions with the AI assistant.

**Endpoint**: `POST {baseUrl}/api/{user_id}/chat`

**Request Structure**:
- **Path Parameters**:
  - `user_id` (number): The authenticated user's ID
- **Headers**:
  - `Authorization` (string): Bearer token with JWT from Better Auth session
  - `Content-Type` (string): application/json
- **Body** (JSON):
  - `message` (string): The user's message to the AI assistant

**Example Request**:
```
POST http://localhost:8000/api/1/chat
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "Add a task to buy groceries"
}
```

**Response Structure**:
- **Status Code**: 200 OK
- **Body** (JSON):
  - `response` (string): The AI-generated response text
  - `routing_decision` (string | null): Agent type the request was routed to (e.g., "add_task_agent")
  - `handoff` (boolean): Whether the request was handed off to another agent
  - `timestamp` (string): ISO 8601 formatted timestamp

**Example Response**:
```
{
  "response": "I've added the task 'buy groceries' to your todo list.",
  "routing_decision": "add_task_agent",
  "handoff": true,
  "timestamp": "2026-01-22T02:30:00.000Z"
}
```

**Error Responses**:
- **401 Unauthorized**: Invalid or expired JWT token
- **403 Forbidden**: User ID in path doesn't match authenticated user
- **422 Validation Error**: Invalid request body format
- **500 Internal Server Error**: Server-side processing error

### Health Check Endpoint
Endpoint to verify backend API availability.

**Endpoint**: `GET {baseUrl}/health`

**Request Structure**:
- **Headers**:
  - `Authorization` (optional): Bearer token (not required for health check)

**Response Structure**:
- **Status Code**: 200 OK
- **Body** (JSON):
  - `status` (string): "healthy"
  - `service` (string): "Phase 3 Todo AI Chatbot"
  - `openai_api_configured` (boolean): Whether OpenAI API key is properly configured

**Example Response**:
```
{
  "status": "healthy",
  "service": "Phase 3 Todo AI Chatbot",
  "openai_api_configured": true
}
```

## Authentication API Contract

### Session Verification
Contract for verifying the Better Auth session.

**Method**: Client-side verification using Better Auth hooks

**Input**:
- Current session state from Better Auth

**Output**:
- `isLoggedIn` (boolean): Whether user is authenticated
- `user` (object | null): User information if authenticated
- `token` (string | null): JWT token for API requests

**Behavior**:
- If no valid session exists, redirect to login page
- If session exists, extract JWT token for API authentication
- Attach token to all backend API requests as `Authorization: Bearer {token}`

## Frontend-to-Component Contracts

### ChatKit Component Interface
Contract for integrating with OpenAI ChatKit component.

**Props**:
- `backendUrl` (string): Base URL for the backend API
- `userIdentifier` (string): Unique identifier for the authenticated user
- `tokenProvider` (function): Function to provide JWT token for authentication
- `onMessage` (function): Callback for handling new messages
- `onError` (function): Callback for handling errors

**Behavior**:
- Component handles all chat UI rendering and user interactions
- Component sends messages to backend via backendUrl
- Component manages conversation history and state
- Component calls onError callback when API errors occur

## Error Handling Contract

### Frontend Error States
Contract for handling different error scenarios in the frontend.

**Network Errors**:
- Display user-friendly error message
- Provide option to retry the request
- Log error details for debugging

**Authentication Errors**:
- Redirect to login page
- Clear any cached session data
- Show notification about authentication requirement

**AI Processing Errors**:
- Display message about temporary service unavailability
- Allow user to try again
- Gracefully degrade functionality

## Loading State Contract

### Frontend Loading States
Contract for handling loading states during AI processing.

**States**:
- `idle`: No ongoing requests
- `sending`: Message is being sent to backend
- `processing`: AI is processing the request
- `receiving`: Response is being received

**UI Behavior**:
- Show loading spinner during processing states
- Disable input during sending/processing
- Auto-scroll to bottom when new messages arrive
- Update UI based on current state