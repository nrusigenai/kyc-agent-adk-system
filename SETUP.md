# KYC Agent System Setup Guide

## Overview
Complete multi-agent KYC (Know Your Customer) system with Google ADK compatibility featuring 4 specialized agents for document processing, parsing, gap analysis, and verification with a professional Streamlit UI.

## System Architecture

### Google ADK Framework
- **AgentInterface**: Base interface for all agents
- **MessageBus**: Async message routing between agents
- **AgentRegistry**: Agent registration and discovery
- **AgentManager**: Orchestrates agent lifecycle and workflows

### KYC Agents
1. **IngestionAgent**: Processes documents using simulated Google Cloud Document AI
2. **ParsingAgent**: Structures extracted data into standardized KYC brief format
3. **GapAnalysisAgent**: Analyzes missing information with priority recommendations
4. **VerificationAgent**: Cross-references information with external databases

## Prerequisites
- Python 3.12+
- Poetry (for dependency management)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kyc-agent-adk-system
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Activate virtual environment**
   ```bash
   poetry shell
   ```

## Running the System

### Start FastAPI Backend
```bash
poetry run python run_api.py
```
- API available at: http://localhost:8000
- API documentation: http://localhost:8000/docs

### Start Streamlit UI
```bash
poetry run python run_ui.py
```
- UI available at: http://localhost:8501

## API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `POST /upload-document` - Upload documents for processing
- `POST /parse-documents` - Parse documents into KYC brief
- `POST /analyze-gaps` - Analyze missing information
- `POST /verify-information` - Verify KYC information
- `POST /process-full-workflow` - Complete end-to-end processing

### ADK Management
- `GET /adk/agents` - List all registered agents
- `GET /adk/message-bus/status` - Message bus status
- `GET /adk/agents/capabilities/{capability}` - Find agents by capability

### Client Management
- `GET /kyc-brief/{client_id}` - Get KYC brief for client
- `GET /clients` - List all clients
- `DELETE /clients/{client_id}` - Delete client data

## Usage Example

1. **Upload Document**
   ```bash
   curl -X POST http://localhost:8000/upload-document \
     -F "file=@passport.pdf" \
     -F "document_type=passport" \
     -F "client_id=client123"
   ```

2. **Process Full Workflow**
   ```bash
   curl -X POST http://localhost:8000/process-full-workflow \
     -H "Content-Type: application/json" \
     -d '{"client_id": "client123"}'
   ```

3. **Get KYC Brief**
   ```bash
   curl http://localhost:8000/kyc-brief/client123
   ```

## Streamlit UI Features

### Navigation Sections
- **Dashboard**: System overview and agent status
- **Document Upload**: Upload and process documents
- **Processing**: Monitor agent processing pipeline
- **Gap Analysis**: View missing information and recommendations
- **Verification**: Review verification results

### Key Features
- Real-time agent status monitoring
- Interactive progress tracking
- Professional material design styling
- Comprehensive error handling
- Responsive layout with modern UI components

## Development

### Project Structure
```
kyc-agent-adk-system/
├── adk/                    # Google ADK framework
│   ├── core/              # Core ADK components
│   ├── interfaces/        # Agent interfaces
│   └── agents/           # KYC-specific agents
├── app/                   # FastAPI application
├── models/               # Pydantic data models
├── utils/                # Utility functions
├── streamlit_app.py      # Streamlit UI
├── run_api.py           # API server launcher
└── run_ui.py            # UI launcher
```

### Adding New Agents
1. Implement `AgentInterface` in `adk/interfaces/agent_interface.py`
2. Create agent class in `adk/agents/`
3. Register agent in `app/main.py` startup event
4. Add API endpoints as needed

### Configuration
- Modify `utils/config.py` for system settings
- Update `pyproject.toml` for dependencies
- Adjust logging levels in launcher scripts

## Demo Features

### Simulated Integrations
- Google Cloud Document AI (simulated responses)
- External database verification (mock data)
- Sanctions list checking (simulated)

### Sample Data
The system includes realistic sample responses for:
- Passport processing
- Utility bill verification
- Bank statement analysis
- Driver's license validation

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 8000 and 8501 are available
2. **Poetry issues**: Run `poetry install --no-dev` if development dependencies fail
3. **Agent registration**: Check logs for agent startup errors

### Logs
- API logs: Console output from `run_api.py`
- UI logs: Console output from `run_ui.py`
- Agent logs: Included in API response messages

## Production Deployment

### Environment Variables
```bash
export KYC_API_HOST=0.0.0.0
export KYC_API_PORT=8000
export KYC_UI_PORT=8501
export KYC_LOG_LEVEL=INFO
```

### Docker Support
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
EXPOSE 8000 8501
CMD ["poetry", "run", "python", "run_api.py"]
```

## Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-agent`
3. Commit changes: `git commit -am 'Add new agent'`
4. Push branch: `git push origin feature/new-agent`
5. Create Pull Request

## License
MIT License - see LICENSE file for details

## Support
For issues and questions, please create a GitHub issue or contact the development team.
