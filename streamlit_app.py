import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import pandas as pd
from typing import Dict, Any, List

st.set_page_config(
    page_title="Customer Document Analysis Agent",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .status-idle {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    
    .status-processing {
        background-color: #fff3e0;
        color: #f57c00;
    }
    
    .status-error {
        background-color: #ffebee;
        color: #d32f2f;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .progress-container {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "https://app-thpikwqx.fly.dev"

class KYCAgentUI:
    def __init__(self):
        self.api_base = API_BASE_URL
        
    def call_api(self, endpoint: str, method: str = "GET", data: Dict = None, files: Dict = None) -> Dict:
        """Make API calls with error handling"""
        try:
            url = f"{self.api_base}{endpoint}"
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                if files:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, json=data)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return {"error": str(e)}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all ADK agents"""
        return self.call_api("/adk/agents")
    
    def get_message_bus_status(self) -> Dict[str, Any]:
        """Get message bus status"""
        return self.call_api("/adk/message-bus/status")

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Customer Document Analysis Agent</h1>
        <p>Google ADK-Compatible Multi-Agent Customer Document Processing Platform</p>
    </div>
    """, unsafe_allow_html=True)

def render_agent_status_card(agent_id: str, agent_data: Dict[str, Any]):
    """Render individual agent status card"""
    status = agent_data.get("status", "unknown")
    agent_type = agent_data.get("agent_type", "Unknown")
    last_activity = agent_data.get("last_activity", "Never")
    
    status_class = f"status-{status.lower()}"
    
    st.markdown(f"""
    <div class="agent-card">
        <div style="display: flex; justify-content: between; align-items: center;">
            <div>
                <h4>{agent_type}</h4>
                <p style="color: #666; margin: 0;">{agent_id}</p>
                <small>Last Activity: {last_activity}</small>
            </div>
            <div>
                <span class="status-badge {status_class}">{status}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_completion_gauge(completion_percentage: float):
    """Render KYC completion gauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = completion_percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "KYC Completion"},
        delta = {'reference': 100},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 50], 'color': "#ffebee"},
                {'range': [50, 80], 'color': "#fff3e0"},
                {'range': [80, 100], 'color': "#e8f5e8"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def document_upload_page():
    """Document upload and processing page"""
    st.header("📄 Document Upload & Processing")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="upload-area">
            <h3>📤 Upload KYC Documents</h3>
            <p>Upload identity documents, address proofs, and financial statements</p>
        </div>
        """, unsafe_allow_html=True)
        
        client_id = st.text_input("Client ID", value=f"client_{int(time.time())}")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']
        )
        
        if uploaded_files:
            st.subheader("Document Types")
            document_types = []
            
            for i, file in enumerate(uploaded_files):
                doc_type = st.selectbox(
                    f"Document type for {file.name}",
                    ["passport", "utility_bill", "bank_statement", "drivers_license", "other"],
                    key=f"doc_type_{i}"
                )
                document_types.append(doc_type)
            
            if st.button("🚀 Process Documents", type="primary"):
                with st.spinner("Processing documents with ADK agents..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    steps = [
                        "Initializing ADK agents...",
                        "Processing documents with Ingestion Agent...",
                        "Parsing data with Parsing Agent...",
                        "Analyzing gaps with Gap Analysis Agent...",
                        "Verifying information with Verification Agent..."
                    ]
                    
                    for i, step in enumerate(steps):
                        status_text.text(step)
                        progress_bar.progress((i + 1) / len(steps))
                        time.sleep(1)
                    
                    ui = KYCAgentUI()
                    
                    upload_success = True
                    for i, file in enumerate(uploaded_files):
                        doc_type = document_types[i] if i < len(document_types) else "other"
                        
                        files_data = {"file": (file.name, file.getvalue(), file.type)}
                        form_data = {
                            "document_type": doc_type,
                            "client_id": client_id
                        }
                        
                        upload_result = ui.call_api("/upload-document", "POST", form_data, files_data)
                        
                        if "error" in upload_result:
                            st.error(f"❌ Failed to upload {file.name}: {upload_result['error']}")
                            upload_success = False
                            break
                        else:
                            st.success(f"✅ Uploaded {file.name} successfully")
                    
                    if upload_success:
                        result = ui.call_api(f"/workflow/{client_id}", "POST")
                    else:
                        result = {"error": "Document upload failed"}
                    
                    if "error" not in result:
                        st.success("✅ Documents processed successfully!")
                        st.session_state[f"workflow_result_{client_id}"] = result
                        st.rerun()
                    else:
                        st.error(f"❌ Processing failed: {result['error']}")
    
    with col2:
        st.subheader("📊 Processing Status")
        
        ui = KYCAgentUI()
        agent_status = ui.get_agent_status()
        
        if "error" not in agent_status:
            agents = agent_status.get("agents", {})
            for agent_id, agent_data in agents.items():
                render_agent_status_card(agent_id, agent_data)

def gap_analysis_page():
    """Gap analysis and recommendations page"""
    st.header("🔍 Gap Analysis & Recommendations")
    
    client_id = st.text_input("Client ID for Analysis", key="gap_client_id")
    
    if st.button("🔍 Perform Gap Analysis"):
        if client_id:
            ui = KYCAgentUI()
            result = ui.call_api(f"/gap-analysis/{client_id}", "POST")
            
            if "error" not in result:
                gap_analysis = result.get("gap_analysis", {})
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    completion = gap_analysis.get("completion_percentage", 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{completion:.1f}%</h2>
                        <p>Completion Rate</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    missing_fields = len(gap_analysis.get("missing_fields", []))
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{missing_fields}</h2>
                        <p>Missing Fields</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    risk_level = gap_analysis.get("risk_level", "unknown").upper()
                    risk_color = {"LOW": "#4caf50", "MEDIUM": "#ff9800", "HIGH": "#f44336"}.get(risk_level, "#666")
                    st.markdown(f"""
                    <div class="metric-card" style="background: {risk_color};">
                        <h2>{risk_level}</h2>
                        <p>Risk Level</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.plotly_chart(render_completion_gauge(completion), use_container_width=True)
                
                if gap_analysis.get("missing_fields"):
                    st.subheader("📋 Missing Information")
                    missing_df = pd.DataFrame(gap_analysis["missing_fields"])
                    st.dataframe(missing_df, use_container_width=True)
                
                if gap_analysis.get("recommendations"):
                    st.subheader("💡 Recommendations")
                    for rec in gap_analysis["recommendations"]:
                        priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get("priority", "low"), "⚪")
                        st.markdown(f"""
                        **{priority_color} {rec.get('title', 'Recommendation')}**
                        
                        {rec.get('description', 'No description available')}
                        
                        *Action: {rec.get('action', 'No action specified')}*
                        """)
            else:
                st.error(f"❌ Gap analysis failed: {result['error']}")

