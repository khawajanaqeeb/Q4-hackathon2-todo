"""
Communication Framework for Todo AI Chatbot

Provides a standardized communication protocol between agents in the system.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum


class MessageType(Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"
    HEARTBEAT = "HEARTBEAT"


@dataclass
class Message:
    """Standard message format for agent communication."""

    request_id: str
    timestamp: str
    sender: str
    receiver: str
    action: str
    payload: Dict[str, Any]
    context: Dict[str, Any]
    message_type: MessageType = MessageType.REQUEST

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        result = asdict(self)
        result['message_type'] = self.message_type.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary format."""
        message_type = MessageType(data.pop('message_type'))
        return cls(message_type=message_type, **data)


class AgentCommunicator:
    """Manages communication between agents using a standardized protocol."""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.agent_registry: Dict[str, Any] = {}

    def register_agent(self, agent_name: str, agent_instance: Any):
        """Register an agent with the communicator."""
        self.agent_registry[agent_name] = agent_instance

    def register_handler(self, action: str, handler: Callable):
        """Register a handler for a specific action."""
        self.handlers[action] = handler

    def send_message(self, sender: str, receiver: str, action: str,
                     payload: Dict[str, Any], context: Dict[str, Any] = None) -> Message:
        """Send a message from one agent to another."""
        if context is None:
            context = {}

        message = Message(
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender=sender,
            receiver=receiver,
            action=action,
            payload=payload,
            context=context
        )

        return message

    def broadcast_message(self, sender: str, action: str,
                         payload: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Message]:
        """Broadcast a message to all registered agents."""
        if context is None:
            context = {}

        responses = {}
        for receiver in self.agent_registry.keys():
            if receiver != sender:  # Don't send to self
                message = self.send_message(sender, receiver, action, payload, context)
                responses[receiver] = message

        return responses

    def route_message(self, message: Message) -> Optional[Message]:
        """Route a message to the appropriate handler or agent."""
        if message.action in self.handlers:
            # Handle with registered handler
            try:
                result = self.handlers[message.action](message)
                return Message(
                    request_id=message.request_id,
                    timestamp=datetime.now().isoformat(),
                    sender=self.__class__.__name__,
                    receiver=message.sender,
                    action=f"{message.action}_response",
                    payload=result,
                    context=message.context,
                    message_type=MessageType.RESPONSE
                )
            except Exception as e:
                return Message(
                    request_id=message.request_id,
                    timestamp=datetime.now().isoformat(),
                    sender=self.__class__.__name__,
                    receiver=message.sender,
                    action=f"{message.action}_error",
                    payload={"error": str(e)},
                    context=message.context,
                    message_type=MessageType.ERROR
                )
        elif message.receiver in self.agent_registry:
            # Forward to registered agent
            target_agent = self.agent_registry[message.receiver]
            if hasattr(target_agent, 'handle_message'):
                try:
                    result = target_agent.handle_message(message)
                    return Message(
                        request_id=message.request_id,
                        timestamp=datetime.now().isoformat(),
                        sender=target_agent.__class__.__name__,
                        receiver=message.sender,
                        action=f"{message.action}_response",
                        payload=result,
                        context=message.context,
                        message_type=MessageType.RESPONSE
                    )
                except Exception as e:
                    return Message(
                        request_id=message.request_id,
                        timestamp=datetime.now().isoformat(),
                        sender=target_agent.__class__.__name__,
                        receiver=message.sender,
                        action=f"{message.action}_error",
                        payload={"error": str(e)},
                        context=message.context,
                        message_type=MessageType.ERROR
                    )

        return None

    def serialize_message(self, message: Message) -> str:
        """Serialize a message to JSON string."""
        return json.dumps(message.to_dict())

    def deserialize_message(self, message_str: str) -> Message:
        """Deserialize a JSON string to a message."""
        data = json.loads(message_str)
        return Message.from_dict(data)


# Example usage
if __name__ == "__main__":
    # Create communicator
    comm = AgentCommunicator()

    # Example agent
    class ExampleAgent:
        def handle_message(self, message: Message):
            return {"status": "processed", "original_action": message.action}

    # Register an agent
    example_agent = ExampleAgent()
    comm.register_agent("example_agent", example_agent)

    # Create and send a message
    msg = comm.send_message(
        sender="user_interface",
        receiver="example_agent",
        action="process_request",
        payload={"data": "some data"},
        context={"user_id": "123", "session_id": "abc"}
    )

    print("Original message:")
    print(comm.serialize_message(msg))

    # Route the message
    response = comm.route_message(msg)
    if response:
        print("\nResponse message:")
        print(comm.serialize_message(response))