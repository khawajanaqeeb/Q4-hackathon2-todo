"""
API Integration Agent

Handles communication between the chatbot and the existing todo backend API, managing authentication,
request formatting, and response processing.
"""

import json
import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin
import time
from datetime import datetime, timedelta


class APIResponse:
    """Represents the response from an API call."""

    def __init__(self, status_code: int, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.status_code = status_code
        self.data = data or {}
        self.error = error
        self.timestamp = datetime.now()

    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return 200 <= self.status_code < 300

    def is_error(self) -> bool:
        """Check if the response indicates an error."""
        return not self.is_success()


class APICommand:
    """Represents an API command to be executed."""

    def __init__(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None):
        self.method = method.upper()  # Convert to uppercase
        self.endpoint = endpoint
        self.data = data or {}
        self.headers = headers or {}


class APIIntegrationAgent:
    """
    Handles communication between the chatbot and the existing todo backend API.
    """

    def __init__(self, base_url: str, jwt_token: Optional[str] = None,
                 timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        self.jwt_token = jwt_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.auth_headers = {}

        # Initialize authentication if token is provided
        if self.jwt_token:
            self._set_auth_headers(self.jwt_token)

    def _set_auth_headers(self, token: str) -> None:
        """Set authentication headers with the provided token."""
        self.auth_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def authenticate(self) -> bool:
        """
        Handle authentication process.
        In a real implementation, this would fetch a token from an auth endpoint.
        """
        # For now, we assume the token was provided during initialization
        # In a real scenario, this would make a request to an authentication endpoint
        return bool(self.jwt_token)

    def send_request(self, api_command: APICommand) -> APIResponse:
        """
        Send API command and return response.
        """
        url = urljoin(self.base_url, api_command.endpoint)

        # Combine auth headers with command headers
        headers = {**self.auth_headers, **api_command.headers}

        # Prepare request data
        json_data = json.dumps(api_command.data) if api_command.data else None

        # Try the request with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=api_command.method,
                    url=url,
                    headers=headers,
                    data=json_data,
                    timeout=self.timeout
                )

                # Return response object
                try:
                    response_data = response.json() if response.content else {}
                except json.JSONDecodeError:
                    response_data = {}

                return APIResponse(response.status_code, response_data)

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    # Last attempt - return error response
                    return APIResponse(500, error=f"Request failed after {self.max_retries} attempts: {str(e)}")

                # Wait before retrying (exponential backoff)
                time.sleep(2 ** attempt)

        # This shouldn't be reached, but just in case
        return APIResponse(500, error="Unexpected error in request processing")

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format API response for chat display.
        """
        if not response_data:
            return "Operation completed successfully."

        # Format different types of responses
        if 'content' in response_data or 'title' in response_data:
            # This looks like a todo object
            todo_info = []
            if 'content' in response_data:
                todo_info.append(f"Task: {response_data['content']}")
            if 'title' in response_data:
                todo_info.append(f"Title: {response_data['title']}")
            if 'priority' in response_data:
                todo_info.append(f"{response_data['priority']} priority")
            if 'completed' in response_data:
                status = "completed" if response_data['completed'] else "pending"
                todo_info.append(f"Status: {status}")

            return " | ".join(todo_info)

        elif 'items' in response_data or isinstance(response_data, list):
            # This looks like a list of todos
            items = response_data.get('items', response_data)
            if not items:
                return "No items found."

            formatted_items = []
            for i, item in enumerate(items[:5]):  # Limit to first 5 items
                item_desc = f"{i+1}. "
                if 'content' in item:
                    item_desc += item['content']
                elif 'title' in item:
                    item_desc += item['title']
                else:
                    item_desc += str(item)

                if 'priority' in item:
                    item_desc += f" ({item['priority']} priority)"

                formatted_items.append(item_desc)

            if len(items) > 5:
                formatted_items.append(f"... and {len(items) - 5} more")

            return "\\n".join(formatted_items)

        else:
            # Generic response
            return json.dumps(response_data, indent=2)

    def handle_error(self, error: str) -> str:
        """
        Process and respond to API errors.
        """
        # Map common error codes to user-friendly messages
        if "401" in error or "unauthorized" in error.lower():
            return "Authentication failed. Please check your credentials."
        elif "403" in error or "forbidden" in error.lower():
            return "Access denied. You don't have permission to perform this action."
        elif "404" in error or "not found" in error.lower():
            return "Item not found. Please check your request."
        elif "500" in error or "server error" in error.lower():
            return "Server error occurred. Please try again later."
        elif "timeout" in error.lower():
            return "Request timed out. Please try again."
        else:
            return f"An error occurred: {error}"

    def validate_response(self, response: APIResponse) -> bool:
        """
        Validate API response structure.
        """
        # Basic validation - response should have expected fields
        if response.is_error() and not response.error:
            return False

        # If it's a success response, data should be a dict or list
        if response.is_success():
            if not isinstance(response.data, (dict, list)) and response.data is not None:
                return False

        return True

    def apply_authentication(self, request: APICommand) -> APICommand:
        """
        Add authentication to requests.
        """
        # Add auth headers to the request
        request.headers.update(self.auth_headers)
        return request

    def transform_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform data to API format.
        """
        # Apply transformations to match the expected API format
        transformed = {}

        for key, value in data.items():
            # Convert common field names to expected API format
            if key == 'content':
                transformed['content'] = value
            elif key == 'description':
                transformed['description'] = value
            elif key == 'priority':
                # Ensure priority is in expected format (could be normalized)
                transformed['priority'] = value.lower()
            elif key == 'completed':
                # Convert to boolean - handle string representations
                if isinstance(value, str):
                    transformed['completed'] = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    transformed['completed'] = bool(value)
            elif key == 'due_date':
                transformed['due_date'] = value
            else:
                transformed[key] = value

        return transformed

    def get_todo(self, todo_id: int) -> APIResponse:
        """Get a specific todo by ID."""
        command = APICommand('GET', f'/api/todos/{todo_id}')
        return self.send_request(command)

    def get_todos(self, filters: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Get todos with optional filters."""
        endpoint = '/api/todos'
        if filters:
            # Add query parameters for filters
            query_params = '&'.join([f"{k}={v}" for k, v in filters.items()])
            endpoint = f"{endpoint}?{query_params}"

        command = APICommand('GET', endpoint)
        return self.send_request(command)

    def create_todo(self, content: str, priority: str = "medium",
                    completed: bool = False, due_date: Optional[str] = None) -> APIResponse:
        """Create a new todo."""
        data = {
            'content': content,
            'priority': priority,
            'completed': completed
        }

        if due_date:
            data['due_date'] = due_date

        command = APICommand('POST', '/api/todos', data)
        return self.send_request(command)

    def update_todo(self, todo_id: int, **kwargs) -> APIResponse:
        """Update a todo."""
        command = APICommand('PUT', f'/api/todos/{todo_id}', kwargs)
        return self.send_request(command)

    def delete_todo(self, todo_id: int) -> APIResponse:
        """Delete a todo."""
        command = APICommand('DELETE', f'/api/todos/{todo_id}')
        return self.send_request(command)


# Example usage
if __name__ == "__main__":
    # Initialize the API integration agent
    # Note: In a real scenario, you'd get the base URL and token from environment/config
    api_agent = APIIntegrationAgent(
        base_url="http://localhost:8000",
        jwt_token="your-jwt-token-here"
    )

    # Example: Create a new todo
    response = api_agent.create_todo(
        content="Buy groceries",
        priority="high",
        due_date="2023-12-25"
    )

    if response.is_success():
        print(f"Todo created successfully: {api_agent.format_response(response.data)}")
    else:
        print(f"Failed to create todo: {api_agent.handle_error(response.error or 'Unknown error')}")

    # Example: Get all todos
    response = api_agent.get_todos()
    if response.is_success():
        print(f"Todos: {api_agent.format_response(response.data)}")
    else:
        print(f"Failed to get todos: {api_agent.handle_error(response.error or 'Unknown error')}")