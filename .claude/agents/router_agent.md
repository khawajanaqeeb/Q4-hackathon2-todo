# Router Agent Specification

## Overview
The Router Agent is the central component of the AI Todo Chatbot system. Its primary responsibility is to analyze user messages and conversation history, then route them to the appropriate specialized agent for processing.

## Purpose
The Router Agent serves as the entry point for all user interactions with the AI Todo Chatbot. It determines the user's intent and delegates the request to the appropriate specialized agent.

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

## Capabilities
- Intent classification based on user input
- Conversation history analysis
- Routing to appropriate specialized agents
- Direct response for unrecognized intents

## Technology Stack
- Model: gpt-4o (or latest available)
- Framework: OpenAI Agents SDK
- Integration: Will connect to specialized agents via MCP tool schemas

## MCP Tool Schemas
The Router Agent will be prepared with the following tool schemas:
- add_task
- list_tasks
- complete_task
- delete_task
- update_task

These schemas will be defined according to @specs/api/mcp-tools.md and made available to the agent for future delegation.

## Integration Points
- Receives input from the chat endpoint
- Routes to specialized agents based on intent
- Maintains conversation state awareness