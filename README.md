# Legal Search & Legal-ai Chatbot System

A production-ready legal chatbot system with two operational modes:
- **Legal Search**: Fast case retrieval with full metadata
- **Legal-ai**: Exhaustive legal analysis for judges and lawyers

## 🚀 Features

### Dual Mode System
- **Legal Search Mode**: Fast case retrieval from Firestore/BigQuery
- **Legal-ai Mode**: Deep, exhaustive legal analysis with Gemini 1.5 Pro

### Backend Integration
- **`/search-law`**: Keyword-based search with legal stopwords filtering
- **`/explain-law`**: AI-powered explanations with Hinglish/English support
- **`/chat`**: Main chat endpoint for Legal Search & Legal-ai

### Key Capabilities
- ✅ Multi-jurisdictional legal analysis
- ✅ Firestore & BigQuery support
- ✅ Gemini 1.5 Flash & Pro integration
- ✅ Hinglish/English language detection
- ✅ Keyword extraction with legal stopwords
- ✅ Semantic search via Vertex AI
- ✅ Fallback error handling
- ✅ Production-ready deployment

## 📋 Prerequisites

- Python 3.11+
- Google Cloud Platform account
- Gemini API key
- Firestore/BigQuery with legal data
- Google Cloud SDK (for deployment)

## 🛠️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/LawGpt.git
cd LawGpt
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```env
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
DATA_SOURCE=firestore
FIRESTORE_ACTS_COLLECTION=acts
FIRESTORE_CASES_COLLECTION=legal_cases
FIRESTORE_STATUTES_COLLECTION=statutes
GEMINI_API_KEY=your-gemini-api-key
API_KEY=your-secure-api-key
```

### 4. Authenticate with GCP

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project your-project-id
```

## 🚀 Quick Start

### Run Locally

```bash
# Run all services
bash run_local.sh
```

Services will be available at:
- Main Router: http://localhost:8000
- Legal Search Agent: http://localhost:8001
- Legal-ai Agent: http://localhost:8002

### Test API

```bash
# Test search-law
curl -X POST http://localhost:8000/search-law \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "right to privacy", "limit": 20}'

# Test explain-law
curl -X POST http://localhost:8000/explain-law \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "What is right to privacy?"}'

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "right to privacy cases", "mode": "legal_search"}'
```

## 📚 API Documentation

Once services are running, visit:
- **Main Router API Docs**: http://localhost:8000/docs
- **Legal Search Agent Docs**: http://localhost:8001/docs
- **Legal-ai Agent Docs**: http://localhost:8002/docs

## 🏗️ Architecture

### Services
1. **Main MCP Router** - Intent detection, routing, synthesis
2. **Legal Search Agent** - Case retrieval from Firestore/BigQuery
3. **Legal-ai Analysis Agent** - Deep legal analysis with Gemini Pro

### Data Sources
- **Firestore**: Legal acts, cases, statutes
- **BigQuery**: Structured legal data (alternative)
- **Vertex AI Vector Search**: Semantic embeddings for RAG

### AI Integration
- **Gemini 1.5 Flash**: Fast intent detection
- **Gemini 1.5 Pro**: Comprehensive legal analysis

## 📁 Project Structure

```
LawGpt/
├── services/              # Microservices
│   ├── main_router.py     # Main API router
│   ├── legal_search_agent.py
│   └── legal_ai_agent.py
├── utils/                 # Utilities
│   ├── firestore_client.py
│   ├── bigquery_client.py
│   ├── gemini_client.py
│   ├── keyword_extractor.py
│   └── language_detector.py
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── deployment/            # Deployment scripts
└── README.md
```

## 🚢 Deployment

### Deploy to Cloud Run

```bash
# Update deploy_with_credentials.sh with your project ID
bash deploy_with_credentials.sh
```

### Manual Deployment

```bash
gcloud run deploy legal-main-router \
  --source . \
  --platform managed \
  --region us-central1 \
  --dockerfile Dockerfile.router
```

See `SETUP.md` and `DEPLOYMENT_READY.md` for detailed instructions.

## 📖 Documentation

- **`SETUP.md`** - Detailed setup guide
- **`QUICKSTART.md`** - Quick start guide
- **`ARCHITECTURE.md`** - System architecture
- **`BACKEND_INTEGRATION.md`** - Backend integration details
- **`FIRESTORE_SETUP.md`** - Firestore configuration

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | Yes |
| `DATA_SOURCE` | `firestore` or `bigquery` | Yes |
| `GEMINI_API_KEY` | Gemini API key | Yes |
| `API_KEY` | API authentication key | Yes |
| `FIRESTORE_ACTS_COLLECTION` | Firestore acts collection | Yes (if using Firestore) |

See `ENV_EXAMPLE.txt` for complete list.

## 🧪 Testing

```bash
# Run test script
python test_api.py

# Or test individual endpoints
curl http://localhost:8000/health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI
- Google Cloud Platform
- FastAPI
- All contributors

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for the legal community**
