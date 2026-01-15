"""
Tests for the Response Generation Agent
"""

import pytest
from agents.response_generation_agent import ResponseGenerationAgent


def test_generate_success_response():
    """Test generating a response for a successful operation."""
    agent = ResponseGenerationAgent()

    api_response = {
        'status_code': 201,
        'data': {
            'id': 123,
            'content': 'Buy groceries',
            'priority': 'high',
            'completed': False
        }
    }

    response = agent.generate_response(api_response)

    assert 'Buy groceries' in response
    assert 'added' in response.lower() or 'created' in response.lower()


def test_generate_error_response():
    """Test generating a response for an error."""
    agent = ResponseGenerationAgent()

    api_response = {
        'status_code': 404,
        'error': 'Task not found'
    }

    response = agent.generate_response(api_response)

    assert 'sorry' in response.lower() or 'find' in response.lower()


def test_format_success_response_create():
    """Test formatting a success response for create operation."""
    agent = ResponseGenerationAgent()

    data = {
        'content': 'Buy groceries',
        'priority': 'high'
    }

    response = agent.format_success_response('create', data)

    assert 'Buy groceries' in response
    assert 'added' in response.lower() or 'created' in response.lower()


def test_format_success_response_update():
    """Test formatting a success response for update operation."""
    agent = ResponseGenerationAgent()

    data = {
        'content': 'Buy groceries',
        'priority': 'medium'
    }

    response = agent.format_success_response('update', data)

    assert 'Buy groceries' in response
    assert 'updated' in response.lower()


def test_format_success_response_complete():
    """Test formatting a success response for complete operation."""
    agent = ResponseGenerationAgent()

    data = {
        'content': 'Buy groceries',
        'completed': True
    }

    response = agent.format_success_response('complete', data)

    assert 'Buy groceries' in response
    assert 'completed' in response.lower() or 'marked' in response.lower()


def test_format_success_response_delete():
    """Test formatting a success response for delete operation."""
    agent = ResponseGenerationAgent()

    data = {
        'content': 'Buy groceries'
    }

    response = agent.format_success_response('delete', data)

    assert 'Buy groceries' in response
    assert 'removed' in response.lower() or 'deleted' in response.lower()


def test_format_list_response_empty():
    """Test formatting a list response when there are no items."""
    agent = ResponseGenerationAgent()

    items = []

    response = agent.format_list_response(items, "Your tasks")

    assert 'any tasks' in response or 'no' in response.lower()


def test_format_list_response_with_items():
    """Test formatting a list response with multiple items."""
    agent = ResponseGenerationAgent()

    items = [
        {'id': 1, 'content': 'Buy groceries', 'completed': False, 'priority': 'high'},
        {'id': 2, 'content': 'Walk the dog', 'completed': True, 'priority': 'medium'}
    ]

    response = agent.format_list_response(items, "Your tasks")

    assert 'Buy groceries' in response
    assert 'Walk the dog' in response
    assert '2' in response  # Should mention the count


def test_format_error_response():
    """Test formatting an error response."""
    agent = ResponseGenerationAgent()

    response = agent.format_error_response("Something went wrong", "I'm sorry, an error occurred")

    assert 'sorry' in response.lower()


def test_format_error_response_with_fallback():
    """Test formatting an error response with fallback message."""
    agent = ResponseGenerationAgent()

    response = agent.format_error_response("Something went wrong", "")

    assert 'Something went wrong' in response


def test_format_confirmation_request_delete():
    """Test formatting a confirmation request for delete action."""
    agent = ResponseGenerationAgent()

    details = {'content': 'Buy groceries'}

    response = agent.format_confirmation_request('delete', details)

    assert 'delete' in response.lower()
    assert 'Buy groceries' in response


def test_format_confirmation_request_complete():
    """Test formatting a confirmation request for complete action."""
    agent = ResponseGenerationAgent()

    details = {'content': 'Buy groceries'}

    response = agent.format_confirmation_request('complete', details)

    assert 'complete' in response.lower()
    assert 'Buy groceries' in response


def test_personalize_response_with_name():
    """Test personalizing a response with user's name."""
    agent = ResponseGenerationAgent()

    user_profile = {'name': 'John'}
    response = "I've added 'Buy groceries' to your todo list."

    personalized = agent.personalize_response(response, user_profile)

    assert 'John' in personalized


def test_personalize_response_formal_tone():
    """Test personalizing a response with formal tone."""
    agent = ResponseGenerationAgent()

    user_profile = {'name': 'John', 'tone': 'formal'}
    response = "Great! Your task has been added."

    personalized = agent.personalize_response(response, user_profile)

    # In formal tone, exclamation marks might be replaced with periods
    assert 'John' in personalized


def test_maintain_context():
    """Test maintaining context in the response."""
    agent = ResponseGenerationAgent()

    response = "Your task has been completed."
    conversation_history = [
        {'role': 'user', 'content': 'Mark the grocery task as complete'}
    ]

    context_response = agent.maintain_context(response, conversation_history)

    # For now, this just returns the response as is
    assert context_response == response


def test_generate_response_with_user_context():
    """Test generating a response with user context."""
    agent = ResponseGenerationAgent()

    api_response = {
        'status_code': 201,
        'data': {
            'id': 123,
            'content': 'Buy groceries',
            'priority': 'high',
            'completed': False
        }
    }

    user_context = {
        'name': 'Alice',
        'preferences': {'tone': 'friendly'}
    }

    response = agent.generate_response(api_response, user_context)

    # Should contain the task content
    assert 'Buy groceries' in response


def test_generate_error_response_with_detailed_error():
    """Test generating an error response with detailed error information."""
    agent = ResponseGenerationAgent()

    api_response = {
        'status_code': 500,
        'data': {
            'detail': 'Database connection failed'
        }
    }

    response = agent.generate_response(api_response)

    # Should contain error-related information (template for 500 status includes "wrong" and "try again")
    assert 'wrong' in response.lower() or 'again' in response.lower()


def test_format_list_response_limited():
    """Test that list responses are limited to prevent overwhelming the user."""
    agent = ResponseGenerationAgent()

    # Create more than 10 items to test the limit
    items = []
    for i in range(15):
        items.append({
            'id': i+1,
            'content': f'Task {i+1}',
            'completed': False,
            'priority': 'medium'
        })

    response = agent.format_list_response(items, "Your tasks")

    # Should only show first 10 items and mention there are more
    assert response.count('\n') >= 10  # At least 10 items shown
    assert 'more items' in response or 'more' in response


if __name__ == "__main__":
    pytest.main([__file__])