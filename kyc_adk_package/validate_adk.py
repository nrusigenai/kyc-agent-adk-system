#!/usr/bin/env python3
"""
ADK Component Validation Script
Validates that all ADK components can be imported successfully
"""

import sys
import traceback

def validate_adk_components():
    """Validate all ADK components can be imported"""
    try:
        print("Validating core ADK components...")
        from adk.core.agent_manager import AgentManager
        from adk.core.agent_registry import AgentRegistry
        from adk.core.message_bus import MessageBus
        print("✅ Core components imported successfully")
        
        print("Validating ADK interfaces...")
        from adk.interfaces.agent_interface import AgentInterface
        from adk.interfaces.message_interface import MessageInterface
        print("✅ Interfaces imported successfully")
        
        print("Validating KYC agents...")
        from adk.agents.kyc_ingestion_agent import KYCIngestionAgent
        from adk.agents.kyc_parsing_agent import KYCParsingAgent
        from adk.agents.kyc_gap_analysis_agent import KYCGapAnalysisAgent
        from adk.agents.kyc_verification_agent import KYCVerificationAgent
        print("✅ KYC agents imported successfully")
        
        print("Validating data models...")
        from adk.models.kyc_models import KYCBrief, Document, GapAnalysisResult, VerificationResult
        print("✅ Data models imported successfully")
        
        print("✅ All ADK components validated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ADK validation failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_adk_components()
    sys.exit(0 if success else 1)
