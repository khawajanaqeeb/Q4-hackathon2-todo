@echo off
echo Starting Phase 3 Chatbot Servers...
echo.

echo Starting backend server...
cd backend
start cmd /k "python -m uvicorn src.main:app --reload --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting frontend server...
cd ../frontend
start cmd /k "npm run dev"

echo.
echo Servers should be starting...
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul