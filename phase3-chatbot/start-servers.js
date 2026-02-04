const { spawn } = require('child_process');
const path = require('path');

// Function to start the backend server
function startBackend() {
    console.log('Starting backend server...');

    const backendProcess = spawn('python', ['-m', 'uvicorn', 'backend.src.main:app', '--reload', '--port', '8000'], {
        cwd: path.join(__dirname),
        stdio: 'inherit',
        env: { ...process.env, PYTHONPATH: path.join(__dirname, 'backend/src') }
    });

    backendProcess.on('error', (err) => {
        console.error('Failed to start backend:', err.message);
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
    });
}

// Function to start the frontend server
function startFrontend() {
    console.log('Starting frontend server...');

    const frontendProcess = spawn('npm', ['run', 'dev'], {
        cwd: path.join(__dirname, 'frontend'),
        stdio: 'inherit'
    });

    frontendProcess.on('error', (err) => {
        console.error('Failed to start frontend:', err.message);
    });

    frontendProcess.on('close', (code) => {
        console.log(`Frontend process exited with code ${code}`);
    });
}

// Start both servers
startBackend();
setTimeout(startFrontend, 3000); // Give backend a moment to start first

console.log('Both servers are starting...');
console.log('- Backend: http://localhost:8000');
console.log('- Frontend: http://localhost:3000 (or as configured in your Next.js setup)');