"""
Google ADK (Agent Development Kit) compatible structure
for KYC multi-agent system
"""

from .core.agent_registry import AgentRegistry
from .core.agent_manager import AgentManager
from .interfaces.agent_interface import AgentInterface
from .interfaces.message_interface import MessageInterface

__version__ = "1.0.0"
__all__ = [
    "AgentRegistry",
    "AgentManager", 
    "AgentInterface",
    "MessageInterface"
]
