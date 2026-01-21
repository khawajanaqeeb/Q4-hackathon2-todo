// check-build-readiness.js
// Script to verify if the frontend is ready for build

const fs = require('fs');
const path = require('path');

console.log('🔍 Checking Frontend Build Readiness...\n');

const readinessChecks = [
  {
    name: 'Package.json exists',
    check: () => fs.existsSync('./package.json')
  },
  {
    name: 'Next.js config exists',
    check: () => fs.existsSync('./next.config.js')
  },
  {
    name: 'TypeScript config exists',
    check: () => fs.existsSync('./tsconfig.json')
  },
  {
    name: 'App directory exists',
    check: () => fs.existsSync('./app')
  },
  {
    name: 'Chat page exists',
    check: () => fs.existsSync('./app/chat/page.tsx')
  },
  {
    name: 'Components directory exists',
    check: () => fs.existsSync('./components')
  },
  {
    name: 'ChatInterface component exists',
    check: () => fs.existsSync('./components/ChatInterface.tsx')
  },
  {
    name: 'Dependencies are specified',
    check: () => {
      if (!fs.existsSync('./package.json')) return false;
      const pkg = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
      return !!pkg.dependencies && Object.keys(pkg.dependencies).length > 0;
    }
  },
  {
    name: 'Build script exists',
    check: () => {
      if (!fs.existsSync('./package.json')) return false;
      const pkg = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
      return !!pkg.scripts && !!pkg.scripts.build;
    }
  },
  {
    name: 'Main components import correctly',
    check: () => {
      try {
        const chatPage = fs.readFileSync('./app/chat/page.tsx', 'utf8');
        const hasUseAuthImport = chatPage.includes("import useAuth");
        const hasChatInterfaceImport = chatPage.includes("import ChatInterface");
        return hasUseAuthImport && hasChatInterfaceImport;
      } catch (e) {
        return false;
      }
    }
  }
];

let passedCount = 0;
readinessChecks.forEach(check => {
  const result = check.check();
  console.log(`  ${result ? '✅' : '❌'} ${check.name}`);
  if (result) passedCount++;
});

console.log(`\n📊 Readiness Score: ${passedCount}/${readinessChecks.length}`);

if (passedCount === readinessChecks.length) {
  console.log('\n🎉 The frontend is ready for build!');
  console.log('\nTo build the project, run:');
  console.log('  npm install'); // Install dependencies first
  console.log('  npm run build'); // Then run build

  console.log('\nIf you encounter issues, make sure you have:');
  console.log('- Node.js 18+ installed');
  console.log('- All dependencies installed (npm install)');
  console.log('- Proper network connectivity for downloading packages');
} else {
  console.log('\n⚠️  The frontend needs attention before building.');
  console.log('Some required files or configurations are missing.');
}

// Check for build artifacts
const buildArtifacts = ['.next', 'out', 'dist', 'build'];
const existingArtifacts = buildArtifacts.filter(dir => fs.existsSync(dir));
if (existingArtifacts.length > 0) {
  console.log(`\n📦 Found existing build artifacts: ${existingArtifacts.join(', ')}`);
} else {
  console.log('\n📦 No build artifacts found - build has not been run or failed.');
}