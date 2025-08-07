#!/bin/bash


set -e

ENVIRONMENT=${1:-development}
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}

echo "🚀 Deploying KYC ADK System to Google Agent Engine"
echo "Environment: $ENVIRONMENT"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔍 Validating ADK components..."
python validate_adk.py

echo "📦 Creating deployment package..."
tar -czf kyc-adk-system.tar.gz adk/ deployment/ requirements.txt

echo "🌐 Deploying to Google Agent Engine..."
gcloud agent-engine deploy \
  --project=$PROJECT_ID \
  --region=$REGION \
  --config=deployment/agent_config.yaml \
  --source=kyc-adk-system.tar.gz \
  --environment=$ENVIRONMENT

echo "✅ Deployment completed successfully!"
echo "🔗 Agent system available at: https://agent-engine-$PROJECT_ID-$REGION.googleapis.com/kyc-agent-system"
