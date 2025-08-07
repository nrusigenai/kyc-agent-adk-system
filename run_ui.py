#!/usr/bin/env python3
"""
KYC Agent Streamlit UI Startup Script
Starts the Streamlit frontend interface
"""

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Start the Streamlit UI"""
    logger.info("🎨 Starting KYC Agent Streamlit UI...")
    logger.info("🌐 UI will be available at: http://localhost:8501")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--theme.primaryColor=#667eea",
            "--theme.backgroundColor=#ffffff",
            "--theme.secondaryBackgroundColor=#f0f2f6"
        ])
    except KeyboardInterrupt:
        logger.info("🛑 UI stopped by user")
    except Exception as e:
        logger.error(f"❌ UI error: {e}")

if __name__ == "__main__":
    main()
