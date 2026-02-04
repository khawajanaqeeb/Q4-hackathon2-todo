import { spawn } from 'child_process';
import { execSync } from 'child_process';

console.log('Starting backend server...');
const backend = spawn('python', ['-m', 'uvicorn', 'src.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'], {
  cwd: './phase3-chatbot/backend',
  stdio: 'inherit'
});

backend.on('close', (code) => {
  console.log(`Backend process exited with code ${code}`);
});

// Wait a bit for the server to start, then start the frontend
setTimeout(() => {
  console.log('Starting frontend server...');
  const frontend = spawn('npm', ['run', 'dev'], {
    cwd: './phase3-chatbot/frontend',
    stdio: 'inherit'
  });

  frontend.on('close', (code) => {
    console.log(`Frontend process exited with code ${code}`);
  });
}, 3000);