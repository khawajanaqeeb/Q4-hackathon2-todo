"""
Conversation Context Manager Agent

Manages conversation state, history, and user preferences across interactions for the Todo AI Chatbot.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message:
    """Represents individual conversation exchanges with role, content, and metadata."""

    def __init__(self, role: MessageRole, content: str, timestamp: Optional[float] = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        role = MessageRole(data['role'])
        return cls(role, data['content'], data.get('timestamp'))


class UserContext:
    """Stores all context information for a specific user."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.preferences: Dict[str, Any] = {}
        self.conversation_history: List[Message] = []
        self.active_context: Dict[str, Any] = {}
        self.last_activity_timestamp = time.time()
        self.session_start_time = time.time()


class ConversationContextManagerAgent:
    """
    Manages conversation state, history, and user preferences across interactions for the Todo AI Chatbot.
    """

    def __init__(self, max_history_size: int = 20, session_timeout: timedelta = timedelta(hours=1)):
        self.max_history_size = max_history_size
        self.session_timeout = session_timeout
        self.user_contexts: Dict[str, UserContext] = {}

    def create_user_context(self, user_id: str) -> UserContext:
        """Create a new user context."""
        context = UserContext(user_id)
        self.user_contexts[user_id] = context
        return context

    def get_user_context(self, user_id: str) -> UserContext:
        """Retrieve user context with session management."""
        if user_id not in self.user_contexts:
            return self.create_user_context(user_id)

        context = self.user_contexts[user_id]

        # Check if session has timed out
        time_since_last_activity = time.time() - context.last_activity_timestamp
        if time_since_last_activity > self.session_timeout.total_seconds():
            # Create a new context, preserving user preferences
            old_preferences = context.preferences.copy()
            new_context = self.create_user_context(user_id)
            new_context.preferences = old_preferences
            self.user_contexts[user_id] = new_context
            return new_context

        # Update last activity time
        context.last_activity_timestamp = time.time()
        return context

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update user preferences."""
        context = self.get_user_context(user_id)
        context.preferences.update(preferences)

    def add_message_to_history(self, user_id: str, role: MessageRole, content: str) -> None:
        """Add message to conversation history."""
        context = self.get_user_context(user_id)
        message = Message(role, content)
        context.conversation_history.append(message)

        # Trim history if it exceeds max size
        if len(context.conversation_history) > self.max_history_size:
            context.conversation_history = context.conversation_history[-self.max_history_size:]

    def get_recent_messages(self, user_id: str, count: int) -> List[Message]:
        """Retrieve recent messages."""
        context = self.get_user_context(user_id)
        return context.conversation_history[-count:]

    def set_active_context(self, user_id: str, context_data: Dict[str, Any]) -> None:
        """Set active context for user."""
        context = self.get_user_context(user_id)
        context.active_context.update(context_data)

    def get_active_context(self, user_id: str) -> Dict[str, Any]:
        """Get current active context."""
        context = self.get_user_context(user_id)
        return context.active_context.copy()

    def infer_reference_from_context(self, user_id: str, possible_references: List[str]) -> Optional[str]:
        """Resolve ambiguous references."""
        context = self.get_user_context(user_id)

        # Look for the most recently mentioned item that matches a possible reference
        for message in reversed(context.conversation_history):
            for ref in possible_references:
                if ref.lower() in message.content.lower():
                    return ref

        # If nothing found, return the first possible reference as default
        return possible_references[0] if possible_references else None

    def update_last_todo_id(self, user_id: str, todo_id: int) -> None:
        """Track last referenced todo."""
        context = self.get_user_context(user_id)
        context.active_context['last_todo_id'] = todo_id

    def get_last_todo_id(self, user_id: str) -> Optional[int]:
        """Get last referenced todo."""
        context = self.get_user_context(user_id)
        return context.active_context.get('last_todo_id')

    def serialize_context(self, user_id: str) -> str:
        """Convert context to JSON for storage."""
        context = self.get_user_context(user_id)
        data = {
            'user_id': context.user_id,
            'preferences': context.preferences,
            'conversation_history': [msg.to_dict() for msg in context.conversation_history],
            'active_context': context.active_context,
            'last_activity_timestamp': context.last_activity_timestamp,
            'session_start_time': context.session_start_time
        }
        return json.dumps(data, indent=2)

    def deserialize_context(self, user_id: str, context_json: str) -> UserContext:
        """Restore context from JSON."""
        data = json.loads(context_json)
        context = UserContext(data['user_id'])
        context.preferences = data['preferences']
        context.conversation_history = [Message.from_dict(msg_data) for msg_data in data['conversation_history']]
        context.active_context = data['active_context']
        context.last_activity_timestamp = data['last_activity_timestamp']
        context.session_start_time = data['session_start_time']

        self.user_contexts[user_id] = context
        return context


# Example usage
if __name__ == "__main__":
    # Initialize the context manager
    context_manager = ConversationContextManagerAgent()

    # Simulate a conversation
    user_id = "user123"

    # Add some messages to history
    context_manager.add_message_to_history(user_id, MessageRole.USER, "Add a new task to buy groceries")
    context_manager.add_message_to_history(user_id, MessageRole.ASSISTANT, "I've added 'buy groceries' to your todo list.")
    context_manager.add_message_to_history(user_id, MessageRole.USER, "Mark it as completed")

    # Update last todo ID referenced
    context_manager.update_last_todo_id(user_id, 123)

    # Get recent messages
    recent_msgs = context_manager.get_recent_messages(user_id, 3)
    print("Recent messages:")
    for msg in recent_msgs:
        print(f"  {msg.role.value}: {msg.content}")

    # Get active context
    active_ctx = context_manager.get_active_context(user_id)
    print(f"\nActive context: {active_ctx}")

    # Infer reference from context
    possible_refs = ["buy groceries", "call mom", "schedule meeting"]
    inferred_ref = context_manager.infer_reference_from_context(user_id, possible_refs)
    print(f"\nInferred reference: {inferred_ref}")

    # Serialize and deserialize context
    serialized = context_manager.serialize_context(user_id)
    print(f"\nSerialized context length: {len(serialized)}")