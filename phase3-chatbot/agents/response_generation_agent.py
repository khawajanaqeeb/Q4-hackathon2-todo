"""
Response Generation Agent

Creates natural language responses from API results and system events for the Todo AI Chatbot,
ensuring responses are conversational, informative, and personalized.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ResponseType(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    INFORMATIONAL = "INFORMATIONAL"
    CONFIRMATION = "CONFIRMATION"
    HELP = "HELP"


class ResponseGenerationAgent:
    """
    Creates natural language responses from API results and system events for the Todo AI Chatbot.
    """

    def __init__(self, response_style: str = "friendly"):
        self.response_style = response_style
        self.success_templates = {
            "create": [
                "I've added '{content}' to your todo list.",
                "Got it! I've created a task for '{content}'.",
                "Sure thing! '{content}' has been added to your tasks."
            ],
            "update": [
                "I've updated your task '{content}' with the changes.",
                "Your task '{content}' has been updated successfully.",
                "Changes applied to '{content}'."
            ],
            "complete": [
                "I've marked '{content}' as completed.",
                "Great job! '{content}' has been marked as done.",
                "'{content}' is now marked as completed."
            ],
            "delete": [
                "I've removed '{content}' from your todo list.",
                "'{content}' has been deleted.",
                "Done! '{content}' is gone."
            ],
            "list": [
                "Here are your {count} tasks:",
                "I found {count} tasks for you:",
                "Here's what you need to do:"
            ]
        }

        self.error_templates = {
            "404": [
                "I couldn't find that task. It might have been deleted or doesn't exist.",
                "Sorry, but I couldn't locate that task.",
                "The task you're looking for doesn't seem to exist."
            ],
            "401": [
                "You don't have permission to perform that action.",
                "I'm sorry, but you're not authorized to do that.",
                "Authentication required for this action."
            ],
            "500": [
                "Something went wrong on my end. Could you try again?",
                "I'm experiencing some technical difficulties. Please try again later.",
                "Sorry, I couldn't complete that action. Something went wrong."
            ],
            "default": [
                "I'm sorry, but I couldn't complete that action: {message}",
                "There was an issue with your request: {message}",
                "Sorry, I encountered an error: {message}"
            ]
        }

    def generate_response(self, api_response: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Main response generation method.
        """
        status_code = api_response.get('status_code', 200)

        # Check if it's an error response
        if api_response.get('error') or status_code >= 400:
            error_detail = api_response.get('error')

            # If no direct error but status code indicates error, extract from data
            if not error_detail and status_code >= 400:
                error_detail = api_response.get('data', {}).get('detail', f'Error occurred with status {status_code}')

            # Create an error dict with status code for proper template selection
            error_dict = {
                'detail': error_detail,
                'status_code': status_code
            }

            return self._generate_error_response(error_dict, user_context)
        else:
            return self._generate_success_response(api_response, user_context)

    def _generate_success_response(self, api_response: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> str:
        """
        Handle successful operations.
        """
        data = api_response.get('data', {})
        status_code = api_response.get('status_code', 200)

        # Determine operation type based on status code and data
        if status_code in [200, 201]:  # GET or POST
            if 'content' in data or 'items' in data:
                if 'items' in data:  # This is a list operation
                    return self.format_list_response(data['items'], "Your tasks")
                else:  # This is a single item operation
                    operation = self._determine_operation_from_status(status_code, data)
                    return self.format_success_response(operation, data)
        elif status_code == 204:  # DELETE
            return self.format_success_response('delete', data)
        elif status_code in [202, 200]:  # PUT/UPDATE
            return self.format_success_response('update', data)

        return "Operation completed successfully."

    def _generate_error_response(self, error: str, user_context: Optional[Dict[str, Any]]) -> str:
        """
        Handle errors gracefully.
        """
        # Extract status code if it's available in the error string
        status_code = 500  # Default to 500
        error_detail = str(error)

        # If error is a dictionary (which can happen if the error contains status info)
        if isinstance(error, dict):
            error_detail = error.get('detail', str(error))
            status_code = error.get('status_code', 500)
        # If error string contains status information, try to extract it
        elif 'status' in error_detail.lower():
            # This is a fallback case where error string might contain status info
            if '404' in error_detail:
                status_code = 404
            elif '401' in error_detail:
                status_code = 401
            elif '500' in error_detail:
                status_code = 500

        # Map status code to error template
        status_str = str(status_code)
        if status_str in self.error_templates:
            template = self.error_templates[status_str][0]  # Pick first template
        else:
            template = self.error_templates['default'][0]

        # Personalize response based on context
        response = template.format(message=error_detail)
        return self.personalize_response(response, user_context or {})

    def format_success_response(self, operation: str, data: Dict[str, Any]) -> str:
        """
        Handle successful operations.
        """
        if operation in self.success_templates:
            template = self.success_templates[operation][0]  # Pick first template
        else:
            return f"Operation completed successfully: {data}"

        # Fill in the template with data
        if 'content' in data:
            response = template.format(content=data['content'])
        elif 'title' in data:
            response = template.format(content=data['title'])
        else:
            response = template.format(content="the task")

        return response

    def format_error_response(self, error: str, user_friendly_msg: str) -> str:
        """
        Handle errors gracefully.
        """
        # If a user-friendly message is provided, use it
        if user_friendly_msg:
            return user_friendly_msg

        # Otherwise, use the error directly
        return f"I'm sorry, but an error occurred: {error}"

    def format_list_response(self, items: List[Dict[str, Any]], title: str) -> str:
        """
        Format lists of todos.
        """
        if not items:
            return "You don't have any tasks on your list."

        count = len(items)
        header_template = self.success_templates['list'][0]
        response = header_template.format(count=count) + "\n\n"

        # Format each item
        for i, item in enumerate(items[:10]):  # Limit to 10 items to avoid overwhelming user
            item_str = self._format_todo_item(item, i+1)
            response += f"{item_str}\n"

        if len(items) > 10:
            response += f"\n... and {len(items) - 10} more items."

        return response

    def format_confirmation_request(self, action: str, details: Dict[str, Any]) -> str:
        """
        Generate confirmation requests.
        """
        if action == "delete":
            return f"Are you sure you want to delete '{details.get('content', 'this task')}'? This cannot be undone."
        elif action == "complete":
            return f"Do you want to mark '{details.get('content', 'this task')}' as completed?"
        else:
            return f"Please confirm: {action} {details.get('content', 'this item')}?"

    def personalize_response(self, response: str, user_profile: Dict[str, Any]) -> str:
        """
        Customize response for user.
        """
        # Add user's name if available
        if user_profile and user_profile.get('name'):
            name = user_profile['name']
            # Add name at the beginning or end depending on response type
            if response.startswith("I've"):
                response = response.replace("I've", f"{name}, I've", 1)
            else:
                response = f"{name}, {response}"

        # Adjust tone based on user preferences
        if user_profile and user_profile.get('tone') == 'formal':
            response = response.replace("!", ".").replace("?", ".")

        return response

    def maintain_context(self, response: str, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Preserve conversation continuity.
        """
        # This could be enhanced to reference previous conversations
        # For now, we'll just return the response as is
        return response

    def _determine_operation_from_status(self, status_code: int, data: Dict[str, Any]) -> str:
        """
        Determine operation type based on status code and data.
        """
        if status_code == 201:  # Created
            return 'create'
        elif status_code == 200 and data.get('completed') is not None:
            return 'complete'
        elif status_code == 200 and 'content' in data:
            return 'update'
        elif status_code == 200:
            return 'list'  # Assume list if status is 200 and it's not create/update/complete
        else:
            return 'unknown'

    def _format_todo_item(self, item: Dict[str, Any], index: int) -> str:
        """
        Format a single todo item for display.
        """
        content = item.get('content', item.get('title', 'Untitled'))
        status = "✓" if item.get('completed', False) else "○"
        priority = item.get('priority', 'medium')

        # Format with priority and status
        formatted = f"{index}. [{status}] {content}"

        if priority != 'medium':
            formatted += f" (Priority: {priority})"

        return formatted


# Example usage
if __name__ == "__main__":
    # Initialize the response generation agent
    response_agent = ResponseGenerationAgent()

    # Example API responses
    success_response = {
        'status_code': 201,
        'data': {
            'id': 123,
            'content': 'Buy groceries',
            'priority': 'high',
            'completed': False
        }
    }

    list_response = {
        'status_code': 200,
        'data': {
            'items': [
                {'id': 1, 'content': 'Buy groceries', 'completed': False, 'priority': 'high'},
                {'id': 2, 'content': 'Walk the dog', 'completed': True, 'priority': 'medium'}
            ]
        }
    }

    error_response = {
        'status_code': 404,
        'error': 'Task not found'
    }

    # Generate responses
    print("Success response:", response_agent.generate_response(success_response))
    print("\nList response:", response_agent.generate_response(list_response))
    print("\nError response:", response_agent.generate_response(error_response))

    # Example with user context
    user_context = {'name': 'John', 'tone': 'friendly'}
    personalized_response = response_agent.personalize_response(
        "I've added 'Buy groceries' to your todo list.",
        user_context
    )
    print("\nPersonalized response:", personalized_response)