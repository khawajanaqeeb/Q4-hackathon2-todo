@echo off
echo Starting Phase 3 Frontend for Local Development...
echo.

REM Navigate to frontend directory
cd /d "%~dp0"

REM Install dependencies if node_modules doesn't exist
if not exist node_modules (
    echo Installing dependencies...
    npm install
)

REM Start the frontend development server
echo Starting frontend server on http://localhost:3000...
npm run dev

pause