from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import uuid

class MessageInterface(ABC):
    """
    Google ADK compatible message interface
    Defines message structure for agent communication
    """
    
    def __init__(self, 
                 message_type: str,
                 sender_id: str,
                 recipient_id: str,
                 payload: Dict[str, Any],
                 correlation_id: Optional[str] = None):
        self.message_id = str(uuid.uuid4())
        self.message_type = message_type
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.payload = payload
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.now()
        self.status = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageInterface':
        """Create message from dictionary"""
        message = cls(
            message_type=data["message_type"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            payload=data["payload"],
            correlation_id=data.get("correlation_id")
        )
        message.message_id = data["message_id"]
        message.timestamp = datetime.fromisoformat(data["timestamp"])
        message.status = data["status"]
        return message
