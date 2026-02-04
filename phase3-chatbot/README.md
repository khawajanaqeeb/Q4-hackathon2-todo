# Phase 3: AI Chatbot Integration

This phase implements an AI-powered chatbot for todo management with MCP integration, featuring enhanced authentication safeguards to prevent memory exhaustion during development.

## Tech Stack

- **Frontend**: Next.js 16+ (App Router) with TypeScript and Tailwind CSS
- **Backend**: FastAPI with SQLModel ORM for type-safe database operations
- **AI Framework**: OpenAI Agents SDK
- **Chatbot UI**: OpenAI ChatKit
- **MCP Server**: Official MCP SDK (Python)
- **State Management**: Database-backed (stateless server)
- **Authentication**: JWT-based auth with circuit breaker and memory safeguards

## Authentication Safeguards

The application implements a secure authentication flow with safeguards against memory exhaustion issues that can occur during development with Turbopack.

### Authentication Architecture

- **Frontend Authentication**: Uses a unified auth proxy at `/api/auth/[...path]/route.ts` that handles all authentication requests
- **Token Management**: Tokens are stored in both localStorage and cookies with proper security settings
- **Verification Flow**: Authentication verification is performed via the `/api/auth/verify` endpoint
- **Circuit Breaker**: Implemented to prevent infinite loops during authentication verification
- **Request Counting**: Tracks verification attempts to prevent abuse
- **Origin Tracking**: Monitors where authentication requests originate from

### Development Safeguards

The system includes several safeguards specifically designed to prevent the memory exhaustion issues that were occurring during development:

1. **Request Limiting**: Maximum 3 verification attempts per minute per path
2. **Circuit Breaker**: Trips after 3 failures and resets after 30 seconds
3. **Memory Monitoring**: Tracks memory usage during authentication operations
4. **Loop Detection**: Identifies potential recursive authentication calls
5. **Turbopack Optimization**: Special handling for hot reloads to prevent state inconsistency
6. **Depth Tracking**: Monitors the depth of authentication verification calls to prevent infinite recursion
7. **State Management**: Proper authentication state management to prevent recursive verification attempts

### Security Measures

- Secure cookie settings with HttpOnly and SameSite attributes
- Proper token validation and refresh mechanisms
- Rate limiting for authentication endpoints
- Protection against token replay attacks
- Verification attempt limiting to prevent brute force attacks

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Git

### Backend Setup (Required First)

```bash
cd phase3-chatbot/backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# The .env file is already configured for local development
# Ensure CORS_ORIGINS includes http://localhost:3000

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd phase3-chatbot/frontend

# Install dependencies (if not already installed)
npm install

# The .env.local file is already configured for local development:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

### Authentication Flow

1. Backend authentication endpoints are working correctly
2. Frontend proxy at `/api/auth/[...path]` forwards requests to backend
3. Registration, login, and verification all tested and working
4. Authentication tokens are properly handled via cookies

✅ **Authentication system is fully functional for local development**

## Troubleshooting

### Common Issues

If experiencing authentication issues during development:

1. Check the browser console for authentication-related errors
2. Verify that the API server is running and accessible
3. Clear authentication tokens from localStorage if needed
4. Restart the development server if authentication state becomes inconsistent

### Production Authentication Setup

For Vercel deployment, you need to configure cross-origin resource sharing properly:

1. **Backend CORS Configuration**: Ensure your Railway backend allows requests from your Vercel domain
2. **Frontend Environment Variables**: Set NEXT_PUBLIC_API_URL to your Railway backend URL in Vercel dashboard
3. **Redeployment**: Remember to redeploy both backend and frontend after configuration changes

See [AUTH_SETUP_INSTRUCTIONS.md](AUTH_SETUP_INSTRUCTIONS.md) for detailed setup instructions.

### Memory Issues During Development

If you encounter memory exhaustion during development:

1. The system has built-in safeguards that should prevent infinite loops
2. Check the console for messages about verification attempts
3. Look for circuit breaker trips that indicate potential issues
4. Verify that hot reloads aren't causing authentication state problems

### Authentication Flow Debugging

Enable detailed logging by setting `NEXT_PUBLIC_DEBUG_AUTH=true` in your environment to get detailed information about authentication flows and potential issues.

## Project Structure

```
phase3-chatbot/
├── backend/               # FastAPI backend service
│   ├── src/              # Python source code
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── dependencies/# Auth and other dependencies
│   ├── tests/            # Backend tests
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # Next.js frontend
│   ├── app/             # Next.js App Router pages
│   ├── components/      # React components
│   ├── lib/             # Utilities and API clients
│   │   └── auth/        # Authentication-specific code
│   ├── src/             # Source files
│   │   └── lib/         # Libraries
│   │       └── auth/    # Authentication utilities
│   ├── middleware.ts    # Route protection
│   └── package.json     # Node dependencies
│
└── README.md            # This file
```

## Features

### Authentication Safeguards (New in Phase 3)
- ✅ Circuit breaker pattern to prevent infinite loops
- ✅ Request counting to limit verification attempts
- ✅ Memory monitoring during authentication
- ✅ Origin tracking for request monitoring
- ✅ Depth tracking to prevent recursion
- ✅ Hot reload handling for Turbopack stability
- ✅ Development-specific safeguards

### AI Chatbot Integration
- ✅ Natural language processing for todo operations
- ✅ MCP integration for enhanced capabilities
- ✅ State management for conversation context
- ✅ Enhanced UI for chat interactions

## Development Workflow

1. **Start Backend**: Run the backend server with `uvicorn`
2. **Start Frontend**: Run the frontend with `npm run dev`
3. **Authentication**: Secure login flow with safeguards
4. **Chat Interaction**: Natural language todo management
5. **Debugging**: Built-in safeguards prevent common memory issues

## Testing

### Frontend Tests
```bash
cd frontend
npm run test:coverage
```

## Documentation

- See `specs/phase-3/` for detailed specifications
- API contracts in `specs/phase-3/contracts/`
- Setup guide in `specs/phase-3/quickstart.md`

## License

MIT