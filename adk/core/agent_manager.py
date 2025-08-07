from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

from .agent_registry import AgentRegistry
from .message_bus import MessageBus
from ..interfaces.agent_interface import AgentInterface
from ..interfaces.message_interface import MessageInterface

class AgentManager:
    """
    Google ADK compatible agent manager
    Orchestrates agent lifecycle and communication
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.message_bus = MessageBus()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        
    async def start_agent(self, agent: AgentInterface) -> bool:
        """Start an agent and register it"""
        try:
            success = await self.registry.register_agent(agent)
            if success:
                await agent.update_status("running")
                return True
            return False
        except Exception as e:
            print(f"Failed to start agent {agent.agent_id}: {e}")
            return False
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent and unregister it"""
        try:
            agent = await self.registry.get_agent(agent_id)
            if agent:
                await agent.update_status("stopped")
                
                if agent_id in self._running_tasks:
                    self._running_tasks[agent_id].cancel()
                    del self._running_tasks[agent_id]
                
                return await self.registry.unregister_agent(agent_id)
            return False
        except Exception as e:
            print(f"Failed to stop agent {agent_id}: {e}")
            return False
    
    async def execute_task(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on a specific agent"""
        try:
            agent = await self.registry.get_agent(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent {agent_id} not found"
                }
            
            if not await agent.validate_input(task):
                return {
                    "success": False,
                    "error": "Invalid input data"
                }
            
            await agent.update_status("processing")
            result = await agent.execute(task)
            await agent.update_status("idle")
            
            return {
                "success": True,
                "result": result,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            if agent:
                await agent.update_status("error")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def send_message(self, message: MessageInterface) -> bool:
        """Send a message between agents"""
        return await self.message_bus.send_message(message)
    
    async def orchestrate_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a multi-agent workflow"""
        try:
            workflow_id = workflow_config.get("workflow_id", "default")
            steps = workflow_config.get("steps", [])
            
            results = {}
            context = workflow_config.get("initial_context", {})
            
            for step in steps:
                agent_id = step.get("agent_id")
                task_data = step.get("task_data", {})
                
                task_data.update(context)
                
                step_result = await self.execute_task(agent_id, task_data)
                
                if not step_result.get("success"):
                    return {
                        "success": False,
                        "error": f"Workflow failed at step {step.get('name', 'unknown')}",
                        "step_error": step_result.get("error"),
                        "workflow_id": workflow_id
                    }
                
                context.update(step_result.get("result", {}))
                results[step.get("name", f"step_{len(results)}")] = step_result
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "results": results,
                "final_context": context,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_config.get("workflow_id", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        agents = await self.registry.list_agents()
        health_checks = await self.registry.health_check_all()
        
        return {
            "total_agents": len(agents),
            "agents": agents,
            "health_checks": health_checks,
            "message_bus_status": await self.message_bus.get_status(),
            "timestamp": datetime.now().isoformat()
        }
