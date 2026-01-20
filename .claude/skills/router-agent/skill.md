# Router Agent Skill

## Overview
The Router Agent Skill enables the central routing functionality for the AI Todo Chatbot. This skill handles intent classification and routes user requests to appropriate specialized agents.

## Purpose
To provide the core routing capability that analyzes user messages and conversation history, then decides which specialized agent should handle the request next.

## Capabilities
- Intent classification based on user input patterns
- Conversation history analysis for context-aware routing
- Integration with 5 specialized agents:
  - add_task_agent
  - list_tasks_agent
  - complete_task_agent
  - delete_task_agent
  - update_task_agent
- Direct response handling for unrecognized intents
- MCP tool schema preparation for future delegation

## Technology Stack
- AI Framework: OpenAI Agents SDK
- Model: gpt-4o (or latest available)
- MCP Server: Official MCP SDK (prepared for future integration)
- Integration: Works with existing FastAPI backend infrastructure

## Integration Points
- Connects to existing /api/{user_id}/chat endpoint
- Loads conversation history from DB (Conversation + Message models)
- Extracts authenticated user_id from JWT (uses existing auth system)
- Stores user messages and router responses in DB
- Prepares for future delegation to other agents via MCP tools

## System Prompt
```
You are the Router Agent for a personal todo list chatbot. Your only job is to analyze the user's message and the conversation history, then decide which specialized agent should handle it next.
Possible intents and routing:

add / create / remember / new task → route to "add_task_agent"
list / show / what do I have / pending / completed → route to "list_tasks_agent"
complete / done / finished / mark as done → route to "complete_task_agent"
delete / remove / cancel / get rid of → route to "delete_task_agent"
update / change / rename / edit / modify → route to "update_task_agent"
anything else (greeting, thanks, unclear) → respond directly and politely, no routing

Always stay in character as a helpful assistant. Never perform the action yourself — only classify and route.
```

## MCP Tool Schemas
Prepared schemas for:
- add_task
- list_tasks
- complete_task
- delete_task
- update_task