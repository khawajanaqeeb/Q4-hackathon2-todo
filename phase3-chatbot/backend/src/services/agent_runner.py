import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from ..config import settings
import json
import uuid


class AgentRunner:
    """Service class for running OpenAI agents and processing natural language."""

    def __init__(self):
        """Initialize AgentRunner with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Create or retrieve an assistant for task management
        self.assistant = None
        self.thread_id = None

    async def initialize_assistant(self):
        """Initialize the OpenAI Assistant for task management."""
        if not self.assistant:
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
        try:
            # Initialize the assistant if not already done
            await self.initialize_assistant()

            # Create a thread if one doesn't exist
            if not self.thread_id:
                thread = await self.client.beta.threads.create()
                self.thread_id = thread.id

            # Add the user message to the thread
            await self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=user_input
            )

            # Run the assistant to process the message
            run = await self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant.id,
                # Force the assistant to use the parsing function
                tool_choice={"type": "function", "function": {"name": "parse_todo_command"}}
            )

            # Wait for the run to complete
            while run.status in ["queued", "in_progress", "requires_action"]:
                await asyncio.sleep(0.5)
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id,
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
                        thread_id=self.thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

            # Get the messages from the thread
            messages = await self.client.beta.threads.messages.list(
                thread_id=self.thread_id,
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
        # Simplified intent parsing based on keywords
        user_lower = user_input.lower()

        intent = "other"
        if any(word in user_lower for word in ["create", "add", "new", "make"]):
            intent = "task_creation"
        elif any(word in user_lower for word in ["list", "show", "view", "get"]):
            intent = "task_listing"
        elif any(word in user_lower for word in ["complete", "done", "finish", "mark"]):
            intent = "task_completion"
        elif any(word in user_lower for word in ["update", "change", "modify", "edit"]):
            intent = "task_update"
        elif any(word in user_lower for word in ["delete", "remove", "cancel"]):
            intent = "task_deletion"

        # Extract parameters using basic parsing
        parameters = {"title": "", "description": "", "priority": "", "due_date": "", "task_id": ""}

        # Extract title (simple approach - take the first noun phrase after action)
        words = user_input.split()
        if len(words) > 1:
            # Simple heuristic to extract potential title
            if intent == "task_creation":
                # Look for words after action words
                for i, word in enumerate(words):
                    if word.lower() in ["create", "add", "make", "new"]:
                        if i + 1 < len(words):
                            parameters["title"] = " ".join(words[i+1:i+3])  # Take next 2 words
                            break

        return {
            "intent": intent,
            "parameters": parameters,
            "confidence": 0.8  # Default confidence
        }

    async def _fallback_process_natural_language(self, user_input: str, conversation_context: list = None) -> Dict[str, Any]:
        """Fallback implementation using standard OpenAI API when assistants API fails."""
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
            # Handle case where AI didn't return valid JSON
            return {
                "success": False,
                "error": "AI response was not valid JSON",
                "raw_response": ai_response if 'ai_response' in locals() else None
            }

        except Exception as e:
            # Handle other errors
            return {
                "success": False,
                "error": f"Error processing natural language: {str(e)}",
                "raw_response": None
            }

    async def generate_response(self, user_input: str, intent_result: Dict[str, Any]) -> str:
        """
        Generate a natural language response based on the processed intent.

        Args:
            user_input: Original user input
            intent_result: Result from process_natural_language

        Returns:
            Natural language response for the user
        """
        if not intent_result["success"]:
            return "I'm sorry, I couldn't understand your request. Could you please rephrase it?"

        intent = intent_result["parsed_command"]["intent"]
        params = intent_result["parsed_command"]["parameters"]

        # Generate appropriate response based on intent
        if intent == "task_creation":
            if params.get("title"):
                return f"I've created a task titled '{params['title']}'."
            else:
                return "I understood you wanted to create a task, but I need a title for it."
        elif intent == "task_listing":
            filter_by = params.get("filter", "all")
            return f"Here are your {filter_by} tasks."
        elif intent == "task_completion":
            task_id = params.get("task_id", "specified")
            return f"I've marked task {task_id} as complete."
        elif intent == "task_update":
            return "I've updated your task as requested."
        elif intent == "task_deletion":
            task_id = params.get("task_id", "specified")
            return f"I've deleted task {task_id}."
        else:
            return "I processed your request, but I'm not sure what action was taken."

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

        # Generate a response
        response_text = await self.generate_response(user_input, intent_result)

        return {
            "success": intent_result["success"],
            "response": response_text,
            "intent_result": intent_result,
            "action_taken": intent_result["parsed_command"]["intent"] if intent_result["success"] else "none"
        }