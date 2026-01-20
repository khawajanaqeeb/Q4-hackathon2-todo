# Data Model: OpenAI Migration for Phase 3 Chatbot

## Overview
This document describes the data models and configurations affected by the migration from Gemini to OpenAI models. The migration primarily affects configuration and runtime parameters rather than persistent data models.

## Configuration Models

### OpenAI Client Configuration
- **Entity**: OpenAIAsyncClient
- **Fields**:
  - api_key: String (loaded from environment variable)
  - base_url: String (default OpenAI endpoint)
  - timeout: Integer (request timeout in seconds)
  - max_retries: Integer (number of retry attempts)

### Model Configuration
- **Entity**: OpenAIModelConfig
- **Fields**:
  - model_name: String (currently "gpt-4o-mini")
  - temperature: Float (creativity control)
  - max_tokens: Integer (response length limit)
  - client: OpenAIAsyncClient (reference to client instance)

### Run Configuration
- **Entity**: RunConfig
- **Fields**:
  - model: OpenAIChatCompletionsModel (model configuration)
  - model_provider: OpenAIAsyncClient (provider reference)
  - tracing_disabled: Boolean (tracing flag)

## Affected Files
The following files will be updated to use the new OpenAI configuration:

### Agent Files
- `phase3-chatbot/backend/agents/base.py`
- `phase3-chatbot/backend/agents/router_agent.py`
- `phase3-chatbot/backend/agents/add_task_agent.py`
- `phase3-chatbot/backend/agents/list_tasks_agent.py`
- `phase3-chatbot/backend/agents/complete_task_agent.py`
- `phase3-chatbot/backend/agents/update_task_agent.py`
- `phase3-chatbot/backend/agents/delete_task_agent.py`

### Configuration Files
- `.env.example`
- `README-phase3.md`

## State Transitions
No state transitions are affected by this migration as it only changes the underlying LLM provider while maintaining all existing functionality.

## Validation Rules
- API key must be properly formatted (starts with "sk-")
- Model name must be valid and available in OpenAI
- Client initialization must succeed before agent startup
- All existing agent interfaces must remain compatible