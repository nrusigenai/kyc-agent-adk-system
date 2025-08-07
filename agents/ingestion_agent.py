import asyncio
import base64
import io
from typing import Dict, Any, List
from PIL import Image
import uuid
from datetime import datetime

from .base_agent import BaseAgent
from ..models.kyc_models import Document, DocumentType, DocumentStatus, AgentResponse

class IngestionAgent(BaseAgent):
    """Agent responsible for document ingestion and initial processing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("IngestionAgent", config)
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Process uploaded documents"""
        try:
            await self.set_status("processing")
            
            file_data = input_data.get("file_data")
            filename = input_data.get("filename", "unknown")
            document_type = input_data.get("document_type", DocumentType.OTHER)
            
            if not file_data:
                return AgentResponse(
                    agent_name=self.name,
                    status="error",
                    message="No file data provided",
                    data=None
                )
            
            await asyncio.sleep(1)  # Simulate processing time
            
            extracted_text = await self._extract_text(file_data, filename)
            
            entities = await self._extract_entities(extracted_text)
            
            document = Document(
                id=str(uuid.uuid4()),
                filename=filename,
                document_type=document_type,
                content=extracted_text,
                entities=entities,
                status=DocumentStatus.COMPLETED,
                processed_at=datetime.now()
            )
            
            await self.set_status("idle")
            
            return AgentResponse(
                agent_name=self.name,
                status="success",
                message=f"Successfully processed document: {filename}",
                data=document.dict()
            )
            
        except Exception as e:
            await self.set_status("error")
            self.log_activity(f"Error processing document: {str(e)}", "error")
            return AgentResponse(
                agent_name=self.name,
                status="error",
                message=f"Failed to process document: {str(e)}",
                data=None
            )
    
    async def _extract_text(self, file_data: bytes, filename: str) -> str:
        """Extract text from document (simulated Google Document AI)"""
        await asyncio.sleep(0.5)
        
        if "passport" in filename.lower():
            return """
            PASSPORT
            United States of America
            Name: JOHN SMITH
            Date of Birth: 15 JAN 1985
            Place of Birth: NEW YORK, NY
            Nationality: USA
            Passport No: 123456789
            Date of Issue: 01 JAN 2020
            Date of Expiry: 01 JAN 2030
            """
        elif "utility" in filename.lower() or "bill" in filename.lower():
            return """
            ELECTRIC COMPANY
            Monthly Statement
            Account Holder: John Smith
            Service Address: 123 Main Street, New York, NY 10001
            Statement Date: December 2024
            Amount Due: $125.50
            """
        elif "bank" in filename.lower():
            return """
            FIRST NATIONAL BANK
            Account Statement
            Account Holder: John Smith
            Account Number: ****1234
            Statement Period: Nov 1 - Nov 30, 2024
            Address: 123 Main Street, New York, NY 10001
            Opening Balance: $5,250.00
            Closing Balance: $4,890.50
            """
        else:
            return f"Extracted text content from {filename}"
    
    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text (simulated)"""
        await asyncio.sleep(0.3)
        
        entities = {}
        
        if "JOHN SMITH" in text or "John Smith" in text:
            entities["name"] = "John Smith"
        
        if "15 JAN 1985" in text:
            entities["date_of_birth"] = "1985-01-15"
        
        if "123 Main Street" in text:
            entities["address"] = "123 Main Street, New York, NY 10001"
        
        if "USA" in text or "United States" in text:
            entities["nationality"] = "USA"
        
        if "123456789" in text:
            entities["passport_number"] = "123456789"
        
        return entities
    
    async def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return self.supported_formats
