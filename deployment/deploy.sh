#!/bin/bash
# Deployment script for Cloud Run services

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}

echo "Deploying Legal Search & Legal-ai services to Cloud Run..."

# Deploy Main Router
echo "Deploying Main Router..."
gcloud run deploy legal-main-router \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --dockerfile Dockerfile.router \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION"

# Deploy Legal Search Agent
echo "Deploying Legal Search Agent..."
gcloud run deploy legal-search-agent \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --dockerfile Dockerfile.search \
  --no-allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION"

# Deploy Legal-ai Agent
echo "Deploying Legal-ai Agent..."
gcloud run deploy legal-ai-agent \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --dockerfile Dockerfile.ai \
  --no-allow-unauthenticated \
  --memory 4Gi \
  --cpu 4 \
  --timeout 600 \
  --max-instances 10 \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION"

echo "Deployment complete!"
echo "Update service URLs in your .env file with the Cloud Run URLs"

