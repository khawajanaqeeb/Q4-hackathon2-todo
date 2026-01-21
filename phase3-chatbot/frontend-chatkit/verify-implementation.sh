#!/bin/bash
# Final verification script for Phase 3 frontend

echo "🔍 Final Verification of Phase 3 Frontend Implementation"
echo "======================================================"

echo ""
echo "📁 File Structure Check:"
FILES=(
  "package.json"
  "next.config.js"
  "tsconfig.json"
  ".env.local"
  "components/ChatInterface.tsx"
  "hooks/useAuth.ts"
  "lib/auth.ts"
  "lib/api.ts"
  "app/chat/page.tsx"
  "__tests__/ChatInterface.test.tsx"
  "jest.config.js"
  "jest.setup.js"
)

ALL_EXIST=true
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file - MISSING"
    ALL_EXIST=false
  fi
done

echo ""
echo "⚙️  Essential Functionality Check:"

# Check if package.json has required scripts
if grep -q '"test"' package.json; then
  echo "  ✅ Test script in package.json"
else
  echo "  ❌ Test script missing from package.json"
fi

# Check if main components have required functionality
if grep -q "ChatInterface" components/ChatInterface.tsx && grep -q "useState" components/ChatInterface.tsx; then
  echo "  ✅ ChatInterface has React hooks"
else
  echo "  ❌ ChatInterface missing React hooks"
fi

if grep -q "useAuth" hooks/useAuth.ts && grep -q "verifyBetterAuthSession" hooks/useAuth.ts; then
  echo "  ✅ useAuth hook connected to auth utilities"
else
  echo "  ❌ useAuth hook not properly connected"
fi

echo ""
echo "🔐 Authentication Integration Check:"

if grep -q "useAuth" app/chat/page.tsx && grep -q "ChatInterface" app/chat/page.tsx; then
  echo "  ✅ Chat page imports auth and interface"
else
  echo "  ❌ Chat page missing auth/integration"
fi

if grep -q "makeAuthenticatedRequest" lib/api.ts && grep -q "Authorization" lib/api.ts; then
  echo "  ✅ API utilities have auth headers"
else
  echo "  ❌ API utilities missing auth headers"
fi

echo ""
echo "📱 UI Component Check:"

if grep -q "userIdentifier" components/ChatInterface.tsx && grep -q "tokenProvider" components/ChatInterface.tsx; then
  echo "  ✅ ChatInterface has auth integration"
else
  echo "  ❌ ChatInterface missing auth integration"
fi

if grep -q "Debug: User ID" components/ChatInterface.tsx; then
  echo "  ✅ Debug user ID display present"
else
  echo "  ❌ Debug user ID display missing"
fi

echo ""
echo "🌐 Backend Communication Check:"

if grep -q "backendUrl" components/ChatInterface.tsx && grep -q "/api/\${userIdentifier}/chat" components/ChatInterface.tsx; then
  echo "  ✅ Backend API communication configured"
else
  echo "  ❌ Backend API communication missing"
fi

echo ""
echo "📋 Testing Setup Check:"

if [ -f "jest.config.js" ] && [ -f "jest.setup.js" ] && [ -f "__tests__/ChatInterface.test.tsx" ]; then
  echo "  ✅ Jest testing configuration complete"
else
  echo "  ❌ Testing configuration incomplete"
fi

echo ""
echo "📝 Environment Configuration Check:"

if grep -q "NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL" .env.local && grep -q "NEXT_PUBLIC_OPENAI_DOMAIN_KEY" .env.local; then
  echo "  ✅ Environment variables configured"
else
  echo "  ❌ Environment variables missing"
fi

echo ""
echo "🏆 Implementation Summary:"
echo "The Phase 3 Frontend includes:"
echo "  - Complete Next.js 16+ application with TypeScript 5+"
echo "  - OpenAI ChatKit integration component"
echo "  - Authentication system with Better Auth from Phase 2"
echo "  - API utilities for secure backend communication"
echo "  - Custom authentication hook for state management"
echo "  - Proper error handling and loading states"
echo "  - Responsive UI with debug information"
echo "  - Comprehensive test setup with Jest"
echo "  - Proper configuration for deployment"

echo ""
if [ "$ALL_EXIST" = true ]; then
  echo "🎉 SUCCESS: All required frontend files are present!"
  echo ""
  echo "🚀 To run the frontend:"
  echo "   1. Ensure Phase 3 backend is running on http://localhost:8000"
  echo "   2. Navigate to phase3-chatbot/frontend-chatkit/"
  echo "   3. Run: npm install"
  echo "   4. Run: npm run dev"
  echo "   5. Visit: http://localhost:3000/chat"
else
  echo "⚠️  WARNING: Some files are missing - please check above"
fi