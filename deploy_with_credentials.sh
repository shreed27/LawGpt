#!/bin/bash
# Complete deployment script with your credentials pre-configured

set -e

# Your credentials (already set)
PROJECT_ID="genial-smoke-478804-t1"
REGION="us-central1"
GEMINI_KEY="AIzaSyCEuBzP8p7RNmL6wO8msi6GVRqv5VkvAxk"
API_KEY="legal-ai-secure-key-2024"

echo "🚀 Starting deployment for project: $PROJECT_ID"
echo ""

# Step 1: Set project and authenticate
echo "📋 Step 1: Setting up GCP project..."
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "⚠️  Not authenticated. Running gcloud auth login..."
    gcloud auth login
    gcloud auth application-default login
fi

# Step 2: Enable required APIs
echo ""
echo "📦 Step 2: Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  bigquery.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com \
  --project=$PROJECT_ID

echo "✅ APIs enabled"
echo ""

# Step 3: Deploy services
echo "🏗️  Step 3: Deploying Cloud Run services..."
echo "This will take 5-10 minutes..."
echo ""

export GCP_PROJECT_ID=$PROJECT_ID
export GCP_REGION=$REGION

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
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION" \
  --quiet

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
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION" \
  --quiet

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
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION" \
  --quiet

echo ""
echo "✅ All services deployed!"
echo ""

# Step 4: Get service URLs
echo "🔗 Step 4: Getting service URLs..."
SEARCH_URL=$(gcloud run services describe legal-search-agent \
  --region $REGION \
  --project $PROJECT_ID \
  --format 'value(status.url)')

AI_URL=$(gcloud run services describe legal-ai-agent \
  --region $REGION \
  --project $PROJECT_ID \
  --format 'value(status.url)')

ROUTER_URL=$(gcloud run services describe legal-main-router \
  --region $REGION \
  --project $PROJECT_ID \
  --format 'value(status.url)')

echo "Main Router: $ROUTER_URL"
echo "Search Agent: $SEARCH_URL"
echo "AI Agent: $AI_URL"
echo ""

# Step 5: Update environment variables
echo "⚙️  Step 5: Configuring environment variables..."

# Update Main Router
echo "Updating Main Router configuration..."
gcloud run services update legal-main-router \
  --region $REGION \
  --project $PROJECT_ID \
  --update-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION,GEMINI_API_KEY=$GEMINI_KEY,API_KEY=$API_KEY,LEGAL_SEARCH_AGENT_URL=$SEARCH_URL,LEGAL_AI_AGENT_URL=$AI_URL,DATA_SOURCE=firestore" \
  --quiet

# Update Search Agent
echo "Updating Search Agent configuration..."
gcloud run services update legal-search-agent \
  --region $REGION \
  --project $PROJECT_ID \
  --update-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION,DATA_SOURCE=firestore" \
  --quiet

# Update AI Agent
echo "Updating AI Agent configuration..."
gcloud run services update legal-ai-agent \
  --region $REGION \
  --project $PROJECT_ID \
  --update-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION,GEMINI_API_KEY=$GEMINI_KEY,DATA_SOURCE=firestore" \
  --quiet

echo "✅ Environment variables configured"
echo ""

# Step 6: Set up IAM permissions
echo "🔐 Step 6: Setting up permissions..."

# Get service account emails
ROUTER_SA=$(gcloud run services describe legal-main-router \
  --region $REGION \
  --project $PROJECT_ID \
  --format 'value(spec.template.spec.serviceAccountName)')

SEARCH_SA=$(gcloud run services describe legal-search-agent \
  --region $REGION \
  --project $PROJECT_ID \
  --format 'value(spec.template.spec.serviceAccountName)')

AI_SA=$(gcloud run services describe legal-ai-agent \
  --region $REGION \
  --project $PROJECT_ID \
  --format 'value(spec.template.spec.serviceAccountName)')

echo "Router Service Account: $ROUTER_SA"
echo "Search Service Account: $SEARCH_SA"
echo "AI Service Account: $AI_SA"
echo ""

# Grant Firestore access
echo "Granting Firestore access..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$ROUTER_SA" \
  --role="roles/datastore.user" \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SEARCH_SA" \
  --role="roles/datastore.user" \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$AI_SA" \
  --role="roles/datastore.user" \
  --quiet

# Grant Vertex AI access
echo "Granting Vertex AI access..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$ROUTER_SA" \
  --role="roles/aiplatform.user" \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SEARCH_SA" \
  --role="roles/aiplatform.user" \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$AI_SA" \
  --role="roles/aiplatform.user" \
  --quiet

# Allow Main Router to invoke agent services
echo "Setting up service-to-service authentication..."
gcloud run services add-iam-policy-binding legal-search-agent \
  --region $REGION \
  --project $PROJECT_ID \
  --member="serviceAccount:$ROUTER_SA" \
  --role="roles/run.invoker" \
  --quiet

gcloud run services add-iam-policy-binding legal-ai-agent \
  --region $REGION \
  --project $PROJECT_ID \
  --member="serviceAccount:$ROUTER_SA" \
  --role="roles/run.invoker" \
  --quiet

echo "✅ Permissions configured"
echo ""

# Step 7: Final summary
echo "═══════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 Main Router URL:"
echo "   $ROUTER_URL"
echo ""
echo "📚 API Documentation:"
echo "   $ROUTER_URL/docs"
echo ""
echo "🔑 API Key for testing:"
echo "   $API_KEY"
echo ""
echo "🧪 Test your API:"
echo "   curl -X POST $ROUTER_URL/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'X-API-Key: $API_KEY' \\"
echo "     -d '{\"query\": \"right to privacy cases\", \"mode\": \"legal_search\"}'"
echo ""
echo "📊 View services:"
echo "   gcloud run services list --project=$PROJECT_ID"
echo ""
echo "📝 View logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=legal-main-router\" --limit 50"
echo ""
echo "═══════════════════════════════════════════════════════════"

