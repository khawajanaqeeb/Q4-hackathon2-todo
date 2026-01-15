"""
Todo Command Interpreter Agent

Translates Natural Language Processing results into specific API commands for the todo system.
"""

from typing import Dict, Any, Optional
from enum import Enum
from .nlp_agent import NLPResult, Intent, EntityType


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class APICommand:
    def __init__(self, method: HttpMethod, endpoint: str, data: Optional[Dict[str, Any]] = None):
        self.method = method
        self.endpoint = endpoint
        self.data = data or {}


class TodoCommandInterpreterAgent:
    """
    Translates NLP results to specific API operations and transforms natural language
    entities to API-compatible parameters.
    """

    def __init__(self):
        self.priority_mapping = {
            "high": "high",
            "urgent": "high",
            "important": "high",
            "medium": "medium",
            "normal": "medium",
            "low": "low"
        }

        self.category_mapping = {
            "work": "work",
            "personal": "personal",
            "shopping": "shopping",
            "health": "health",
            "family": "family",
            "home": "home"
        }

    def interpret(self, nlp_result: NLPResult) -> APICommand:
        """
        Main method to interpret NLP results and return API command
        """
        intent = nlp_result.intent
        entities = nlp_result.entities

        if intent == Intent.ADD_TODO:
            return self._interpret_add_todo(nlp_result)
        elif intent == Intent.LIST_TODOS:
            return self._interpret_list_todos(nlp_result)
        elif intent == Intent.COMPLETE_TODO:
            return self._interpret_complete_todo(nlp_result)
        elif intent == Intent.DELETE_TODO:
            return self._interpret_delete_todo(nlp_result)
        elif intent == Intent.MODIFY_TODO:
            return self._interpret_modify_todo(nlp_result)
        elif intent == Intent.SEARCH_TODOS:
            return self._interpret_search_todos(nlp_result)
        elif intent == Intent.HELP:
            return self._interpret_help(nlp_result)
        else:
            # For unknown intents, return a generic help command
            return self._interpret_help(nlp_result)

    def _interpret_add_todo(self, nlp_result: NLPResult) -> APICommand:
        """
        Handle add todo commands
        """
        # Extract content from the original text (we need to extract the actual task content)
        # For now, we'll create a placeholder and assume the task content comes from elsewhere
        # In a real implementation, we'd extract the actual task content from the input

        data = {"content": "todo content extracted from input"}

        # Add priority if specified
        if EntityType.PRIORITY.value in nlp_result.entities:
            priority = nlp_result.entities[EntityType.PRIORITY.value].lower()
            if priority in self.priority_mapping:
                data["priority"] = self.priority_mapping[priority]

        # Add due date if specified
        if EntityType.DATE.value in nlp_result.entities:
            data["due_date"] = nlp_result.entities[EntityType.DATE.value]

        # Add category if specified
        if EntityType.CATEGORY.value in nlp_result.entities:
            category = nlp_result.entities[EntityType.CATEGORY.value].lower()
            if category in self.category_mapping:
                data["category"] = self.category_mapping[category]

        return APICommand(HttpMethod.POST, "/api/todos", data)

    def _interpret_list_todos(self, nlp_result: NLPResult) -> APICommand:
        """
        Handle list todos commands
        """
        # Build query parameters based on entities
        params = {}

        # Add priority filter if specified
        if EntityType.PRIORITY.value in nlp_result.entities:
            priority = nlp_result.entities[EntityType.PRIORITY.value].lower()
            if priority in self.priority_mapping:
                params["priority"] = self.priority_mapping[priority]

        # Add category filter if specified
        if EntityType.CATEGORY.value in nlp_result.entities:
            category = nlp_result.entities[EntityType.CATEGORY.value].lower()
            if category in self.category_mapping:
                params["category"] = self.category_mapping[category]

        # Construct endpoint with query parameters
        endpoint = "/api/todos"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"/api/todos?{param_str}"

        return APICommand(HttpMethod.GET, endpoint)

    def _interpret_complete_todo(self, nlp_result: NLPResult) -> APICommand:
        """
        Handle complete todo commands
        """
        # Extract todo ID from entities (number entity)
        todo_id = 1  # Default to 1 if no ID specified

        if EntityType.NUMBER.value in nlp_result.entities:
            try:
                todo_id = int(nlp_result.entities[EntityType.NUMBER.value])
            except ValueError:
                # If it's a word like "first", "second", etc., we'd need more sophisticated parsing
                todo_id = 1

        # For now, we'll use a placeholder ID
        # In a real implementation, we'd resolve the ID based on context or user input
        return APICommand(HttpMethod.PUT, f"/api/todos/{todo_id}", {"completed": True})

    def _interpret_delete_todo(self, nlp_result: NLPResult) -> APICommand:
        """
        Handle delete todo commands
        """
        # Extract todo ID from entities (number entity)
        todo_id = 1  # Default to 1 if no ID specified

        if EntityType.NUMBER.value in nlp_result.entities:
            try:
                todo_id = int(nlp_result.entities[EntityType.NUMBER.value])
            except ValueError:
                # If it's a word like "first", "second", etc., we'd need more sophisticated parsing
                todo_id = 1

        # For now, we'll use a placeholder ID
        # In a real implementation, we'd resolve the ID based on context or user input
        return APICommand(HttpMethod.DELETE, f"/api/todos/{todo_id}")

    def _interpret_modify_todo(self, nlp_result: NLPResult) -> APICommand:
        """
        Handle modify todo commands
        """
        # Extract todo ID from entities (number entity)
        todo_id = 1  # Default to 1 if no ID specified

        if EntityType.NUMBER.value in nlp_result.entities:
            try:
                todo_id = int(nlp_result.entities[EntityType.NUMBER.value])
            except ValueError:
                # If it's a word like "first", "second", etc., we'd need more sophisticated parsing
                todo_id = 1

        # Build data payload with modifications
        data = {}

        # Add priority if specified
        if EntityType.PRIORITY.value in nlp_result.entities:
            priority = nlp_result.entities[EntityType.PRIORITY.value].lower()
            if priority in self.priority_mapping:
                data["priority"] = self.priority_mapping[priority]

        # Add due date if specified
        if EntityType.DATE.value in nlp_result.entities:
            data["due_date"] = nlp_result.entities[EntityType.DATE.value]

        # Add category if specified
        if EntityType.CATEGORY.value in nlp_result.entities:
            category = nlp_result.entities[EntityType.CATEGORY.value].lower()
            if category in self.category_mapping:
                data["category"] = self.category_mapping[category]

        return APICommand(HttpMethod.PUT, f"/api/todos/{todo_id}", data)

    def _interpret_search_todos(self, nlp_result: NLPResult) -> APICommand:
        """
        Handle search commands
        """
        # Build search parameters based on entities
        params = {}

        # Add keyword search if available
        if EntityType.KEYWORD.value in nlp_result.entities:
            params["search"] = nlp_result.entities[EntityType.KEYWORD.value]
        elif EntityType.CATEGORY.value in nlp_result.entities:
            category = nlp_result.entities[EntityType.CATEGORY.value].lower()
            if category in self.category_mapping:
                params["category"] = self.category_mapping[category]

        # Add priority filter if specified
        if EntityType.PRIORITY.value in nlp_result.entities:
            priority = nlp_result.entities[EntityType.PRIORITY.value].lower()
            if priority in self.priority_mapping:
                params["priority"] = self.priority_mapping[priority]

        # Construct search endpoint
        endpoint = "/api/todos/search"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"/api/todos/search?{param_str}"

        return APICommand(HttpMethod.GET, endpoint)

    def _interpret_help(self, nlp_result: NLPResult) -> APICommand:
        """
        Handle help commands
        """
        return APICommand(HttpMethod.GET, "/api/help")


# Example usage
if __name__ == "__main__":
    from agents.nlp_agent import NLPAgent

    # Initialize both agents
    nlp_agent = NLPAgent()
    interpreter_agent = TodoCommandInterpreterAgent()

    # Test examples
    test_inputs = [
        "Add a new todo to buy groceries tomorrow",
        "Show me my todos",
        "Mark the first todo as complete",
        "Delete the urgent task",
        "Update the shopping list priority to high",
        "Find tasks with work category",
        "Help me"
    ]

    for test_input in test_inputs:
        # Process with NLP agent
        nlp_result = nlp_agent.process(test_input)

        # Interpret with command interpreter
        api_command = interpreter_agent.interpret(nlp_result)

        print(f"Input: '{test_input}'")
        print(f"Intent: {nlp_result.intent}")
        print(f"Entities: {nlp_result.entities}")
        print(f"API Command: {api_command.method} {api_command.endpoint}")
        if api_command.data:
            print(f"Data: {api_command.data}")
        print("---")