# KYC Agent Development Kit (ADK) for Google Agent Engine

This package contains the core ADK components for deploying KYC agents to Google Agent Engine.

## Structure

```
kyc_adk_package/
├── adk/
│   ├── core/                 # Core ADK infrastructure
│   │   ├── agent_manager.py  # Agent lifecycle management
│   │   ├── agent_registry.py # Agent registration and discovery
│   │   └── message_bus.py    # Inter-agent communication
│   ├── interfaces/           # ADK interfaces
│   │   ├── agent_interface.py    # Base agent interface
│   │   └── message_interface.py  # Message handling interface
│   ├── agents/              # Specialized KYC agents
│   │   ├── kyc_ingestion_agent.py     # Document ingestion
│   │   ├── kyc_parsing_agent.py       # Document parsing & structuring
│   │   ├── kyc_gap_analysis_agent.py  # Gap analysis & recommendations
│   │   └── kyc_verification_agent.py  # Information verification
│   └── models/              # Data models
│       └── kyc_models.py    # KYC-specific data structures
├── requirements.txt         # Python dependencies
└── deployment/             # Google Agent Engine deployment configs
    ├── agent_config.yaml   # Agent configuration
    └── deploy.sh          # Deployment script
```

## Features

- **Google ADK Compatible**: Fully compatible with Google Agent Engine
- **Multi-Agent Architecture**: 4 specialized agents working in coordination
- **Async Processing**: Built for high-performance async operations
- **Extensible**: Easy to add new agents and capabilities
- **Production Ready**: Includes proper error handling and logging

## Agents

1. **KYCIngestionAgent**: Processes uploaded documents and extracts raw content
2. **KYCParsingAgent**: Structures raw data into standardized KYC briefs
3. **KYCGapAnalysisAgent**: Analyzes missing information and provides recommendations
4. **KYCVerificationAgent**: Verifies information against external databases

## Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud SDK
- Google Agent Engine access

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Validate ADK components
python validate_adk.py
```

### Deployment to Google Agent Engine
```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"

# Deploy to development environment
chmod +x deployment/deploy.sh
./deployment/deploy.sh development

# Deploy to production environment
./deployment/deploy.sh production
```

## Usage Example

```python
import asyncio
from adk.core.agent_manager import AgentManager
from adk.agents.kyc_ingestion_agent import KYCIngestionAgent
from adk.agents.kyc_parsing_agent import KYCParsingAgent
from adk.agents.kyc_gap_analysis_agent import KYCGapAnalysisAgent
from adk.agents.kyc_verification_agent import KYCVerificationAgent

async def main():
    # Initialize agent manager
    manager = AgentManager()
    
    # Create and register agents
    ingestion_agent = KYCIngestionAgent()
    parsing_agent = KYCParsingAgent()
    gap_analysis_agent = KYCGapAnalysisAgent()
    verification_agent = KYCVerificationAgent()
    
    await manager.start_agent(ingestion_agent)
    await manager.start_agent(parsing_agent)
    await manager.start_agent(gap_analysis_agent)
    await manager.start_agent(verification_agent)
    
    # Execute workflow
    workflow_config = {
        "workflow_id": "kyc_processing",
        "steps": [
            {
                "name": "ingestion",
                "agent_id": ingestion_agent.agent_id,
                "task_data": {"document_data": "base64_encoded_document"}
            },
            {
                "name": "parsing",
                "agent_id": parsing_agent.agent_id,
                "task_data": {}
            },
            {
                "name": "gap_analysis",
                "agent_id": gap_analysis_agent.agent_id,
                "task_data": {}
            },
            {
                "name": "verification",
                "agent_id": verification_agent.agent_id,
                "task_data": {"fields_to_verify": ["full_name", "date_of_birth"]}
            }
        ]
    }
    
    result = await manager.orchestrate_workflow(workflow_config)
    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

The `deployment/agent_config.yaml` file contains all agent configurations:

- **Agent Settings**: Timeouts, file size limits, confidence thresholds
- **Message Bus**: Queue sizes, retry attempts, message timeouts
- **Agent Manager**: Concurrent agent limits, health check intervals

## Architecture

### Core Components

- **AgentManager**: Orchestrates agent lifecycle and workflow execution
- **AgentRegistry**: Manages agent registration and discovery
- **MessageBus**: Handles async inter-agent communication
- **AgentInterface**: Abstract base class for all agents
- **MessageInterface**: Defines message structure and handling

### Data Models

- **KYCBrief**: Standardized client information structure
- **Document**: Document metadata and content
- **GapAnalysisResult**: Missing information analysis
- **VerificationResult**: Information verification outcomes

## Deployment

Deploy to Google Agent Engine using the provided configuration files and deployment script.

### Environment Variables

- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_CLOUD_REGION`: Deployment region (default: us-central1)

### Monitoring

After deployment, monitor your agents through:
- Google Cloud Console
- Agent Engine dashboard
- Health check endpoints
- Message bus metrics

## Support

For issues or questions:
1. Check the deployment logs
2. Verify agent configurations
3. Test individual agent components
4. Review Google Agent Engine documentation
