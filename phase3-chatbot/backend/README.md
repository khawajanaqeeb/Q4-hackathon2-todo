# Phase III: AI Chatbot Todo Application - Backend

This is the backend for the AI-powered chatbot todo application. It provides APIs for managing todos through natural language commands using OpenAI's API and MCP (Model Context Protocol) tools.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLModel ORM)
- **AI Integration**: OpenAI API
- **MCP Integration**: Model Context Protocol for task operations
- **Authentication**: JWT-based
- **Testing**: pytest

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd phase3-chatbot/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your `DATABASE_URL`, `OPENAI_API_KEY`, `SECRET_KEY`, and other configurations.

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, API documentation is available at:
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Features

- Natural language processing for todo management
- Task creation, listing, updating, completion, and deletion via chat
- Conversation history management
- User authentication and authorization
- MCP integration for task operations
- Error handling and graceful degradation

## Endpoints

- `POST /chat/{user_id}` - Send a message to the chatbot
- `GET /chat/{user_id}/conversations` - Get user's conversations
- `GET /chat/{user_id}/conversations/{conversation_id}` - Get messages in a conversation
- `DELETE /chat/{user_id}/conversations/{conversation_id}` - Delete a conversation
- `GET /health` - Health check endpoint

## Architecture

The application follows a layered architecture:
1. **API Layer**: FastAPI handlers for chat endpoints
2. **Service Layer**: Business logic for chat processing and AI integration
3. **Data Layer**: SQLModel models and database operations
4. **External Services**: OpenAI API and MCP server