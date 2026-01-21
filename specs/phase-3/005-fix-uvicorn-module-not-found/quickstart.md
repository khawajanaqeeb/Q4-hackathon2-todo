# Quickstart: Running Phase 3 Backend After ModuleNotFoundError Fix

## Overview

This guide provides the essential steps to run the Phase 3 Todo AI Chatbot backend after fixing the ModuleNotFoundError that occurred when starting with uvicorn.

## Prerequisites

- Python 3.13+
- OpenAI API key (properly configured in .env)
- Dependencies installed (from requirements.txt)

## Setup Steps

### 1. Verify Package Structure
Ensure the following __init__.py files exist in the backend directory:
```
phase3-chatbot/
└── backend/
    ├── __init__.py          # Added to make backend a package
    ├── agents/
    │   ├── __init__.py      # Added to make agents a sub-package
    │   └── *.py
    ├── app/
    │   ├── __init__.py      # Added to make app a sub-package
    │   └── *.py
    ├── routers/
    │   ├── __init__.py      # Added to make routers a sub-package
    │   └── *.py
    └── main_phase3.py       # Entry point
```

### 2. Install Dependencies
```bash
cd phase3-chatbot
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual OpenAI API key and other values
```

### 4. Run the Application

#### Local Development
```bash
cd phase3-chatbot
uvicorn backend.main_phase3:app --reload --host 0.0.0.0 --port 8000
```

#### Production Deployment
```bash
cd phase3-chatbot
uvicorn backend.main_phase3:app --host 0.0.0.0 --port $PORT
```

## Key Changes Made

### Added Package Markers
- Added `__init__.py` files to make directories proper Python packages
- Ensured Python can import the backend module correctly

### Updated Run Commands
- New working directory requirement: run from phase3-chatbot/
- Correct module path: `backend.main_phase3:app`
- Proper environment setup with PYTHONPATH

## Verification
1. Start the server with the command above
2. Visit http://localhost:8000 to verify the server is running
3. Check the health endpoint at http://localhost:8000/health
4. Test the chat endpoint functionality

## Troubleshooting
- If ModuleNotFoundError still occurs, verify all __init__.py files are in place
- Ensure you're running the command from the phase3-chatbot directory
- Check that the PYTHONPATH includes the current directory
- Verify all dependencies are properly installed