---
id: 1
title: switch-openai-models
stage: spec
date_iso: 2026-01-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: switch-openai-models
branch: 001-switch-openai-models
user: user
command: /sp.specify
labels: ["specification", "openai", "migration", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - specs/001-switch-openai-models/spec.md
  - specs/001-switch-openai-models/checklists/requirements.md
tests_yaml: []
prompt_text: "/sp.specify\n\nWe have purchased a real OpenAI API key and added it to phase3-chatbot/.env as OPENAI_API_KEY.\n\nSwitch the entire Phase 3 backend to use native OpenAI models instead of the Gemini compatibility layer.\n\nPlease perform the following changes across all relevant files in phase3-chatbot/backend/:\n\n1. Remove all Gemini-specific code:\n   - Delete any AsyncOpenAI(base_url=\"https://generativelanguage.googleapis.com/v1beta/openai/\")\n   - Delete any model=\"gemini-2.0-flash\" or similar\n   - Remove external_client creation and passing\n\n2. Replace with native OpenAI configuration:\n   - Import from openai import AsyncOpenAI (standard client)\n   - Load key directly: openai_client = AsyncOpenAI(api_key=os.getenv(\"OPENAI_API_KEY\"))\n   - Use model=\"gpt-4o-mini\" \n   - Update RunConfig to use this client and model:\n     config = RunConfig(\n         model=OpenAIChatCompletionsModel(model=\"gpt-4o\", openai_client=openai_client),\n         model_provider=openai_client,\n         tracing_disabled=True\n     )\n\n3. Affected files to update (search and replace where needed):\n   - phase3-chatbot/backend/agents/base.py (if client is created there)\n   - phase3-chatbot/backend/agents/router_agent.py\n   - phase3-chatbot/backend/agents/add_task_agent.py\n   - phase3-chatbot/backend/agents/list_tasks_agent.py\n   - phase3-chatbot/backend/agents/complete_task_agent.py\n   - phase3-chatbot/backend/agents/update_task_agent.py\n   - phase3-chatbot/backend/agents/delete_task_agent.py\n   - Any other agent files that initialize models or run configs\n\n4. Update .env.example (or .env comments):\n   - Remove GEMINI_API_KEY\n   - Keep / add comment: OPENAI_API_KEY=sk-...  # Required - real OpenAI key\n\n5. Update README-phase3.md:\n   - Change any mention of \"Gemini\" or \"Google Generative Language\" to \"OpenAI (gpt-4o)\"\n   - Update setup instructions: \"Set OPENAI_API_KEY in .env\"\n   - Remove any Gemini API key instructions\n\n6. Keep all other functionality unchanged:\n   - Agents, handoff pattern, MCP tools, DB operations, JWT auth, conversation persistence"
response_text: "Created complete specification for switching Phase 3 backend to native OpenAI models, including user scenarios, functional requirements, and success criteria. The specification covers removing Gemini-specific code, updating agent configurations, and updating documentation while preserving all existing functionality."
outcome: "Specification successfully created and validated for the OpenAI migration feature"
evaluation: "The specification is comprehensive and ready for the planning phase"
---

# PHR: switch-openai-models

Specification created for switching Phase 3 backend from Gemini to native OpenAI models.