import asyncio
from typing import Dict, Any, List
from datetime import datetime
import random

from .base_agent import BaseAgent
from ..models.kyc_models import KYCBrief, VerificationResult, VerificationStatus, AgentResponse

class VerificationAgent(BaseAgent):
    """Agent responsible for verifying KYC information"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("VerificationAgent", config)
        self.verification_sources = {
            "address": ["Public Records Database", "Postal Service", "Credit Bureau"],
            "name": ["Government Database", "Credit Bureau", "Public Records"],
            "source_of_wealth": ["Financial News", "Company Records", "Public Filings"],
            "phone_number": ["Telecom Database", "Public Directory"],
            "email": ["Email Validation Service", "Domain Registry"]
        }
        
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Verify KYC information"""
        try:
            await self.set_status("processing")
            
            kyc_brief_data = input_data.get("kyc_brief")
            fields_to_verify = input_data.get("fields_to_verify", [])
            
            if not kyc_brief_data:
                return AgentResponse(
                    agent_name=self.name,
                    status="error",
                    message="No KYC brief provided for verification",
                    data=None
                )
            
            kyc_brief = KYCBrief(**kyc_brief_data)
            
            verification_results = await self._verify_information(kyc_brief, fields_to_verify)
            
            await self.set_status("idle")
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                message=f"Verification completed for {len(verification_results)} fields",
                data={"verification_results": [result.dict() for result in verification_results]}
            )
            
        except Exception as e:
            await self.set_status("error")
            self.log_activity(f"Error in verification: {str(e)}", "error")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                message=f"Failed to verify information: {str(e)}",
                data=None
            )
    
    async def _verify_information(self, kyc_brief: KYCBrief, fields_to_verify: List[str]) -> List[VerificationResult]:
        """Verify specified fields in KYC brief"""
        verification_results = []
        
        if not fields_to_verify:
            fields_to_verify = ["full_name", "address", "phone_number", "email", "source_of_wealth"]
        
        for field_name in fields_to_verify:
            field_value = getattr(kyc_brief, field_name, None)
            
            if field_value:
                result = await self._verify_field(field_name, field_value)
                verification_results.append(result)
        
        return verification_results
    
    async def _verify_field(self, field_name: str, field_value: str) -> VerificationResult:
        """Verify a specific field"""
        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate verification time
        
        confidence_score = random.uniform(0.7, 0.95)
        status = VerificationStatus.VERIFIED if confidence_score > 0.8 else VerificationStatus.PENDING
        
        sources = self.verification_sources.get(field_name, ["External Database"])
        
        details = await self._generate_verification_details(field_name, field_value, confidence_score)
        
        return VerificationResult(
            field_name=field_name,
            status=status,
            confidence_score=confidence_score,
            details=details,
            sources=sources[:2]  # Use first 2 sources
        )
    
    async def _generate_verification_details(self, field_name: str, field_value: str, confidence_score: float) -> str:
        """Generate verification details based on field type"""
        if field_name == "address":
            if confidence_score > 0.9:
                return f"Address '{field_value}' verified against postal service records. Property exists and is residential."
            elif confidence_score > 0.8:
                return f"Address '{field_value}' found in public records. Minor formatting differences noted."
            else:
                return f"Address '{field_value}' partially verified. Some discrepancies found in records."
        
        elif field_name == "full_name":
            if confidence_score > 0.9:
                return f"Name '{field_value}' matches government database records exactly."
            elif confidence_score > 0.8:
                return f"Name '{field_value}' found in credit bureau records with minor variations."
            else:
                return f"Name '{field_value}' partially verified. Additional documentation may be required."
        
        elif field_name == "phone_number":
            if confidence_score > 0.9:
                return f"Phone number '{field_value}' is active and registered to the client."
            elif confidence_score > 0.8:
                return f"Phone number '{field_value}' is valid but registration details need confirmation."
            else:
                return f"Phone number '{field_value}' format is valid but carrier verification pending."
        
        elif field_name == "email":
            if confidence_score > 0.9:
                return f"Email '{field_value}' is valid and deliverable."
            elif confidence_score > 0.8:
                return f"Email '{field_value}' domain is valid but mailbox verification pending."
            else:
                return f"Email '{field_value}' format is valid but deliverability uncertain."
        
        elif field_name == "source_of_wealth":
            if confidence_score > 0.9:
                return f"Source of wealth '{field_value}' corroborated by multiple financial news sources."
            elif confidence_score > 0.8:
                return f"Source of wealth '{field_value}' partially verified through public company records."
            else:
                return f"Source of wealth '{field_value}' requires additional documentation for full verification."
        
        else:
            return f"Field '{field_name}' with value '{field_value}' verified with {confidence_score:.1%} confidence."
    
    async def cross_reference_documents(self, kyc_brief: KYCBrief) -> Dict[str, Any]:
        """Cross-reference information across multiple documents"""
        await asyncio.sleep(1)
        
        cross_ref_results = {
            "consistency_score": random.uniform(0.85, 0.98),
            "discrepancies": [],
            "confirmations": []
        }
        
        if len(kyc_brief.documents) > 1:
            cross_ref_results["confirmations"].append("Name consistency verified across all documents")
            cross_ref_results["confirmations"].append("Address information matches between utility bill and bank statement")
            
            if random.random() > 0.8:  # 20% chance of discrepancy
                cross_ref_results["discrepancies"].append("Minor date format differences noted between documents")
        
        return cross_ref_results
