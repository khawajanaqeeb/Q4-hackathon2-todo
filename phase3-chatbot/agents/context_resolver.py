"""
Context Resolver for Todo AI Chatbot

Resolves ambiguous references in user input based on conversation history and context for the Todo AI Chatbot.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from agents.conversation_context_manager_agent import Message, MessageRole, UserContext


class ContextResolver:
    """
    Resolves ambiguous references in user input based on conversation history and context.
    """

    def __init__(self):
        self.pronoun_mapping = {
            'it': 'last_referenced_item',
            'that': 'last_referenced_item',
            'this': 'last_referenced_item',
            'they': 'recent_items',
            'them': 'recent_items',
            'those': 'recent_items'
        }

    def resolve_reference_from_context(self, user_input: str, user_context: UserContext) -> Optional[str]:
        """
        Resolve ambiguous references like "it", "that", "the first one", etc.
        """
        # Check if the input contains pronouns or ambiguous references
        lower_input = user_input.lower()

        # Handle pronouns like "it", "that", "this"
        for pronoun, reference_type in self.pronoun_mapping.items():
            if pronoun in lower_input:
                if reference_type == 'last_referenced_item':
                    return self._get_last_referenced_item(user_context)
                elif reference_type == 'recent_items':
                    return self._get_recent_items(user_context)

        # Handle ordinal references like "the first one", "the second task", etc.
        ordinal_match = self._check_for_ordinal_reference(lower_input)
        if ordinal_match:
            return self._resolve_ordinal_reference(ordinal_match, user_context)

        # Handle "the one I just added" or similar references
        if 'just added' in lower_input or 'recently added' in lower_input:
            return self._get_last_added_item(user_context)

        # Handle "the one about" or "the task about" references
        about_match = self._check_for_about_reference(lower_input)
        if about_match:
            return self._find_item_by_content(user_context, about_match)

        # If no specific reference found, return None
        return None

    def _get_last_referenced_item(self, user_context: UserContext) -> Optional[str]:
        """
        Get the last referenced item from context.
        """
        # Check if there's a last todo ID in the active context
        last_todo_id = user_context.active_context.get('last_todo_id')
        if last_todo_id:
            # In a real implementation, this would fetch the todo details
            # For now, we'll return a placeholder
            return f"todo_{last_todo_id}"

        # If no specific ID, return the most recent item from conversation history
        for message in reversed(user_context.conversation_history):
            if message.role == MessageRole.ASSISTANT:
                # Look for mentions of items in assistant responses
                if 'todo' in message.content.lower() or 'task' in message.content.lower():
                    # Extract item reference from the message
                    import re
                    # Look for patterns like "task 'buy groceries'"
                    match = re.search(r"(?:task|todo)\s+'([^']+)'", message.content, re.IGNORECASE)
                    if match:
                        return match.group(1)

        return None

    def _get_recent_items(self, user_context: UserContext) -> Optional[str]:
        """
        Get recent items from context.
        """
        # Return the last few items mentioned
        recent_items = []
        for message in reversed(user_context.conversation_history[-5:]):  # Look at last 5 messages
            if message.role == MessageRole.ASSISTANT:
                import re
                # Look for tasks mentioned in assistant responses
                matches = re.findall(r"(?:task|todo)\s+'([^']+)'", message.content, re.IGNORECASE)
                recent_items.extend(matches)

        if recent_items:
            # Return the most recent item
            return recent_items[0]

        return None

    def _check_for_ordinal_reference(self, text: str) -> Optional[str]:
        """
        Check if the text contains ordinal references like "the first one".
        """
        ordinals = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']

        for ordinal in ordinals:
            if f'the {ordinal}' in text or f'{ordinal} one' in text:
                return ordinal

        # Also check for numeric references like "number 1", "item 2", etc.
        import re
        match = re.search(r'(?:number|item|task)\s+(\d+)', text)
        if match:
            return match.group(1)

        return None

    def _resolve_ordinal_reference(self, ordinal: str, user_context: UserContext) -> Optional[str]:
        """
        Resolve ordinal references like "the first one" based on context.
        """
        # In a real implementation, this would map ordinal to specific items
        # For now, we'll simulate by finding the nth item in the conversation

        # Convert ordinal to number
        ordinal_map = {
            'first': 0, 'second': 1, 'third': 2, 'fourth': 3, 'fifth': 4,
            'sixth': 5, 'seventh': 6, 'eighth': 7, 'ninth': 8, 'tenth': 9
        }

        if ordinal.isdigit():
            index = int(ordinal) - 1  # Convert to 0-based index
        else:
            index = ordinal_map.get(ordinal, 0)

        # Find tasks in the conversation history
        tasks_found = []
        for message in user_context.conversation_history:
            if message.role == MessageRole.ASSISTANT:
                import re
                # Look for tasks mentioned in assistant responses
                matches = re.findall(r"(?:task|todo)\s+'([^']+)'", message.content, re.IGNORECASE)
                tasks_found.extend(matches)

        # Return the indexed task
        if 0 <= index < len(tasks_found):
            return tasks_found[index]

        return None

    def _check_for_about_reference(self, text: str) -> Optional[str]:
        """
        Check if the text contains "about" references like "the one about groceries".
        """
        import re
        match = re.search(r"(?:the one|that|this)\s+(?:about|regarding|related to)\s+([^.!?]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    def _find_item_by_content(self, user_context: UserContext, content_hint: str) -> Optional[str]:
        """
        Find an item based on content hint.
        """
        # Look through conversation history for items matching the content hint
        for message in reversed(user_context.conversation_history):
            if message.role == MessageRole.ASSISTANT:
                if content_hint.lower() in message.content.lower():
                    import re
                    # Extract the task name from the message
                    match = re.search(r"(?:task|todo)\s+'([^']+)'", message.content, re.IGNORECASE)
                    if match:
                        return match.group(1)

        return None

    def _get_last_added_item(self, user_context: UserContext) -> Optional[str]:
        """
        Get the last added item from context.
        """
        # Look for the most recent "added" message in conversation history
        for message in reversed(user_context.conversation_history):
            if message.role == MessageRole.ASSISTANT and 'added' in message.content.lower():
                import re
                # Extract the task name from the message
                match = re.search(r"(?:task|todo)\s+'([^']+)'", message.content, re.IGNORECASE)
                if match:
                    return match.group(1)

        return None

    def infer_reference_from_context(self, user_input: str, user_context: UserContext,
                                     possible_references: List[str]) -> Optional[str]:
        """
        Infer the most likely reference from context when multiple possibilities exist.
        """
        # First, try to resolve using specific reference resolution
        resolved_ref = self.resolve_reference_from_context(user_input, user_context)
        if resolved_ref:
            return resolved_ref

        # If no specific resolution, try to match against possible references
        lower_input = user_input.lower()

        # Look for exact matches in possible references
        for possible_ref in possible_references:
            if possible_ref.lower() in lower_input:
                return possible_ref

        # If no exact match, look for partial matches
        for possible_ref in possible_references:
            if any(word in lower_input for word in possible_ref.lower().split()):
                return possible_ref

        # If still no match, return the first possible reference as default
        return possible_references[0] if possible_references else None


# Example usage
if __name__ == "__main__":
    from agents.conversation_context_manager_agent import UserContext

    # Create a mock user context
    user_context = UserContext("test_user")

    # Add some conversation history
    user_context.conversation_history.append(
        Message(MessageRole.USER, "Add a task to buy groceries")
    )
    user_context.conversation_history.append(
        Message(MessageRole.ASSISTANT, "I've added the task 'buy groceries' to your list.")
    )
    user_context.conversation_history.append(
        Message(MessageRole.USER, "Mark it as completed")
    )

    # Set the last todo ID
    user_context.active_context['last_todo_id'] = 123

    # Test the context resolver
    resolver = ContextResolver()

    # Test resolving "it"
    result = resolver.resolve_reference_from_context("Mark it as completed", user_context)
    print(f"Resolved 'it': {result}")

    # Test with possible references
    possible_refs = ["buy groceries", "call mom", "schedule meeting"]
    inferred = resolver.infer_reference_from_context("Update the groceries task", user_context, possible_refs)
    print(f"Inferred reference: {inferred}")