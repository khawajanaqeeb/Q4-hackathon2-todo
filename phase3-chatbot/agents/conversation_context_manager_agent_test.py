"""
Tests for the Conversation Context Manager Agent
"""

import pytest
import time
from datetime import timedelta
from agents.conversation_context_manager_agent import (
    ConversationContextManagerAgent,
    MessageRole,
    UserContext
)


def test_create_user_context():
    """Test creating a new user context."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    context = manager.create_user_context(user_id)

    assert context.user_id == user_id
    assert isinstance(context.preferences, dict)
    assert len(context.conversation_history) == 0
    assert isinstance(context.active_context, dict)
    assert user_id in manager.user_contexts


def test_get_user_context_new():
    """Test retrieving a new user context."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    context = manager.get_user_context(user_id)

    assert context.user_id == user_id
    assert isinstance(context, UserContext)


def test_get_user_context_existing():
    """Test retrieving an existing user context."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    # First call creates the context
    first_context = manager.get_user_context(user_id)
    # Second call retrieves the same context
    second_context = manager.get_user_context(user_id)

    assert first_context.user_id == second_context.user_id
    assert first_context is second_context


def test_update_user_preferences():
    """Test updating user preferences."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    preferences = {"theme": "dark", "language": "en"}

    manager.update_user_preferences(user_id, preferences)

    context = manager.get_user_context(user_id)
    assert context.preferences["theme"] == "dark"
    assert context.preferences["language"] == "en"


def test_add_message_to_history():
    """Test adding messages to conversation history."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    manager.add_message_to_history(user_id, MessageRole.USER, "Hello")
    manager.add_message_to_history(user_id, MessageRole.ASSISTANT, "Hi there!")

    context = manager.get_user_context(user_id)
    assert len(context.conversation_history) == 2
    assert context.conversation_history[0].role == MessageRole.USER
    assert context.conversation_history[0].content == "Hello"
    assert context.conversation_history[1].role == MessageRole.ASSISTANT
    assert context.conversation_history[1].content == "Hi there!"


def test_get_recent_messages():
    """Test retrieving recent messages."""
    manager = ConversationContextManagerAgent(max_history_size=5)

    user_id = "test_user"
    # Add 5 messages
    for i in range(5):
        manager.add_message_to_history(user_id, MessageRole.USER, f"Message {i}")

    # Get last 3 messages
    recent_messages = manager.get_recent_messages(user_id, 3)

    assert len(recent_messages) == 3
    assert recent_messages[0].content == "Message 2"  # Third from the end
    assert recent_messages[1].content == "Message 3"
    assert recent_messages[2].content == "Message 4"


def test_set_and_get_active_context():
    """Test setting and getting active context."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    context_data = {"current_task": "shopping", "filter": "high_priority"}

    manager.set_active_context(user_id, context_data)

    retrieved_context = manager.get_active_context(user_id)

    assert retrieved_context["current_task"] == "shopping"
    assert retrieved_context["filter"] == "high_priority"


def test_infer_reference_from_context():
    """Test inferring references from context."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    manager.add_message_to_history(user_id, MessageRole.USER, "Add a task to buy groceries")
    manager.add_message_to_history(user_id, MessageRole.ASSISTANT, "I've added 'buy groceries' to your list")
    manager.add_message_to_history(user_id, MessageRole.USER, "Set it as high priority")

    possible_refs = ["buy groceries", "call mom", "schedule meeting"]
    inferred_ref = manager.infer_reference_from_context(user_id, possible_refs)

    assert inferred_ref == "buy groceries"


def test_update_and_get_last_todo_id():
    """Test updating and getting last todo ID."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    manager.update_last_todo_id(user_id, 123)

    last_id = manager.get_last_todo_id(user_id)

    assert last_id == 123


def test_context_serialization():
    """Test context serialization and deserialization."""
    manager = ConversationContextManagerAgent()

    user_id = "test_user"
    manager.update_user_preferences(user_id, {"theme": "light"})
    manager.add_message_to_history(user_id, MessageRole.USER, "Test message")
    manager.set_active_context(user_id, {"current_task": "testing"})
    manager.update_last_todo_id(user_id, 42)

    # Serialize the context
    serialized = manager.serialize_context(user_id)

    # Create a new manager instance
    new_manager = ConversationContextManagerAgent()

    # Deserialize the context
    new_manager.deserialize_context(user_id, serialized)

    # Verify the deserialized context
    new_context = new_manager.get_user_context(user_id)
    assert new_context.preferences["theme"] == "light"
    assert len(new_context.conversation_history) == 1
    assert new_context.conversation_history[0].content == "Test message"
    assert new_context.active_context["current_task"] == "testing"


def test_session_timeout():
    """Test session timeout functionality."""
    manager = ConversationContextManagerAgent(session_timeout=timedelta(seconds=0.1))

    user_id = "test_user"
    context = manager.get_user_context(user_id)
    original_preferences = {"theme": "dark"}
    context.preferences = original_preferences

    # Add some context data
    manager.set_active_context(user_id, {"current_task": "before_timeout"})

    # Wait for timeout
    time.sleep(0.2)

    # Get context again - should create a new one
    new_context = manager.get_user_context(user_id)

    # Preferences should be preserved, but active context should be reset
    assert new_context.preferences["theme"] == "dark"
    assert new_context.active_context != {"current_task": "before_timeout"}


def test_max_history_size_trimming():
    """Test that history is trimmed when exceeding max size."""
    manager = ConversationContextManagerAgent(max_history_size=3)

    user_id = "test_user"

    # Add 5 messages
    for i in range(5):
        manager.add_message_to_history(user_id, MessageRole.USER, f"Message {i}")

    # Get all messages
    context = manager.get_user_context(user_id)

    # Should only have the last 3 messages
    assert len(context.conversation_history) == 3
    assert context.conversation_history[0].content == "Message 2"
    assert context.conversation_history[1].content == "Message 3"
    assert context.conversation_history[2].content == "Message 4"


if __name__ == "__main__":
    pytest.main([__file__])