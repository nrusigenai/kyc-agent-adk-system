import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..interfaces.agent_interface import AgentInterface
from ..models.kyc_models import KYCBrief, Document

class KYCParsingAgent(AgentInterface):
    """
    Google ADK compatible KYC Parsing Agent
    Structures extracted data into standardized KYC brief format
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id or f"kyc_parsing_{uuid.uuid4().hex[:8]}",
            agent_type="KYCParsingAgent",
            config=config or {}
        )
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute KYC brief parsing task"""
        try:
            await self.update_status("processing")
            
            documents = task.get("documents", [])
            client_id = task.get("client_id", str(uuid.uuid4()))
            
            if not documents:
                raise ValueError("No documents provided for parsing")
            
            await asyncio.sleep(1.5)
            
            kyc_brief = await self._parse_documents_to_brief(documents, client_id)
            
            await self.update_status("idle")
            
            return {
                "success": True,
                "kyc_brief": kyc_brief.dict(),
                "message": f"Successfully parsed {len(documents)} documents into KYC brief",
                "processing_time": 1.5
            }
            
        except Exception as e:
            await self.update_status("error")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to parse documents: {str(e)}"
            }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for parsing"""
        documents = input_data.get("documents", [])
        
        if not documents:
            return False
        
        for doc in documents:
            if not isinstance(doc, dict):
                return False
            if "content" not in doc or "entities" not in doc:
                return False
        
        return True
    
    async def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return [
            "document_parsing",
            "data_structuring",
            "entity_consolidation",
            "kyc_brief_generation",
            "multi_document_analysis"
        ]
    
    async def _parse_documents_to_brief(self, documents: List[Dict[str, Any]], client_id: str) -> KYCBrief:
        """Parse multiple documents into a consolidated KYC brief"""
        await asyncio.sleep(0.8)  # Simulate processing
        
        brief_data = {
            "client_id": client_id,
            "full_name": None,
            "date_of_birth": None,
            "address": None,
            "nationality": None,
            "phone": None,
            "email": None,
            "occupation": None,
            "source_of_wealth": None,
            "documents": documents,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        for doc in documents:
            entities = doc.get("entities", {})
            content = doc.get("content", "")
            
            if "name" in entities and not brief_data["full_name"]:
                brief_data["full_name"] = entities["name"]
            
            if "date_of_birth" in entities and not brief_data["date_of_birth"]:
                brief_data["date_of_birth"] = entities["date_of_birth"]
            
            if "address" in entities and not brief_data["address"]:
                brief_data["address"] = entities["address"]
            
            if "nationality" in entities and not brief_data["nationality"]:
                brief_data["nationality"] = entities["nationality"]
            
            if "phone" in entities and not brief_data["phone"]:
                brief_data["phone"] = entities["phone"]
            
            if "email" in entities and not brief_data["email"]:
                brief_data["email"] = entities["email"]
            
            if not brief_data["occupation"]:
                brief_data["occupation"] = await self._extract_occupation(content)
            
            if not brief_data["source_of_wealth"]:
                brief_data["source_of_wealth"] = await self._extract_source_of_wealth(content)
        
        return KYCBrief(**brief_data)
    
    async def _extract_occupation(self, content: str) -> str:
        """Extract occupation from document content"""
        await asyncio.sleep(0.2)
        
        content_lower = content.lower()
        
        if "engineer" in content_lower:
            return "Software Engineer"
        elif "doctor" in content_lower or "physician" in content_lower:
            return "Medical Doctor"
        elif "lawyer" in content_lower or "attorney" in content_lower:
            return "Legal Professional"
        elif "teacher" in content_lower or "professor" in content_lower:
            return "Education Professional"
        elif "manager" in content_lower:
            return "Business Manager"
        elif "consultant" in content_lower:
            return "Business Consultant"
        else:
            return "Professional"
    
    async def _extract_source_of_wealth(self, content: str) -> str:
        """Extract source of wealth from document content"""
        await asyncio.sleep(0.2)
        
        content_lower = content.lower()
        
        if "salary" in content_lower or "employment" in content_lower:
            return "Employment Income"
        elif "business" in content_lower or "company" in content_lower:
            return "Business Ownership"
        elif "investment" in content_lower or "portfolio" in content_lower:
            return "Investment Returns"
        elif "inheritance" in content_lower:
            return "Inheritance"
        elif "real estate" in content_lower or "property" in content_lower:
            return "Real Estate"
        else:
            return "Professional Income"
    
    async def update_brief_with_additional_info(self, brief: KYCBrief, additional_data: Dict[str, Any]) -> KYCBrief:
        """Update existing KYC brief with additional information"""
        brief_dict = brief.dict()
        
        for key, value in additional_data.items():
            if key in brief_dict and value is not None:
                brief_dict[key] = value
        
        brief_dict["updated_at"] = datetime.now()
        
        return KYCBrief(**brief_dict)
