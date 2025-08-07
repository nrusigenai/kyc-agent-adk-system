from abc import ABC, abstractmethod
from typing import Any, Dict
import logging
import asyncio
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all KYC agents"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        self.status = "idle"
        
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data and return result"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health status"""
        return {
            "agent": self.name,
            "status": self.status,
            "timestamp": datetime.now().isoformat(),
            "config": self.config
        }
    
    def log_activity(self, message: str, level: str = "info"):
        """Log agent activity"""
        getattr(self.logger, level)(f"[{self.name}] {message}")
        
    async def set_status(self, status: str):
        """Update agent status"""
        self.status = status
        self.log_activity(f"Status changed to: {status}")
