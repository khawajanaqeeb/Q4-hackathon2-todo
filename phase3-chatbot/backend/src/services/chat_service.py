from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from sqlmodel import Session, select
from ..models.conversation import Conversation, Message, MessageRole
from ..models.task import Task
from ..models.user import User  # Assuming User model exists from phase 2


class ChatService:
    """Service class for handling chatbot functionality."""

    def __init__(self, session: Session):
        """Initialize ChatService with database session."""
        self.session = session

    def create_conversation(self, user_id: uuid.UUID, initial_message: Optional[str] = None) -> Conversation:
        """Create a new conversation for a user."""
        title = initial_message[:50] + "..." if initial_message and len(initial_message) > 50 else initial_message
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_or_create_conversation(self, user_id: uuid.UUID, conversation_id: Optional[uuid.UUID] = None) -> Conversation:
        """Get existing conversation or create a new one."""
        if conversation_id:
            # Try to get existing conversation
            conversation = self.session.get(Conversation, conversation_id)
            if conversation and conversation.user_id == user_id:
                return conversation
            else:
                raise ValueError("Conversation not found or does not belong to user")

        # Create new conversation
        return self.create_conversation(user_id)

    def add_message(self, conversation_id: uuid.UUID, role: MessageRole, content: str) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_conversation_messages(self, conversation_id: uuid.UUID) -> list[Message]:
        """Get all messages for a conversation."""
        messages = self.session.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()
        return messages

    def get_user_conversations(self, user_id: uuid.UUID) -> list[Conversation]:
        """Get all conversations for a user."""
        conversations = self.session.exec(
            select(Conversation).where(Conversation.user_id == user_id)
        ).all()
        return conversations

    def process_user_message(self, user_id: uuid.UUID, message_content: str, conversation_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Process a user message and return response."""
        # Get or create conversation
        conversation = self.get_or_create_conversation(user_id, conversation_id)

        # Add user message to conversation
        user_message = self.add_message(conversation.id, MessageRole.USER, message_content)

        # This is where the AI processing would happen
        # For now, return a placeholder response
        response_content = f"I received your message: '{message_content}'. This is a placeholder response."

        # Add AI response to conversation
        ai_message = self.add_message(conversation.id, MessageRole.ASSISTANT, response_content)

        return {
            "message": response_content,
            "conversation_id": conversation.id,
            "timestamp": ai_message.timestamp,
            "action_taken": "message_processed",
            "confirmation_message": f"Message processed in conversation {conversation.id}"
        }

    def delete_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a conversation if it belongs to the user."""
        conversation = self.session.get(Conversation, conversation_id)
        if conversation and conversation.user_id == user_id:
            conversation.is_active = False  # Soft delete
            self.session.add(conversation)
            self.session.commit()
            return True
        return False