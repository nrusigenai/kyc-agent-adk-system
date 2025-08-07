from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import datetime

class DocumentType(str, Enum):
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    PROOF_OF_INCOME = "proof_of_income"
    BUSINESS_REGISTRATION = "business_registration"
    OTHER = "other"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VerificationStatus(str, Enum):
    NOT_VERIFIED = "not_verified"
    VERIFIED = "verified"
    FAILED = "failed"
    PENDING = "pending"

class Document(BaseModel):
    id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    document_type: DocumentType = Field(..., description="Type of document")
    content: Optional[str] = Field(None, description="Extracted text content")
    entities: Optional[Dict[str, Any]] = Field(None, description="Extracted entities")
    status: DocumentStatus = Field(DocumentStatus.PENDING, description="Processing status")
    uploaded_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    processed_at: Optional[datetime.datetime] = Field(None)

class KYCBrief(BaseModel):
    client_id: str = Field(..., description="Unique client identifier")
    full_name: Optional[str] = Field(None, description="Client's full name")
    date_of_birth: Optional[str] = Field(None, description="Date of birth")
    address: Optional[str] = Field(None, description="Current address")
    nationality: Optional[str] = Field(None, description="Nationality")
    occupation: Optional[str] = Field(None, description="Occupation")
    source_of_wealth: Optional[str] = Field(None, description="Source of wealth")
    source_of_funds: Optional[str] = Field(None, description="Source of funds")
    phone_number: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    documents: List[Document] = Field(default_factory=list, description="Associated documents")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

class GapAnalysisItem(BaseModel):
    field_name: str = Field(..., description="Missing field name")
    description: str = Field(..., description="Description of what's missing")
    required_documents: List[DocumentType] = Field(..., description="Documents that could fill this gap")
    priority: str = Field(..., description="Priority level: high, medium, low")

class GapAnalysisResult(BaseModel):
    client_id: str = Field(..., description="Client identifier")
    missing_fields: List[Dict[str, Any]] = Field(..., description="List of missing fields")
    missing_documents: List[Dict[str, Any]] = Field(..., description="List of missing documents")
    completion_percentage: float = Field(..., description="Percentage of KYC completion")
    recommendations: List[Dict[str, Any]] = Field(..., description="Recommendations for next steps")
    risk_level: str = Field(..., description="Risk level assessment")
    analysis_date: datetime.datetime = Field(default_factory=datetime.datetime.now)

class VerificationResult(BaseModel):
    field_name: str = Field(..., description="Field being verified")
    status: VerificationStatus = Field(..., description="Verification status")
    confidence_score: float = Field(..., description="Confidence score 0-1")
    details: str = Field(..., description="Verification details")
    sources: List[str] = Field(default_factory=list, description="Verification sources")
    verified_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

class VerifyRequest(BaseModel):
    fields_to_verify: Optional[List[str]] = Field(default=None, description="List of fields to verify")

class AgentResponse(BaseModel):
    agent_name: str = Field(..., description="Name of the agent")
    status: str = Field(..., description="Response status")
    data: Optional[Any] = Field(None, description="Response data")
    message: str = Field(..., description="Response message")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
