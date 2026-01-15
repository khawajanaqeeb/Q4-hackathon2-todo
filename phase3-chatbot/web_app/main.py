"""
Web Application for Todo AI Chatbot

FastAPI application providing a web-based chat interface for the Todo AI Chatbot.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List
import asyncio
import json
from datetime import datetime

from agents.nlp_agent import NLPAgent
from agents.todo_command_interpreter_agent import TodoCommandInterpreterAgent
from agents.api_integration_agent import APIIntegrationAgent
from agents.response_generation_agent import ResponseGenerationAgent
from agents.conversation_context_manager_agent import ConversationContextManagerAgent
from config.api_config import get_api_config


app = FastAPI(title="Todo AI Chatbot", description="AI-powered chatbot for todo management")

# Mount static files
app.mount("/static", StaticFiles(directory="web_app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="web_app/templates")

# Initialize agents
nlp_agent = NLPAgent()
interpreter_agent = TodoCommandInterpreterAgent()
config = get_api_config()
api_agent = APIIntegrationAgent(
    base_url=config.get_base_url(),
    jwt_token=config.get_api_key(),  # In real app, would get from session/auth
    timeout=config.get_timeout(),
    max_retries=config.get_max_retries()
)
response_agent = ResponseGenerationAgent()
context_manager = ConversationContextManagerAgent()

# Store active connections (in production, use Redis or similar)
active_connections: Dict[str, WebSocket] = {}


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Serve the main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time chat."""
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            user_message = json.loads(data)

            user_id = user_message.get("user_id", "default_user")
            message_text = user_message.get("message", "")

            # Add user message to context
            context_manager.add_message_to_history(user_id, "user", message_text)

            # Process the message through the AI pipeline
            try:
                # Step 1: Process with NLP agent
                nlp_result = nlp_agent.process(message_text)

                # Step 2: Interpret with command interpreter
                api_command = interpreter_agent.interpret(nlp_result)

                # Step 3: Execute API command
                api_response = api_agent.send_request(api_command)

                # Step 4: Generate natural language response
                user_context = context_manager.get_active_context(user_id)
                response_text = response_agent.generate_response(
                    {
                        'status_code': api_response.status_code,
                        'data': api_response.data if api_response.is_success() else {},
                        'error': api_response.error if api_response.is_error() else None
                    },
                    user_context
                )

                # Add bot response to context
                context_manager.add_message_to_history(user_id, "assistant", response_text)

                # Prepare response
                response = {
                    "type": "response",
                    "message": response_text,
                    "timestamp": datetime.now().isoformat()
                }

            except Exception as e:
                # Handle any errors in the pipeline
                response = {
                    "type": "error",
                    "message": f"Sorry, I encountered an issue: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }

            # Send response back to client
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user")
        # Optionally notify other clients or clean up resources


@app.post("/api/chat")
async def chat_api(request: Request):
    """REST API endpoint for chat (alternative to WebSocket)."""
    body = await request.json()
    user_id = body.get("user_id", "default_user")
    message_text = body.get("message", "")

    # Add user message to context
    context_manager.add_message_to_history(user_id, "user", message_text)

    # Process the message through the AI pipeline
    try:
        # Step 1: Process with NLP agent
        nlp_result = nlp_agent.process(message_text)

        # Step 2: Interpret with command interpreter
        api_command = interpreter_agent.interpret(nlp_result)

        # Step 3: Execute API command
        api_response = api_agent.send_request(api_command)

        # Step 4: Generate natural language response
        user_context = context_manager.get_active_context(user_id)
        response_text = response_agent.generate_response(
            {
                'status_code': api_response.status_code,
                'data': api_response.data if api_response.is_success() else {},
                'error': api_response.error if api_response.is_error() else None
            },
            user_context
        )

        # Add bot response to context
        context_manager.add_message_to_history(user_id, "assistant", response_text)

        return {
            "success": True,
            "response": response_text,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Sorry, I encountered an issue: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "nlp_agent": "ready",
            "interpreter_agent": "ready",
            "api_agent": "ready",
            "response_agent": "ready",
            "context_manager": "ready"
        }
    }


# Initialize the web app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)