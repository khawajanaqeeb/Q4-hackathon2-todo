"""
Message Protocol for Todo AI Chatbot

Defines standardized message formats and protocols for agent communication.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict, field


class MessageProtocol:
    """
    Defines the standardized message format and protocol for agent communication.

    All agents in the system will communicate using this protocol.
    """

    @staticmethod
    def create_message(
        sender: str,
        receiver: str,
        action: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        message_type: str = "request"
    ) -> Dict[str, Any]:
        """
        Create a standardized message following the protocol.

        Args:
            sender: Name of the sending agent
            receiver: Name of the receiving agent
            action: Action to be performed
            payload: Data to be transmitted
            context: Contextual information
            correlation_id: ID to correlate related messages
            message_type: Type of message (request, response, error, etc.)

        Returns:
            Dictionary representing the standardized message
        """
        if context is None:
            context = {}

        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        message = {
            "protocol_version": "1.0",
            "correlation_id": correlation_id,
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "receiver": receiver,
            "action": action,
            "message_type": message_type,
            "payload": payload,
            "context": context,
            "meta": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

        return message

    @staticmethod
    def create_response(
        original_message: Dict[str, Any],
        payload: Dict[str, Any],
        status: str = "success"
    ) -> Dict[str, Any]:
        """
        Create a standardized response message.

        Args:
            original_message: The original message being responded to
            payload: Response data
            status: Status of the response (success, error, etc.)

        Returns:
            Dictionary representing the standardized response message
        """
        response = {
            "protocol_version": "1.0",
            "correlation_id": original_message.get("correlation_id"),
            "request_id": original_message.get("request_id"),
            "timestamp": datetime.now().isoformat(),
            "sender": original_message.get("receiver", "system"),
            "receiver": original_message.get("sender"),
            "action": f"{original_message.get('action', 'unknown')}_response",
            "message_type": "response",
            "status": status,
            "payload": payload,
            "context": original_message.get("context", {}),
            "meta": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "original_action": original_message.get("action")
            }
        }

        return response

    @staticmethod
    def create_error_response(
        original_message: Dict[str, Any],
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized error response message.

        Args:
            original_message: The original message that caused the error
            error_code: Code representing the error
            error_message: Human-readable error message
            details: Additional error details

        Returns:
            Dictionary representing the standardized error message
        """
        if details is None:
            details = {}

        error_payload = {
            "error": {
                "code": error_code,
                "message": error_message,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
        }

        return MessageProtocol.create_response(
            original_message=original_message,
            payload=error_payload,
            status="error"
        )

    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
        """
        Validate that a message follows the protocol.

        Args:
            message: Message to validate

        Returns:
            True if message is valid, False otherwise
        """
        required_fields = [
            "protocol_version",
            "correlation_id",
            "request_id",
            "timestamp",
            "sender",
            "receiver",
            "action",
            "message_type",
            "payload",
            "context"
        ]

        for field in required_fields:
            if field not in message:
                return False

        # Check that protocol version is supported
        if message["protocol_version"] != "1.0":
            return False

        return True

    @staticmethod
    def serialize_message(message: Dict[str, Any]) -> str:
        """
        Serialize a message to JSON string.

        Args:
            message: Message to serialize

        Returns:
            JSON string representation of the message
        """
        return json.dumps(message, indent=2)

    @staticmethod
    def deserialize_message(message_str: str) -> Dict[str, Any]:
        """
        Deserialize a JSON string to a message.

        Args:
            message_str: JSON string to deserialize

        Returns:
            Dictionary representing the message
        """
        return json.loads(message_str)

    @staticmethod
    def extract_payload(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract the payload from a message.

        Args:
            message: Message containing payload

        Returns:
            Payload dictionary
        """
        return message.get("payload", {})

    @staticmethod
    def extract_context(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract the context from a message.

        Args:
            message: Message containing context

        Returns:
            Context dictionary
        """
        return message.get("context", {})


# Example usage and testing
if __name__ == "__main__":
    # Create a sample message
    msg = MessageProtocol.create_message(
        sender="nlp_agent",
        receiver="command_interpreter_agent",
        action="process_intent",
        payload={
            "intent": "ADD_TODO",
            "entities": {"date": "tomorrow", "priority": "high"},
            "confidence": 0.95
        },
        context={
            "user_id": "user123",
            "session_id": "session456",
            "conversation_history": []
        }
    )

    print("Created message:")
    print(MessageProtocol.serialize_message(msg))

    # Validate the message
    is_valid = MessageProtocol.validate_message(msg)
    print(f"\nMessage is valid: {is_valid}")

    # Create a response
    response = MessageProtocol.create_response(
        original_message=msg,
        payload={
            "method": "POST",
            "endpoint": "/api/todos",
            "data": {"content": "todo content", "priority": "high", "due_date": "tomorrow"}
        }
    )

    print("\nResponse message:")
    print(MessageProtocol.serialize_message(response))

    # Create an error response
    error_response = MessageProtocol.create_error_response(
        original_message=msg,
        error_code="INVALID_INPUT",
        error_message="The input could not be processed",
        details={"raw_input": "unclear command"}
    )

    print("\nError response:")
    print(MessageProtocol.serialize_message(error_response))