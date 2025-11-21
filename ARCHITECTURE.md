# Legal Search & Legal-ai Architecture

## System Overview

A production-ready legal chatbot system with two operational modes:
1. **Legal Search**: Fast case retrieval with full metadata
2. **Legal-ai**: Exhaustive legal analysis for judges and lawyers

## Architecture Components

### 1. Main MCP Router (`services/main_router.py`)
- **Technology**: FastAPI + Gemini 1.5 Flash
- **Purpose**: Central intelligence hub
- **Responsibilities**:
  - Intent detection and classification
  - Routing to appropriate agents
  - Response synthesis
  - API endpoint management

**Key Features**:
- Auto-detects query complexity and mode
- Parallel agent execution
- Unified response formatting
- Health monitoring

### 2. Legal Search Agent (`services/legal_search_agent.py`)
- **Technology**: FastAPI + BigQuery + Vertex AI
- **Purpose**: Fast case retrieval
- **Responsibilities**:
  - Query BigQuery for structured case data
  - Semantic search via Vertex AI Vector Search
  - Format case results with metadata

**Output Format**:
- Case cards with: title, court, year, citations, articles, sections, summary
- Sorted by citation count and relevance

### 3. Legal-ai Analysis Agent (`services/legal_ai_agent.py`)
- **Technology**: FastAPI + Gemini 1.5 Pro + BigQuery + Vertex AI
- **Purpose**: Deep legal analysis
- **Responsibilities**:
  - Comprehensive legal research
  - Multi-jurisdictional analysis
  - Exhaustive reasoning and citation
  - Risk assessment and recommendations

**Output Format**:
- Structured legal brief with:
  - Executive Summary
  - Facts & Assumptions
  - Issues Presented
  - Applicable Law (statutes, articles, sections)
  - Comparative Case Analysis
  - Detailed Legal Analysis
  - Multi-jurisdictional Perspective
  - Legal Tests Applied
  - Risk Assessment
  - Practical Implications
  - Remedies & Recommendations
  - Conclusion with Reasoning

## Data Flow

```
User Query (Lovable UI)
    ↓
Main MCP Router (Intent Detection)
    ↓
    ├─→ Legal Search Agent
    │       ├─→ BigQuery (Structured Cases)
    │       └─→ Vertex AI Vector Search (Semantic)
    │
    └─→ Legal-ai Analysis Agent
            ├─→ BigQuery (Cases + Statutes)
            ├─→ Vertex AI Vector Search (Semantic)
            └─→ Gemini 1.5 Pro (Analysis Generation)
    ↓
Response Synthesis (Main Router)
    ↓
Formatted Response (UI)
```

## Data Sources

### BigQuery Tables

1. **legal_cases**
   - Structured case metadata
   - Fields: case_id, title, court, year, citations, articles, sections, summary, jurisdiction
   - Partitioned by year, clustered by jurisdiction

2. **statutes**
   - Acts, sections, regulations
   - Fields: statute_id, act_name, section_number, section_text, jurisdiction
   - Partitioned by effective_date

### Vertex AI Vector Search
- Semantic embeddings of case law
- Enables similarity-based retrieval
- Multi-jurisdictional knowledge base

## API Endpoints

### Main Router (`/chat`)
- **Method**: POST
- **Request**:
  ```json
  {
    "query": "user question",
    "mode": "legal_search" | "legal_ai" (optional, auto-detected),
    "context": {}
  }
  ```
- **Response**:
  ```json
  {
    "response": "summary text",
    "mode": "legal_search" | "legal_ai",
    "cases": [...],
    "analysis": {...},
    "sources": [...],
    "diagnostics": {...}
  }
  ```

## Security

- API key authentication via `X-API-Key` header
- Service-to-service authentication for Cloud Run
- IAM roles for GCP resource access

## Scalability

- Cloud Run auto-scaling (0 to N instances)
- Stateless services (horizontal scaling)
- Async agent execution (parallel processing)
- Connection pooling for BigQuery

## Monitoring

- Structured logging via Python logging
- Health check endpoints (`/health`)
- Diagnostics in response payload
- Error tracking and reporting

## Deployment

### Local Development
- Run all services locally with `run_local.sh`
- Services on ports 8000, 8001, 8002

### Cloud Run Production
- Deploy with `deployment/deploy.sh`
- Auto-scaling, load balancing
- Environment-based configuration

## Performance Optimizations

1. **Caching**: Consider Redis for frequent queries
2. **Parallel Execution**: Agents run concurrently
3. **Query Optimization**: BigQuery clustering and partitioning
4. **Response Streaming**: For long analyses (future enhancement)

## Future Enhancements

- [ ] Response streaming for real-time updates
- [ ] Caching layer (Redis)
- [ ] Advanced RAG with re-ranking
- [ ] Multi-language support
- [ ] Citation verification
- [ ] Regulatory update notifications
- [ ] Custom agent plugins (Drafting, Compliance)

