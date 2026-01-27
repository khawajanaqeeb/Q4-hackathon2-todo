# Phase 3 Chatbot Quickstart Guide

## Overview
This guide provides instructions for setting up and running the Phase 3 chatbot functionality while preserving all Phase 2 authentication behaviors.

## Prerequisites
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- PostgreSQL database (existing from Phase 2)
- OpenAI API key
- MCP server (to be implemented)

## Setup Instructions

### 1. Backend Setup
1. Navigate to the backend directory:
   ```
   cd phase3-chatbot/backend
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Update the following variables:
   OPENAI_API_KEY=your_openai_api_key
   MCP_SERVER_URL=your_mcp_server_url
   ```

4. Run database migrations (includes new chat tables):
   ```
   alembic upgrade head
   ```

5. Start the backend server:
   ```
   uvicorn main:app --reload --port 8000
   ```

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd phase3-chatbot/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   ```bash
   # Copy the example file
   cp .env.local.example .env.local

   # Update API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```
   npm run dev
   ```

### 3. MCP Server Setup
1. Initialize the MCP server that exposes todo operations as tools
2. Configure the MCP server to validate existing auth tokens
3. Connect the MCP server to the backend

## Key Features

### Chat Interface
- Access the chat interface at `/chat` route
- Natural language processing for todo operations
- Conversation history persistence

### Todo Operations via Chat
- Create todos: "Add a grocery shopping task"
- List todos: "Show my tasks for today"
- Update todos: "Mark task 'buy milk' as complete"
- Delete todos: "Remove the meeting reminder"

### Authentication Preservation
- All existing login/registration flows remain unchanged
- Protected routes continue to function as in Phase 2
- Token refresh and verification work identically to Phase 2

## Development Guidelines

### Adding New Chat Features
1. Ensure new features don't interfere with authentication flows
2. Use separate state management for chat and auth contexts
3. Validate user permissions through existing auth tokens
4. Persist chat data separately from auth data

### Testing
1. Verify all Phase 2 functionality remains intact
2. Test authentication preservation during chat interactions
3. Confirm no authentication loops are created
4. Validate MCP tool functionality with proper auth validation

## Troubleshooting

### Authentication Issues
- Ensure the auth token is properly passed to chat API calls
- Check that chat operations don't trigger unnecessary auth verification
- Verify middleware continues to protect routes as in Phase 2

### Chat Functionality Issues
- Confirm MCP server is running and connected
- Verify OpenAI API key is properly configured
- Check database connections for chat data persistence