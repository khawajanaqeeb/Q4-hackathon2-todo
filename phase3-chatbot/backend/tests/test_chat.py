"""Test suite for chat/chatbot endpoints and conversation management."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
import uuid

from src.models.conversation import Conversation
from src.models.message import Message


class TestSendMessage:
    """Tests for POST /api/chat/{user_id}"""

    def test_send_message_success(self, client: TestClient, test_user, auth_headers):
        """Test sending a message creates a conversation and returns a response."""
        response = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Hello, create a task called Buy groceries"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "conversation_id" in data
        assert "timestamp" in data
        assert "action_taken" in data
        assert len(data["conversation_id"]) > 0

    def test_send_message_creates_conversation_in_db(
        self, client: TestClient, test_user, auth_headers, session: Session
    ):
        """Sending a message persists a conversation record."""
        response = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "List all my tasks"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        conv_id = uuid.UUID(response.json()["conversation_id"])
        conversation = session.get(Conversation, conv_id)
        assert conversation is not None
        assert conversation.user_id == test_user.id

    def test_send_message_continues_existing_conversation(
        self, client: TestClient, test_user, auth_headers
    ):
        """Sending with an existing conversation_id reuses it."""
        # First message
        r1 = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Hello"},
            headers=auth_headers,
        )
        assert r1.status_code == 200
        conv_id = r1.json()["conversation_id"]

        # Second message using same conversation
        r2 = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Show my tasks", "conversation_id": conv_id},
            headers=auth_headers,
        )
        assert r2.status_code == 200
        assert r2.json()["conversation_id"] == conv_id

    def test_send_message_wrong_user_forbidden(
        self, client: TestClient, test_user, test_user2, auth_headers
    ):
        """User cannot send messages on behalf of another user."""
        response = client.post(
            f"/api/chat/{test_user2.id}",
            json={"message": "Hello"},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_send_message_unauthenticated(self, client: TestClient, test_user):
        """Unauthenticated request is rejected."""
        response = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Hello"},
        )
        assert response.status_code == 401

    def test_send_message_invalid_conversation_id(
        self, client: TestClient, test_user, auth_headers
    ):
        """Invalid UUID for conversation_id returns 400."""
        response = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Hello", "conversation_id": "not-a-uuid"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_send_empty_message(self, client: TestClient, test_user, auth_headers):
        """Empty message should return a response (not crash)."""
        response = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": ""},
            headers=auth_headers,
        )
        # Either 200 with a response or 422 validation error — both acceptable
        assert response.status_code in [200, 422]

    def test_chatbot_task_creation_intent(
        self, client: TestClient, test_user, auth_headers
    ):
        """Message with creation intent gets parsed correctly."""
        response = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Create a new task: Buy milk"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # action_taken should reflect the detected intent
        assert data["action_taken"] is not None

    def test_chatbot_listing_intent(
        self, client: TestClient, test_user, auth_headers
    ):
        """Message asking to list tasks is handled."""
        response = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Show me all my tasks"},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_chatbot_deletion_intent(
        self, client: TestClient, test_user, auth_headers
    ):
        """Message asking to delete a task is handled."""
        response = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Delete task abc123"},
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestGetConversations:
    """Tests for GET /api/chat/{user_id}/conversations"""

    def test_get_conversations_empty(
        self, client: TestClient, test_user, auth_headers
    ):
        """Returns empty list when no conversations exist."""
        response = client.get(
            f"/api/chat/{test_user.id}/conversations",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert data["total_count"] == 0

    def test_get_conversations_after_chat(
        self, client: TestClient, test_user, auth_headers
    ):
        """Conversations list populates after sending a message."""
        client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Hello"},
            headers=auth_headers,
        )
        response = client.get(
            f"/api/chat/{test_user.id}/conversations",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["total_count"] >= 1

    def test_get_conversations_wrong_user(
        self, client: TestClient, test_user, test_user2, auth_headers
    ):
        """Cannot list another user's conversations."""
        response = client.get(
            f"/api/chat/{test_user2.id}/conversations",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_get_conversations_unauthenticated(
        self, client: TestClient, test_user
    ):
        """Unauthenticated request is rejected."""
        response = client.get(f"/api/chat/{test_user.id}/conversations")
        assert response.status_code == 401


class TestGetConversationHistory:
    """Tests for GET /api/chat/{user_id}/conversations/{conversation_id}"""

    def test_get_conversation_history(
        self, client: TestClient, test_user, auth_headers
    ):
        """Can retrieve message history for a conversation."""
        # Create a conversation first
        r = client.post(
            f"/api/chat/{test_user.id}",
            json={"message": "Hello chatbot"},
            headers=auth_headers,
        )
        conv_id = r.json()["conversation_id"]

        response = client.get(
            f"/api/chat/{test_user.id}/conversations/{conv_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) >= 1

    def test_get_nonexistent_conversation(
        self, client: TestClient, test_user, auth_headers
    ):
        """Returns 404 for a conversation that doesn't exist."""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/chat/{test_user.id}/conversations/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
