# Legal Search & Legal-ai Setup Guide

## Prerequisites

1. **Google Cloud Platform Account**
   - Project with billing enabled
   - BigQuery dataset and tables set up
   - Vertex AI API enabled
   - Service account with appropriate permissions

2. **Python 3.11+**
   - Install Python 3.11 or higher

3. **Google Cloud SDK**
   - Install and authenticate: `gcloud auth application-default login`

4. **Gemini API Key**
   - Get API key from Google AI Studio: https://makersuite.google.com/app/apikey

## Installation

### 1. Clone and Install Dependencies

```bash
cd /Applications/LawGpt
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
BIGQUERY_DATASET=legal_data
BIGQUERY_CASE_TABLE=legal_cases
BIGQUERY_STATUTE_TABLE=statutes
VERTEX_AI_LOCATION=us-central1
GEMINI_API_KEY=your-gemini-api-key
API_KEY=your-secure-api-key-for-authentication
```

### 3. Set Up BigQuery

Run the schema setup script in BigQuery:

```bash
# Using bq command line tool
bq query --use_legacy_sql=false < setup_bigquery_schema.sql

# Or use BigQuery Console and paste the SQL
```

### 4. Populate BigQuery with Data

You need to populate your BigQuery tables with legal cases and statutes. Example:

```sql
INSERT INTO `legal_data.legal_cases` VALUES
('CASE001', 'Justice K.S. Puttaswamy v. Union of India', 'Supreme Court of India', 2017, 540, 'Article 21', 'Section 43A IT Act', 'Landmark case on right to privacy as fundamental right', 'https://example.com/case001', 'India', 'Constitutional', 'K.S. Puttaswamy, Union of India', '2017-08-24');
```

### 5. Set Up Vertex AI Vector Search (Optional but Recommended)

1. Create a Vertex AI index endpoint
2. Upload embeddings for your legal cases
3. Update `VERTEX_AI_INDEX_ENDPOINT` in `.env`

## Running Locally

### Option 1: Run All Services Together

```bash
bash run_local.sh
```

This starts:
- Main Router on http://localhost:8000
- Legal Search Agent on http://localhost:8001
- Legal-ai Agent on http://localhost:8002

### Option 2: Run Services Individually

```bash
# Terminal 1 - Main Router
python -m services.main_router

# Terminal 2 - Legal Search Agent
python -m services.legal_search_agent

# Terminal 3 - Legal-ai Agent
python -m services.legal_ai_agent
```

## Testing

Test the API:

```bash
python test_api.py
```

Or use curl:

```bash
# Health check
curl http://localhost:8000/health

# Legal Search query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "right to privacy data protection cases",
    "mode": "legal_search"
  }'

# Legal-ai Analysis query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "Am I legally bound to not buy land from an Adivasi in MP?",
    "mode": "legal_ai"
  }'
```

## Deployment to Cloud Run

### 1. Build and Deploy

```bash
# Make sure you're authenticated
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Run deployment script
bash deployment/deploy.sh
```

### 2. Update Service URLs

After deployment, update your `.env` file with the Cloud Run URLs:

```env
LEGAL_SEARCH_AGENT_URL=https://legal-search-agent-xxx.run.app
LEGAL_AI_AGENT_URL=https://legal-ai-agent-xxx.run.app
```

### 3. Set Up IAM Permissions

Ensure Cloud Run services have permissions to:
- Read from BigQuery
- Access Vertex AI
- Invoke other Cloud Run services

```bash
# Grant BigQuery access
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/bigquery.dataViewer"

# Grant Vertex AI access
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```

## API Documentation

Once services are running, visit:
- Main Router API Docs: http://localhost:8000/docs
- Legal Search Agent Docs: http://localhost:8001/docs
- Legal-ai Agent Docs: http://localhost:8002/docs

## Integration with Frontend (Lovable UI)

Your Lovable UI should make POST requests to the Main Router:

```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    query: 'right to privacy data protection',
    mode: 'legal_search' // or 'legal_ai'
  })
});

const data = await response.json();
// data.response - main response text
// data.cases - array of case objects (for legal_search mode)
// data.analysis - analysis object (for legal_ai mode)
// data.sources - list of source URLs
```

## Troubleshooting

### Common Issues

1. **BigQuery Permission Errors**
   - Ensure service account has `bigquery.dataViewer` role
   - Check that dataset and tables exist

2. **Gemini API Errors**
   - Verify API key is correct
   - Check API quota limits

3. **Service Communication Errors**
   - Verify service URLs in `.env` are correct
   - Check that all services are running
   - For Cloud Run, ensure services can communicate (same VPC or public)

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version: `python --version` (should be 3.11+)

## Production Checklist

- [ ] Set up proper authentication (API keys or OAuth)
- [ ] Configure CORS for your frontend domain
- [ ] Set up monitoring and logging (Cloud Logging)
- [ ] Configure auto-scaling for Cloud Run
- [ ] Set up error alerting
- [ ] Enable Cloud Run authentication for agent services
- [ ] Set up CI/CD pipeline
- [ ] Configure rate limiting
- [ ] Set up backup and disaster recovery

