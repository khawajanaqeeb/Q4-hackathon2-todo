# Phase 3 Chatbot - Local Development Setup

## Prerequisites
- Node.js (v18 or higher)
- Python (v3.9 or higher)
- pip
- npm

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd phase3-chatbot/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   If no requirements.txt exists, install the required packages:
   ```bash
   pip install fastapi uvicorn sqlmodel python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv psycopg2-binary redis slowapi
   ```

4. Make sure your `.env` file is properly configured for local development:
   - DATABASE_URL should point to a local SQLite database: `sqlite:///./todo_app.db`
   - CORS_ORIGINS should include `http://localhost:3000`

5. Start the backend server:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd phase3-chatbot/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Make sure your `.env.local` file contains:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```

### Running Both Servers
You can use the provided batch files to start both servers:
- `start_local.bat` in the backend directory
- `start_local.bat` in the frontend directory

## Troubleshooting Common Issues

1. **401 Unauthorized errors**: Make sure both servers are running and the API URL is correct
2. **Database connection errors**: Check that the DATABASE_URL in your backend .env file is correct
3. **CORS errors**: Verify that CORS settings in the backend allow requests from the frontend
4. **Cookie issues**: Modern browsers may block third-party cookies; make sure both services are running on localhost

## Testing the Authentication System

1. Visit http://localhost:3000
2. Try registering a new account
3. Log in with your credentials
4. Verify that you can access protected routes