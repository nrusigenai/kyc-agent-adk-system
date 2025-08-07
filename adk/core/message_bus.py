import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid

from ..interfaces.message_interface import MessageInterface

class MessageBus:
    """
    Google ADK compatible message bus
    Handles async message routing between agents
    """
    
    def __init__(self):
        self._message_queues: Dict[str, asyncio.Queue] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_history: List[Dict[str, Any]] = []
        self._running = False
        
    async def start(self):
        """Start the message bus"""
        self._running = True
        
    async def stop(self):
        """Stop the message bus"""
        self._running = False
        
    async def register_agent(self, agent_id: str) -> bool:
        """Register an agent with the message bus"""
        if agent_id not in self._message_queues:
            self._message_queues[agent_id] = asyncio.Queue()
            self._subscribers[agent_id] = []
            return True
        return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the message bus"""
        if agent_id in self._message_queues:
            del self._message_queues[agent_id]
            del self._subscribers[agent_id]
            return True
        return False
    
    async def send_message(self, message: MessageInterface) -> bool:
        """Send a message to a specific agent"""
        try:
            if not self._running:
                return False
                
            recipient_id = message.recipient_id
            
            if recipient_id not in self._message_queues:
                return False
            
            self._message_history.append({
                "message": message.to_dict(),
                "timestamp": datetime.now().isoformat(),
                "status": "sent"
            })
            
            await self._message_queues[recipient_id].put(message)
            message.status = "delivered"
            
            return True
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    async def receive_message(self, agent_id: str, timeout: float = 1.0) -> Optional[MessageInterface]:
        """Receive a message for a specific agent"""
        try:
            if agent_id not in self._message_queues:
                return None
            
            message = await asyncio.wait_for(
                self._message_queues[agent_id].get(),
                timeout=timeout
            )
            
            message.status = "received"
            return message
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            print(f"Failed to receive message: {e}")
            return None
    
    async def broadcast_message(self, message: MessageInterface, exclude_sender: bool = True) -> int:
        """Broadcast a message to all registered agents"""
        sent_count = 0
        
        for agent_id in self._message_queues.keys():
            if exclude_sender and agent_id == message.sender_id:
                continue
                
            broadcast_message = MessageInterface(
                message_type=message.message_type,
                sender_id=message.sender_id,
                recipient_id=agent_id,
                payload=message.payload.copy(),
                correlation_id=message.correlation_id
            )
            
            if await self.send_message(broadcast_message):
                sent_count += 1
        
        return sent_count
    
    async def subscribe_to_message_type(self, agent_id: str, message_type: str, callback: Callable):
        """Subscribe an agent to a specific message type"""
        if agent_id in self._subscribers:
            self._subscribers[agent_id].append({
                "message_type": message_type,
                "callback": callback
            })
    
    async def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent message history"""
        return self._message_history[-limit:]
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get status of all message queues"""
        status = {}
        for agent_id, queue in self._message_queues.items():
            status[agent_id] = {
                "queue_size": queue.qsize(),
                "subscribers": len(self._subscribers.get(agent_id, []))
            }
        return status
    
    async def get_status(self) -> Dict[str, Any]:
        """Get overall message bus status"""
        return {
            "running": self._running,
            "registered_agents": len(self._message_queues),
            "total_messages": len(self._message_history),
            "queue_status": await self.get_queue_status(),
            "timestamp": datetime.now().isoformat()
        }
