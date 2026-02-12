import asyncio
from typing import Dict, Any, Optional
from ..config import settings
import json
import re

# Import OpenAI conditionally to avoid crashes when it's not available
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

# Function definition for Chat Completions function calling
PARSE_TODO_FUNCTION = {
    "type": "function",
    "function": {
        "name": "parse_todo_command",
        "description": "Parse a natural language command related to todo/task management",
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": [
                        "task_creation", "task_listing", "task_completion",
                        "task_update", "task_deletion", "other"
                    ],
                    "description": "The type of task operation the user wants"
                },
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title if applicable"},
                        "description": {"type": "string", "description": "Task description if applicable"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "Priority level"},
                        "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format"},
                        "task_id": {"type": "integer", "description": "Numeric task ID if the user mentions one"},
                        "status": {"type": "string", "enum": ["all", "completed", "pending"], "description": "Status filter for listing"},
                    },
                    "required": []
                },
                "confidence": {"type": "number", "description": "Confidence level from 0.0 to 1.0"}
            },
            "required": ["intent", "parameters", "confidence"]
        }
    }
}

SYSTEM_PROMPT = (
    "You are a task management assistant that parses user commands. "
    "Interpret the user's message and call parse_todo_command with the structured intent. "
    "For task operations referencing a specific task by numeric ID, include task_id. "
    "For task operations referencing a task by name/title, include title. "
    "Only include parameters that are clearly provided by the user."
)

# Greeting / help words for instant local detection (no API call needed)
GREETING_WORDS = [
    "hi", "hello", "hey", "greetings", "howdy", "sup", "yo",
    "good morning", "good afternoon", "good evening",
]
HELP_PHRASES = ["help", "what can you do", "how do i", "how to"]


