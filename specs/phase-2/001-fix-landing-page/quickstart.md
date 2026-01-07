# Quickstart Guide: Fix Auth Proxy Error and Create Modern Landing Page

## Overview
This guide provides quick setup instructions for the authentication proxy fix and modern landing page implementation. The feature addresses a Next.js App Router error where `params` is treated as a Promise in catch-all routes and creates a professional landing page with sample task table display.

## Prerequisites
- Node.js 18+ (Node 20+ recommended for React 19 compatibility)
- Python 3.11+
- Neon PostgreSQL account (no local SQLite files allowed)
- Git for version control
- Operating System: Cross-platform support (Windows, macOS, Linux)

## Development Setup

### 1. Clone and Navigate to Project
```bash
cd phase2-fullstack/backend
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (IMPORTANT: Use Neon PostgreSQL URL, NO local SQLite files)
cat > .env << EOF
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
EOF

# Run database migrations
alembic upgrade head

# Start backend server (IMPORTANT: Run from backend/ directory)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
# Navigate to frontend
cd phase2-fullstack/frontend

# Install dependencies
npm install

# Create environment file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start development server
npm run dev
```

## Key Features

### Authentication Proxy Fix
- Fixed Next.js App Router error where `params` Promise wasn't properly awaited in catch-all routes
- Updated `/api/auth/proxy/[...path]/route.ts` to properly handle dynamic parameters
- Ensured API requests are correctly forwarded to backend with proper authentication

### Modern Landing Page
- Professional landing page with welcome message and value proposition
- Responsive task table displaying sample todo items with columns (ID, Title, Description, Priority, Tags, Status, Created Date)
- Search functionality for filtering sample tasks
- Filter sidebar with status, priority, and tags filters
- Sortable column headers with visual indicators
- Priority color coding (high: red, medium: yellow, low: green)
- Tag chips display with hover effects
- Action buttons for each task row
- Mobile-responsive design with card layout on small screens

## File Structure
```
phase2-fullstack/
├── backend/
│   └── app/
│       └── api/
│           └── auth/
│               └── proxy/
│                   └── [...path]/
│                       └── route.ts  # Fixed proxy route with proper Promise handling
├── frontend/
│   ├── app/
│   │   └── page.tsx               # Modern landing page with table display
│   ├── components/
│   │   └── todos/
│   │       ├── TodoTable.tsx      # Responsive task table component
│   │       └── TodoCard.tsx       # Mobile card view component
│   └── types/
│       └── todo.ts                # Todo type definitions
```

## Running Tests
### Backend Tests
```bash
# From backend directory
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests
```bash
# From frontend directory
npm run test -- --coverage
```

## API Endpoints Used
- `GET /api/auth/proxy/[...path]` - Fixed proxy route that properly handles dynamic parameters
- `GET /todos` - Fetch sample todo data for landing page display
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'app'**
   - Ensure you're in the `phase2-fullstack/backend/` directory before running uvicorn
   - Verify `app/__init__.py` exists (even if empty)
   - Verify `app/main.py` contains the FastAPI instance as 'app'

2. **Hydration Errors**
   - Check for client-side only code running during server-side rendering
   - Ensure consistent date formatting between server and client
   - Verify no random values are generated during SSR

3. **Middleware Deprecation Warning**
   - The warning "middleware file convention is deprecated" refers to newer Next.js patterns
   - Current implementation follows established proxy pattern for auth

4. **422 Unprocessable Entity Errors**
   - Verify Pydantic schemas match frontend payload exactly
   - Check that all required fields are provided in requests
   - Ensure data types match expected schema types

### Environment Variables
Make sure these variables are set correctly:
- `NEXT_PUBLIC_API_URL` - Points to your backend API (should be http://localhost:8000 for local dev)
- `DATABASE_URL` - Points to your Neon PostgreSQL instance (no local files)
- `SECRET_KEY` - Should be a 256-bit secret for JWT signing