#!/bin/bash
# Health check script for Phase 3 Chatbot Authentication System

echo "=== Phase 3 Chatbot Authentication System Health Check ==="
echo ""

echo "1. Checking Backend Configuration..."
if [ -f "../backend/.env" ]; then
    echo "   ✓ Backend .env file exists"
    DB_URL=$(grep DATABASE_URL ../backend/.env | head -n1)
    echo "   ✓ Database URL: $DB_URL"
else
    echo "   ✗ Backend .env file missing"
fi

echo ""
echo "2. Checking Frontend Configuration..."
if [ -f "../frontend/.env.local" ]; then
    echo "   ✓ Frontend .env.local file exists"
    API_URL=$(grep NEXT_PUBLIC_API_URL ../frontend/.env.local | head -n1)
    echo "   ✓ API URL: $API_URL"
else
    echo "   ✗ Frontend .env.local file missing"
fi

echo ""
echo "3. Checking Startup Scripts..."
if [ -f "../backend/start_local.bat" ]; then
    echo "   ✓ Backend startup script exists"
else
    echo "   ✗ Backend startup script missing"
fi

if [ -f "../frontend/start_local.bat" ]; then
    echo "   ✓ Frontend startup script exists"
else
    echo "   ✗ Frontend startup script missing"
fi

echo ""
echo "4. Checking Authentication Files..."
if [ -f "../backend/src/api/auth.py" ]; then
    echo "   ✓ Backend auth.py exists"
else
    echo "   ✗ Backend auth.py missing"
fi

if [ -f "../frontend/app/api/auth/[...path]/route.ts" ]; then
    echo "   ✓ Frontend auth proxy exists"
else
    echo "   ✗ Frontend auth proxy missing"
fi

if [ -f "../frontend/context/AuthContext.tsx" ]; then
    echo "   ✓ AuthContext exists"
else
    echo "   ✗ AuthContext missing"
fi

echo ""
echo "=== Health Check Complete ==="
echo "To start the application:"
echo "1. Start backend: cd ../backend && ./start_local.bat"
echo "2. Start frontend: cd ../frontend && ./start_local.bat"
echo "3. Visit http://localhost:3000 to access the application"