class AgentRunner:
    """Service class for running OpenAI agents and processing natural language."""

    def __init__(self):
        """Initialize AgentRunner with OpenAI client."""
        if OPENAI_AVAILABLE:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    # ------------------------------------------------------------------
    # Main entry: process natural language
    # ------------------------------------------------------------------
    async def process_natural_language(
        self, user_input: str, conversation_context: list = None
    ) -> Dict[str, Any]:
        """Process natural language input via Chat Completions function calling (single HTTP call)."""

        # 1. Instant local detection for greetings / help (no API call)
        local = self._detect_greeting_or_help(user_input)
        if local:
            return {"success": True, "parsed_command": local, "raw_response": user_input}

        # 2. If OpenAI unavailable, fall back to keyword parser
        if not OPENAI_AVAILABLE or not self.client:
            parsed = self._parse_intent_from_input(user_input)
            return {"success": True, "parsed_command": parsed, "raw_response": user_input}

        # 3. Single Chat Completions call with function calling
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if conversation_context:
                messages.extend(conversation_context[-4:])  # last 4 for context
            messages.append({"role": "user", "content": user_input})

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                tools=[PARSE_TODO_FUNCTION],
                tool_choice={"type": "function", "function": {"name": "parse_todo_command"}},
                temperature=0.1,
                max_tokens=300,
            )

            # Extract function call arguments
            choice = response.choices[0]
            if choice.message.tool_calls:
                args_json = choice.message.tool_calls[0].function.arguments
                parsed = json.loads(args_json)
                return {"success": True, "parsed_command": parsed, "raw_response": user_input}

            # If no tool call returned, fall back to keyword parser
            parsed = self._parse_intent_from_input(user_input)
            return {"success": True, "parsed_command": parsed, "raw_response": user_input}

        except Exception as e:
            print(f"Chat Completions error: {e}")
            parsed = self._parse_intent_from_input(user_input)
            return {"success": True, "parsed_command": parsed, "raw_response": user_input}

    # ------------------------------------------------------------------
    # Local greeting / help detection (zero latency)
    # ------------------------------------------------------------------
    @staticmethod
    def _detect_greeting_or_help(user_input: str) -> Optional[Dict[str, Any]]:
        user_lower = user_input.lower().strip()
        for g in GREETING_WORDS:
            if user_lower == g or user_lower.startswith(g + " ") or \
               user_lower.startswith(g + "!") or user_lower.startswith(g + ","):
                return {"intent": "greeting", "parameters": {}, "confidence": 0.95}
        for phrase in HELP_PHRASES:
            if phrase in user_lower:
                return {"intent": "help", "parameters": {}, "confidence": 0.9}
        return None

    # ------------------------------------------------------------------
    # Keyword-based fallback parser (no API call)
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_intent_from_input(user_input: str) -> Dict[str, Any]:
        """Parse intent from input using keyword matching (offline fallback)."""
        user_lower = user_input.lower().strip()
        words = user_input.split()

        # Detect greetings / help (shouldn't reach here normally)
        for g in GREETING_WORDS:
            if user_lower == g or user_lower.startswith(g + " ") or \
               user_lower.startswith(g + "!") or user_lower.startswith(g + ","):
                return {"intent": "greeting", "parameters": {}, "confidence": 0.95}
        for phrase in HELP_PHRASES:
            if phrase in user_lower:
                return {"intent": "help", "parameters": {}, "confidence": 0.9}

        # Determine intent
        is_question = user_lower.startswith(("what", "which", "how many"))
        intent = "other"

        if is_question and any(w in user_lower for w in ["completed", "done", "pending", "task", "todo", "left", "remaining"]):
            intent = "task_listing"
        elif any(w in user_lower for w in ["create", "add", "new", "make", "remember"]):
            intent = "task_creation"
        elif any(w in user_lower for w in ["list", "show", "view", "get", "my task", "all task", "pending"]):
            intent = "task_listing"
        elif any(w in user_lower for w in ["complete", "done", "finish", "mark"]):
            intent = "task_completion"
        elif any(w in user_lower for w in ["update", "change", "modify", "edit", "rename"]):
            intent = "task_update"
        elif any(w in user_lower for w in ["delete", "remove", "cancel"]):
            intent = "task_deletion"
        elif any(w in user_lower for w in ["sort", "order", "arrange"]):
            intent = "task_listing"

        parameters: Dict[str, Any] = {}

        if intent == "task_creation":
            filler_words = {"a", "an", "the", "new", "task", "todo", "to", "called", "named", "titled", "need", "i"}
            action_words = {"create", "add", "make", "new", "remember"}
            found_action = False
            title_words = []
            for word in words:
                if not found_action:
                    if word.lower() in action_words:
                        found_action = True
                    continue
                if word.lower() in filler_words and not title_words:
                    continue
                title_words.append(word)
            if title_words:
                parameters["title"] = " ".join(title_words)
            if "high" in user_lower:
                parameters["priority"] = "high"
            elif "low" in user_lower:
                parameters["priority"] = "low"

        elif intent == "task_listing":
            if any(w in user_lower for w in ["pending", "remaining", "left", "incomplete"]):
                parameters["status"] = "pending"
            elif any(w in user_lower for w in ["completed", "done", "finished"]):
                parameters["status"] = "completed"

        elif intent in ("task_deletion", "task_completion", "task_update"):
            id_match = re.search(r'\b(\d+)\b', user_input)
            if id_match:
                parameters["task_id"] = id_match.group(1)
            else:
                action_words_set = {
                    "delete", "remove", "cancel", "complete", "done", "finish",
                    "mark", "update", "change", "modify", "edit", "rename"
                }
                filler_set = {"the", "a", "an", "task", "todo", "my", "as", "is"}
                title_words = []
                found_action = False
                for word in words:
                    if not found_action:
                        if word.lower() in action_words_set:
                            found_action = True
                        continue
                    if word.lower() in filler_set and not title_words:
                        continue
                    if intent == "task_update" and word.lower() == "to" and title_words:
                        break
                    title_words.append(word)
                if title_words:
                    parameters["task_id"] = " ".join(title_words)

            if intent == "task_update":
                quoted_match = re.search(r"""['"](.+?)['"]""", user_input)
                if quoted_match:
                    parameters["title"] = quoted_match.group(1)
                else:
                    to_pattern = re.search(r'\bto\s+(.+)$', user_input, re.IGNORECASE)
                    if to_pattern:
                        new_title = to_pattern.group(1).strip()
                        if new_title and new_title.lower() not in ("done", "complete", "completed"):
                            parameters["title"] = new_title

        return {"intent": intent, "parameters": parameters, "confidence": 0.8}

    # ------------------------------------------------------------------
    # Response generation (pure string formatting, no API call)
    # ------------------------------------------------------------------
    async def generate_response(
        self, user_input: str, intent_result: Dict[str, Any], mcp_result: Dict[str, Any] = None
    ) -> str:
        """Generate a natural language response based on the processed intent."""
        if not intent_result.get("success"):
            return "I'm sorry, I couldn't understand your request. Could you please rephrase it?"

        intent = intent_result["parsed_command"]["intent"]
        params = intent_result["parsed_command"].get("parameters", {})

        if intent == "greeting":
            return (
                "Hello! I'm your AI Todo Assistant. I can help you manage your tasks. "
                "Try saying things like:\n"
                "- \"Add a task to buy groceries\"\n"
                "- \"Show my tasks\"\n"
                "- \"Delete task <id>\"\n"
                "- \"Mark task <id> as complete\""
            )

        if intent == "help":
            return (
                "I can help you with the following:\n"
                "- Create tasks: \"Add a task to buy groceries\"\n"
                "- List tasks: \"Show my tasks\"\n"
                "- Complete tasks: \"Mark task <id> as done\"\n"
                "- Delete tasks: \"Delete task <id>\"\n"
                "- Update tasks: \"Update task <id> title to new title\""
            )

        inner_result = mcp_result.get("result", {}) if mcp_result else {}
        inner_success = inner_result.get("success", False) if isinstance(inner_result, dict) else False

        if intent == "task_creation":
            if mcp_result and mcp_result.get("success") and inner_success:
                return inner_result.get("message", f"Task '{params.get('title', '')}' created successfully!")
            elif mcp_result and mcp_result.get("success") and not inner_success:
                return f"Sorry, I couldn't create the task: {inner_result.get('error', 'Unknown error')}"
            elif params.get("title"):
                return f"I've created a task titled '{params['title']}'."
            else:
                return "I understood you wanted to create a task, but I need a title for it. Try: \"Add a task to buy groceries\""

        elif intent == "task_listing":
            if mcp_result and mcp_result.get("success") and inner_success:
                tasks = inner_result.get("tasks", [])
                count = inner_result.get("count", len(tasks))
                if count == 0:
                    return "You don't have any tasks yet. Try adding one: \"Add a task to buy groceries\""
                lines = [f"Here are your tasks ({count} total):\n"]
                for i, task in enumerate(tasks, 1):
                    status_str = "Done" if task.get("completed") else "Pending"
                    priority = task.get("priority", "medium").capitalize()
                    lines.append(f"{i}. [{status_str}] {task['title']} (Priority: {priority}, ID: {task['id']})")
                return "\n".join(lines)
            elif mcp_result and mcp_result.get("success") and not inner_success:
                return f"Sorry, I couldn't list your tasks: {inner_result.get('error', 'Unknown error')}"
            return "Here are your tasks."

        elif intent == "task_completion":
            if mcp_result and mcp_result.get("success") and inner_success:
                return inner_result.get("message", "Task marked as complete!")
            elif mcp_result and mcp_result.get("success") and not inner_success:
                return f"Sorry, I couldn't complete the task: {inner_result.get('error', 'Unknown error')}. Try: \"Show my tasks\" first to see IDs."
            return "I need a task ID to mark as complete. Try: \"Show my tasks\" first to see IDs."

        elif intent == "task_update":
            if mcp_result and mcp_result.get("success") and inner_success:
                return inner_result.get("message", "Task updated successfully!")
            elif mcp_result and mcp_result.get("success") and not inner_success:
                return f"Sorry, I couldn't update the task: {inner_result.get('error', 'Unknown error')}"
            return "I've updated your task as requested."

        elif intent == "task_deletion":
            if mcp_result and mcp_result.get("success") and inner_success:
                return inner_result.get("message", "Task deleted successfully!")
            elif mcp_result and mcp_result.get("success") and not inner_success:
                return f"Sorry, I couldn't delete the task: {inner_result.get('error', 'Unknown error')}. Try: \"Show my tasks\" first to see IDs."
            return "I need a task ID to delete. Try: \"Show my tasks\" first to see IDs."

        else:
            return (
                f"I'm not sure what you mean by \"{user_input}\". "
                "I can help you manage tasks — try \"Add a task\", \"Show my tasks\", or say \"help\" for more options."
            )

    # ------------------------------------------------------------------
    # Public API used by chat.py
    # ------------------------------------------------------------------
    async def run_agent(self, user_input: str, conversation_context: list = None) -> Dict[str, Any]:
        """Run the full agent cycle: process input, determine action, generate response."""
        intent_result = await self.process_natural_language(user_input, conversation_context)
        response_text = await self.generate_response(user_input, intent_result)

        return {
            "success": intent_result["success"],
            "response": response_text,
            "intent_result": intent_result,
            "action_taken": intent_result["parsed_command"]["intent"] if intent_result["success"] else "none"
        }

    async def generate_response_with_mcp(
        self, user_input: str, intent_result: Dict[str, Any], mcp_result: Dict[str, Any]
    ) -> str:
        """Generate response including MCP tool results."""
        return await self.generate_response(user_input, intent_result, mcp_result)
