# Phase II Quickstart Guide

**Date**: 2026-01-03
**Feature**: Phase II Full-Stack Web Application
**Spec**: [specs/phase-2/spec.md](./spec.md)

## Overview

This guide provides step-by-step instructions to set up, run, and test the Phase II Full-Stack Todo Application locally. The application consists of a Next.js frontend and FastAPI backend with Neon PostgreSQL database.

## Prerequisites

### System Requirements
- **Node.js**: 18+ (Node 20+ recommended for React 19 compatibility)
- **Python**: 3.11+ (for FastAPI backend)
- **Git**: For version control
- **npm/yarn**: Package managers (npm comes with Node.js)
- **Neon Account**: For PostgreSQL database (free tier available)

### Optional Development Tools
- **Docker**: For containerized development (if using docker-compose)
- **PostgreSQL Client**: For direct database access (e.g., psql, pgAdmin)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/khawajanaqeeb/Q4-hackathon2-todo.git
cd Q4-hackathon2-todo
cd phase2-fullstack
```

### 2. Backend Setup

#### Create Python Virtual Environment
```bash
cd backend
python -m venv venv

# On Windows
venv\\Scripts\\activate
# On macOS/Linux
source venv/bin/activate
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the `backend/` directory:

```bash
# Use Neon PostgreSQL URL (get from your Neon dashboard)
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Generate a 256-bit secret key
SECRET_KEY=your-256-bit-secret-key-here

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Configuration
DEBUG=true
CORS_ORIGINS=http://localhost:3000
```

To generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Run Database Migrations
```bash
alembic upgrade head
```

#### Start Backend Server
```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Node Dependencies
```bash
# Open a new terminal/command prompt
cd phase2-fullstack/frontend

# Install dependencies
npm install
```

#### Configure Frontend Environment
Create a `.env.local` file in the `frontend/` directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Start Frontend Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Testing the Application

### 1. Verify Backend
- Open `http://localhost:8000/docs` in your browser
- You should see the FastAPI auto-generated documentation
- Test the `/health` endpoint to verify the backend is running

### 2. Verify Frontend
- Open `http://localhost:3000` in your browser
- You should see the application homepage
- Navigate to `/register` to test user registration

### 3. End-to-End Testing
1. Navigate to `http://localhost:3000/register`
2. Create a new user account with valid email and password
3. Verify you can log in at `http://localhost:3000/login`
4. Once logged in, go to the dashboard to create, view, update, and delete todo items
5. Test all features:
   - Add new tasks with title, description, priority, and tags
   - Mark tasks as complete/incomplete
   - Filter tasks by completion status, priority, and tags
   - Sort tasks by different criteria
   - Search for tasks by title

## Common Issues and Troubleshooting

### Backend Issues

#### ModuleNotFoundError: No module named 'app'
**Cause**: Not running uvicorn from the correct directory or missing `__init__.py`
**Solution**:
1. Ensure you're in the `phase2-fullstack/backend/` directory
2. Verify `backend/app/__init__.py` exists (can be empty)
3. Verify `backend/app/main.py` contains `app = FastAPI(...)`

#### Database Connection Issues
**Symptoms**: Connection errors, SSL issues
**Solution**:
1. Verify your Neon DATABASE_URL is correct
2. Ensure SSL mode is set to `require` in the connection string
3. Check that your Neon project allows connections from your IP

#### Environment Variables Not Loading
**Solution**:
1. Ensure `.env` file is in the `backend/` directory
2. Verify environment variable names match exactly
3. Restart the server after making changes to `.env`

### Frontend Issues

#### API Connection Errors
**Symptoms**: Network errors, CORS issues
**Solution**:
1. Verify `NEXT_PUBLIC_API_URL` points to your running backend
2. Check that the backend CORS settings allow `http://localhost:3000`
3. Ensure both frontend and backend are running

#### React 19 Compatibility Issues
**Symptoms**: Runtime errors, deprecated API warnings
**Solution**:
1. Verify you have the correct testing libraries installed
2. Check that `@testing-library/react@^15.0.0` or latest is installed
3. Update any deprecated React patterns

### Windows-Specific Issues

#### Virtual Environment Activation
Use PowerShell or Command Prompt instead of Git Bash:
```cmd
# In Command Prompt
venv\\Scripts\\activate.bat

# In PowerShell
venv\\Scripts\\Activate.ps1
```

#### Path Issues
Use Windows-style paths and ensure line endings are consistent (CRLF vs LF).

## Development Workflow

### Running Tests

#### Backend Tests
```bash
# From the backend directory
pytest tests/ -v --cov=app --cov-report=html
```

Target: 80%+ coverage

#### Frontend Tests
```bash
# From the frontend directory
npm run test -- --coverage
```

Target: 70%+ coverage

#### E2E Tests
```bash
# From the frontend directory
npx playwright test
```

### Database Migrations
When you make changes to the data model:
```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply the migration
alembic upgrade head
```

## Deployment Preparation

### Environment Configuration
For production deployment, ensure these environment variables are set:

**Backend (.env)**:
```
DATABASE_URL=your-neon-postgres-url
SECRET_KEY=your-production-secret
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.com
```

**Frontend (.env.local)**:
```
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

### Health Checks
The backend provides a health check endpoint at `GET /health` which returns:
```json
{
  "status": "healthy"
}
```

## Performance Considerations

### API Response Times
- Target: <200ms p95 for list queries
- Target: <100ms p95 for single-item queries
- Monitor with the provided performance metrics

### Frontend Performance
- Lighthouse performance: Target 90+
- Lighthouse accessibility: Target 95+
- Bundle optimization enabled by default with Next.js

## Security Notes

### JWT Tokens
- Tokens expire after 30 minutes (configurable)
- Secure storage in localStorage (for simplicity in Phase II)
- All API requests require Authorization header with Bearer token

### Rate Limiting
- Login attempts limited to 5 per minute per IP
- Configured in the backend dependencies

### Input Validation
- All user inputs validated at API boundaries
- SQL injection prevention via SQLModel parameterized queries
- XSS prevention via React auto-escaping

## Next Steps

After successful local setup:
1. Implement the features specified in the requirements
2. Run all tests to ensure functionality
3. Deploy to Vercel (frontend) and Railway/Render (backend)
4. Update the deployed URLs in your documentation

## Support

If you encounter issues:
1. Check the error logs in both frontend and backend consoles
2. Verify all environment variables are correctly set
3. Ensure your Neon database is active and accessible
4. Confirm all dependencies are installed correctly

## Middleware Migration

### Addressing Deprecation Warning
- **Issue**: "The 'middleware' file convention is deprecated. Please use 'proxy' instead."
- **Solution**: Migrate from middleware.ts to the new proxy pattern using API routes or server actions
- **Migration Steps**:
  - Replace middleware.ts with API route handlers in app/api/ directory
  - Use server actions for authentication checks instead of middleware
  - Implement route protection using server components in layout.tsx
  - Test all protected routes to ensure authentication still works