# Phase 3: AI Chatbot Todo Application

AI-powered chatbot that lets users manage todos through natural language. Built on top of the Phase 2 full-stack application with added chat capabilities, OpenAI integration, and MCP tool orchestration.

## Tech Stack

- **Frontend**: Next.js 16.1 (App Router, Turbopack) with TypeScript and Tailwind CSS
- **Backend**: FastAPI with SQLModel ORM
- **AI**: OpenAI Chat Completions API with function calling
- **MCP**: Model Context Protocol for task tool orchestration
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT with httpOnly cookies via Next.js API proxy

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Frontend (Next.js 16.1 / Vercel)                   │
│  ├── /dashboard      Task management UI             │
│  ├── /chat           AI chat interface               │
│  └── /api/auth/[...] Cookie-based auth proxy         │
└────────────────────┬────────────────────────────────┘
                     │ httpOnly cookies
┌────────────────────▼────────────────────────────────┐
│  Backend API (FastAPI)                               │
│  ├── /auth/*         Registration, login, verify     │
│  ├── /api/chat/*     Chat + AI agent processing      │
│  ├── /api/todos/*    CRUD todo endpoints             │
│  └── /api/mcp/*      MCP tool management             │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────────┐
        ▼            ▼                ▼
   PostgreSQL    OpenAI API      MCP Tools
   (Neon DB)     (Chat Completions  (create, list,
                  + function        complete, update,
                  calling)          delete tasks)
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (or Neon account)
- OpenAI API key

### Backend

```bash
cd phase3-chatbot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env (DATABASE_URL, OPENAI_API_KEY, SECRET_KEY)
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd phase3-chatbot/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start dev server
npm run dev
```

Frontend: http://localhost:3000 | Backend: http://localhost:8000 | API docs: http://localhost:8000/docs

## Project Structure

```
phase3-chatbot/
├── backend/
│   ├── src/
│   │   ├── api/               # API endpoints
│   │   │   ├── auth.py        # Registration, login, verify, logout
│   │   │   ├── chat.py        # Chat message processing
│   │   │   ├── todos.py       # Todo CRUD
│   │   │   ├── mcp.py         # MCP tool management
│   │   │   └── api_keys.py    # API key management
│   │   ├── models/            # SQLModel database models
│   │   ├── services/          # Business logic
│   │   │   ├── agent_runner.py    # OpenAI Chat Completions + function calling
│   │   │   ├── chat_service.py    # Conversation management
│   │   │   ├── mcp_integration.py # MCP tool invocation
│   │   │   └── audit_service.py   # Audit logging
│   │   ├── tools/             # MCP tool implementations
│   │   │   └── todo_tools.py  # Task CRUD via MCP
│   │   └── dependencies/      # Auth middleware
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   └── requirements.txt
│
├── frontend/
│   ├── app/                   # Next.js App Router pages
│   │   ├── api/auth/[...path] # Auth proxy (cookie management)
│   │   ├── api/chat/[userId]  # Chat API proxy
│   │   ├── dashboard/         # Task dashboard
│   │   ├── chat/              # AI chat page
│   │   ├── login/             # Login page
│   │   └── register/          # Registration page
│   ├── components/
│   │   ├── ChatInterface.tsx  # Chat UI component
│   │   └── Navigation.tsx     # App navigation
│   ├── context/               # Auth & theme context
│   ├── lib/                   # API clients
│   └── types/                 # TypeScript types
│
└── README.md
```

## Features

### AI Chat Interface
- Natural language task management (create, list, complete, update, delete)
- Instant local detection for greetings and help (zero latency)
- OpenAI function calling for intent parsing (single API call)
- Keyword-based fallback when OpenAI is unavailable
- Conversation history with context

### Task Management
- Full CRUD with priority, tags, search, filter, sort
- Dashboard UI with traditional form-based management
- Real-time sync between chat actions and task list

### Authentication
- Cookie-based auth (httpOnly, secure)
- Next.js API proxy handles token management transparently
- Route protection via middleware
- Rate limiting on auth endpoints

### MCP Integration
- 7 registered tools: create, list, update, complete, delete, search, get details
- Tool invocation via MCP integration service
- Audit logging for all operations

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login (returns JWT) |
| GET | `/auth/verify` | Verify session |
| POST | `/auth/logout` | Logout |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/{user_id}` | Send message to chatbot |
| GET | `/api/chat/{user_id}/conversations` | List conversations |
| GET | `/api/chat/{user_id}/conversations/{id}` | Get conversation messages |
| DELETE | `/api/chat/{user_id}/conversations/{id}` | Delete conversation |

### Todos
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos` | Get user's todos |
| POST | `/api/todos` | Create todo |
| PUT | `/api/todos/{id}` | Update todo |
| PATCH | `/api/todos/{id}/complete` | Toggle completion |
| DELETE | `/api/todos/{id}` | Delete todo |

## Testing

```bash
# Backend
cd backend && pytest tests/ -v --cov=src

# Frontend
cd frontend && npm test
```

## Deployment

### Backend (Railway/Render)
1. Set root directory: `phase3-chatbot/backend`
2. Add env vars: `DATABASE_URL`, `OPENAI_API_KEY`, `SECRET_KEY`, `CORS_ORIGINS`
3. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Set root directory: `phase3-chatbot/frontend`
2. Add env var: `NEXT_PUBLIC_API_URL` (deployed backend URL)
3. Deploy

## License

MIT
