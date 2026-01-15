"""
Tests for the Todo Command Interpreter Agent
"""

import pytest
from .todo_command_interpreter_agent import TodoCommandInterpreterAgent, APICommand, HttpMethod
from .nlp_agent import NLPResult, Intent, EntityType


def test_interpret_add_todo():
    """Test interpretation of ADD_TODO intent"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for adding a todo
    entities = {EntityType.DATE.value: "tomorrow", EntityType.PRIORITY.value: "high"}
    nlp_result = NLPResult(Intent.ADD_TODO, entities)

    command = interpreter.interpret(nlp_result)

    assert command.method == HttpMethod.POST
    assert command.endpoint == "/api/todos"
    assert "content" in command.data
    assert command.data.get("priority") == "high"
    assert command.data.get("due_date") == "tomorrow"


def test_interpret_list_todos():
    """Test interpretation of LIST_TODOS intent"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for listing todos with priority filter
    entities = {EntityType.PRIORITY.value: "high"}
    nlp_result = NLPResult(Intent.LIST_TODOS, entities)

    command = interpreter.interpret(nlp_result)

    assert command.method == HttpMethod.GET
    assert "priority=high" in command.endpoint


def test_interpret_list_todos_with_category():
    """Test interpretation of LIST_TODOS intent with category filter"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for listing todos with category filter
    entities = {EntityType.CATEGORY.value: "work"}
    nlp_result = NLPResult(Intent.LIST_TODOS, entities)

    command = interpreter.interpret(nlp_result)

    assert command.method == HttpMethod.GET
    assert "category=work" in command.endpoint


def test_interpret_complete_todo():
    """Test interpretation of COMPLETE_TODO intent"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for completing a todo
    entities = {EntityType.NUMBER.value: "1"}
    nlp_result = NLPResult(Intent.COMPLETE_TODO, entities)

    command = interpreter.interpret(nlp_result)

    assert command.method == HttpMethod.PUT
    assert command.endpoint == "/api/todos/1"
    assert command.data.get("completed") is True


def test_interpret_delete_todo():
    """Test interpretation of DELETE_TODO intent"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for deleting a todo
    entities = {EntityType.NUMBER.value: "2"}
    nlp_result = NLPResult(Intent.DELETE_TODO, entities)

    command = interpreter.interpret(nlp_result)

    assert command.method == HttpMethod.DELETE
    assert command.endpoint == "/api/todos/2"


def test_interpret_modify_todo():
    """Test interpretation of MODIFY_TODO intent"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for modifying a todo
    entities = {EntityType.NUMBER.value: "3", EntityType.PRIORITY.value: "low", EntityType.DATE.value: "next week"}
    nlp_result = NLPResult(Intent.MODIFY_TODO, entities)

    command = interpreter.interpret(nlp_result)

    assert command.method == HttpMethod.PUT
    assert command.endpoint == "/api/todos/3"
    assert command.data.get("priority") == "low"
    assert command.data.get("due_date") == "next week"


def test_interpret_search_todos():
    """Test interpretation of SEARCH_TODOS intent"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for searching todos
    entities = {EntityType.CATEGORY.value: "work"}
    nlp_result = NLPResult(Intent.SEARCH_TODOS, entities)

    command = interpreter.interpret(nlp_result)

    assert command.method == HttpMethod.GET
    assert "/api/todos/search" in command.endpoint
    assert "category=work" in command.endpoint


def test_interpret_help():
    """Test interpretation of HELP intent"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for help
    nlp_result = NLPResult(Intent.HELP, {})

    command = interpreter.interpret(nlp_result)

    assert command.method == HttpMethod.GET
    assert command.endpoint == "/api/help"


def test_interpret_unknown_intent():
    """Test interpretation of UNKNOWN intent"""
    interpreter = TodoCommandInterpreterAgent()

    # Create a mock NLP result for unknown intent
    nlp_result = NLPResult(Intent.UNKNOWN, {})

    command = interpreter.interpret(nlp_result)

    # Unknown intent should default to help
    assert command.method == HttpMethod.GET
    assert command.endpoint == "/api/help"


def test_priority_mapping():
    """Test that priority mappings work correctly"""
    interpreter = TodoCommandInterpreterAgent()

    # Test different priority synonyms
    test_cases = [
        ("high", "high"),
        ("urgent", "high"),
        ("important", "high"),
        ("medium", "medium"),
        ("normal", "medium"),
        ("low", "low")
    ]

    for input_priority, expected_output in test_cases:
        entities = {EntityType.PRIORITY.value: input_priority}
        nlp_result = NLPResult(Intent.ADD_TODO, entities)

        command = interpreter.interpret(nlp_result)

        assert command.data.get("priority") == expected_output


def test_category_mapping():
    """Test that category mappings work correctly"""
    interpreter = TodoCommandInterpreterAgent()

    # Test different category synonyms
    test_cases = [
        ("work", "work"),
        ("personal", "personal"),
        ("shopping", "shopping"),
        ("health", "health"),
        ("family", "family"),
        ("home", "home")
    ]

    for input_category, expected_output in test_cases:
        entities = {EntityType.CATEGORY.value: input_category}
        nlp_result = NLPResult(Intent.ADD_TODO, entities)

        command = interpreter.interpret(nlp_result)

        assert command.data.get("category") == expected_output


if __name__ == "__main__":
    pytest.main([__file__])