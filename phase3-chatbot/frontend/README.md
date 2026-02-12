# Phase III: AI Chatbot Todo Application - Frontend

Next.js frontend for the AI-powered chatbot todo application. Users manage todos through natural language chat commands and a traditional dashboard UI.

## Tech Stack

- **Framework**: Next.js 16.1 (App Router, Turbopack)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context + Hooks
- **Testing**: Jest + React Testing Library + Playwright

## Prerequisites

- Node.js 18+
- Backend server running (default: `http://localhost:8000`)

## Setup

1. **Install dependencies**
   ```bash
   cd phase3-chatbot/frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env.local
   ```

   Set your backend URL in `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   npm run start
   ```

## Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── api/
│   │   ├── auth/[...path]/   # Auth proxy (login, register, verify, logout)
│   │   └── chat/[userId]/    # Chat API proxy
│   ├── chat/                 # AI Chat page
│   ├── dashboard/            # Task dashboard page
│   ├── login/                # Login page
│   ├── register/             # Registration page
│   ├── layout.tsx            # Root layout
│   ├── middleware.ts         # Route protection middleware
│   └── page.tsx              # Landing page
├── components/
│   ├── ChatInterface.tsx     # Main chat UI (messages, input, loading states)
│   ├── Navigation.tsx        # App navigation bar
│   └── Providers.tsx         # Context providers wrapper
├── context/
│   ├── AuthContext.tsx        # Authentication state management
│   └── ThemeContext.tsx       # Theme (light/dark) management
├── lib/
│   ├── api.ts                # Todo API client (CRUD operations)
│   ├── api-utils.ts          # Shared request utilities
│   └── chat-api.ts           # Chat API client
├── types/
│   ├── todo.ts               # Todo type definitions
│   └── user.ts               # User type definitions
└── tests/                    # Test files
```

## Features

- **AI Chat Interface**: Natural language task management (create, list, complete, update, delete tasks)
- **Task Dashboard**: Traditional CRUD UI with filtering, sorting, and priority management
- **Cookie-Based Auth**: Secure httpOnly cookie authentication via Next.js API proxy
- **Route Protection**: Middleware-based auth guards on `/dashboard` and `/chat` routes
- **Responsive Design**: Mobile-friendly layout

## Authentication

Authentication uses httpOnly cookies managed by the Next.js API proxy layer:

- `POST /api/auth/login` - Login (sets auth cookie)
- `POST /api/auth/register` - Register new account
- `GET /api/auth/verify` - Verify current session
- `POST /api/auth/logout` - Logout (clears cookie)

All API requests to the backend are proxied through `/api/auth/[...path]` which attaches the auth token automatically.

## Chat API

The chat interface communicates through:

- `POST /api/chat/{user_id}` - Send a message to the AI chatbot
- `GET /api/chat/{user_id}/conversations` - List conversations
- `GET /api/chat/{user_id}/conversations/{id}` - Get conversation messages
- `DELETE /api/chat/{user_id}/conversations/{id}` - Delete a conversation

### Supported Chat Commands

| Command | Example |
|---------|---------|
| Create task | "Add a task to buy groceries" |
| List tasks | "Show my tasks" |
| Complete task | "Mark task 3 as done" |
| Update task | "Update task 5 title to Review PR" |
| Delete task | "Delete task 2" |
| Help | "What can you do?" |

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run format` | Format code with Prettier |
| `npm run test` | Run Jest tests |
| `npm run test:coverage` | Run tests with coverage report |

## Deployment (Vercel)

1. Push your code to a Git repository
2. Import the project on [vercel.com](https://vercel.com)
3. Set the **Root Directory** to `phase3-chatbot/frontend`
4. Add environment variables:
   - `NEXT_PUBLIC_API_URL` - Your deployed backend URL
5. Deploy
