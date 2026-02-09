from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from sqlmodel import Session, select
from ..models.conversation import Conversation, MessageRole
from ..models.message import Message
from ..models.task import Task
from ..models.user import User  # Assuming User model exists from phase 2


class ChatService:
    """Service class for handling chatbot functionality."""

    def __init__(self, session: Session):
        """Initialize ChatService with database session."""
        self.session = session

    def create_conversation(self, user_id: uuid.UUID, initial_message: Optional[str] = None) -> Conversation:
        """Create a new conversation for a user."""
        title = None
        if initial_message:
            title = initial_message[:50] + "..." if len(initial_message) > 50 else initial_message
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
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
            timestamp=datetime.now(timezone.utc)
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_conversation_messages(self, conversation_id: uuid.UUID) -> list[Message]:
        """Get all messages for a conversation."""
        messages = self.session.exec(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
        ).all()
        return messages

    def get_user_conversations(self, user_id: uuid.UUID) -> list[Conversation]:
        """Get all conversations for a user."""
        conversations = self.session.exec(
            select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
        ).all()
        return conversations

    def process_user_message(self, user_id: uuid.UUID, message_content: str, conversation_id: Optional[uuid.UUID] = None, agent_response: Optional[str] = None, action_taken: Optional[str] = None) -> Dict[str, Any]:
        """Process a user message and return response."""
        # Get or create conversation
        conversation = self.get_or_create_conversation(user_id, conversation_id)

        # Add user message to conversation
        user_message = self.add_message(conversation.id, MessageRole.USER, message_content)

        # Use the agent response if provided, otherwise use a fallback message
        response_content = agent_response if agent_response else f"I understand you said: '{message_content}'. How can I help you with your tasks?"

        # Add AI response to conversation
        ai_message = self.add_message(conversation.id, MessageRole.ASSISTANT, response_content)

        return {
            "message": response_content,
            "conversation_id": conversation.id,
            "timestamp": ai_message.timestamp,
            "action_taken": action_taken or "message_processed",
            "confirmation_message": response_content
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