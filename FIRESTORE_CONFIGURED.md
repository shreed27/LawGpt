# ✅ Firestore Configuration Complete!

Your system is now configured to use Firestore from project: **genial-smoke-478804-t1**

## What's Been Updated

1. ✅ `.env` file - Updated with Firestore project ID
2. ✅ `deploy_with_credentials.sh` - Updated deployment script
3. ✅ Configuration set to use Firestore as data source

## Current Configuration

- **Project ID**: `genial-smoke-478804-t1`
- **Data Source**: `firestore`
- **Collections**: 
  - `legal_cases`
  - `statutes`
- **Gemini API**: Configured ✅
- **Region**: `us-central1`

## Quick Start

### 1. Verify Access

```bash
# Set the project
gcloud config set project genial-smoke-478804-t1

# Verify Firestore access
gcloud firestore databases list

# Check collections (if accessible)
gcloud firestore collections list
```

### 2. Authenticate (if needed)

```bash
gcloud auth login
gcloud auth application-default login
```

### 3. Test Locally

```bash
# Install dependencies (if not done)
pip install -r requirements.txt

# Run services
bash run_local.sh
```

### 4. Test Firestore Connection

```bash
# Test the API
python test_api.py

# Or test manually
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: legal-ai-secure-key-2024" \
  -d '{
    "query": "right to privacy cases",
    "mode": "legal_search"
  }'
```

## Deploy to Cloud Run

When ready to deploy:

```bash
bash deploy_with_credentials.sh
```

This will deploy to project `genial-smoke-478804-t1` and connect directly to Firestore.

## Firestore Document Structure

Make sure your Firestore collections have this structure:

### `legal_cases` collection:
```json
{
  "case_title": "Case Name",
  "court": "Court Name",
  "year": 2023,
  "citation_count": 10,
  "articles": "Article 21",
  "sections": "Section 1",
  "summary": "Case summary...",
  "full_text_url": "https://...",
  "jurisdiction": "India",
  "case_type": "Constitutional",
  "parties": "Party A, Party B",
  "judgment_date": "2023-01-01"
}
```

### `statutes` collection:
```json
{
  "act_name": "Act Name",
  "section_number": "1",
  "section_title": "Section Title",
  "section_text": "Section text...",
  "jurisdiction": "India",
  "effective_date": "2023-01-01",
  "related_cases": "CASE001,CASE002",
  "amendments": ""
}
```

## Troubleshooting

### "Permission denied"
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

### "Project not found"
- Verify you have access to `genial-smoke-478804-t1`
- Ask your teammate to confirm access

### "Collection not found"
- Verify collection names are `legal_cases` and `statutes`
- Or update `FIRESTORE_CASES_COLLECTION` and `FIRESTORE_STATUTES_COLLECTION` in `.env`

### "No data returned"
- Check if Firestore has documents in the collections
- Verify document structure matches expected format

## Next Steps

1. ✅ Configuration updated
2. ⏭️ Test locally
3. ⏭️ Verify Firestore connection
4. ⏭️ Deploy to Cloud Run
5. ⏭️ Integrate with your UI

Your system is ready to use Firestore! 🚀

