import os
from typing import Dict, Any

class Config:
    """Configuration management for Customer Document Analysis Agent"""
    
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us")
    DOCUMENT_AI_PROCESSOR_ID = os.getenv("DOCUMENT_AI_PROCESSOR_ID", "")
    
    AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", 30))
    MAX_CONCURRENT_AGENTS = int(os.getenv("MAX_CONCURRENT_AGENTS", 10))
    
    USE_PERSISTENT_STORAGE = os.getenv("USE_PERSISTENT_STORAGE", "false").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    API_KEY = os.getenv("API_KEY", "")
    ENABLE_CORS = os.getenv("ENABLE_CORS", "true").lower() == "true"
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Dict[str, Any]:
        """Get configuration for specific agent"""
        base_config = {
            "timeout": cls.AGENT_TIMEOUT,
            "google_cloud_project": cls.GOOGLE_CLOUD_PROJECT,
            "google_cloud_location": cls.GOOGLE_CLOUD_LOCATION
        }
        
        if agent_name == "IngestionAgent":
            base_config.update({
                "processor_id": cls.DOCUMENT_AI_PROCESSOR_ID,
                "supported_formats": ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
            })
        
        return base_config
