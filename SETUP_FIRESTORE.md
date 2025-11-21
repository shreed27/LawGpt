# 🔥 Firestore Setup Complete - Ready to Use!

## ✅ What's Been Configured

Your system is now configured to use Firestore from project: **genial-smoke-478804-t1**

### Updated Files:
1. ✅ `.env` - Project ID set to `genial-smoke-478804-t1`
2. ✅ `deploy_with_credentials.sh` - Deployment script updated
3. ✅ Data source set to `firestore`

## 🚀 Quick Start

### Step 1: Set Up Environment

Create/update your `.env` file with:

```env
GCP_PROJECT_ID=genial-smoke-478804-t1
GCP_REGION=us-central1
DATA_SOURCE=firestore
FIRESTORE_CASES_COLLECTION=legal_cases
FIRESTORE_STATUTES_COLLECTION=statutes
GEMINI_API_KEY=AIzaSyCEuBzP8p7RNmL6wO8msi6GVRqv5VkvAxk
API_KEY=legal-ai-secure-key-2024
```

### Step 2: Authenticate with GCP

```bash
# Login to Google Cloud
gcloud auth login

# Set application default credentials
gcloud auth application-default login

# Set the project
gcloud config set project genial-smoke-478804-t1
```

### Step 3: Verify Firestore Access

```bash
# Check if you can access Firestore
gcloud firestore databases list

# If successful, you should see the database
```

### Step 4: Install Dependencies

```bash
cd /Applications/LawGpt
pip install -r requirements.txt
```

### Step 5: Test Locally

```bash
# Run all services
bash run_local.sh
```

In another terminal, test:

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

## 📊 Firestore Collection Structure

Make sure your Firestore has these collections with proper structure:

### Collection: `legal_cases`

Each document should have:
```json
{
  "case_title": "Justice K.S. Puttaswamy v. Union of India",
  "court": "Supreme Court of India",
  "year": 2017,
  "citation_count": 540,
  "articles": "Article 21",
  "sections": "Section 43A IT Act",
  "summary": "Landmark case on right to privacy",
  "full_text_url": "https://example.com/case001",
  "jurisdiction": "India",
  "case_type": "Constitutional",
  "parties": "K.S. Puttaswamy, Union of India",
  "judgment_date": "2017-08-24"
}
```

### Collection: `statutes`

Each document should have:
```json
{
  "act_name": "Information Technology Act",
  "section_number": "43A",
  "section_title": "Compensation for failure to protect data",
  "section_text": "Where a body corporate...",
  "jurisdiction": "India",
  "effective_date": "2000-10-17",
  "related_cases": "CASE001,CASE002",
  "amendments": ""
}
```

## 🚢 Deploy to Cloud Run

When ready to deploy:

```bash
# Make sure you're authenticated
gcloud auth login
gcloud config set project genial-smoke-478804-t1

# Deploy everything
bash deploy_with_credentials.sh
```

This will:
- Deploy to project `genial-smoke-478804-t1`
- Connect directly to Firestore
- Configure all environment variables
- Set up permissions

## 🔍 Verify Configuration

Check your configuration is correct:

```bash
# Verify project is set
gcloud config get-value project

# Should output: genial-smoke-478804-t1

# Verify Firestore access
gcloud firestore databases list
```

## 🐛 Troubleshooting

### Issue: "Permission denied"
**Solution:**
```bash
gcloud auth login
gcloud auth application-default login
gcloud projects add-iam-policy-binding genial-smoke-478804-t1 \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/datastore.user"
```

### Issue: "Project not found"
**Solution:**
- Verify you have access to `genial-smoke-478804-t1`
- Ask your teammate to confirm you're added to the project

### Issue: "Collection not found"
**Solution:**
- Check Firestore Console: https://console.firebase.google.com/project/genial-smoke-478804-t1/firestore
- Verify collections are named `legal_cases` and `statutes`
- Or update collection names in `.env` if different

### Issue: "No data returned"
**Solution:**
- Check if Firestore has documents
- Verify document structure matches expected format
- Check logs: `gcloud logging read "resource.type=cloud_run_revision" --limit 50`

## 📝 Environment Variables Summary

Your `.env` should have:
```env
GCP_PROJECT_ID=genial-smoke-478804-t1          # ✅ Firestore project
DATA_SOURCE=firestore                           # ✅ Using Firestore
FIRESTORE_CASES_COLLECTION=legal_cases          # ✅ Collection name
FIRESTORE_STATUTES_COLLECTION=statutes          # ✅ Collection name
GEMINI_API_KEY=AIzaSyCEuBzP8p7RNmL6wO8msi6GVRqv5VkvAxk  # ✅ Your API key
```

## ✅ Checklist

- [x] Project ID updated to `genial-smoke-478804-t1`
- [x] Deployment script updated
- [x] Data source set to `firestore`
- [ ] GCP authentication completed
- [ ] Firestore access verified
- [ ] Dependencies installed
- [ ] Local testing successful
- [ ] Ready to deploy

## 🎉 Next Steps

1. **Test Locally**: Run `bash run_local.sh` and test the API
2. **Verify Data**: Make sure Firestore has data in `legal_cases` and `statutes`
3. **Deploy**: Run `bash deploy_with_credentials.sh` when ready
4. **Integrate**: Use the Cloud Run URL in your Lovable UI

Your system is configured and ready to use Firestore! 🚀

