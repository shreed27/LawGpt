"""Legal Search Agent - Fast case retrieval service."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from config import settings
from utils.logger import setup_logger
from utils.bigquery_client import BigQueryClient
from utils.firestore_client import FirestoreClient
from utils.vertex_ai_client import VertexAIClient

logger = setup_logger(__name__)

app = FastAPI(title="Legal Search Agent")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients based on data source configuration
if settings.data_source.lower() == "firestore":
    data_client = FirestoreClient()
    logger.info("Using Firestore as data source")
else:
    data_client = BigQueryClient()
    logger.info("Using BigQuery as data source")

vertex_client = VertexAIClient()


class ProcessRequest(BaseModel):
    """Process request model."""
    query: str
    topics: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    limit: int = 20


class ProcessResponse(BaseModel):
    """Process response model."""
    cases: List[Dict[str, Any]]
    summary: str
    sources: List[str]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "legal_search_agent"
    }


@app.post("/process", response_model=ProcessResponse)
async def process_query(request: ProcessRequest):
    """
    Process case retrieval query.
    Returns cases with full metadata.
    """
    logger.info(f"Processing case retrieval query: {request.query}")
    
    try:
        # Extract main topic from query
        main_topic = request.query
        if request.topics:
            main_topic = " ".join(request.topics)
        
        # Step 1: Query data source for structured case data
        jurisdiction = request.jurisdictions[0] if request.jurisdictions else None
        cases = data_client.search_cases(
            topic=main_topic,
            jurisdiction=jurisdiction,
            limit=request.limit
        )
        
        # Step 2: Enhance with semantic search from Vertex AI
        semantic_results = vertex_client.semantic_search(
            query=request.query,
            top_k=min(10, request.limit),
            filter_dict={"jurisdiction": jurisdiction} if jurisdiction else None
        )
        
        # Merge semantic results with BigQuery results
        # In production, you'd merge based on case_id and boost semantic matches
        if semantic_results:
            # Add similarity scores to cases that match
            semantic_case_ids = {r["case_id"]: r["similarity_score"] for r in semantic_results}
            for case in cases:
                if case["case_id"] in semantic_case_ids:
                    case["semantic_score"] = semantic_case_ids[case["case_id"]]
        
        # Step 3: Format response
        if not cases:
            summary = f"No cases found for query: {request.query}"
        else:
            summary = f"Found {len(cases)} relevant cases. Top cases by citation count: {', '.join([c['case_title'] for c in cases[:3]])}"
        
        # Collect sources
        sources = []
        for case in cases:
            if case.get("full_text_url"):
                sources.append(case["full_text_url"])
        
        return ProcessResponse(
            cases=cases,
            summary=summary,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing case retrieval: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.search_agent_host,
        port=settings.search_agent_port,
        log_level=settings.log_level.lower()
    )

