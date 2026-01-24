# Implementation Plan: Phase 3 – Todo AI Chatbot Core

## Summary
This plan outlines the implementation of the AI-powered chatbot core logic for the Todo application. The feature enables users to interact with their todo lists using natural language commands through an AI agent that maps user requests to MCP tools for task management operations.

## Technical Context
- **Architecture**: Stateless backend with conversation state stored in database
- **AI Integration**: OpenAI Agents SDK for natural language processing
- **Data Storage**: SQLModel ORM for conversation and message persistence
- **API Framework**: FastAPI for REST endpoints
- **Communication**: WebSocket for real-time chat interactions
- **Security**: JWT-based authentication for user identification

## Project Structure
```
phase3-chatbot/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── conversation.py      # Conversation entity
│   │   │   ├── message.py          # Message entity
│   │   │   └── todo.py             # Todo entity (extended)
│   │   ├── schemas/
│   │   │   ├── conversation.py     # Conversation schema
│   │   │   ├── message.py          # Message schema
│   │   │   └── chat.py             # Chat request/response schemas
│   │   ├── services/
│   │   │   ├── chat_service.py     # Core chatbot logic
│   │   │   ├── conversation_service.py # Conversation management
│   │   │   ├── mcp_integration.py  # MCP tools integration
│   │   │   └── ai_agent.py         # AI agent orchestration
│   │   ├── routers/
│   │   │   └── chat.py             # Chat endpoints
│   │   ├── dependencies/
│   │   │   └── chat_dependencies.py # Chat-specific dependencies
│   │   └── utils/
│   │       └── chat_utils.py       # Chat utilities
│   ├── tests/
│   │   └── test_chat.py            # Chat functionality tests
│   └── alembic/
│       └── versions/                # Migration scripts
└── frontend/
    └── components/
        └── ChatInterface.tsx        # Chat UI component
```

## Models Needed

### Conversation Model
- `id`: UUID primary key
- `user_id`: Foreign key to user
- `title`: String, nullable (auto-generated from first message)
- `created_at`: DateTime
- `updated_at`: DateTime
- `is_active`: Boolean (for soft deletion)

### Message Model
- `id`: UUID primary key
- `conversation_id`: Foreign key to conversation
- `role`: Enum (user/assistant/system)
- `content`: Text content of message
- `timestamp`: DateTime
- `metadata`: JSONB for additional data (tokens used, etc.)

## Services Needed

### AI Agent Service
- Initialize OpenAI Agent with appropriate tools
- Process user messages through AI agent
- Handle tool calls and responses
- Format responses for frontend

### MCP Integration Service
- Map natural language to MCP tool calls
- Handle task creation, listing, completion, update, deletion
- Validate user permissions
- Return structured responses

### Conversation Service
- Create new conversations
- Retrieve conversation history
- Update conversation state
- Manage message threading

### Chat Service
- Handle incoming chat requests
- Validate user input
- Coordinate between AI agent and MCP services
- Format responses with confirmation messages
- Handle error scenarios gracefully

## Endpoints Needed

### POST `/chat/send`
- **Purpose**: Send a message to the chatbot
- **Request**: `{message: string, conversation_id?: string}`
- **Response**: `{message: string, conversation_id: string, timestamp: datetime}`
- **Auth**: JWT required

### GET `/chat/conversations`
- **Purpose**: List user's conversations
- **Response**: Array of conversation objects
- **Auth**: JWT required

### GET `/chat/conversations/{conversation_id}/messages`
- **Purpose**: Get messages for a specific conversation
- **Response**: Array of message objects
- **Auth**: JWT required

### POST `/chat/conversations`
- **Purpose**: Create a new conversation
- **Response**: New conversation object
- **Auth**: JWT required

## Implementation Phases

### Phase 1: Foundation
1. Create Conversation and Message models
2. Set up database migrations
3. Implement basic conversation service
4. Create chat router with basic endpoints

### Phase 2: AI Integration
1. Integrate OpenAI Agents SDK
2. Implement MCP tools mapping
3. Create AI agent service
4. Connect AI service to chat endpoints

### Phase 3: Frontend Integration
1. Create ChatInterface component
2. Implement WebSocket connection
3. Add real-time message display
4. Implement loading states and error handling

### Phase 4: Polish and Testing
1. Add comprehensive tests
2. Implement error handling and validation
3. Add confirmation messages
4. Performance optimization
5. Security hardening

## Key Dependencies
- `openai`: OpenAI API client
- `fastapi`: Web framework
- `sqlmodel`: ORM for database operations
- `pydantic`: Data validation
- `websockets`: Real-time communication
- `python-jose`: JWT handling

## Security Considerations
- Input validation for all user messages
- Rate limiting for API endpoints
- Proper JWT token validation
- Sanitize AI-generated responses
- Limit conversation length to prevent abuse

## Performance Considerations
- Implement caching for frequently accessed data
- Optimize database queries with proper indexing
- Monitor AI API usage and costs
- Implement pagination for conversation history

## Testing Strategy
- Unit tests for individual services
- Integration tests for AI agent functionality
- End-to-end tests for complete chat flows
- Mock OpenAI API for testing
- Performance tests for concurrent users