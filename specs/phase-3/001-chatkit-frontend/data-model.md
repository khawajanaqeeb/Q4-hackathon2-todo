# Data Model: OpenAI ChatKit Frontend for Phase 3 Todo AI Chatbot

## Overview
This document defines the data models and structures for the frontend components that will interact with the OpenAI ChatKit integration and Phase 3 backend API.

## Frontend State Models

### ChatSessionState
The state management structure for the chat interface.

**Fields**:
- `isLoading` (boolean): Indicates if the AI is processing a response
- `error` (string | null): Error message if an API call fails
- `userId` (number | null): The authenticated user's ID
- `userToken` (string | null): The JWT token for authentication
- `sessionId` (string | null): Unique session identifier for the chat

**Validation Rules**:
- `userId` must be a positive integer when authenticated
- `userToken` must be a valid JWT format when present
- `sessionId` should be a unique identifier for the current chat session

**Relationships**:
- Connected to user authentication state
- Associated with API communication state

### ApiResponse
The structure of responses received from the Phase 3 backend API.

**Fields**:
- `response` (string): The AI-generated response text
- `routing_decision` (string | null): Indicates if the request was routed to a specific agent
- `handoff` (boolean): Whether the request was handed off to another agent
- `timestamp` (Date): When the response was generated

**Validation Rules**:
- `response` must be a non-empty string
- `timestamp` must be a valid date/time

**Relationships**:
- Connected to the chat message history
- Associated with the original user request

## Authentication Models

### AuthState
The structure representing the user's authentication state.

**Fields**:
- `isLoggedIn` (boolean): Whether the user is currently authenticated
- `user` (UserInfo | null): User information if authenticated
- `token` (string | null): JWT token for API authentication
- `isLoading` (boolean): Whether auth status is being determined

**Validation Rules**:
- `token` must be a valid JWT when user is logged in
- `user` object must contain required fields (id, email) when logged in

**Relationships**:
- Connected to all API requests that require authentication
- Associated with the user ID used in backend API calls

### UserInfo
The structure of user information from the Better Auth system.

**Fields**:
- `id` (number): Unique user identifier
- `email` (string): User's email address
- `name` (string): User's display name
- `createdAt` (Date): When the account was created

**Validation Rules**:
- `id` must be a positive integer
- `email` must be a valid email format
- `name` must be a non-empty string

## API Communication Models

### ChatRequest
The structure of requests sent to the Phase 3 backend API.

**Fields**:
- `message` (string): The user's message to the AI
- `userId` (number): The ID of the authenticated user
- `timestamp` (Date): When the request was created

**Validation Rules**:
- `message` must be a non-empty string
- `userId` must be a positive integer
- `timestamp` must be a valid date/time

**Relationships**:
- Associated with the user's authentication state
- Connected to the response that will be received

### APIConfig
The configuration structure for API communications.

**Fields**:
- `baseUrl` (string): The base URL for the Phase 3 backend
- `headers` (Record<string, string>): Headers to include with requests
- `timeout` (number): Request timeout in milliseconds

**Validation Rules**:
- `baseUrl` must be a valid URL
- `headers` must include Authorization header when authenticated
- `timeout` must be a positive number

## Component Data Structures

### ChatMessage
The structure for individual messages in the chat interface.

**Fields**:
- `id` (string): Unique identifier for the message
- `role` ('user' | 'assistant'): Who sent the message
- `content` (string): The message content
- `timestamp` (Date): When the message was created
- `status` ('sent' | 'delivered' | 'error'): Delivery status

**Validation Rules**:
- `id` must be unique within the chat session
- `role` must be either 'user' or 'assistant'
- `content` must be a non-empty string
- `timestamp` must be a valid date/time

**State Transitions**:
- During creation: status = 'sent'
- After successful delivery: status = 'delivered'
- If delivery fails: status = 'error'

## Environment Configuration

### EnvVars
The structure of required environment variables.

**Fields**:
- `NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL` (string): Backend API base URL
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` (string): OpenAI domain verification key

**Validation Rules**:
- Both variables must be defined in the environment
- URLs must be valid and accessible
- Domain key must match the registered domain with OpenAI

**Relationships**:
- Used by API client configuration
- Required for OpenAI ChatKit component initialization