import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from ..config import settings
import json


class AgentRunner:
    """Service class for running OpenAI agents and processing natural language."""

    def __init__(self):
        """Initialize AgentRunner with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def process_natural_language(self, user_input: str, conversation_context: list = None) -> Dict[str, Any]:
        """
        Process natural language input and return structured response.

        Args:
            user_input: Natural language command from user
            conversation_context: Previous conversation messages for context

        Returns:
            Dictionary with parsed command and parameters
        """
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