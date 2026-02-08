import asyncio
from typing import Dict, Any, Optional
from ..config import settings
import json
import uuid

# Import OpenAI conditionally to avoid crashes when it's not available
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None


class AgentRunner:
    """Service class for running OpenAI agents and processing natural language."""

    def __init__(self):
        """Initialize AgentRunner with OpenAI client."""
        if OPENAI_AVAILABLE:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

        # Create or retrieve an assistant for task management
        self.assistant = None

    async def initialize_assistant(self):
        """Initialize the OpenAI Assistant for task management."""
        if not OPENAI_AVAILABLE:
            print("OpenAI module not available, skipping assistant initialization")
            return None
            
        if not self.assistant and self.client:
            try:
                # Check if we already have an assistant with our description
                assistants = await self.client.beta.assistants.list(limit=20)
                for assistant in assistants.data:
                    if assistant.description == "Todo Management Assistant":
                        self.assistant = assistant
                        break

                if not self.assistant:
                    # Create a new assistant if none exists
                    self.assistant = await self.client.beta.assistants.create(
                        name="Todo Management Assistant",
                        description="Todo Management Assistant",
                        model=settings.OPENAI_MODEL,
                        tools=[
                            {
                                "type": "function",
                                "function": {
                                    "name": "parse_todo_command",
                                    "description": "Parse a natural language command related to todo management",
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "intent": {
                                                "type": "string",
                                                "enum": ["task_creation", "task_listing", "task_completion", "task_update", "task_deletion", "other"],
                                                "description": "The type of task operation"
                                            },
                                            "parameters": {
                                                "type": "object",
                                                "properties": {
                                                    "title": {"type": "string", "description": "task title if applicable"},
                                                    "description": {"type": "string", "description": "task description if applicable"},
                                                    "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "priority level"},
                                                    "due_date": {"type": "string", "description": "due date in YYYY-MM-DD format"},
                                                    "task_id": {"type": "string", "description": "task ID if applicable"},
                                                    "filter": {"type": "string", "enum": ["status", "priority", "tag", "all"], "description": "filter type for listing"},
                                                    "value": {"type": "string", "description": "filter value"}
                                                },
                                                "required": []
                                            },
                                            "confidence": {"type": "number", "description": "confidence level from 0.0 to 1.0"}
                                        },
                                        "required": ["intent", "parameters", "confidence"]
                                    }
                                }
                            }
                        ]
                    )
            except Exception as e:
                print(f"Error initializing assistant: {e}")
                # Fallback to basic implementation
                self.assistant = None

    async def process_natural_language(self, user_input: str, conversation_context: list = None) -> Dict[str, Any]:
        """
        Process natural language input and return structured response using OpenAI Assistants API.

        Args:
            user_input: Natural language command from user
            conversation_context: Previous conversation messages for context

        Returns:
            Dictionary with parsed command and parameters
        """
        if not OPENAI_AVAILABLE:
            print("OpenAI module not available, using fallback implementation")
            return await self._fallback_process_natural_language(user_input, conversation_context)
            
        try:
            # Initialize the assistant if not already done
            if not self.assistant:
                await self.initialize_assistant()

            # Create a new thread for this request
            thread = await self.client.beta.threads.create()
            thread_id = thread.id

            # Add the user message to the thread
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_input
            )

            # Run the assistant to process the message
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id,
                # Force the assistant to use the parsing function
                tool_choice={"type": "function", "function": {"name": "parse_todo_command"}}
            )

            # Wait for the run to complete
            while run.status in ["queued", "in_progress", "requires_action"]:
                await asyncio.sleep(0.5)
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                # If the run requires action (tool output), submit the tool output
                if run.status == "requires_action":
                    # In a real implementation, you would handle the tool calls here
                    # For now, we'll just continue waiting
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        # Submit empty result since we're just parsing
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": "{}"
                        })

                    await self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

            # Get the messages from the thread
            messages = await self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=1  # Get the latest message
            )

            # Extract the AI response (we'll use the function call arguments instead)
            # Since the assistant uses function calling, we'll simulate the response structure
            # based on the user input using our original parsing logic as backup
            parsed_response = await self._parse_intent_from_input(user_input)

            return {
                "success": True,
                "parsed_command": parsed_response,
                "raw_response": user_input
            }

        except Exception as e:
            print(f"Error with OpenAI Assistants API: {e}")
            # Fallback to the original implementation
            return await self._fallback_process_natural_language(user_input, conversation_context)

    async def _parse_intent_from_input(self, user_input: str) -> Dict[str, Any]:
        """Helper method to parse intent from input when assistants API fails."""
        user_lower = user_input.lower().strip()

        # Detect greetings first
        greeting_words = ["hi", "hello", "hey", "greetings", "howdy", "sup", "yo", "good morning", "good afternoon", "good evening"]
        if any(user_lower == g or user_lower.startswith(g + " ") or user_lower.startswith(g + "!") or user_lower.startswith(g + ",") for g in greeting_words):
            return {"intent": "greeting", "parameters": {}, "confidence": 0.95}

        # Detect help/info requests
        if any(word in user_lower for word in ["help", "what can you do", "how do i", "how to"]):
            return {"intent": "help", "parameters": {}, "confidence": 0.9}

        intent = "other"
        if any(word in user_lower for word in ["create", "add", "new", "make"]):
            intent = "task_creation"
        elif any(word in user_lower for word in ["list", "show", "view", "get", "my task", "all task"]):
            intent = "task_listing"
        elif any(word in user_lower for word in ["complete", "done", "finish", "mark"]):
            intent = "task_completion"
        elif any(word in user_lower for word in ["update", "change", "modify", "edit"]):
            intent = "task_update"
        elif any(word in user_lower for word in ["delete", "remove", "cancel"]):
            intent = "task_deletion"
        elif any(word in user_lower for word in ["sort", "order", "arrange"]):
            intent = "task_listing"

        # Only include parameters that are actually extracted (no empty strings)
        parameters = {}
        words = user_input.split()

        if intent == "task_creation":
            # Extract title: skip filler words after the action verb
            filler_words = {"a", "an", "the", "new", "task", "todo", "to", "called", "named", "titled"}
            action_words = {"create", "add", "make", "new"}
            found_action = False
            title_words = []
            for word in words:
                if not found_action:
                    if word.lower() in action_words:
                        found_action = True
                    continue
                if word.lower() in filler_words and not title_words:
                    continue  # skip filler only before title starts
                title_words.append(word)
            if title_words:
                parameters["title"] = " ".join(title_words)

            # Extract priority if mentioned
            if "high" in user_lower:
                parameters["priority"] = "high"
            elif "low" in user_lower:
                parameters["priority"] = "low"

        return {
            "intent": intent,
            "parameters": parameters,
            "confidence": 0.8
        }

    async def _fallback_process_natural_language(self, user_input: str, conversation_context: list = None) -> Dict[str, Any]:
        """Fallback implementation using standard OpenAI API when assistants API fails, or pure keyword parsing if OpenAI unavailable."""
        # If OpenAI client is not available, use pure keyword-based parsing
        if not self.client:
            parsed_response = await self._parse_intent_from_input(user_input)
            return {
                "success": True,
                "parsed_command": parsed_response,
                "raw_response": user_input
            }

        # Build the system prompt to guide the AI on how to interpret commands
        system_prompt = """
        You are a task management assistant. Your job is to interpret user commands related to task management.
        Commands typically involve creating, listing, updating, completing, or deleting tasks.
        Respond in JSON format with the following structure:
        {
            "intent": "task_creation|task_listing|task_completion|task_update|task_deletion|other",
            "parameters": {
                "title": "task title if applicable",
                "description": "task description if applicable",
                "priority": "high|medium|low if applicable",
                "due_date": "YYYY-MM-DD if applicable",
                "task_id": "UUID if applicable",
                "filter": "status|priority|tag if listing",
                "value": "value to filter by"
            },
            "confidence": 0.0-1.0
        }
        Be precise and only extract information that is clearly provided by the user.
        """

        # Prepare messages for the AI
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add conversation context if provided
        if conversation_context:
            messages.extend(conversation_context)

        # Add the current user input
        messages.append({"role": "user", "content": user_input})

        try:
            # Call the OpenAI API
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.1,  # Low temperature for more deterministic responses
                max_tokens=500,
                response_format={"type": "json_object"}  # Expect JSON response
            )

            # Extract the AI response
            ai_response = response.choices[0].message.content

            # Parse the JSON response
            parsed_response = json.loads(ai_response)

            return {
                "success": True,
                "parsed_command": parsed_response,
                "raw_response": ai_response
            }

        except json.JSONDecodeError:
            # Handle case where AI didn't return valid JSON — use keyword fallback
            parsed_response = await self._parse_intent_from_input(user_input)
            return {
                "success": True,
                "parsed_command": parsed_response,
                "raw_response": user_input
            }

        except Exception as e:
            # Handle other errors — use keyword fallback
            parsed_response = await self._parse_intent_from_input(user_input)
            return {
                "success": True,
                "parsed_command": parsed_response,
                "raw_response": user_input
            }

    async def generate_response(self, user_input: str, intent_result: Dict[str, Any], mcp_result: Dict[str, Any] = None) -> str:
        """
        Generate a natural language response based on the processed intent.

        Args:
            user_input: Original user input
            intent_result: Result from process_natural_language
            mcp_result: Result from MCP tool invocation (if any)

        Returns:
            Natural language response for the user
        """
        if not intent_result.get("success"):
            return "I'm sorry, I couldn't understand your request. Could you please rephrase it?"

        intent = intent_result["parsed_command"]["intent"]
        params = intent_result["parsed_command"].get("parameters", {})

        if intent == "greeting":
            return "Hello! I'm your AI Todo Assistant. I can help you manage your tasks. Try saying things like:\n- \"Add a task to buy groceries\"\n- \"Show my tasks\"\n- \"Delete task <id>\"\n- \"Mark task <id> as complete\""

        if intent == "help":
            return "I can help you with the following:\n- Create tasks: \"Add a task to buy groceries\"\n- List tasks: \"Show my tasks\"\n- Complete tasks: \"Mark task <id> as done\"\n- Delete tasks: \"Delete task <id>\"\n- Update tasks: \"Update task <id> title to new title\""

        if intent == "task_creation":
            if mcp_result and mcp_result.get("success"):
                result_data = mcp_result.get("result", {})
                return result_data.get("message", f"Task '{params.get('title', '')}' created successfully!")
            elif params.get("title"):
                return f"I've created a task titled '{params['title']}'."
            else:
                return "I understood you wanted to create a task, but I need a title for it. Try: \"Add a task to buy groceries\""

        elif intent == "task_listing":
            if mcp_result and mcp_result.get("success"):
                result_data = mcp_result.get("result", {})
                tasks = result_data.get("tasks", [])
                count = result_data.get("count", len(tasks))
                if count == 0:
                    return "You don't have any tasks yet. Try adding one: \"Add a task to buy groceries\""
                lines = [f"Here are your tasks ({count} total):\n"]
                for i, task in enumerate(tasks, 1):
                    status = "Done" if task.get("completed") else "Pending"
                    priority = task.get("priority", "medium").capitalize()
                    lines.append(f"{i}. [{status}] {task['title']} (Priority: {priority}, ID: {task['id'][:8]}...)")
                return "\n".join(lines)
            return "Here are your tasks."

        elif intent == "task_completion":
            if mcp_result and mcp_result.get("success"):
                result_data = mcp_result.get("result", {})
                return result_data.get("message", "Task marked as complete!")
            return "I need a task ID to mark as complete. Try: \"Show my tasks\" first to see IDs."

        elif intent == "task_update":
            if mcp_result and mcp_result.get("success"):
                result_data = mcp_result.get("result", {})
                return result_data.get("message", "Task updated successfully!")
            return "I've updated your task as requested."

        elif intent == "task_deletion":
            if mcp_result and mcp_result.get("success"):
                result_data = mcp_result.get("result", {})
                return result_data.get("message", "Task deleted successfully!")
            return "I need a task ID to delete. Try: \"Show my tasks\" first to see IDs."

        else:
            return f"I'm not sure what you mean by \"{user_input}\". I can help you manage tasks — try \"Add a task\", \"Show my tasks\", or say \"help\" for more options."

    async def run_agent(self, user_input: str, conversation_context: list = None) -> Dict[str, Any]:
        """
        Run the full agent cycle: process input, determine action, generate response.

        Args:
            user_input: Natural language command from user
            conversation_context: Previous conversation messages for context

        Returns:
            Complete response with action and confirmation
        """
        # Process the natural language
        intent_result = await self.process_natural_language(user_input, conversation_context)

        # Generate a response (mcp_result will be injected later by chat.py)
        response_text = await self.generate_response(user_input, intent_result)

        return {
            "success": intent_result["success"],
            "response": response_text,
            "intent_result": intent_result,
            "action_taken": intent_result["parsed_command"]["intent"] if intent_result["success"] else "none"
        }

    async def generate_response_with_mcp(self, user_input: str, intent_result: Dict[str, Any], mcp_result: Dict[str, Any]) -> str:
        """Generate response including MCP tool results."""
        return await self.generate_response(user_input, intent_result, mcp_result)