def verification_page():
    """Verification results page"""
    st.header("✅ Verification Results")
    
    client_id = st.text_input("Client ID for Verification", key="verify_client_id")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fields_to_verify = st.multiselect(
            "Fields to Verify",
            ["full_name", "date_of_birth", "address", "nationality"],
            default=["full_name", "date_of_birth", "address"]
        )
    
    with col2:
        if st.button("🔍 Verify Information"):
            if client_id:
                ui = KYCAgentUI()
                result = ui.call_api(f"/verify/{client_id}", "POST", {"fields_to_verify": fields_to_verify})
                
                if "error" not in result:
                    st.success("✅ Verification completed!")
                    
                    verification_results = result.get("verification_results", [])
                    if verification_results:
                        st.subheader("📊 Field Verification Results")
                        
                        for vr in verification_results:
                            status = vr.get("status", "unknown")
                            confidence = vr.get("confidence_score", 0) * 100
                            field_name = vr.get("field_name", "Unknown")
                            
                            status_emoji = {"verified": "✅", "failed": "❌", "pending": "⏳"}.get(status, "❓")
                            
                            st.markdown(f"""
                            **{status_emoji} {field_name.replace('_', ' ').title()}**
                            - Status: {status.upper()}
                            - Confidence: {confidence:.1f}%
                            - Details: {vr.get('details', 'No details available')}
                            """)
                    
                    sanctions = result.get("sanctions_check", {})
                    if sanctions:
                        st.subheader("🚨 Sanctions Screening")
                        is_sanctioned = sanctions.get("sanctioned", False)
                        risk_score = sanctions.get("risk_score", 0) * 100
                        
                        if is_sanctioned:
                            st.error("⚠️ SANCTIONS MATCH FOUND")
                        else:
                            st.success("✅ No sanctions matches")
                        
                        st.metric("Risk Score", f"{risk_score:.1f}%")
                    
                    doc_auth = result.get("document_authenticity", {})
                    if doc_auth:
                        st.subheader("📄 Document Authenticity")
                        overall_score = doc_auth.get("overall_score", 0) * 100
                        is_authentic = doc_auth.get("overall_authentic", False)
                        
                        if is_authentic:
                            st.success(f"✅ Documents verified authentic ({overall_score:.1f}%)")
                        else:
                            st.warning(f"⚠️ Document authenticity concerns ({overall_score:.1f}%)")
                else:
                    st.error(f"❌ Verification failed: {result['error']}")

