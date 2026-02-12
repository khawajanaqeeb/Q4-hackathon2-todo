# Phase 3: AI Chatbot Todo Application - Backend

FastAPI backend for the AI chatbot todo application. Processes natural language messages via OpenAI Chat Completions API with function calling, executes task operations through MCP tools, and manages conversations.

## Tech Stack

- **Framework**: FastAPI 0.109
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon Serverless)
- **AI**: OpenAI Chat Completions API with function calling
- **MCP**: Model Context Protocol for tool orchestration
- **Auth**: JWT with bcrypt password hashing
- **Migrations**: Alembic
- **Rate Limiting**: slowapi
- **Testing**: pytest + pytest-asyncio

## Setup

1. **Create virtual environment**
   ```bash
   cd phase3-chatbot/backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Required variables in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@host/database?sslmode=require
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=sk-...
   CORS_ORIGINS=http://localhost:3000
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the server**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

API docs available at http://localhost:8000/docs

## API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | Login and get JWT token |
| GET | `/auth/verify` | Yes | Verify current session |
| POST | `/auth/logout` | Yes | Logout |

### Chat
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/chat/{user_id}` | Yes | Send message to AI chatbot |
| GET | `/api/chat/{user_id}/conversations` | Yes | List user's conversations |
| GET | `/api/chat/{user_id}/conversations/{id}` | Yes | Get conversation messages |
| DELETE | `/api/chat/{user_id}/conversations/{id}` | Yes | Delete a conversation |

### Todos
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/todos` | Yes | Get user's todos |
| POST | `/api/todos` | Yes | Create todo |
| PUT | `/api/todos/{id}` | Yes | Update todo |
| PATCH | `/api/todos/{id}/complete` | Yes | Toggle completion |
| DELETE | `/api/todos/{id}` | Yes | Delete todo |

### MCP Tools
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/mcp/tools` | Yes | List registered MCP tools |
| POST | `/api/mcp/tools/invoke` | Yes | Invoke an MCP tool |

### Health
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Health check |

## Architecture

```
Request Flow (Chat):

User message
  → POST /api/chat/{user_id}
  → AgentRunner.process_natural_language()
      ├── Local detection (greetings/help) → instant response
      ├── OpenAI Chat Completions + function calling → parsed intent
      └── Keyword fallback parser → parsed intent (if OpenAI unavailable)
  → McpIntegrationService.invoke_tool()
      └── TodoTools (create/list/complete/update/delete)
  → ChatService.process_user_message()
      └── Save to DB (conversation + messages)
  → Response with confirmation
```

### Key Services

| Service | File | Purpose |
|---------|------|---------|
| AgentRunner | `services/agent_runner.py` | NLP intent parsing via OpenAI function calling |
| ChatService | `services/chat_service.py` | Conversation and message persistence |
| McpIntegrationService | `services/mcp_integration.py` | MCP tool invocation and routing |
| TodoTools | `tools/todo_tools.py` | Task CRUD operations |
| AuditService | `services/audit_service.py` | Operation audit logging |

### Database Models

| Model | Table | Primary Key |
|-------|-------|-------------|
| User | `users` | `id` (UUID string) |
| Task | `todos` | `id` (auto-increment int) |
| Conversation | `conversations` | `id` (auto-increment int) |
| Message | `messages` | `id` (auto-increment int) |
| McpTool | `mcp_tools` | `id` (auto-increment int) |
| ApiKey | `api_keys` | `id` (auto-increment int) |
| AuditLog | `audit_logs` | `id` (auto-increment int) |

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Deployment

### Railway/Render

1. Set root directory: `phase3-chatbot/backend`
2. Add environment variables: `DATABASE_URL`, `OPENAI_API_KEY`, `SECRET_KEY`, `CORS_ORIGINS`
3. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
