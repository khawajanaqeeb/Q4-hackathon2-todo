"""
Tests for the NLP Agent
"""

import pytest
from .nlp_agent import NLPAgent, Intent, EntityType


def test_preprocess_text():
    """Test text preprocessing functionality"""
    nlp_agent = NLPAgent()

    # Test basic preprocessing
    result = nlp_agent.preprocess_text("  HELLO   WORLD  ")
    assert result == "hello world"

    # Test with mixed case
    result = nlp_agent.preprocess_text("ThIs Is TeSt")
    assert result == "this is test"


def test_classify_add_todo_intent():
    """Test ADD_TODO intent classification"""
    nlp_agent = NLPAgent()

    test_cases = [
        "Add a new todo to buy groceries",
        "Create a task for tomorrow",
        "I need to add a task",
        "add",
        "create"
    ]

    for test_input in test_cases:
        result = nlp_agent.process(test_input)
        assert result.intent == Intent.ADD_TODO


def test_classify_list_todos_intent():
    """Test LIST_TODOS intent classification"""
    nlp_agent = NLPAgent()

    test_cases = [
        "Show me my todos",
        "List all tasks",
        "What tasks do I have?",
        "list",
        "show"
    ]

    for test_input in test_cases:
        result = nlp_agent.process(test_input)
        assert result.intent == Intent.LIST_TODOS


def test_classify_complete_todo_intent():
    """Test COMPLETE_TODO intent classification"""
    nlp_agent = NLPAgent()

    test_cases = [
        "Complete the first task",
        "Finish my work",
        "Mark as done",
        "complete",
        "finish"
    ]

    for test_input in test_cases:
        result = nlp_agent.process(test_input)
        assert result.intent == Intent.COMPLETE_TODO


def test_classify_delete_todo_intent():
    """Test DELETE_TODO intent classification"""
    nlp_agent = NLPAgent()

    test_cases = [
        "Delete the old task",
        "Remove this todo",
        "delete",
        "remove"
    ]

    for test_input in test_cases:
        result = nlp_agent.process(test_input)
        assert result.intent == Intent.DELETE_TODO


def test_classify_modify_todo_intent():
    """Test MODIFY_TODO intent classification"""
    nlp_agent = NLPAgent()

    test_cases = [
        "Change the priority of this task",
        "Update my shopping list",
        "Edit the todo",
        "modify",
        "update",
        "edit"
    ]

    for test_input in test_cases:
        result = nlp_agent.process(test_input)
        assert result.intent == Intent.MODIFY_TODO


def test_classify_search_todos_intent():
    """Test SEARCH_TODOS intent classification"""
    nlp_agent = NLPAgent()

    test_cases = [
        "Search for work tasks",
        "Find the urgent todo",
        "Look for shopping items",
        "search",
        "find"
    ]

    for test_input in test_cases:
        result = nlp_agent.process(test_input)
        assert result.intent == Intent.SEARCH_TODOS


def test_classify_help_intent():
    """Test HELP intent classification"""
    nlp_agent = NLPAgent()

    test_cases = [
        "help",
        "what can you do",
        "how do i add a task",
        "assist me"
    ]

    for test_input in test_cases:
        result = nlp_agent.process(test_input)
        assert result.intent == Intent.HELP


def test_extract_date_entities():
    """Test date entity extraction"""
    nlp_agent = NLPAgent()

    test_input = "Add a task for tomorrow"
    result = nlp_agent.process(test_input)

    assert EntityType.DATE.value in result.entities
    assert result.entities[EntityType.DATE.value] == "tomorrow"


def test_extract_priority_entities():
    """Test priority entity extraction"""
    nlp_agent = NLPAgent()

    test_input = "Add a high priority task"
    result = nlp_agent.process(test_input)

    assert EntityType.PRIORITY.value in result.entities
    assert result.entities[EntityType.PRIORITY.value] == "high"


def test_extract_category_entities():
    """Test category entity extraction"""
    nlp_agent = NLPAgent()

    test_input = "Add a work task"
    result = nlp_agent.process(test_input)

    assert EntityType.CATEGORY.value in result.entities
    assert result.entities[EntityType.CATEGORY.value] == "work"


def test_unknown_intent():
    """Test unknown intent classification"""
    nlp_agent = NLPAgent()

    result = nlp_agent.process("asdfghjkl qwertyuiop")
    assert result.intent == Intent.UNKNOWN


def test_process_method():
    """Test the main process method"""
    nlp_agent = NLPAgent()

    result = nlp_agent.process("Add a task for tomorrow")

    assert result.intent == Intent.ADD_TODO
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__])