def dashboard_page():
    """Main dashboard page"""
    st.header("📊 KYC Dashboard")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🤖 ADK Agent Status")
        ui = KYCAgentUI()
        agent_status = ui.get_agent_status()
        
        if "error" not in agent_status:
            agents = agent_status.get("agents", {})
            
            agent_names = []
            agent_statuses = []
            
            for agent_id, agent_data in agents.items():
                agent_names.append(agent_data.get("agent_type", "Unknown"))
                status = agent_data.get("status", "unknown")
                agent_statuses.append(1 if status == "idle" else 0.5 if status == "processing" else 0)
            
            if agent_names:
                fig = px.bar(
                    x=agent_names,
                    y=agent_statuses,
                    title="Agent Status Overview",
                    color=agent_statuses,
                    color_continuous_scale=["red", "yellow", "green"]
                )
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            for agent_id, agent_data in agents.items():
                render_agent_status_card(agent_id, agent_data)
    
    with col2:
        st.subheader("📈 System Metrics")
        
        bus_status = ui.get_message_bus_status()
        if "error" not in bus_status:
            status_data = bus_status.get("status", {})
            
            st.metric("Registered Agents", status_data.get("registered_agents", 0))
            st.metric("Total Messages", status_data.get("total_messages", 0))
            
            if status_data.get("running"):
                st.success("🟢 Message Bus Active")
            else:
                st.error("🔴 Message Bus Inactive")

def main():
    """Main application"""
    render_header()
    
    page = st.sidebar.selectbox(
        "🧭 Navigation",
        ["📊 Dashboard", "📄 Document Upload", "🔍 Gap Analysis", "✅ Verification"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    
    **Google ADK Compatible**
    - 🤖 Multi-Agent Architecture
    - 📄 Document AI Processing
    - 🔍 Intelligent Gap Analysis
    - ✅ Automated Verification
    
    **Agents:**
    - 📥 Ingestion Agent
    - 📝 Parsing Agent  
    - 🔍 Gap Analysis Agent
    - ✅ Verification Agent
    """)
    
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "📄 Document Upload":
        document_upload_page()
    elif page == "🔍 Gap Analysis":
        gap_analysis_page()
    elif page == "✅ Verification":
        verification_page()

if __name__ == "__main__":
    main()
