# Quickstart Guide: OpenAI ChatKit Frontend for Phase 3 Todo AI Chatbot

## Overview
This guide provides quick instructions for setting up and running the OpenAI ChatKit frontend for the Phase 3 Todo AI Chatbot.

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Access to Phase 3 backend API
- OpenAI account with domain verification enabled
- Better Auth session from Phase 2 system

## Setup Instructions

### 1. Clone and Navigate to Frontend Directory
```bash
cd phase3-chatbot/frontend-chatkit
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Configure Environment Variables
Create a `.env.local` file with the following variables:

```env
NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-openai-domain-key
```

### 4. Run the Development Server
```bash
npm run dev
# or
yarn dev
```

### 5. Access the Application
Open your browser to `http://localhost:3000/chat` to access the chat interface.

## Key Features Setup

### Authentication Integration
- The application will automatically check for Better Auth session
- If no session exists, user will be redirected to login
- JWT token will be attached to all backend API requests

### OpenAI ChatKit Configuration
- The ChatKit component will be loaded with the configured backend URL
- User ID will be extracted from the authenticated session
- Authentication token will be passed to the ChatKit component

## Development Workflow

### Running in Development Mode
```bash
npm run dev
```

### Building for Production
```bash
npm run build
npm start
```

### Environment Configuration
- `NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL`: Points to your Phase 3 backend
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: Required for OpenAI's domain verification

## Common Issues and Solutions

### Issue: OpenAI Domain Verification Error
**Solution**: Ensure your domain is added to the OpenAI domain allowlist at https://platform.openai.com/settings/organization/security/domain-allowlist

### Issue: Authentication Failure
**Solution**: Verify that Better Auth session is properly configured and the user is logged in

### Issue: Backend API Connection Error
**Solution**: Check that the `NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL` is pointing to the correct Phase 3 backend URL and that the backend is running

## Next Steps
- Customize the chat interface styling if needed
- Add additional error handling as required
- Test the integration with the Phase 3 backend API
- Deploy to your preferred hosting platform