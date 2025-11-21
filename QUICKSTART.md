# Quick Start Guide

Get your Legal Search & Legal-ai chatbot running in 5 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with minimum required values:

```env
GCP_PROJECT_ID=your-project-id
GEMINI_API_KEY=your-gemini-api-key
```

## Step 3: Set Up BigQuery (One-Time)

1. Go to BigQuery Console
2. Run the SQL from `setup_bigquery_schema.sql`
3. Insert at least one test case:

```sql
INSERT INTO `legal_data.legal_cases` VALUES
('TEST001', 'Test Case', 'Supreme Court', 2023, 10, 'Article 21', 'Section 1', 'Test summary', 'https://example.com', 'India', 'Constitutional', 'Party A, Party B', '2023-01-01');
```

## Step 4: Run Services

```bash
bash run_local.sh
```

Or run individually:

```bash
# Terminal 1
python -m services.main_router

# Terminal 2  
python -m services.legal_search_agent

# Terminal 3
python -m services.legal_ai_agent
```

## Step 5: Test

```bash
python test_api.py
```

Or use curl:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "right to privacy",
    "mode": "legal_search"
  }'
```

## Step 6: Integrate with Your UI

Your Lovable UI should call:

```javascript
POST http://localhost:8000/chat
Headers: { "Content-Type": "application/json", "X-API-Key": "your-key" }
Body: { "query": "user question", "mode": "legal_search" | "legal_ai" }
```

## Troubleshooting

**"No cases found"**: Make sure BigQuery has data and table names match `.env`

**"Gemini API error"**: Check your API key is valid

**"Connection refused"**: Ensure all three services are running

**"BigQuery permission error"**: Run `gcloud auth application-default login`

## Next Steps

- See `SETUP.md` for detailed configuration
- See `ARCHITECTURE.md` for system design
- Deploy to Cloud Run with `deployment/deploy.sh`

