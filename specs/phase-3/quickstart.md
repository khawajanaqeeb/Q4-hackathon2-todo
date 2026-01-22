# Quickstart Guide: Phase 3 Enhancement

**Feature**: Phase 3 Copy and Enhancement
**Created**: 2026-01-22

## Development Setup

### Prerequisites
- Python 3.13+
- Node.js 20+
- uv (Python package manager)
- OPENAI_API_KEY
- Git

### Initial Setup

1. **Phase 3 directory structure already exists**
   The phase3-chatbot directory with backend and frontend is already set up.

2. **Install backend dependencies**
   ```bash
   cd phase3-chatbot/backend
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd phase3-chatbot/frontend-chatkit
   npm install
   ```

4. **Configure environment variables**
   ```bash
   # In phase3-chatbot/.env
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_URL=postgresql://user:password@localhost/dbname
   SECRET_KEY=your_secret_key
   ```

5. **Run the backend**
   ```bash
   cd phase3-chatbot/backend
   uv run uvicorn main_phase3:app --reload --port 8000
   ```

6. **Run the frontend**
   ```bash
   cd phase3-chatbot/frontend-chatkit
   npm run dev
   ```

## Adding MCP Tools

1. **Create MCP tools directory**
   ```bash
   mkdir -p phase3-chatbot/backend/mcp/tools
   ```

2. **Create task operation tools**
   ```bash
   touch phase3-chatbot/backend/mcp/tools/__init__.py
   touch phase3-chatbot/backend/mcp/tools/task_tools.py
   ```

3. **Register MCP tools with OpenAI**
   - In your agent initialization code, register the task tools
   - Ensure JWT validation is performed for each tool call

## Running Tests

### Backend Tests
```bash
cd phase3-chatbot/backend
uv run pytest
```

### Frontend Tests
```bash
cd phase3-chatbot/frontend-chatkit
npm test
```

## Deployment

### Local Development
- Backend runs on http://localhost:8000
- Frontend runs on http://localhost:3000
- Chat interface available at http://localhost:3000/chat
- Use main_phase3.py to run the Phase 3 specific server

### Environment Variables
Required for Phase 3:
- `OPENAI_API_KEY` - OpenAI API key for chat functionality
- `DATABASE_URL` - PostgreSQL database connection string
- `SECRET_KEY` - JWT signing key
- `NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL` - Base URL for chat API calls

## Key Directories
- `phase3-chatbot/backend/` - Phase 3 backend code
- `phase3-chatbot/frontend-chatkit/` - Phase 3 frontend code with OpenAI ChatKit
- `phase3-chatbot/backend/mcp/` - MCP tools implementation
- `phase3-chatbot/backend/agents/` - AI agent implementations
- `phase3-chatbot/frontend-chatkit/app/chat/` - Chat interface page
