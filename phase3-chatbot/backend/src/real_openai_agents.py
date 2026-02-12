"""Real OpenAI Agents SDK implementation for todo management."""

import asyncio
from typing import Dict, Any, Optional
from sqlmodel import Session
from .services.mcp_integration import McpIntegrationService
from .services.api_key_manager import ApiKeyManager
from .services.audit_service import AuditService

# Try to import OpenAI, but handle gracefully if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class RealOpenAiAgentsSdk:
    def __init__(self, api_key: str, session: Session):
        self.session = session
        self.api_key_manager = ApiKeyManager()
        self.audit_service = AuditService(session)
        self.mcp_service = McpIntegrationService(session, self.api_key_manager, self.audit_service)
        self.agent = None
        
        # Check if OpenAI is available
        if not OPENAI_AVAILABLE:
            self.client = None
            print("Warning: OpenAI module not available. Chatbot functionality will use fallback responses.")
            return
        
        # Check if API key is provided
        if not api_key or api_key.strip() == "":
            # If no API key, try to get it from the API key manager
            from .config import settings
            api_key = settings.OPENAI_API_KEY
        
        if not api_key or api_key.strip() == "":
            # If still no API key, set client to None
            self.client = None
            print("Warning: OpenAI API key not configured. Chatbot functionality will use fallback responses.")
            return
        
        self.client = OpenAI(api_key=api_key)
        
    def create_todo_management_agent(self):
        """Create an OpenAI agent for todo management."""
        # For now, we'll use the chat completions API as a simpler approach
        # In a real implementation, this would create an actual OpenAI Assistant
        self.agent = {
            "instructions": """
            You are a helpful todo management assistant. You can help users create, list, update, complete, and delete tasks.
            Use the available tools to perform these operations.
            
            Available tools:
            1. create_task: Create a new task
            2. list_tasks: List all tasks for a user
            3. update_task: Update an existing task
            4. complete_task: Mark a task as completed
            5. delete_task: Delete a task
            6. search_tasks: Search tasks by keyword
            7. get_task_details: Get details of a specific task
            """,
            "model": "gpt-4-turbo-preview"
        }
        return self.agent
    
    async def process_user_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process a user message through the OpenAI agent."""
        try:
            # Check if OpenAI is available and configured
            if not self.client:
                # Fallback: use keyword-based intent parsing and MCP tools
                from .services.agent_runner import AgentRunner
                agent_runner = AgentRunner()
                agent_result = await agent_runner.run_agent(message)

                if not agent_result.get("success"):
                    return {"response": "Sorry, I couldn't understand your request.", "success": True}

                intent = agent_result.get("action_taken", "other")
                params = {}
                if "intent_result" in agent_result and "parsed_command" in agent_result["intent_result"]:
                    params = agent_result["intent_result"]["parsed_command"].get("parameters", {})

                # Execute MCP tool if it's a task operation
                mcp_result = None
                if intent in ["task_creation", "task_listing", "task_update", "task_deletion", "task_completion"]:
                    tool_mapping = {
                        "task_creation": "create_task",
                        "task_listing": "list_tasks",
                        "task_update": "update_task",
                        "task_deletion": "delete_task",
                        "task_completion": "complete_task"
                    }
                    tool_name = tool_mapping.get(intent)
                    if tool_name:
                        mcp_result = await self.mcp_service.invoke_tool(
                            tool_name=tool_name,
                            parameters=params,
                            user_id=user_id
                        )

                response_text = await agent_runner.generate_response(message, agent_result["intent_result"], mcp_result)
                return {"response": response_text, "success": True}

            # Get available tools from the MCP service
            tools = self.mcp_service.get_available_tools(user_id)

            # Prepare tools in OpenAI format
            openai_tools = []
            for tool in tools:
                # Get the tool schema from the database
                from ..models.mcp_tool import McpTool
                from sqlmodel import select
                db_tool = self.session.exec(
                    select(McpTool).where(McpTool.name == tool['name'])
                ).first()
                
                if db_tool:
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool['name'],
                            "description": tool['description'],
                            "parameters": db_tool.tool_schema
                        }
                    })

            # Call OpenAI API with tools
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful todo management assistant. Use the available tools to help users manage their tasks."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                tools=openai_tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # Process tool calls
                tool_results = []
                for tool_call in tool_calls:
                    import ast
                    try:
                        function_args = ast.literal_eval(tool_call.function.arguments)
                    except (ValueError, SyntaxError):
                        # If literal_eval fails, try json.loads as fallback
                        import json
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            # If both fail, return an error
                            return {
                                "response": "Error parsing function arguments",
                                "success": False,
                                "error": "Could not parse function arguments"
                            }

                    function_name = tool_call.function.name
                    
                    # Add user_id to function args if not present
                    if 'user_id' not in function_args:
                        function_args['user_id'] = user_id

                    # Call the MCP service to execute the tool
                    result = await self.mcp_service.invoke_tool(
                        tool_name=function_name,
                        parameters=function_args,
                        user_id=user_id
                    )

                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(result)
                    })

                # Get final response from OpenAI with tool results
                final_response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful todo management assistant. Use the available tools to help users manage their tasks."
                        },
                        {
                            "role": "user",
                            "content": message
                        },
                        response_message,
                    ] + tool_results,
                )

                return {
                    "response": final_response.choices[0].message.content,
                    "success": True
                }
            else:
                # No tool calls, return the assistant's response directly
                return {
                    "response": response_message.content,
                    "success": True
                }

        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def cleanup_agent(self):
        """Clean up agent resources."""
        self.agent = None