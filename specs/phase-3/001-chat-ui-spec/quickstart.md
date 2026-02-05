# Quickstart Guide: Chat UI Implementation

## Prerequisites

- Node.js 18+ installed
- Access to backend chat API endpoints
- ChatKit conversation engine configured
- MCP tools for todo operations available
- Authentication system in place

## Setup

1. Clone the repository:
```bash
git clone https://github.com/khawajanaqeeb/Q4-hackathon2-todo
cd Q4-hackathon2-todo
```

2. Install dependencies:
```bash
cd frontend  # or wherever the frontend code resides
npm install
```

3. Configure environment variables:
```bash
# Copy environment template
cp .env.example .env

# Update with your backend API endpoints
REACT_APP_CHAT_API_URL=http://localhost:8000/chat
REACT_APP_MCP_API_URL=http://localhost:8000/api/mcp
```

## Development

1. Start the development server:
```bash
npm start
```

2. The chat UI will be available at `http://localhost:3000/chat`

## Key Components

- `ChatContainer`: Main wrapper for chat functionality
- `MessageList`: Displays conversation history
- `MessageInput`: Handles user input and submission
- `TodoPanel`: Synchronized todo list view
- `CommandSuggestions`: Contextual command recommendations

## API Integration Points

- POST `/chat/{user_id}`: Send messages to chatbot
- GET `/chat/{user_id}/conversations`: Get conversation history
- GET `/chat/{user_id}/conversations/{conversation_id}`: Get specific conversation
- POST `/api/mcp/tools/invoke`: Trigger MCP tool operations
- GET `/api/mcp/tools/available`: Get available tools list

## Testing

1. Unit tests:
```bash
npm test
```

2. End-to-end tests:
```bash
npm run test:e2e
```

## Building for Production

```bash
npm run build
```

## Architecture Notes

- UI follows thin-client pattern, deferring to ChatKit for conversation logic
- MCP tools handle all todo operations
- Real-time synchronization between chat and todo panel
- Responsive design for desktop, tablet, and mobile
- WCAG 2.1 AA accessibility compliance