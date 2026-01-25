# Todo Chat Assistant Frontend

This is the frontend for the Todo Chat Assistant application that integrates with ChatKit and MCP tools for natural language todo management.

## Features

- Natural language chat interface for todo management
- Real-time messaging with streaming responses
- Todo list synchronization with chat actions
- Command suggestions for guided interactions
- Dark/light theme support
- Responsive design for desktop and mobile
- Accessibility compliant (WCAG 2.1 AA)

## Tech Stack

- React 18 with TypeScript
- Redux Toolkit for state management
- Tailwind CSS for styling
- WebSocket for real-time updates
- React Router for navigation
- Axios for API communication

## Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update environment variables in `.env` with your API endpoints

## Running the Application

Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`

## Building for Production

Create a production build:
```bash
npm run build
```

## Testing

Run the tests:
```bash
npm test
```

## Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (irreversible)

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── chat/          # Chat-specific components
│   │   ├── layout/        # Layout components
│   │   └── shared/        # Shared components
│   ├── pages/              # Page components
│   ├── services/           # API services and WebSocket
│   ├── hooks/              # Custom React hooks
│   ├── store/              # Redux store and slices
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   └── styles/             # Global styles
├── package.json
└── tsconfig.json
```

## Environment Variables

- `REACT_APP_CHAT_API_URL` - Base URL for chat API
- `REACT_APP_MCP_API_URL` - Base URL for MCP tools API
- `REACT_APP_WEBSOCKET_URL` - WebSocket URL for real-time updates

## API Integration

The frontend communicates with:
- Chat API at `/chat/:user_id` endpoints
- MCP tools at `/api/mcp/tools/*` endpoints
- WebSocket for real-time message streaming

## Accessibility

This application follows WCAG 2.1 AA guidelines:
- Proper ARIA labels and roles
- Keyboard navigation support
- Sufficient color contrast
- Screen reader compatibility

## Performance

- Virtualized message lists for long conversations
- Optimized rendering with React.memo
- Efficient state management with Redux Toolkit
- Lazy loading where appropriate