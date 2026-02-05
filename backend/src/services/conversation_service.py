"""Conversation service for managing chat conversations in the Phase 3 chatbot system."""
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from datetime import datetime, timedelta
from uuid import UUID
import json

from ..models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationUpdate,
    Message,
    TodoOperationLog
)
from ..models.user import User
from ..database import get_session


class ConversationService:
    """Service class for handling conversation-related operations."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_conversation(self, user_id: int, title: str = "New Conversation") -> Conversation:
        """
        Create a new conversation for the specified user.

        Args:
            user_id: ID of the user creating the conversation
            title: Title for the conversation (defaults to "New Conversation")

        Returns:
            The created Conversation object
        """
        conversation = Conversation(
            title=title,
            user_id=user_id
        )
        self.db_session.add(conversation)
        self.db_session.commit()
        self.db_session.refresh(conversation)
        return conversation

    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to retrieve

        Returns:
            Conversation object if found, None otherwise
        """
        return self.db_session.get(Conversation, UUID(conversation_id))

    def get_user_conversations(self, user_id: int) -> List[Conversation]:
        """
        Retrieve all conversations for a specific user.

        Args:
            user_id: The ID of the user whose conversations to retrieve

        Returns:
            List of Conversation objects for the user
        """
        statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = self.db_session.exec(statement).all()
        return conversations

    def update_conversation(self, conversation_id: str, update_data: ConversationUpdate) -> Optional[Conversation]:
        """
        Update a conversation with new data.

        Args:
            conversation_id: ID of the conversation to update
            update_data: Update data for the conversation

        Returns:
            Updated Conversation object if successful, None otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return None

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(conversation, field, value)

        # Update timestamp
        conversation.updated_at = datetime.utcnow()

        self.db_session.add(conversation)
        self.db_session.commit()
        self.db_session.refresh(conversation)
        return conversation

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation by its ID.

        Args:
            conversation_id: ID of the conversation to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return False

        self.db_session.delete(conversation)
        self.db_session.commit()
        return True

    def archive_conversation(self, conversation_id: str) -> bool:
        """
        Archive a conversation by setting its status to 'archived'.

        Args:
            conversation_id: ID of the conversation to archive

        Returns:
            True if archival was successful, False otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return False

        conversation.status = "archived"
        conversation.updated_at = datetime.utcnow()

        self.db_session.add(conversation)
        self.db_session.commit()
        return True

    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """
        Retrieve all messages in a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            List of Message objects in the conversation
        """
        statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
        messages = self.db_session.exec(statement).all()
        return messages

    def add_message_to_conversation(self, conversation_id: str, role: str, content: str) -> Message:
        """
        Add a new message to a conversation.

        Args:
            conversation_id: ID of the conversation
            role: Role of the message sender ('user', 'assistant', 'tool')
            content: Content of the message

        Returns:
            Created Message object
        """
        from ..models.conversation import Message as MessageModel

        message = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        self.db_session.add(message)
        self.db_session.commit()
        self.db_session.refresh(message)
        return message

    def log_todo_operation(self, conversation_id: str, message_id: str, operation: str,
                          todo_id: str, previous_state: Optional[Dict] = None,
                          new_state: Optional[Dict] = None) -> TodoOperationLog:
        """
        Log a todo operation performed during a conversation.

        Args:
            conversation_id: ID of the conversation where operation occurred
            message_id: ID of the message that triggered the operation
            operation: Type of operation ('create', 'update', 'delete', 'complete')
            todo_id: ID of the affected todo item
            previous_state: State of the todo before operation
            new_state: State of the todo after operation

        Returns:
            Created TodoOperationLog object
        """
        # Convert state dictionaries to JSON strings if they exist
        previous_state_json = json.dumps(previous_state) if previous_state else None
        new_state_json = json.dumps(new_state) if new_state else None

        log_entry = TodoOperationLog(
            conversation_id=conversation_id,
            message_id=message_id,
            operation=operation,
            todo_id=todo_id,
            previous_state=previous_state_json,
            new_state=new_state_json
        )
        self.db_session.add(log_entry)
        self.db_session.commit()
        self.db_session.refresh(log_entry)
        return log_entry

    def get_conversation_todo_operations(self, conversation_id: str) -> List[TodoOperationLog]:
        """
        Retrieve all todo operation logs for a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            List of TodoOperationLog objects
        """
        statement = select(TodoOperationLog).where(
            TodoOperationLog.conversation_id == conversation_id
        ).order_by(TodoOperationLog.timestamp)
        logs = self.db_session.exec(statement).all()
        return logs

    def cleanup_expired_conversations(self, days_old: int = 30) -> int:
        """
        Clean up conversations that are older than the specified number of days.

        Args:
            days_old: Age threshold in days

        Returns:
            Number of conversations cleaned up
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        statement = select(Conversation).where(Conversation.updated_at < cutoff_date)
        conversations = self.db_session.exec(statement).all()

        count = 0
        for conversation in conversations:
            self.db_session.delete(conversation)
            count += 1

        if count > 0:
            self.db_session.commit()

        return count

    def search_conversations_by_content(self, user_id: int, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for conversations containing the search term in message content.

        Args:
            user_id: ID of the user whose conversations to search
            search_term: Term to search for in message content

        Returns:
            List of conversation summaries that contain the search term
        """
        # Get all conversations for the user
        user_conversations = self.get_user_conversations(user_id)

        matching_conversations = []

        for conv in user_conversations:
            # Get messages for this conversation
            messages = self.get_conversation_messages(str(conv.id))

            # Check if any message contains the search term
            for msg in messages:
                if search_term.lower() in msg.content.lower():
                    conversation_summary = {
                        "id": str(conv.id),
                        "title": conv.title,
                        "created_at": conv.created_at,
                        "updated_at": conv.updated_at,
                        "message_count": len(messages),
                        "first_match_preview": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                    }
                    if conversation_summary not in matching_conversations:
                        matching_conversations.append(conversation_summary)
                    break  # Only add the conversation once

        return matching_conversations