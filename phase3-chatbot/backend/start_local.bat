@echo off
echo Starting Phase 3 Backend for Local Development with NeonDB...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo Warning: Virtual environment not found. Make sure you've run 'python -m venv venv' and installed dependencies.
)

REM Start the backend server in a separate window
echo Starting backend server on http://localhost:8000...
echo Connecting to NeonDB database...

start "FastAPI Server" cmd /k "uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"

REM Pause briefly before starting MCP server
timeout /t 5 /nobreak

REM Start MCP server in another window
echo Starting MCP server on tcp://localhost:3000...
start "MCP Server" cmd /k "python -c \"from src.mcp_server import TodoMcpServer; import asyncio; server = TodoMcpServer(); asyncio.run(server.start_server('0.0.0.0', 3000))\""

echo Both servers started successfully!
echo - FastAPI server: http://localhost:8000
echo - MCP server: tcp://localhost:3000
echo.
echo Press any key to exit...
pause