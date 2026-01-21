# OpenAI ChatKit Frontend for Phase 3 Todo AI Chatbot

This is the frontend implementation for the Phase 3 Todo AI Chatbot, featuring an OpenAI ChatKit interface for natural language todo management.

## Features

- Natural language interaction with AI assistant for todo management
- Secure authentication using Better Auth from Phase 2
- Responsive design for desktop and mobile
- Real-time chat interface
- User identification display for debugging

## Prerequisites

- Node.js 18+
- npm or yarn package manager
- Access to Phase 3 backend API
- OpenAI account with domain verification enabled
- Better Auth session from Phase 2 system

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd phase3-chatbot/frontend-chatkit
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Configure environment variables by creating a `.env.local` file:
   ```env
   NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL=http://localhost:8000
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-openai-domain-key
   ```

4. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. Open your browser to `http://localhost:3000/chat` to access the chat interface.

## Key Features

### Authentication Integration
- The application automatically checks for Better Auth session
- If no session exists, user will be redirected to login
- JWT token is attached to all backend API requests

### OpenAI ChatKit Configuration
- The ChatKit component is loaded with the configured backend URL
- User ID is extracted from the authenticated session
- Authentication token is passed to the ChatKit component

## Environment Configuration

- `NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL`: Points to your Phase 3 backend
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: Required for OpenAI's domain verification

## Development Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run linter

## Common Issues and Solutions

### Issue: OpenAI Domain Verification Error
**Solution**: Ensure your domain is added to the OpenAI domain allowlist at https://platform.openai.com/settings/organization/security/domain-allowlist

### Issue: Authentication Failure
**Solution**: Verify that Better Auth session is properly configured and the user is logged in

### Issue: Backend API Connection Error
**Solution**: Check that the `NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL` is pointing to the correct Phase 3 backend URL and that the backend is running

## Project Structure

```
frontend-chatkit/
├── app/
│   └── chat/
│       └── page.tsx                 # Main chat page component
├── components/
│   └── ChatInterface.tsx           # Custom wrapper for ChatKit component
├── lib/
│   ├── auth.ts                     # Authentication utilities
│   └── api.ts                      # API client utilities
├── hooks/
│   └── useAuth.ts                  # Custom authentication hook
├── .env.local                      # Local environment variables
├── next.config.js                  # Next.js configuration
├── package.json                    # Dependencies including @openai/chatkit
├── tsconfig.json                   # TypeScript configuration
└── README.md                       # This file
```