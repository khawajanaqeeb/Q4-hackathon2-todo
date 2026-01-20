# Research: Migration from Gemini to OpenAI Models

## Overview
This research document outlines the approach for migrating the Phase 3 chatbot backend from Google Gemini compatibility layer to native OpenAI models, as specified in the feature requirements.

## Decision: Remove Gemini Compatibility Layer
**Rationale**: The current implementation uses Google's Gemini compatibility layer which adds unnecessary complexity and potential performance overhead. Switching to native OpenAI client will provide better performance, reliability, and direct access to OpenAI's features.

**Alternatives considered**:
- Keep Gemini compatibility layer and add OpenAI as backup: Would add complexity without clear benefit
- Create abstraction layer for multiple providers: Would add unnecessary complexity for this specific requirement
- Gradual migration: Would extend timeline and add risk of inconsistencies

## Decision: Use OpenAI AsyncOpenAI Client
**Rationale**: Native OpenAI AsyncOpenAI client provides the most direct and efficient integration with OpenAI services. It offers better error handling, logging, and performance compared to compatibility layers.

**Alternatives considered**:
- OpenAI SDK with synchronous client: Would block threads unnecessarily
- Direct HTTP calls to OpenAI API: Would lose built-in retry logic and error handling
- Third-party wrapper libraries: Would add unnecessary dependencies

## Decision: Configure gpt-4o-mini as Primary Model
**Rationale**: gpt-4o-mini provides an excellent balance of capability, speed, and cost-effectiveness for the chatbot's requirements. It offers strong performance for natural language understanding and response generation.

**Alternatives considered**:
- gpt-4o: More capable but more expensive, likely unnecessary for chatbot tasks
- GPT-3.5 Turbo: Less capable than gpt-4o-mini, being phased out
- Other models: Less suitable for the specific requirements of the chatbot

## Decision: Update RunConfig with OpenAIChatCompletionsModel
**Rationale**: The RunConfig structure needs to be updated to use OpenAI's native model interface instead of the compatibility layer. This ensures proper integration with the OpenAI Agents SDK.

**Alternatives considered**:
- Custom model wrapper: Would add unnecessary complexity
- Generic interface: Would not leverage OpenAI's specific capabilities effectively

## Decision: Update All Agent Files Consistently
**Rationale**: All agent files (base.py, router_agent.py, add_task_agent.py, list_tasks_agent.py, complete_task_agent.py, update_task_agent.py, delete_task_agent.py) need consistent updates to ensure uniform behavior across the multi-agent system.

**Alternatives considered**:
- Partial updates: Would create inconsistent behavior across agents
- Separate configurations per agent: Would make maintenance more complex

## Security Considerations
- API key handling: Continue using environment variables for secure storage
- No hardcoding: Ensure API keys are never committed to version control
- Error handling: Ensure API errors don't expose sensitive information

## Backward Compatibility
- Maintain all existing functionality (agents, handoff pattern, MCP tools, DB operations, JWT auth, conversation persistence)
- Preserve existing API contracts and interfaces
- Ensure no disruption to ongoing conversations or user data