// test-frontend.js - Basic test to verify component structure
const fs = require('fs');
const path = require('path');

console.log('🔍 Testing Phase 3 Frontend Components...\n');

// Define the paths to check
const pathsToCheck = [
  'components/ChatInterface.tsx',
  'hooks/useAuth.ts',
  'lib/auth.ts',
  'lib/api.ts',
  'app/chat/page.tsx',
  'package.json',
  'next.config.js',
  'tsconfig.json',
  '.env.local'
];

let allFilesExist = true;

// Check if each file exists
pathsToCheck.forEach(filePath => {
  const fullPath = path.join(__dirname, filePath);
  if (fs.existsSync(fullPath)) {
    console.log(`✅ ${filePath} - Exists`);
  } else {
    console.log(`❌ ${filePath} - Missing`);
    allFilesExist = false;
  }
});

console.log('\n📋 Checking component functionality...\n');

// Read and verify the main components
try {
  // Check ChatInterface component
  const chatInterfaceContent = fs.readFileSync(path.join(__dirname, 'components/ChatInterface.tsx'), 'utf8');
  const hasEssentialFeatures = [
    'useState',
    'useEffect',
    'handleSendMessage',
    'tokenProvider',
    'backendUrl',
    'userIdentifier'
  ].every(feature => chatInterfaceContent.includes(feature));

  console.log(hasEssentialFeatures ? '✅ ChatInterface has essential features' : '❌ ChatInterface missing essential features');

  // Check useAuth hook
  const useAuthContent = fs.readFileSync(path.join(__dirname, 'hooks/useAuth.ts'), 'utf8');
  const hasAuthFeatures = [
    'verifyBetterAuthSession',
    'AuthState',
    'isLoggedIn',
    'user',
    'token'
  ].every(feature => useAuthContent.includes(feature));

  console.log(hasAuthFeatures ? '✅ useAuth hook has essential features' : '❌ useAuth hook missing essential features');

  // Check auth utilities
  const authContent = fs.readFileSync(path.join(__dirname, 'lib/auth.ts'), 'utf8');
  const hasAuthUtils = [
    'verifyBetterAuthSession',
    'extractJWTToken',
    'redirectToLogin'
  ].every(feature => authContent.includes(feature));

  console.log(hasAuthUtils ? '✅ auth utilities have essential features' : '❌ auth utilities missing essential features');

  // Check API utilities
  const apiContent = fs.readFileSync(path.join(__dirname, 'lib/api.ts'), 'utf8');
  const hasApiFeatures = [
    'makeAuthenticatedRequest',
    'sendChatMessage',
    'checkBackendHealth'
  ].every(feature => apiContent.includes(feature));

  console.log(hasApiFeatures ? '✅ API utilities have essential features' : '❌ API utilities missing essential features');

  // Check main chat page
  const chatPageContent = fs.readFileSync(path.join(__dirname, 'app/chat/page.tsx'), 'utf8');
  const hasPageFeatures = [
    'useAuth',
    'ChatInterface',
    'isLoggedIn',
    'user',
    'token'
  ].every(feature => chatPageContent.includes(feature));

  console.log(hasPageFeatures ? '✅ Chat page has essential features' : '❌ Chat page missing essential features');

  console.log('\n🎯 Frontend Structure Test Results:');
  console.log(allFilesExist ? '✅ All required files exist' : '❌ Some files are missing');

  const allComponentsValid = hasEssentialFeatures && hasAuthFeatures && hasAuthUtils && hasApiFeatures && hasPageFeatures;
  console.log(allComponentsValid ? '✅ All components have required functionality' : '❌ Some components are missing functionality');

  if (allFilesExist && allComponentsValid) {
    console.log('\n🎉 Phase 3 Frontend is properly structured and ready!');
    console.log('\n🚀 To run the frontend:');
    console.log('   1. Make sure Phase 3 backend is running on http://localhost:8000');
    console.log('   2. Run: npm install');
    console.log('   3. Run: npm run dev');
    console.log('   4. Visit: http://localhost:3000/chat');
  } else {
    console.log('\n❌ Frontend structure needs attention');
  }

} catch (error) {
  console.error('❌ Error reading files:', error.message);
}