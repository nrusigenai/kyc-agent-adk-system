import asyncio
from typing import Dict, Any, List
from datetime import datetime
import re

from .base_agent import BaseAgent
from ..models.kyc_models import Document, KYCBrief, AgentResponse

class ParsingAgent(BaseAgent):
    """Agent responsible for parsing and structuring extracted data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ParsingAgent", config)
        
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Parse documents and populate KYC brief"""
        try:
            await self.set_status("processing")
            
            documents = input_data.get("documents", [])
            client_id = input_data.get("client_id")
            
            if not documents:
                return AgentResponse(
                    agent_name=self.name,
                    status="error",
                    message="No documents provided for parsing",
                    data=None
                )
            
            kyc_brief = await self._create_kyc_brief(client_id, documents)
            
            await self.set_status("idle")
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                message=f"Successfully parsed {len(documents)} documents",
                data=kyc_brief.dict()
            )
            
        except Exception as e:
            await self.set_status("error")
            self.log_activity(f"Error parsing documents: {str(e)}", "error")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                message=f"Failed to parse documents: {str(e)}",
                data=None
            )
    
    async def _create_kyc_brief(self, client_id: str, documents: List[Dict]) -> KYCBrief:
        """Create KYC brief from documents"""
        await asyncio.sleep(1)  # Simulate processing time
        
        kyc_brief = KYCBrief(client_id=client_id)
        
        for doc_data in documents:
            doc = Document(**doc_data)
            kyc_brief.documents.append(doc)
            
            if doc.entities:
                await self._extract_personal_info(kyc_brief, doc)
        
        kyc_brief.updated_at = datetime.now()
        
        return kyc_brief
    
    async def _extract_personal_info(self, kyc_brief: KYCBrief, document: Document):
        """Extract personal information from document entities"""
        entities = document.entities or {}
        
        if "name" in entities and not kyc_brief.full_name:
            kyc_brief.full_name = entities["name"]
        
        if "date_of_birth" in entities and not kyc_brief.date_of_birth:
            kyc_brief.date_of_birth = entities["date_of_birth"]
        
        if "address" in entities and not kyc_brief.address:
            kyc_brief.address = entities["address"]
        
        if "nationality" in entities and not kyc_brief.nationality:
            kyc_brief.nationality = entities["nationality"]
        
        if document.content:
            await self._extract_contact_info(kyc_brief, document.content)
    
    async def _extract_contact_info(self, kyc_brief: KYCBrief, content: str):
        """Extract contact information from document content"""
        if not kyc_brief.email:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, content)
            if email_match:
                kyc_brief.email = email_match.group()
        
        if not kyc_brief.phone_number:
            phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
            phone_match = re.search(phone_pattern, content)
            if phone_match:
                kyc_brief.phone_number = phone_match.group()
    
    async def standardize_data(self, kyc_brief: KYCBrief) -> KYCBrief:
        """Standardize and clean data in KYC brief"""
        if kyc_brief.full_name:
            kyc_brief.full_name = kyc_brief.full_name.title().strip()
        
        if kyc_brief.address:
            kyc_brief.address = kyc_brief.address.strip()
        
        if kyc_brief.nationality:
            nationality_map = {
                "USA": "United States",
                "UK": "United Kingdom",
                "UAE": "United Arab Emirates"
            }
            kyc_brief.nationality = nationality_map.get(kyc_brief.nationality, kyc_brief.nationality)
        
        return kyc_brief
