# Quickstart: OpenAI Migration for Phase 3 Chatbot

## Overview
This guide provides the essential steps to set up and run the Phase 3 chatbot with native OpenAI integration after the migration from Gemini.

## Prerequisites
- Python 3.13+
- OpenAI API key (real key, not compatibility layer)
- Existing project dependencies (FastAPI, SQLModel, etc.)

## Setup Steps

### 1. Environment Configuration
1. Copy `.env.example` to `.env`
2. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. Remove any existing GEMINI_API_KEY entries

### 2. Install Dependencies
```bash
pip install openai
```

### 3. Verify Agent Configuration
Ensure all agent files are updated to use:
- `from openai import AsyncOpenAI`
- `openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))`
- `model="gpt-4o-mini"`

### 4. Run the Application
```bash
cd phase3-chatbot/backend
uvicorn main:app --reload
```

## Key Changes

### Removed Components
- Gemini compatibility layer
- `AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/")`
- `model="gemini-2.0-flash"`
- External client passing mechanisms

### Added Components
- Native OpenAI AsyncOpenAI client
- Direct API key loading from environment
- OpenAIChatCompletionsModel configuration

## Verification
1. Start the application
2. Test chatbot functionality
3. Verify API calls are made to OpenAI (not Gemini)
4. Confirm all existing features work as before

## Troubleshooting
- If API calls fail, verify your OpenAI API key is valid and has sufficient credits
- If agents don't start, check that all agent files have been updated correctly
- If functionality is broken, ensure all existing features were preserved during migration