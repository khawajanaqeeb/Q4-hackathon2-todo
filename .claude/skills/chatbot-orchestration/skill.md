# Chatbot Orchestration Skill

## Overview
The Chatbot Orchestration skill coordinates agent interactions in the AI Todo Chatbot system. It manages the flow between different specialized agents and ensures proper routing and delegation.

## Purpose
To provide a centralized orchestration mechanism that enables seamless interaction between the Router Agent and specialized agents (add_task_agent, list_tasks_agent, complete_task_agent, delete_task_agent, update_task_agent).

## Capabilities
- Agent routing and delegation
- Conversation flow management
- State persistence across agent interactions
- Error handling and fallback procedures
- MCP tool schema coordination

## Integration Points
- Connects Router Agent to specialized agents
- Manages MCP tool schemas for inter-agent communication
- Coordinates database access for conversation history
- Integrates with JWT authentication for user context

## Technology Stack
- MCP Server: Official MCP SDK for inter-agent communication
- Framework: Compatible with OpenAI Agents SDK
- Database: Neon Serverless PostgreSQL via SQLModel
- Auth: Better Auth JWT verification

## Components
- Routing engine for agent delegation
- State management for multi-turn conversations
- Tool schema registry for MCP integration
- Error recovery mechanisms