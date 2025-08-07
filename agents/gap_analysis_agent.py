import asyncio
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from ..models.kyc_models import KYCBrief, GapAnalysisResult, GapAnalysisItem, DocumentType, AgentResponse

class GapAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing gaps in KYC documentation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("GapAnalysisAgent", config)
        self.required_fields = {
            "full_name": {"priority": "high", "documents": [DocumentType.PASSPORT, DocumentType.DRIVERS_LICENSE]},
            "date_of_birth": {"priority": "high", "documents": [DocumentType.PASSPORT, DocumentType.DRIVERS_LICENSE]},
            "address": {"priority": "high", "documents": [DocumentType.UTILITY_BILL, DocumentType.BANK_STATEMENT]},
            "nationality": {"priority": "medium", "documents": [DocumentType.PASSPORT]},
            "source_of_wealth": {"priority": "high", "documents": [DocumentType.PROOF_OF_INCOME, DocumentType.BANK_STATEMENT]},
            "source_of_funds": {"priority": "high", "documents": [DocumentType.BANK_STATEMENT, DocumentType.PROOF_OF_INCOME]},
            "phone_number": {"priority": "medium", "documents": [DocumentType.UTILITY_BILL, DocumentType.BANK_STATEMENT]},
            "email": {"priority": "low", "documents": [DocumentType.BANK_STATEMENT, DocumentType.OTHER]}
        }
        
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Analyze gaps in KYC documentation"""
        try:
            await self.set_status("processing")
            
            kyc_brief_data = input_data.get("kyc_brief")
            if not kyc_brief_data:
                return AgentResponse(
                    agent_name=self.name,
                    status="error",
                    message="No KYC brief provided for gap analysis",
                    data=None
                )
            
            kyc_brief = KYCBrief(**kyc_brief_data)
            
            gap_analysis = await self._analyze_gaps(kyc_brief)
            
            await self.set_status("idle")
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                message=f"Gap analysis completed. {len(gap_analysis.missing_items)} gaps identified.",
                data=gap_analysis.dict()
            )
            
        except Exception as e:
            await self.set_status("error")
            self.log_activity(f"Error in gap analysis: {str(e)}", "error")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                message=f"Failed to perform gap analysis: {str(e)}",
                data=None
            )
    
    async def _analyze_gaps(self, kyc_brief: KYCBrief) -> GapAnalysisResult:
        """Analyze gaps in KYC brief"""
        await asyncio.sleep(1)  # Simulate analysis time
        
        missing_items = []
        filled_fields = 0
        total_fields = len(self.required_fields)
        
        for field_name, field_config in self.required_fields.items():
            field_value = getattr(kyc_brief, field_name, None)
            
            if not field_value:
                gap_item = GapAnalysisItem(
                    field_name=field_name,
                    description=self._get_field_description(field_name),
                    required_documents=field_config["documents"],
                    priority=field_config["priority"]
                )
                missing_items.append(gap_item)
            else:
                filled_fields += 1
        
        completion_percentage = (filled_fields / total_fields) * 100
        
        recommendations = await self._generate_recommendations(missing_items, kyc_brief)
        
        return GapAnalysisResult(
            client_id=kyc_brief.client_id,
            missing_items=missing_items,
            completion_percentage=completion_percentage,
            recommendations=recommendations
        )
    
    def _get_field_description(self, field_name: str) -> str:
        """Get description for missing field"""
        descriptions = {
            "full_name": "Client's full legal name as it appears on official documents",
            "date_of_birth": "Client's date of birth for age verification and identity confirmation",
            "address": "Current residential address for address verification",
            "nationality": "Client's nationality for compliance and regulatory requirements",
            "source_of_wealth": "Information about how the client accumulated their wealth",
            "source_of_funds": "Information about the source of funds for this specific transaction",
            "phone_number": "Contact phone number for client communication",
            "email": "Email address for client communication and notifications"
        }
        return descriptions.get(field_name, f"Information about {field_name.replace('_', ' ')}")
    
    async def _generate_recommendations(self, missing_items: List[GapAnalysisItem], kyc_brief: KYCBrief) -> List[str]:
        """Generate recommendations based on missing items"""
        recommendations = []
        
        high_priority_items = [item for item in missing_items if item.priority == "high"]
        medium_priority_items = [item for item in missing_items if item.priority == "medium"]
        
        if high_priority_items:
            recommendations.append("🔴 High Priority: Address critical missing information first")
            for item in high_priority_items[:3]:  # Top 3 high priority items
                doc_types = ", ".join([doc.value.replace("_", " ").title() for doc in item.required_documents[:2]])
                recommendations.append(f"   • Obtain {doc_types} for {item.field_name.replace('_', ' ')}")
        
        if medium_priority_items:
            recommendations.append("🟡 Medium Priority: Complete additional verification requirements")
        
        existing_doc_types = [doc.document_type for doc in kyc_brief.documents]
        
        if DocumentType.PASSPORT not in existing_doc_types and DocumentType.DRIVERS_LICENSE not in existing_doc_types:
            recommendations.append("📄 Request primary identification document (Passport or Driver's License)")
        
        if DocumentType.UTILITY_BILL not in existing_doc_types and DocumentType.BANK_STATEMENT not in existing_doc_types:
            recommendations.append("🏠 Request proof of address document (Utility Bill or Bank Statement)")
        
        if not any(doc.document_type in [DocumentType.BANK_STATEMENT, DocumentType.PROOF_OF_INCOME] for doc in kyc_brief.documents):
            recommendations.append("💰 Request financial documentation for source of funds verification")
        
        completion_percentage = ((len(self.required_fields) - len(missing_items)) / len(self.required_fields)) * 100
        if completion_percentage >= 80:
            recommendations.append("✅ KYC profile is nearly complete - focus on remaining high-priority items")
        elif completion_percentage >= 50:
            recommendations.append("⚠️ KYC profile is partially complete - continue gathering required documents")
        else:
            recommendations.append("🚨 KYC profile requires significant additional documentation")
        
        return recommendations
