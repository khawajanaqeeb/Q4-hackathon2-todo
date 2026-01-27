# Phase 3 Chatbot Quickstart Guide v2

## Overview
This guide provides instructions for setting up and running the Phase 3 chatbot functionality while preserving all Phase 2 authentication behaviors. This version emphasizes the hard prerequisites: MCP tools and AI agents must be fully implemented before any chat features are considered complete.

## Prerequisites
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- PostgreSQL database (existing from Phase 2)
- OpenAI API key
- MCP server (to be implemented as HARD PREREQUISITE)

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

### 2. MCP Server Setup (HARD PREREQUISITE)
1. Initialize the MCP server that exposes todo operations as tools
2. Configure the MCP server to validate existing auth tokens
3. Connect the MCP server to the backend
4. Ensure all MCP tools are fully functional before proceeding
5. Verify that each MCP tool properly validates user authentication

### 3. AI Agent Configuration (HARD PREREQUISITE)
1. Configure OpenAI Agents SDK
2. Define system prompts for todo management
3. Connect AI agents to MCP tools
4. Verify natural language processing functionality
5. Ensure AI agents can properly utilize MCP tools

### 4. Frontend Setup
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

## Critical Prerequisites

### MCP Tools Completion
Before any chat functionality can be considered complete:
- All MCP tools must be fully implemented and tested
- Each tool must properly validate existing auth tokens
- All todo operations must be exposed through MCP tools
- MCP tools must operate within existing user authentication context

### AI Agent Configuration
Before any chat functionality can be considered complete:
- OpenAI Agents SDK must be fully configured
- AI agents must be connected to MCP tools
- Natural language processing must be functional
- AI agents must properly utilize MCP tools for todo operations

### Authentication Verification
Before frontend integration:
- All Phase 2 authentication behaviors must be verified as unchanged
- No authentication loops must be created during chat usage
- Chat operations must not interfere with auth lifecycle

## Development Guidelines

### MCP Tools First Approach
1. Implement all MCP tools before proceeding with chat features
2. Ensure each tool validates user authentication properly
3. Test MCP tools independently before integration
4. Verify all todo operations work through MCP tools

### AI Agent Integration
1. Connect AI agents to MCP tools after MCP tools are complete
2. Test AI agent functionality with MCP tools
3. Ensure natural language processing works properly
4. Verify AI agents respect user authentication boundaries

### Testing
1. Verify all Phase 2 functionality remains intact
2. Test authentication preservation during chat interactions
3. Confirm MCP tools work properly with auth validation
4. Validate AI agent integration with MCP tools
5. Test complete end-to-end chat functionality

## Troubleshooting

### MCP Tool Issues
- Ensure MCP server is running and connected
- Verify all MCP tools properly validate auth tokens
- Check that MCP tools operate within user authentication context

### AI Agent Issues
- Confirm OpenAI API key is properly configured
- Verify AI agents are connected to MCP tools
- Test natural language processing functionality

### Authentication Issues
- Ensure the auth token is properly passed to chat API calls
- Check that chat operations don't trigger unnecessary auth verification
- Verify middleware continues to protect routes as in Phase 2