from typing import Dict, List, Optional, Type
import asyncio
from datetime import datetime

from ..interfaces.agent_interface import AgentInterface

class AgentRegistry:
    """
    Google ADK compatible agent registry
    Manages agent registration and discovery
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentInterface] = {}
        self._agent_types: Dict[str, Type[AgentInterface]] = {}
        self._capabilities: Dict[str, List[str]] = {}
        
    async def register_agent(self, agent: AgentInterface) -> bool:
        """Register an agent instance"""
        try:
            self._agents[agent.agent_id] = agent
            capabilities = await agent.get_capabilities()
            self._capabilities[agent.agent_id] = capabilities
            return True
        except Exception as e:
            print(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            if agent_id in self._capabilities:
                del self._capabilities[agent_id]
            return True
        return False
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInterface]:
        """Get agent by ID"""
        return self._agents.get(agent_id)
    
    async def list_agents(self) -> List[Dict[str, any]]:
        """List all registered agents"""
        agents_info = []
        for agent_id, agent in self._agents.items():
            status = await agent.get_status()
            agents_info.append(status)
        return agents_info
    
    async def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that have a specific capability"""
        matching_agents = []
        for agent_id, capabilities in self._capabilities.items():
            if capability in capabilities:
                matching_agents.append(agent_id)
        return matching_agents
    
    async def find_agents_by_type(self, agent_type: str) -> List[str]:
        """Find agents by type"""
        matching_agents = []
        for agent_id, agent in self._agents.items():
            if agent.agent_type == agent_type:
                matching_agents.append(agent_id)
        return matching_agents
    
    async def health_check_all(self) -> Dict[str, Dict[str, any]]:
        """Perform health check on all agents"""
        health_results = {}
        for agent_id, agent in self._agents.items():
            try:
                health_results[agent_id] = await agent.health_check()
            except Exception as e:
                health_results[agent_id] = {
                    "agent_id": agent_id,
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        return health_results
