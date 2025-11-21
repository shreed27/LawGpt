# 🚀 Ready to Deploy - Your Credentials Configured!

Your project is now configured with:
- **Project ID**: `labbb-478804`
- **Gemini API Key**: Configured ✅
- **Region**: `us-central1`

## Quick Start - Deploy Now!

### Option 1: One-Command Deployment (Recommended)

```bash
cd /Applications/LawGpt
bash deploy_with_credentials.sh
```

This script will:
1. ✅ Set up your GCP project
2. ✅ Enable all required APIs
3. ✅ Deploy all 3 services to Cloud Run
4. ✅ Configure environment variables
5. ✅ Set up all permissions
6. ✅ Give you the final URLs

**Just run it and wait 5-10 minutes!**

### Option 2: Step-by-Step Manual Deployment

If you prefer to do it step by step:

```bash
# 1. Set project
gcloud config set project labbb-478804

# 2. Authenticate (if not done)
gcloud auth login
gcloud auth application-default login

# 3. Enable APIs
gcloud services enable \
  run.googleapis.com \
  bigquery.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  --project=labbb-478804

# 4. Deploy services
bash deployment/deploy.sh

# 5. Get URLs and configure (see below)
```

## After Deployment

### Get Your Service URLs

```bash
# Main Router (this is what you'll use)
gcloud run services describe legal-main-router \
  --region us-central1 \
  --project labbb-478804 \
  --format 'value(status.url)'

# Search Agent
gcloud run services describe legal-search-agent \
  --region us-central1 \
  --project labbb-478804 \
  --format 'value(status.url)'

# AI Agent
gcloud run services describe legal-ai-agent \
  --region us-central1 \
  --project labbb-478804 \
  --format 'value(status.url)'
```

### Update Environment Variables

The `deploy_with_credentials.sh` script does this automatically, but if you need to do it manually:

```bash
# Replace SEARCH_URL and AI_URL with actual URLs from above
gcloud run services update legal-main-router \
  --region us-central1 \
  --project labbb-478804 \
  --update-env-vars="GCP_PROJECT_ID=labbb-478804,GCP_REGION=us-central1,GEMINI_API_KEY=AIzaSyCEuBzP8p7RNmL6wO8msi6GVRqv5VkvAxk,API_KEY=legal-ai-secure-key-2024,LEGAL_SEARCH_AGENT_URL=SEARCH_URL,LEGAL_AI_AGENT_URL=AI_URL,DATA_SOURCE=firestore"
```

## Test Your Deployment

Once deployed, test with:

```bash
# Get your router URL first
ROUTER_URL=$(gcloud run services describe legal-main-router \
  --region us-central1 \
  --project labbb-478804 \
  --format 'value(status.url)')

# Test health check
curl $ROUTER_URL/health

# Test Legal Search
curl -X POST $ROUTER_URL/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: legal-ai-secure-key-2024" \
  -d '{
    "query": "right to privacy cases",
    "mode": "legal_search"
  }'

# Test Legal-ai Analysis
curl -X POST $ROUTER_URL/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: legal-ai-secure-key-2024" \
  -d '{
    "query": "Am I legally bound to not buy land from an Adivasi in MP?",
    "mode": "legal_ai"
  }'
```

## View API Documentation

Once deployed, visit:
```
https://legal-main-router-xxxxx.run.app/docs
```

## Important Notes

1. **API Key Security**: Your Gemini API key is in the `.env` file. Keep this file secure and never commit it to Git.

2. **Firestore Data**: Make sure your Firestore has:
   - Collection: `legal_cases`
   - Collection: `statutes`
   - With proper document structure (see FIRESTORE_SETUP.md)

3. **Billing**: Make sure billing is enabled on your GCP project.

4. **First Deployment**: The first deployment takes longer (5-10 minutes) as it builds Docker images.

## Troubleshooting

### "Permission denied"
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

### "API not enabled"
```bash
# Enable APIs
gcloud services enable run.googleapis.com bigquery.googleapis.com firestore.googleapis.com aiplatform.googleapis.com cloudbuild.googleapis.com --project=labbb-478804
```

### "Service not found"
Wait a few minutes after deployment, then check:
```bash
gcloud run services list --project=labbb-478804
```

### View logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=legal-main-router" --limit 50 --project=labbb-478804
```

## Next Steps

1. ✅ Run `bash deploy_with_credentials.sh`
2. ✅ Wait for deployment to complete
3. ✅ Test with curl commands above
4. ✅ Integrate with your Lovable UI using the Main Router URL
5. ✅ Monitor logs and usage

Your system is ready to deploy! 🎉

