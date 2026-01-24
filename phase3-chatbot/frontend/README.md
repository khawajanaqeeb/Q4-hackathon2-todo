# Phase III: AI Chatbot Todo Application - Frontend

This is the frontend for the AI-powered chatbot todo application. It provides a conversational interface for managing todos through natural language commands.

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks

## Setup

1. **Navigate to frontend directory**
   ```bash
   cd phase3-chatbot/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` with your backend URL:

   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

## Components

- `ChatInterface.tsx` - Main chat interface component
- API client for communicating with the backend

## Features

- Real-time chat interface for natural language task management
- Loading states and error handling
- Conversation history display
- Typing indicators for AI responses
- Responsive design for all device sizes

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run linter

## API Integration

The frontend communicates with the backend through the following endpoints:
- `POST /chat/{user_id}` - Send messages to the chatbot
- `GET /chat/{user_id}/conversations` - Get user's conversations
- `GET /chat/{user_id}/conversations/{conversation_id}` - Get messages in a conversation
- `DELETE /chat/{user_id}/conversations/{conversation_id}` - Delete a conversation