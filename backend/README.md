# Phase 3 Chatbot Authentication & Integration Backend

This backend implements secure authentication with JWT tokens and HTTP-only cookies for a chatbot-enabled todo application.

## Features

- User registration and authentication with secure JWT tokens
- HTTP-only cookie session management
- Todo management with CRUD operations
- Chatbot integration for natural language todo management
- Rate limiting to prevent abuse
- Secure password hashing with bcrypt
- Proper CORS configuration with credentials support

## Tech Stack

- FastAPI: Modern, fast web framework for building APIs with Python
- SQLModel: SQL databases for Python, combining SQLAlchemy and Pydantic
- Alembic: Database migration tool for SQLAlchemy
- OpenAI Agents SDK: Framework for building AI assistants
- slowapi: Rate limiting for FastAPI applications

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```
   SECRET_KEY=your-super-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DATABASE_URL=sqlite:///./todo_app.db
   FRONTEND_URL=http://localhost:3000
   ```

3. Run the application:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and create session
- `GET /api/auth/verify` - Verify current session
- `POST /api/auth/logout` - Logout and destroy session

### Todo Management
- `GET /api/todos` - Get user's todos
- `POST /api/todos` - Create a new todo
- `PUT /api/todos/{id}` - Update a todo
- `PATCH /api/todos/{id}/complete` - Mark todo as complete/incomplete
- `DELETE /api/todos/{id}` - Delete a todo

### Chat
- `POST /api/chat/messages` - Send message to chatbot
- `GET /api/chat/conversations` - Get user's conversations

## Security Features

- JWT tokens with HTTP-only cookies for secure session management
- Passwords hashed with bcrypt
- Rate limiting to prevent brute force attacks
- CORS configured to allow only trusted origins
- Input validation and sanitization