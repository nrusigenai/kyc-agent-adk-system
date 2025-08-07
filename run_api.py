#!/usr/bin/env python3
"""
KYC Agent API Server Startup Script
Starts the FastAPI backend with Google ADK agent system
"""

import uvicorn
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Start the KYC Agent API server"""
    logger.info("🚀 Starting KYC Agent API with Google ADK...")
    logger.info("📡 API will be available at: http://localhost:8000")
    logger.info("📚 API docs will be available at: http://localhost:8000/docs")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
