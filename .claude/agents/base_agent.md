# Base Agent Utilities Specification

## Overview
The Base Agent Utilities provide shared functionality for all agents in the AI Todo Chatbot system. This includes common utilities for database loading, JWT user extraction, and other shared services.

## Purpose
To provide a consistent foundation for all agents in the system, ensuring standardized access to common services like database connections, user authentication, and conversation history management.

## Components

### Database Loading Utilities
- Functions to load conversation history from DB (Conversation + Message models)
- Session management for SQLModel database connections
- Error handling for database operations
- Connection pooling and optimization

### JWT User Extraction
- Utility functions to extract authenticated user_id from JWT tokens
- Token validation and verification
- User context management
- Integration with existing Better Auth JWT verification system

### Shared Agent Services
- Common logging and monitoring utilities
- Error handling and exception management
- Configuration loading and environment variable access
- Model selection and management utilities

## Technology Stack
- ORM: SQLModel for database operations
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth JWT verification (integrated with existing system)
- Framework: Compatible with OpenAI Agents SDK

## Integration Points
- Used by all specialized agents in the system
- Connects to existing authentication infrastructure
- Provides database access for conversation history
- Supports the router agent's requirements for user context and history loading

## Environment Variables
- OPENAI_API_KEY (for agent model access)
- BETTER_AUTH_SECRET (for JWT verification, already in place)
- DATABASE_URL (for SQLModel connections)
- NEON_DATABASE_URL (specific to Neon PostgreSQL)