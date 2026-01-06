# Phase II: Full-Stack Web Application

Transform the Phase I console-based todo application into a production-ready full-stack web application with multi-user support, authentication, persistent cloud storage, and responsive UI.

## Tech Stack

- **Frontend**: Next.js 16+ (App Router) with TypeScript and Tailwind CSS
- **Backend**: FastAPI with SQLModel ORM for type-safe database operations
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT-based auth with bcrypt password hashing
- **Deployment**: Vercel (frontend) + Railway/Render (backend)

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Neon PostgreSQL account (free tier)
- Git

### Backend Setup

```bash
cd phase2-fullstack/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000
API docs at http://localhost:8000/docs

### Frontend Setup

```bash
cd phase2-fullstack/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your backend URL

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

### Docker Setup (Optional)

```bash
cd phase2-fullstack
docker-compose up --build
```

This starts all services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

## Project Structure

```
phase2-fullstack/
├── backend/               # FastAPI backend service
│   ├── app/              # Python package
│   │   ├── __init__.py  # REQUIRED for package structure
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── config.py    # Settings from environment
│   │   ├── database.py  # SQLModel engine
│   │   ├── models/      # Database table definitions
│   │   ├── schemas/     # Request/response schemas
│   │   ├── routers/     # API endpoints
│   │   ├── dependencies/# Auth and DB dependencies
│   │   └── utils/       # Security helpers
│   ├── tests/           # Backend tests (pytest)
│   ├── alembic/         # Database migrations
│   └── requirements.txt # Python dependencies
│
├── frontend/            # Next.js frontend
│   ├── app/            # Next.js App Router pages
│   ├── components/     # React components
│   ├── lib/            # API client and utilities
│   ├── types/          # TypeScript interfaces
│   ├── context/        # Auth state management
│   ├── middleware.ts   # Route protection
│   └── package.json    # Node dependencies
│
└── docker-compose.yml  # Local development orchestration
```

## Features

### Basic Features (MVP)
- ✅ User Registration & Login
- ✅ Add New Task
- ✅ View Task List
- ✅ Update Task
- ✅ Delete Task
- ✅ Mark Task Complete/Incomplete

### Intermediate Features
- ✅ Task Priorities (Low, Medium, High)
- ✅ Task Tags (max 10 per task)
- ✅ Search Tasks by Title
- ✅ Filter by Status/Priority/Tags
- ✅ Sort by Date/Priority/Title

### Technical Features
- ✅ JWT Authentication
- ✅ User Isolation (users only see their tasks)
- ✅ Responsive Design (mobile-first)
- ✅ Cloud Database (Neon PostgreSQL)
- ✅ Production Deployment
- ✅ Comprehensive Testing (80% backend, 70% frontend coverage)

## Development Workflow

1. **Register**: Navigate to /register, create account
2. **Login**: Login with credentials, receive JWT token
3. **Dashboard**: View/manage personal todo list
4. **CRUD Operations**: Add, edit, delete, toggle tasks
5. **Search & Filter**: Find tasks by keywords or filters
6. **Logout**: Clear session and return to login

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test:coverage
```

### E2E Tests
```bash
cd frontend
npx playwright test
```

## Deployment

### Backend (Railway/Render)
1. Create new project from GitHub repo
2. Set root directory: `/phase2-fullstack/backend`
3. Add environment variables (DATABASE_URL, SECRET_KEY, etc.)
4. Deploy (auto-detects Dockerfile)

### Frontend (Vercel)
1. Import GitHub repository
2. Set root directory: `phase2-fullstack/frontend`
3. Framework: Next.js
4. Add environment variable: NEXT_PUBLIC_API_URL
5. Deploy

## Documentation

- See `specs/001-fullstack-web-app/` for detailed specifications
- API contracts in `specs/001-fullstack-web-app/contracts/`
- Setup guide in `specs/001-fullstack-web-app/quickstart.md`

## License

MIT
