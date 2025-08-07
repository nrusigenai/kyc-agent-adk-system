import asyncio
import uuid
from typing import Dict, Any, List
from datetime import datetime

from ..interfaces.agent_interface import AgentInterface
from models.kyc_models import KYCBrief, GapAnalysisResult, DocumentType

class KYCGapAnalysisAgent(AgentInterface):
    """
    Google ADK compatible KYC Gap Analysis Agent
    Analyzes missing information and provides prioritized recommendations
    """
    
    def __init__(self, agent_id: str = None, config: Dict[str, Any] = None):
        super().__init__(
            agent_id=agent_id or f"kyc_gap_analysis_{uuid.uuid4().hex[:8]}",
            agent_type="KYCGapAnalysisAgent",
            config=config
        )
        
        self.required_fields = {
            "full_name": {"priority": "high", "category": "identity"},
            "date_of_birth": {"priority": "high", "category": "identity"},
            "address": {"priority": "high", "category": "identity"},
            "nationality": {"priority": "medium", "category": "identity"},
            "phone": {"priority": "medium", "category": "contact"},
            "email": {"priority": "medium", "category": "contact"},
            "occupation": {"priority": "high", "category": "financial"},
            "source_of_wealth": {"priority": "high", "category": "financial"}
        }
        
        self.required_documents = {
            DocumentType.PASSPORT: {"priority": "high", "category": "identity"},
            DocumentType.UTILITY_BILL: {"priority": "high", "category": "address_proof"},
            DocumentType.BANK_STATEMENT: {"priority": "medium", "category": "financial"},
            DocumentType.DRIVERS_LICENSE: {"priority": "low", "category": "identity"}
        }
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute gap analysis task"""
        try:
            await self.update_status("processing")
            
            kyc_brief_data = task.get("kyc_brief")
            
            if not kyc_brief_data:
                raise ValueError("No KYC brief provided for gap analysis")
            
            kyc_brief = KYCBrief(**kyc_brief_data)
            
            await asyncio.sleep(1.2)
            
            gap_analysis = await self._analyze_gaps(kyc_brief)
            
            await self.update_status("idle")
            
            gap_analysis_dict = gap_analysis.dict()
            if "analysis_date" in gap_analysis_dict:
                gap_analysis_dict["analysis_date"] = gap_analysis_dict["analysis_date"].isoformat()
            
            return {
                "success": True,
                "gap_analysis": gap_analysis_dict,
                "message": f"Gap analysis completed. Found {len(gap_analysis.missing_fields)} missing fields and {len(gap_analysis.missing_documents)} missing documents",
                "processing_time": 1.2
            }
            
        except Exception as e:
            await self.update_status("error")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to perform gap analysis: {str(e)}"
            }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for gap analysis"""
        kyc_brief = input_data.get("kyc_brief")
        
        if not kyc_brief:
            return False
        
        required_brief_fields = ["client_id", "documents"]
        for field in required_brief_fields:
            if field not in kyc_brief:
                return False
        
        return True
    
    async def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "gap_analysis",
            "compliance_checking",
            "risk_assessment",
            "document_validation",
            "priority_recommendations"
        ]
    
    async def _analyze_gaps(self, kyc_brief: KYCBrief) -> GapAnalysisResult:
        """Perform comprehensive gap analysis"""
        await asyncio.sleep(0.8)  # Simulate processing
        
        missing_fields = []
        missing_documents = []
        recommendations = []
        
        for field_name, field_config in self.required_fields.items():
            field_value = getattr(kyc_brief, field_name, None)
            
            if not field_value or field_value == "":
                missing_fields.append({
                    "field_name": field_name,
                    "priority": field_config["priority"],
                    "category": field_config["category"],
                    "description": self._get_field_description(field_name)
                })
        
        provided_doc_types = []
        for doc in kyc_brief.documents:
            if isinstance(doc, dict):
                doc_type = doc.get("document_type")
            else:
                doc_type = getattr(doc, "document_type", None)
            if doc_type:
                provided_doc_types.append(doc_type)
        
        for doc_type, doc_config in self.required_documents.items():
            if doc_type not in provided_doc_types:
                missing_documents.append({
                    "document_type": doc_type.value,
                    "priority": doc_config["priority"],
                    "category": doc_config["category"],
                    "description": self._get_document_description(doc_type)
                })
        
        recommendations = await self._generate_recommendations(missing_fields, missing_documents)
        
        total_fields = len(self.required_fields)
        completed_fields = total_fields - len(missing_fields)
        completion_percentage = (completed_fields / total_fields) * 100
        
        risk_level = await self._assess_risk_level(missing_fields, missing_documents)
        
        return GapAnalysisResult(
            client_id=kyc_brief.client_id,
            missing_fields=missing_fields,
            missing_documents=missing_documents,
            recommendations=recommendations,
            completion_percentage=completion_percentage,
            risk_level=risk_level,
            analysis_date=datetime.now()
        )
    
    def _get_field_description(self, field_name: str) -> str:
        """Get description for missing field"""
        descriptions = {
            "full_name": "Legal full name as it appears on official documents",
            "date_of_birth": "Date of birth in YYYY-MM-DD format",
            "address": "Current residential address with postal code",
            "nationality": "Country of citizenship or nationality",
            "phone": "Primary contact phone number",
            "email": "Primary email address for communication",
            "occupation": "Current job title or profession",
            "source_of_wealth": "Primary source of income or wealth"
        }
        return descriptions.get(field_name, f"Required field: {field_name}")
    
    def _get_document_description(self, doc_type: DocumentType) -> str:
        """Get description for missing document"""
        descriptions = {
            DocumentType.PASSPORT: "Government-issued passport for identity verification",
            DocumentType.UTILITY_BILL: "Recent utility bill (within 3 months) for address proof",
            DocumentType.BANK_STATEMENT: "Bank statement (within 3 months) for financial verification",
            DocumentType.DRIVERS_LICENSE: "Valid driver's license for additional identity verification"
        }
        return descriptions.get(doc_type, f"Required document: {doc_type.value}")
    
    async def _generate_recommendations(self, missing_fields: List[Dict], missing_documents: List[Dict]) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations"""
        await asyncio.sleep(0.3)
        
        recommendations = []
        
        high_priority_fields = [f for f in missing_fields if f["priority"] == "high"]
        if high_priority_fields:
            recommendations.append({
                "type": "critical",
                "title": "Complete Critical Identity Information",
                "description": f"Provide {len(high_priority_fields)} critical fields: {', '.join([f['field_name'] for f in high_priority_fields])}",
                "action": "Collect missing identity and financial information",
                "priority": "high"
            })
        
        high_priority_docs = [d for d in missing_documents if d["priority"] == "high"]
        if high_priority_docs:
            recommendations.append({
                "type": "document",
                "title": "Submit Required Identity Documents",
                "description": f"Upload {len(high_priority_docs)} required documents: {', '.join([d['document_type'] for d in high_priority_docs])}",
                "action": "Upload missing identity and address proof documents",
                "priority": "high"
            })
        
        medium_priority_items = [f for f in missing_fields if f["priority"] == "medium"] + [d for d in missing_documents if d["priority"] == "medium"]
        if medium_priority_items:
            recommendations.append({
                "type": "enhancement",
                "title": "Complete Additional Information",
                "description": f"Provide {len(medium_priority_items)} additional items to strengthen KYC profile",
                "action": "Submit supplementary information and documents",
                "priority": "medium"
            })
        
        return recommendations
    
    async def _assess_risk_level(self, missing_fields: List[Dict], missing_documents: List[Dict]) -> str:
        """Assess overall risk level based on missing information"""
        await asyncio.sleep(0.2)
        
        high_priority_missing = len([item for item in missing_fields + missing_documents if item["priority"] == "high"])
        
        if high_priority_missing >= 3:
            return "high"
        elif high_priority_missing >= 1:
            return "medium"
        else:
            return "low"
