"""
Tests for the Communication Framework
"""

import pytest
from .communication import AgentCommunicator, Message, MessageType
from .message_protocol import MessageProtocol


def test_create_message():
    """Test creating a basic message."""
    comm = AgentCommunicator()

    message = comm.send_message(
        sender="test_sender",
        receiver="test_receiver",
        action="test_action",
        payload={"test": "data"},
        context={"user_id": "123"}
    )

    assert message.sender == "test_sender"
    assert message.receiver == "test_receiver"
    assert message.action == "test_action"
    assert message.payload == {"test": "data"}
    assert message.context == {"user_id": "123"}
    assert message.message_type == MessageType.REQUEST


def test_register_agent():
    """Test registering an agent with the communicator."""
    comm = AgentCommunicator()

    class TestAgent:
        def handle_message(self, message):
            return {"handled": True}

    test_agent = TestAgent()
    comm.register_agent("test_agent", test_agent)

    assert "test_agent" in comm.agent_registry
    assert comm.agent_registry["test_agent"] == test_agent


def test_register_handler():
    """Test registering a handler with the communicator."""
    comm = AgentCommunicator()

    def test_handler(message):
        return {"handled": True}

    comm.register_handler("test_action", test_handler)

    assert "test_action" in comm.handlers
    assert comm.handlers["test_action"] == test_handler


def test_serialize_deserialize_message():
    """Test serializing and deserializing a message."""
    comm = AgentCommunicator()

    original_message = comm.send_message(
        sender="test_sender",
        receiver="test_receiver",
        action="test_action",
        payload={"test": "data"},
        context={"user_id": "123"}
    )

    serialized = comm.serialize_message(original_message)
    deserialized = comm.deserialize_message(serialized)

    assert deserialized.request_id == original_message.request_id
    assert deserialized.sender == original_message.sender
    assert deserialized.receiver == original_message.receiver
    assert deserialized.action == original_message.action
    assert deserialized.payload == original_message.payload
    assert deserialized.context == original_message.context


def test_broadcast_message():
    """Test broadcasting a message to multiple agents."""
    comm = AgentCommunicator()

    class TestAgent:
        def handle_message(self, message):
            return {"handled_by": self.__class__.__name__}

    agent1 = TestAgent()
    agent2 = TestAgent()

    comm.register_agent("agent1", agent1)
    comm.register_agent("agent2", agent2)

    responses = comm.broadcast_message(
        sender="broadcaster",
        action="broadcast_test",
        payload={"test": "data"},
        context={"user_id": "123"}
    )

    assert len(responses) == 2
    assert "agent1" in responses
    assert "agent2" in responses


def test_message_protocol_create_message():
    """Test creating a message with the message protocol."""
    message = MessageProtocol.create_message(
        sender="test_sender",
        receiver="test_receiver",
        action="test_action",
        payload={"test": "data"},
        context={"user_id": "123"}
    )

    assert message["sender"] == "test_sender"
    assert message["receiver"] == "test_receiver"
    assert message["action"] == "test_action"
    assert message["payload"]["test"] == "data"
    assert message["context"]["user_id"] == "123"
    assert "correlation_id" in message
    assert "request_id" in message
    assert "timestamp" in message


def test_message_protocol_create_response():
    """Test creating a response with the message protocol."""
    original_message = MessageProtocol.create_message(
        sender="sender",
        receiver="receiver",
        action="test_action",
        payload={"test": "data"}
    )

    response = MessageProtocol.create_response(
        original_message=original_message,
        payload={"result": "success"}
    )

    assert response["sender"] == "receiver"  # Should be reversed
    assert response["receiver"] == "sender"  # Should be reversed
    assert response["action"] == "test_action_response"
    assert response["payload"]["result"] == "success"
    assert response["status"] == "success"


def test_message_protocol_create_error_response():
    """Test creating an error response with the message protocol."""
    original_message = MessageProtocol.create_message(
        sender="sender",
        receiver="receiver",
        action="test_action",
        payload={"test": "data"}
    )

    error_response = MessageProtocol.create_error_response(
        original_message=original_message,
        error_code="TEST_ERROR",
        error_message="This is a test error"
    )

    assert error_response["status"] == "error"
    assert error_response["payload"]["error"]["code"] == "TEST_ERROR"
    assert error_response["payload"]["error"]["message"] == "This is a test error"


def test_message_protocol_validate_message():
    """Test validating a message with the message protocol."""
    valid_message = MessageProtocol.create_message(
        sender="sender",
        receiver="receiver",
        action="test_action",
        payload={"test": "data"}
    )

    is_valid = MessageProtocol.validate_message(valid_message)
    assert is_valid is True

    # Test with missing field
    invalid_message = MessageProtocol.create_message(
        sender="sender",
        receiver="receiver",
        action="test_action",
        payload={"test": "data"}
    )
    del invalid_message["correlation_id"]

    is_valid = MessageProtocol.validate_message(invalid_message)
    assert is_valid is False


def test_message_protocol_serialize_deserialize():
    """Test serializing and deserializing messages with the protocol."""
    original_message = MessageProtocol.create_message(
        sender="sender",
        receiver="receiver",
        action="test_action",
        payload={"test": "data"}
    )

    serialized = MessageProtocol.serialize_message(original_message)
    deserialized = MessageProtocol.deserialize_message(serialized)

    assert deserialized["sender"] == original_message["sender"]
    assert deserialized["receiver"] == original_message["receiver"]
    assert deserialized["action"] == original_message["action"]
    assert deserialized["payload"] == original_message["payload"]


def test_message_protocol_extract_payload_and_context():
    """Test extracting payload and context from messages."""
    message = MessageProtocol.create_message(
        sender="sender",
        receiver="receiver",
        action="test_action",
        payload={"test": "data", "other": "value"},
        context={"user_id": "123", "session": "abc"}
    )

    payload = MessageProtocol.extract_payload(message)
    context = MessageProtocol.extract_context(message)

    assert payload["test"] == "data"
    assert payload["other"] == "value"
    assert context["user_id"] == "123"
    assert context["session"] == "abc"


if __name__ == "__main__":
    pytest.main([__file__])