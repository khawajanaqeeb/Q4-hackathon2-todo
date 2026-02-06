@echo off
echo === Phase 3 Chatbot Authentication System Health Check ===
echo.

echo 1. Checking Backend Configuration...
if exist "..\backend\.env" (
    echo    ^✓ Backend .env file exists
    for /f "tokens=*" %%a in ('findstr DATABASE_URL "..\backend\.env"') do echo    ^✓ Database URL: %%a
) else (
    echo    ^✗ Backend .env file missing
)

echo.
echo 2. Checking Frontend Configuration...
if exist "..\frontend\.env.local" (
    echo    ^✓ Frontend .env.local file exists
    for /f "tokens=*" %%a in ('findstr NEXT_PUBLIC_API_URL "..\frontend\.env.local"') do echo    ^✓ API URL: %%a
) else (
    echo    ^✗ Frontend .env.local file missing
)

echo.
echo 3. Checking Startup Scripts...
if exist "..\backend\start_local.bat" (
    echo    ^✓ Backend startup script exists
) else (
    echo    ^✗ Backend startup script missing
)

if exist "..\frontend\start_local.bat" (
    echo    ^✓ Frontend startup script exists
) else (
    echo    ^✗ Frontend startup script missing
)

echo.
echo 4. Checking Authentication Files...
if exist "..\backend\src\api\auth.py" (
    echo    ^✓ Backend auth.py exists
) else (
    echo    ^✗ Backend auth.py missing
)

if exist "..\frontend\app\api\auth\[...path]\route.ts" (
    echo    ^✓ Frontend auth proxy exists
) else (
    echo    ^✗ Frontend auth proxy missing
)

if exist "..\frontend\context\AuthContext.tsx" (
    echo    ^✓ AuthContext exists
) else (
    echo    ^✗ AuthContext missing
)

echo.
echo === Health Check Complete ===
echo To start the application:
echo 1. Start backend: cd ..\backend ^&^& start_local.bat
echo 2. Start frontend: cd ..\frontend ^&^& start_local.bat
echo 3. Visit http://localhost:3000 to access the application