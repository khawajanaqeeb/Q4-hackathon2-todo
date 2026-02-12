# Quickstart Guide: Phase 3 Chatbot Enhancement

## Overview
This guide provides the essential steps to get the Phase 3 chatbot enhancement up and running.

## Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- PostgreSQL database (Neon recommended)
- OpenAI API key
- MCP SDK-compatible environment
- Existing Phase 2 application deployed

## Environment Setup

### Backend Configuration
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```env
   DATABASE_URL="postgresql://user:password@localhost/dbname"
   OPENAI_API_KEY="your-openai-api-key"
   SECRET_KEY="your-secret-key"
   ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   MCP_SERVER_PORT=8001
   ```

### Frontend Configuration
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables in `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL="http://localhost:8000"
   NEXT_PUBLIC_MCP_ENDPOINT="http://localhost:8001"
   ```

## Database Setup

1. Run the existing Phase 2 migrations to ensure base schema:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. The chatbot enhancement uses the same database as Phase 2 with additional conversation tables.

## Running the Application

### Backend Services
1. Start the main FastAPI server:
   ```bash
   cd backend
   uvicorn src.main:app --reload --port 8000
   ```

2. Start the MCP server in a separate terminal:
   ```bash
   cd backend
   python -m src.mcp_server
   ```

### Frontend Service
1. Start the Next.js development server:
   ```bash
   cd frontend
   npm run dev
   ```

## Key Endpoints

### Chat Endpoint
- **POST** `/chat`: Process chat messages and return AI response
- Requires authentication cookie
- Expects JSON with `message` and optional `conversation_id`

### MCP Endpoints
- **GET** `/mcp/manifest`: MCP server manifest
- **POST** `/mcp/tools`: MCP tool invocation endpoint

## Frontend Pages
- **Chat Interface**: Available at `/chat` route
- Uses existing authentication context
- Connects to backend chat endpoint

## Testing the Setup

1. Visit `http://localhost:3000` to access the frontend
2. Log in with existing credentials
3. Navigate to the chat page
4. Test basic conversation with the chatbot
5. Verify that todo operations work through the chat interface

## Troubleshooting

### Common Issues
- **Authentication failures**: Verify auth cookie is being sent correctly
- **MCP server not connecting**: Check MCP endpoint configuration
- **Database migration conflicts**: Run alembic migrations again

### Environment Variables
- Ensure all required environment variables are set
- Check that API keys are valid and have necessary permissions
- Verify database connection strings are correct

## Next Steps
1. Review the conversation data models in the database
2. Test the various MCP tools for todo operations
3. Experiment with different chat interactions
4. Review the API contracts for integration points