from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from typing import List, Dict, Any, Optional
import uuid
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adk.core.agent_manager import AgentManager
from adk.agents import KYCIngestionAgent, KYCParsingAgent, KYCGapAnalysisAgent, KYCVerificationAgent
from models.kyc_models import DocumentType, KYCBrief, AgentResponse

app = FastAPI(
    title="KYC Agent System API",
    description="Multi-agent KYC processing system with specialized agents",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

agent_manager = AgentManager()

ingestion_agent = KYCIngestionAgent()
parsing_agent = KYCParsingAgent()
gap_analysis_agent = KYCGapAnalysisAgent()
verification_agent = KYCVerificationAgent()

kyc_briefs: Dict[str, Dict] = {}
documents: Dict[str, Dict] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the ADK system on startup"""
    await agent_manager.message_bus.start()
    
    await agent_manager.start_agent(ingestion_agent)
    await agent_manager.start_agent(parsing_agent)
    await agent_manager.start_agent(gap_analysis_agent)
    await agent_manager.start_agent(verification_agent)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup ADK system on shutdown"""
    await agent_manager.message_bus.stop()

@app.get("/")
async def root():
    return {
        "message": "KYC Agent System API",
        "version": "1.0.0",
        "agents": ["KYCIngestionAgent", "KYCParsingAgent", "KYCGapAnalysisAgent", "KYCVerificationAgent"],
        "adk_enabled": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    agent_health = await asyncio.gather(
        ingestion_agent.health_check(),
        parsing_agent.health_check(),
        gap_analysis_agent.health_check(),
        verification_agent.health_check()
    )
    
    return {
        "status": "healthy",
        "agents": agent_health,
        "adk_status": await agent_manager.message_bus.get_status(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    client_id: str = Form(...)
):
    """Upload and process a document"""
    try:
        file_data = await file.read()
        
        ingestion_result = await ingestion_agent.execute({
            "file_data": file_data,
            "filename": file.filename,
            "document_type": DocumentType(document_type)
        })
        
        if ingestion_result.get("success"):
            document_data = ingestion_result["document"]
            documents[document_data["id"]] = document_data
            
            if client_id not in kyc_briefs:
                kyc_briefs[client_id] = {
                    "client_id": client_id,
                    "documents": [],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            
            kyc_briefs[client_id]["documents"].append(document_data)
            kyc_briefs[client_id]["updated_at"] = datetime.now().isoformat()
            
            return JSONResponse(content={
                "status": "success",
                "message": "Document uploaded and processed successfully",
                "document_id": document_data["id"],
                "client_id": client_id
            })
        else:
            raise HTTPException(status_code=400, detail=ingestion_result.get("message", "Processing failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/parse-documents/{client_id}")
async def parse_documents(client_id: str):
    """Parse documents and create/update KYC brief"""
    try:
        if client_id not in kyc_briefs:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client_data = kyc_briefs[client_id]
        
        parsing_result = await parsing_agent.execute({
            "client_id": client_id,
            "documents": client_data["documents"]
        })
        
        if parsing_result.get("success"):
            kyc_briefs[client_id] = parsing_result["kyc_brief"]
            
            return JSONResponse(content={
                "status": "success",
                "message": "Documents parsed successfully",
                "kyc_brief": parsing_result["kyc_brief"]
            })
        else:
            raise HTTPException(status_code=400, detail=parsing_result.get("message", "Parsing failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing documents: {str(e)}")

@app.post("/analyze-gaps/{client_id}")
async def analyze_gaps(client_id: str):
    """Perform gap analysis on KYC brief"""
    try:
        if client_id not in kyc_briefs:
            raise HTTPException(status_code=404, detail="Client not found")
        
        gap_result = await gap_analysis_agent.execute({
            "kyc_brief": kyc_briefs[client_id]
        })
        
        if gap_result.get("success"):
            return JSONResponse(content={
                "status": "success",
                "message": "Gap analysis completed",
                "gap_analysis": gap_result["gap_analysis"]
            })
        else:
            raise HTTPException(status_code=400, detail=gap_result.get("message", "Gap analysis failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in gap analysis: {str(e)}")

@app.post("/verify-information/{client_id}")
async def verify_information(
    client_id: str,
    fields_to_verify: Optional[List[str]] = None
):
    """Verify KYC information"""
    try:
        if client_id not in kyc_briefs:
            raise HTTPException(status_code=404, detail="Client not found")
        
        verification_result = await verification_agent.execute({
            "kyc_brief": kyc_briefs[client_id],
            "fields_to_verify": fields_to_verify or []
        })
        
        if verification_result.get("success"):
            return JSONResponse(content={
                "status": "success",
                "message": "Verification completed",
                "verification_results": verification_result["verification_results"],
                "sanctions_check": verification_result.get("sanctions_check"),
                "document_authenticity": verification_result.get("document_authenticity")
            })
        else:
            raise HTTPException(status_code=400, detail=verification_result.get("message", "Verification failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in verification: {str(e)}")

@app.get("/kyc-brief/{client_id}")
async def get_kyc_brief(client_id: str):
    """Get KYC brief for a client"""
    if client_id not in kyc_briefs:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return JSONResponse(content={
        "status": "success",
        "kyc_brief": kyc_briefs[client_id]
    })

@app.get("/clients")
async def list_clients():
    """List all clients"""
    return JSONResponse(content={
        "status": "success",
        "clients": list(kyc_briefs.keys()),
        "count": len(kyc_briefs)
    })

@app.post("/process-workflow/{client_id}")
async def process_full_workflow(client_id: str):
    """Process complete KYC workflow for a client"""
    try:
        if client_id not in kyc_briefs:
            raise HTTPException(status_code=404, detail="Client not found")
        
        parsing_result = await parsing_agent.execute({
            "client_id": client_id,
            "documents": kyc_briefs[client_id]["documents"]
        })
        
        if not parsing_result.get("success"):
            raise HTTPException(status_code=400, detail=f"Parsing failed: {parsing_result.get('message', 'Unknown error')}")
        
        kyc_briefs[client_id] = parsing_result["kyc_brief"]
        
        gap_result = await gap_analysis_agent.execute({
            "kyc_brief": kyc_briefs[client_id]
        })
        
        if not gap_result.get("success"):
            raise HTTPException(status_code=400, detail=f"Gap analysis failed: {gap_result.get('message', 'Unknown error')}")
        
        verification_result = await verification_agent.execute({
            "kyc_brief": kyc_briefs[client_id],
            "fields_to_verify": []
        })
        
        if not verification_result.get("success"):
            raise HTTPException(status_code=400, detail=f"Verification failed: {verification_result.get('message', 'Unknown error')}")
        
        return JSONResponse(content={
            "status": "success",
            "message": "Complete KYC workflow processed using Google ADK",
            "results": {
                "kyc_brief": parsing_result["kyc_brief"],
                "gap_analysis": gap_result["gap_analysis"],
                "verification": {
                    "verification_results": verification_result["verification_results"],
                    "sanctions_check": verification_result.get("sanctions_check"),
                    "document_authenticity": verification_result.get("document_authenticity")
                }
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in workflow processing: {str(e)}")

@app.delete("/client/{client_id}")
async def delete_client(client_id: str):
    """Delete a client and all associated data"""
    if client_id not in kyc_briefs:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client_docs = kyc_briefs[client_id].get("documents", [])
    for doc in client_docs:
        if doc.get("id") in documents:
            del documents[doc["id"]]
    
    del kyc_briefs[client_id]
    
    return JSONResponse(content={
        "status": "success",
        "message": f"Client {client_id} deleted successfully"
    })

@app.get("/adk/agents")
async def get_registered_agents():
    """Get all registered ADK agents"""
    try:
        agents = await agent_manager.registry.list_agents()
        agent_statuses = {}
        
        for agent_status in agents:
            agent_statuses[agent_status["agent_id"]] = agent_status
        
        return {
            "message": "Retrieved all registered ADK agents",
            "agents": agent_statuses,
            "total_agents": len(agents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/adk/agents/{agent_id}/capabilities")
async def get_agent_capabilities(agent_id: str):
    """Get capabilities of a specific ADK agent"""
    try:
        agent = await agent_manager.registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        capabilities = await agent.get_capabilities()
        status = await agent.get_status()
        
        return {
            "agent_id": agent_id,
            "capabilities": capabilities,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/adk/message-bus/status")
async def get_message_bus_status():
    """Get ADK message bus status"""
    try:
        status = await agent_manager.message_bus.get_status()
        return {
            "message": "Message bus status retrieved",
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/adk/agents/by-capability/{capability}")
async def find_agents_by_capability(capability: str):
    """Find ADK agents by capability"""
    try:
        agent_ids = await agent_manager.registry.find_agents_by_capability(capability)
        agent_info = []
        
        for agent_id in agent_ids:
            agent = await agent_manager.registry.get_agent(agent_id)
            if agent:
                status = await agent.get_status()
                capabilities = await agent.get_capabilities()
                agent_info.append({
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "status": status,
                    "capabilities": capabilities
                })
        
        return {
            "capability": capability,
            "matching_agents": agent_info,
            "count": len(agent_info)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
