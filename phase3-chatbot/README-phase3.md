# Phase 3: Todo AI Chatbot

This directory contains the implementation for the AI-powered chatbot functionality that allows users to manage their todo lists through natural language conversations.

## Architecture

The Phase 3 implementation follows a multi-agent architecture with real OpenAI integration:

- **Router Agent**: Analyzes user intent and routes to appropriate specialized agents
- **Real OpenAI API**: Uses official OpenAI API with gpt-4o-mini model
- **Shared Utilities**: Common functions for JWT handling, history loading, etc.

## Components

### Router Agent
- Located in `backend/agents/router_agent.py`
- Uses REAL OpenAI models (gpt-4o-mini) for cost-effective processing
- Implements handoff pattern to delegate tasks to specialized agents
- Contains the exact system prompt specified in requirements
- Makes real API calls to OpenAI servers (consumes OpenAI credits)

### Specialized Agents
- `add_task_agent.py`: Handles adding new tasks
- `list_tasks_agent.py`: Handles listing tasks
- `complete_task_agent.py`: Handles completing tasks
- `update_task_agent.py`: Handles updating tasks
- `delete_task_agent.py`: Handles deleting tasks

### Base Utilities
- Located in `backend/agents/base.py`
- Provides functions for loading conversation history
- Handles JWT user ID extraction from Better Auth
- Formats messages for OpenAI consumption

### Chat Endpoint
- Located in `backend/routers/chat_router.py`
- Provides `/api/{user_id}/chat` endpoint
- Stateless design with database history loading
- Integrates with existing authentication system
- REAL functionality - every request makes actual OpenAI API call

## Setup

To run the Phase 3 chatbot functionality:

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. Required environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key (REAL API calls consume credits)
   - `DATABASE_URL`: PostgreSQL connection string for Neon
   - `BETTER_AUTH_SECRET`: Your Better Auth secret
   - `JWT_SECRET_KEY`: Secret key for JWT token signing
   - `PHASE2_BACKEND_PATH`: Path to Phase 2 backend (default: ./phase2-fullstack/backend)

4. Configuration Notes:
   - The system uses a custom Phase 3 settings configuration that extends Phase 2 settings
   - Phase 3 includes additional environment variables while maintaining compatibility with Phase 2
   - The configuration allows extra environment variables to prevent Pydantic validation errors
   - Phase 2 functionality remains unchanged and continues to work as expected

## How to Run Phase 3 Chatbot

### Running the Server
Start the server:
```bash
cd phase3-chatbot
uvicorn backend.main_phase3:app --reload --host 0.0.0.0 --port 8000
```

Or with the main runner:
```bash
cd phase3-chatbot
python -c "from backend.main_phase3 import app; print('Application loaded successfully')"
```

For deployment:
```bash
cd phase3-chatbot
uvicorn backend.main_phase3:app --host 0.0.0.0 --port $PORT
```

### API Usage

Once running, you can interact with the chat endpoint:

#### 1. Add Task
```bash
curl -X POST "http://localhost:8000/api/1/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

Expected response: `"Added: Buy groceries"`

#### 2. List Tasks
```bash
curl -X POST "http://localhost:8000/api/1/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
```

Expected response: `"I found 2 tasks for you: 1. Buy groceries, 2. Complete project"`

#### 3. Complete Task
```bash
curl -X POST "http://localhost:8000/api/1/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark task 1 as done"}'
```

Expected response: `"Task 1 marked as complete!"`

#### 4. Update Task
```bash
curl -X POST "http://localhost:8000/api/1/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Update task 2 title to Important Meeting"}'
```

Expected response: `"Updated task 2: title to 'Important Meeting'"`

#### 5. Delete Task
```bash
curl -X POST "http://localhost:8000/api/1/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Delete task 1"}'
```

Expected response: `"Deleted task 1."`

### Multi-Turn Test Example
Here's a sequence showing the full CRUD loop:

1. Add task: `"Add a task to prepare presentation"`
2. List tasks: `"Show my tasks"` → Should show the new task
3. Complete task: `"Mark task 1 as done"`
4. List tasks: `"Show my tasks"` → Should show the task as completed

## Important Notes

- This implementation makes REAL API calls to OpenAI servers
- Each chat interaction consumes OpenAI credits
- The system expects a real PostgreSQL database (Neon) with proper schema
- JWT authentication is verified against the existing Phase II system
- Conversation history is loaded from and stored to the database (placeholder implementation)

## Integration

The chat endpoint is designed to work with the existing Phase II backend models and authentication system. It follows the same user isolation patterns and security practices as the rest of the application.

## Note: Uses native OpenAI API for reliable performance

This implementation uses native OpenAI API to ensure reliable performance and access to the latest AI capabilities.