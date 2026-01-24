# Quickstart Guide: Phase 3 – Chat Core

## Overview
This guide provides instructions for setting up, configuring, and running the AI-powered todo chatbot core functionality.

## Prerequisites
- Python 3.11+
- PostgreSQL database (Neon Serverless recommended)
- OpenAI API key
- MCP server running and accessible

## Environment Setup

### 1. Clone the repository
```bash
git clone https://github.com/khawajanaqeeb/Q4-hackathon2-todo.git
cd Q4-hackathon2-todo
```

### 2. Create virtual environment and install dependencies
```bash
cd phase3-chatbot/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@host:port/database_name
OPENAI_API_KEY=your_openai_api_key_here
MCP_SERVER_URL=https://your-mcp-server-url.com
SECRET_KEY=your-secret-key-for-jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Database Setup

### 1. Run database migrations
```bash
alembic upgrade head
```

### 2. Initialize the database
```bash
python scripts/init_db.py
```

## Running the Application

### 1. Start the backend server
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. The chat API will be available at:
- Base URL: `http://localhost:8000/api`
- Chat endpoint: `POST /chat/{user_id}`
- Conversations endpoint: `GET /chat/{user_id}/conversations`

## API Usage Examples

### Sending a message to the chatbot
```bash
curl -X POST "http://localhost:8000/api/chat/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a new task to buy groceries"
  }'
```

### Retrieving conversation history
```bash
curl -X GET "http://localhost:8000/api/chat/123e4567-e89b-12d3-a456-426614174000/conversations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Configuration Options

### 1. Adjust rate limiting
Modify the rate limiter settings in `src/main.py`:
```python
# Current settings: 100 requests per hour per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per hour"])
```

### 2. Customize AI behavior
Adjust the AI agent settings in `src/services/agent_runner.py`:
- Temperature settings for creativity vs consistency
- Maximum tokens for response length
- System prompt for chatbot personality

## Testing

### Run unit tests
```bash
pytest tests/unit/
```

### Run integration tests
```bash
pytest tests/integration/
```

### Run contract tests
```bash
pytest tests/contract/
```

## Troubleshooting

### Common Issues:
1. **Database connection errors**: Verify DATABASE_URL is correct and database is accessible
2. **OpenAI API errors**: Check OPENAI_API_KEY is valid and has sufficient credits
3. **MCP server unreachable**: Verify MCP_SERVER_URL is correct and server is running
4. **JWT authentication errors**: Ensure tokens are properly generated and not expired

### Enable debug logging:
Add the following to your `.env` file:
```env
LOG_LEVEL=DEBUG
```

## Scaling Recommendations

### For increased load:
1. Use connection pooling for database connections
2. Implement caching for frequently accessed data
3. Consider using a message queue for heavy processing tasks
4. Implement read replicas for database if needed

## Security Notes

- Never expose API keys in client-side code
- Use HTTPS in production
- Validate all user inputs
- Implement proper rate limiting to prevent abuse
- Regularly rotate API keys and secret tokens