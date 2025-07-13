from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from enum import Enum

class AgentMessageType(str, Enum):
    """Defines types of messages exchanged between agents."""
    TASK_REQUEST = "task_request"
    TASK_STATUS = "task_status"
    TASK_RESULT = "task_result"
    ERROR_REPORT = "error_report"
    INFO = "info"

class AgentMessage(BaseModel):
    """Represents a standardized message exchanged between agents."""
    sender: str = Field(..., description="The name of the sending agent.")
    receiver: str = Field(..., description="The name of the receiving agent.")
    message_type: AgentMessageType = Field(..., description="The type of message.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="The content of the message.")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat(), description="Timestamp of message creation.")

class AgentCommunicationChannel:
    """
    A simplified in-memory communication channel for agents.
    In a real system, this would be a message queue (e.g., Kafka, RabbitMQ).
    """
    def __init__(self):
        self._message_queue: List[AgentMessage] = []

    def send_message(self, message: AgentMessage) -> None:
        """Sends a message to the channel."""
        print(f"[COMMUNICATION] Sending from {message.sender} to {message.receiver}: {message.message_type.value}")
        self._message_queue.append(message)

    def receive_messages(self, receiver: str) -> List[AgentMessage]:
        """
        Retrieves messages for a specific receiver from the channel.
        (Simplified: In a real system, messages would be consumed and removed).
        """
        received = [msg for msg in self._message_queue if msg.receiver == receiver]
        # In a real system, messages would be removed after consumption.
        # For this simulation, we keep them for simplicity.
        return received

    def clear_channel(self) -> None:
        """Clears all messages from the channel (for testing/resetting)."""
        self._message_queue = []
