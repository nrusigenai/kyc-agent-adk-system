import asyncio
import uuid
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..interfaces.agent_interface import AgentInterface
from ..models.kyc_models import KYCBrief, VerificationResult, VerificationStatus

class KYCVerificationAgent(AgentInterface):
    """
    Google ADK compatible KYC Verification Agent
    Cross-references information with external databases and sources
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id or f"kyc_verification_{uuid.uuid4().hex[:8]}",
            agent_type="KYCVerificationAgent",
            config=config or {}
        )
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute verification task"""
        try:
            await self.update_status("processing")
            
            kyc_brief_data = task.get("kyc_brief")
            fields_to_verify = task.get("fields_to_verify", [])
            
            if not kyc_brief_data:
                raise ValueError("No KYC brief provided for verification")
            
            kyc_brief = KYCBrief(**kyc_brief_data)
            
            await asyncio.sleep(2.0)
            
            verification_results = await self._verify_information(kyc_brief, fields_to_verify)
            
            sanctions_check = await self._verify_against_sanctions_list(kyc_brief.full_name or "")
            document_authenticity = await self._verify_document_authenticity(kyc_brief.documents)
            
            await self.update_status("idle")
            
            return {
                "success": True,
                "verification_results": verification_results,
                "sanctions_check": sanctions_check,
                "document_authenticity": document_authenticity,
                "message": f"Verification completed for {len(verification_results)} fields",
                "processing_time": 2.0
            }
            
        except Exception as e:
            await self.update_status("error")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to verify information: {str(e)}"
            }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for verification"""
        kyc_brief = input_data.get("kyc_brief")
        
        if not kyc_brief:
            return False
        
        if "client_id" not in kyc_brief:
            return False
        
        return True
    
    async def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "identity_verification",
            "sanctions_screening",
            "document_authenticity",
            "address_verification",
            "database_cross_reference",
            "risk_assessment"
        ]
    
    async def _verify_information(self, kyc_brief: KYCBrief, fields_to_verify: List[str]) -> List[Dict[str, Any]]:
        """Verify information against external sources"""
        await asyncio.sleep(1.5)  # Simulate verification time
        
        verification_results = []
        
        if not fields_to_verify:
            fields_to_verify = ["full_name", "date_of_birth", "address", "nationality"]
        
        for field_name in fields_to_verify:
            field_value = getattr(kyc_brief, field_name, None)
            
            if field_value:
                result = await self._verify_field(field_name, field_value, kyc_brief)
                result_dict = result.dict()
                if "verified_at" in result_dict:
                    result_dict["verified_at"] = result_dict["verified_at"].isoformat()
                verification_results.append(result_dict)
        
        return verification_results
    
    async def _verify_field(self, field_name: str, field_value: str, kyc_brief: KYCBrief) -> VerificationResult:
        """Verify a specific field against external databases"""
        await asyncio.sleep(0.5)  # Simulate API call
        
        if field_name == "full_name":
            confidence = 0.95 if "John Smith" in field_value else random.uniform(0.7, 0.9)
            status = VerificationStatus.VERIFIED if confidence > 0.8 else VerificationStatus.FAILED
            details = f"Name verified against government database with {confidence:.1%} confidence"
            sources = ["Government ID Database", "Credit Bureau"]
            
        elif field_name == "date_of_birth":
            confidence = 0.92 if "1985" in field_value else random.uniform(0.75, 0.95)
            status = VerificationStatus.VERIFIED if confidence > 0.8 else VerificationStatus.FAILED
            details = f"Date of birth cross-referenced with official records"
            sources = ["Birth Registry", "Government ID Database"]
            
        elif field_name == "address":
            confidence = 0.88 if "123 Main Street" in field_value else random.uniform(0.6, 0.85)
            status = VerificationStatus.VERIFIED if confidence > 0.7 else VerificationStatus.FAILED
            details = f"Address verified against postal service and utility records"
            sources = ["Postal Service", "Utility Companies", "Property Records"]
            
        elif field_name == "nationality":
            confidence = 0.96 if field_value in ["USA", "United States"] else random.uniform(0.8, 0.95)
            status = VerificationStatus.VERIFIED if confidence > 0.8 else VerificationStatus.FAILED
            details = f"Nationality confirmed through passport and citizenship records"
            sources = ["Passport Database", "Immigration Records"]
            
        else:
            confidence = random.uniform(0.5, 0.8)
            status = VerificationStatus.PENDING
            details = f"Verification pending for {field_name}"
            sources = ["External Database"]
        
        return VerificationResult(
            field_name=field_name,
            status=status,
            confidence_score=confidence,
            details=details,
            sources=sources
        )
    
    async def _verify_against_sanctions_list(self, full_name: str) -> Dict[str, Any]:
        """Check against sanctions and watchlists"""
        await asyncio.sleep(1.0)
        
        is_sanctioned = False  # In real implementation, check against OFAC, UN, etc.
        
        return {
            "sanctioned": is_sanctioned,
            "watchlist_matches": [],
            "risk_score": random.uniform(0.1, 0.3),  # Low risk for demo
            "checked_lists": ["OFAC", "UN Sanctions", "EU Sanctions", "PEP List"],
            "last_updated": datetime.now().isoformat()
        }
    
    async def _verify_document_authenticity(self, documents: List[Any]) -> Dict[str, Any]:
        """Verify document authenticity using digital forensics"""
        await asyncio.sleep(1.5)
        
        document_results = []
        
        for doc in documents:
            authenticity_score = random.uniform(0.85, 0.98)
            
            if isinstance(doc, dict):
                doc_id = doc.get("id", "unknown")
                filename = doc.get("filename", "unknown")
            else:
                doc_id = getattr(doc, "id", "unknown")
                filename = getattr(doc, "filename", "unknown")
            
            document_results.append({
                "document_id": doc_id,
                "filename": filename,
                "authentic": authenticity_score > 0.8,
                "authenticity_score": authenticity_score,
                "security_features_detected": ["Watermark", "Security Thread", "Microprint"],
                "tampering_detected": False
            })
        
        overall_authenticity = sum(doc["authenticity_score"] for doc in document_results) / len(document_results) if document_results else 0
        
        return {
            "overall_authentic": overall_authenticity > 0.8,
            "overall_score": overall_authenticity,
            "documents": document_results,
            "verification_method": "Digital Forensics Analysis",
            "timestamp": datetime.now().isoformat()
        }
    
    async def verify_pep_status(self, full_name: str) -> Dict[str, Any]:
        """Check Politically Exposed Person (PEP) status"""
        await asyncio.sleep(0.8)
        
        is_pep = False  # Low probability for demo
        
        return {
            "is_pep": is_pep,
            "pep_category": None,
            "risk_level": "low",
            "sources_checked": ["World-Check", "PEP Database", "Government Records"],
            "last_updated": datetime.now().isoformat()
        }
