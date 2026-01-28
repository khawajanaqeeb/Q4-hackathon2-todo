from sqlmodel import Session, select
from typing import Dict, List, Optional
from datetime import datetime
import json
import re

from ..models.conversation import Conversation, ConversationCreate
from ..models.message import Message, MessageCreate
from ..models.todo import TodoCreate, TodoUpdate
from ..models.user import User
from .todo import create_todo, get_todos, update_todo, delete_todo


class ChatService:
    """Service for handling chatbot interactions and todo management."""

    def __init__(self, session: Session):
        self.session = session

    def process_message(self, user_id: int, message_content: str, conversation_id: Optional[str] = None):
        """
        Process a user message and return appropriate response and actions.
        """
        # If no conversation ID is provided, create a new one
        if not conversation_id:
            conversation_title = f"Conversation with {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            conversation_create = ConversationCreate(
                title=conversation_title,
                user_id=user_id
            )

            # Create conversation
            db_conversation = Conversation(
                title=conversation_create.title,
                user_id=conversation_create.user_id,
                id=conversation_create.id if hasattr(conversation_create, 'id') else None
            )
            self.session.add(db_conversation)
            self.session.commit()
            self.session.refresh(db_conversation)
            conversation_id = db_conversation.id

        # Create user message
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=message_content
        )
        self.session.add(user_message)
        self.session.commit()
        self.session.refresh(user_message)

        # Analyze the message for todo-related intents
        response_text, actions = self._analyze_intent_and_execute_actions(user_id, message_content, conversation_id)

        # Create assistant message
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text
        )
        self.session.add(assistant_message)
        self.session.commit()

        return {
            "response": response_text,
            "conversation_id": conversation_id,
            "actions": actions
        }

    def _analyze_intent_and_execute_actions(self, user_id: int, message: str, conversation_id: str):
        """Analyze message intent and execute corresponding actions."""
        message_lower = message.lower()
        actions = []

        # Intent: Create todo
        if any(word in message_lower for word in ["create", "add", "make", "new", "todo", "task"]):
            todo_title = self._extract_todo_title(message)
            if todo_title:
                todo_data = {
                    "title": todo_title,
                    "description": "",
                    "completed": False,
                    "priority": "medium"
                }

                # Create the todo
                todo_create = TodoCreate(**todo_data)
                created_todo = create_todo(self.session, todo_create, user_id)

                actions.append({
                    "type": "create_todo",
                    "data": {"id": created_todo.id, "title": created_todo.title}
                })

                return f"I've created a todo for '{todo_title}'.", actions

        # Intent: List todos
        if any(word in message_lower for word in ["list", "show", "view", "my", "todos", "tasks"]):
            todos = get_todos(self.session, user_id)
            if todos:
                todo_list = [f"- {todo.title}" for todo in todos[:5]]  # Limit to first 5
                todo_str = "\n".join(todo_list)
                response = f"Here are your todos:\n{todo_str}"
            else:
                response = "You don't have any todos yet."

            actions.append({
                "type": "list_todos",
                "data": {"count": len(todos)}
            })

            return response, actions

        # Intent: Update todo (could be mark as complete, change priority, etc.)
        if any(word in message_lower for word in ["complete", "done", "finish", "finished"]):
            # Extract potential todo title or ID from message
            todo_title = self._extract_todo_title(message)
            if todo_title:
                # Find the todo to update
                statement = select(Todo).where(
                    Todo.user_id == user_id,
                    Todo.title.contains(todo_title)
                )
                todo_to_update = self.session.exec(statement).first()

                if todo_to_update:
                    # Update the todo to mark as complete
                    todo_update = TodoUpdate(completed=True)
                    updated_todo = update_todo(self.session, todo_to_update.id, todo_update, user_id)

                    if updated_todo:
                        actions.append({
                            "type": "update_todo",
                            "data": {"id": updated_todo.id, "completed": True}
                        })

                        return f"I've marked '{updated_todo.title}' as complete.", actions

            return "I couldn't find that todo to mark as complete.", actions

        # Default response if no specific intent detected
        return "I understand you're talking about your todos. You can ask me to create, list, or update your todos.", actions

    def _extract_todo_title(self, message: str) -> Optional[str]:
        """Extract a potential todo title from a message."""
        # Look for patterns like "create [title]", "add [title]", etc.
        patterns = [
            r'(?:create|add|make|new)\s+(.+?)(?:\.|$)',
            r'(?:to\s+do|todo|task):\s*(.+?)(?:\.|$)',
            r'(?:to\s+do|todo|task)\s+(.+?)(?:\.|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                title = match.group(1).strip()
                # Remove trailing punctuation
                title = re.sub(r'[.!?,;:]+$', '', title)
                return title.title()  # Capitalize the first letter of each word

        # If no pattern matched, return the part after common verbs
        parts = message.split()
        if len(parts) > 1:
            # Skip common verbs and return the rest as a potential title
            if parts[0].lower() in ['create', 'add', 'make', 'new']:
                return ' '.join(parts[1:]).title()

        return None

    def get_conversations(self, user_id: int) -> List[Dict]:
        """Get all conversations for a user."""
        statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = self.session.exec(statement).all()

        return [{
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at
        } for conv in conversations]