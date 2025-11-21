"""Main MCP Router - Central intelligence for routing and synthesis."""
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import asyncio
from config import settings
from utils.logger import setup_logger
from utils.gemini_client import GeminiClient
from utils.auth import verify_api_key
from utils.keyword_extractor import extract_keywords
from utils.language_detector import detect_hinglish_preference
from utils.firestore_client import FirestoreClient

logger = setup_logger(__name__)

app = FastAPI(title="Legal Search & Legal-ai Main Router")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client for intent detection
gemini_client = GeminiClient(model_name=settings.gemini_model_flash)

# Initialize Firestore client for acts collection (existing backend)
firestore_client = FirestoreClient()


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str
    mode: Optional[str] = None  # "legal_search" or "legal_ai" - auto-detected if not provided
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    mode: str
    cases: Optional[List[Dict[str, Any]]] = None
    analysis: Optional[Dict[str, Any]] = None
    sources: List[str]
    diagnostics: Dict[str, Any]


class SearchLawRequest(BaseModel):
    """Search law request model."""
    query: str
    limit: Optional[int] = 20


class SearchLawResponse(BaseModel):
    """Search law response model."""
    query: str
    keywords: List[str]
    results: List[Dict[str, Any]]
    count: int
    error: Optional[str] = None


class ExplainLawRequest(BaseModel):
    """Explain law request model."""
    query: str
    act_id: Optional[str] = None


class ExplainLawResponse(BaseModel):
    """Explain law response model."""
    query: str
    language: str
    explanation: str
    act_reference: Optional[str] = None
    error: Optional[str] = None


async def call_agent_service(
    url: str,
    payload: Dict[str, Any],
    timeout: float = 30.0
) -> Dict[str, Any]:
    """Call an agent service asynchronously."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{url}/process", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout calling agent service: {url}")
        raise HTTPException(status_code=504, detail=f"Agent service timeout: {url}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error calling agent service {url}: {e}")
        raise HTTPException(status_code=502, detail=f"Agent service error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error calling agent {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")




@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "main_router",
        "agents": {
            "legal_search": settings.legal_search_agent_url,
            "legal_ai": settings.legal_ai_agent_url
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    _: bool = Security(verify_api_key)
):
    """
    Main chat endpoint - routes to appropriate agents and synthesizes response.
    """
    logger.info(f"Received chat request: mode={request.mode}, query_length={len(request.query)}")
    
    # Step 1: Intent Detection
    if request.mode:
        # User explicitly specified mode
        mode = request.mode
        intent_data = {
            "mode": mode,
            "complexity": "medium",
            "required_agents": ["case_search"] if mode == "legal_search" else ["case_search", "analysis"],
            "jurisdictions": [],
            "topics": []
        }
    else:
        # Auto-detect intent using Gemini
        intent_data = gemini_client.detect_intent(request.query)
        mode = "legal_search" if intent_data["mode"] == "case_retrieval" else "legal_ai"
    
    logger.info(f"Detected intent: {intent_data}")
    
    # Step 2: Route to appropriate agents
    agent_tasks = []
    
    if mode == "legal_search" or "case_search" in intent_data.get("required_agents", []):
        # Call Legal Search Agent
        search_payload = {
            "query": request.query,
            "topics": intent_data.get("topics", []),
            "jurisdictions": intent_data.get("jurisdictions", []),
            "limit": 20
        }
        agent_tasks.append(
            ("legal_search", call_agent_service(
                settings.legal_search_agent_url,
                search_payload
            ))
        )
    
    if mode == "legal_ai" or "analysis" in intent_data.get("required_agents", []):
        # Call Legal-ai Analysis Agent
        analysis_payload = {
            "query": request.query,
            "topics": intent_data.get("topics", []),
            "jurisdictions": intent_data.get("jurisdictions", []),
            "complexity": intent_data.get("complexity", "medium"),
            "context": request.context or {}
        }
        agent_tasks.append(
            ("legal_ai", call_agent_service(
                settings.legal_ai_agent_url,
                analysis_payload
            ))
        )
    
    # Step 3: Execute agents in parallel
    results = {}
    if agent_tasks:
        task_results = await asyncio.gather(
            *[task for _, task in agent_tasks],
            return_exceptions=True
        )
        
        for (agent_name, _), result in zip(agent_tasks, task_results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_name} failed: {result}")
                results[agent_name] = {"error": str(result)}
            else:
                results[agent_name] = result
    
    # Step 4: Synthesize response
    if mode == "legal_search":
        # Legal Search mode - return cases directly
        search_result = results.get("legal_search", {})
        cases = search_result.get("cases", [])
        summary = search_result.get("summary", "Found relevant cases.")
        
        return ChatResponse(
            response=summary,
            mode="legal_search",
            cases=cases,
            sources=search_result.get("sources", []),
            diagnostics={
                "intent": intent_data,
                "agents_called": ["legal_search"],
                "cases_found": len(cases)
            }
        )
    
    else:
        # Legal-ai mode - synthesize comprehensive analysis
        search_result = results.get("legal_search", {})
        analysis_result = results.get("legal_ai", {})
        
        # Merge results
        cases = search_result.get("cases", [])
        analysis = analysis_result.get("analysis", {})
        summary = analysis_result.get("summary", "Analysis completed.")
        
        # Combine sources
        all_sources = search_result.get("sources", []) + analysis_result.get("sources", [])
        
        return ChatResponse(
            response=summary,
            mode="legal_ai",
            cases=cases,
            analysis=analysis,
            sources=list(set(all_sources)),  # Remove duplicates
            diagnostics={
                "intent": intent_data,
                "agents_called": list(results.keys()),
                "cases_found": len(cases),
                "analysis_depth": analysis_result.get("depth", "standard")
            }
        )


@app.post("/search-law", response_model=SearchLawResponse)
async def search_law(
    request: SearchLawRequest,
    _: bool = Security(verify_api_key)
):
    """
    Search legal acts using keyword matching with legal stopwords filtering.
    Matches existing /search-law endpoint functionality.
    """
    logger.info(f"Search law request: {request.query}")
    
    try:
        # Extract keywords (filters legal stopwords)
        keywords = extract_keywords(request.query, top_n=5)
        
        if not keywords:
            # If no keywords extracted, use original query words
            keywords = [word for word in request.query.lower().split() if len(word) > 3][:5]
        
        # Search Firestore "acts" collection
        acts = firestore_client.search_acts(
            keywords=keywords,
            limit=request.limit or 20,
            max_scan=2000  # Your existing limit
        )
        
        return SearchLawResponse(
            query=request.query,
            keywords=keywords,
            results=acts,
            count=len(acts)
        )
        
    except Exception as e:
        logger.error(f"Error in search-law: {str(e)}")
        # Fallback: return empty results (works even when Firestore is down)
        return SearchLawResponse(
            query=request.query,
            keywords=[],
            results=[],
            count=0,
            error="Search temporarily unavailable. Please try again later."
        )


@app.post("/explain-law", response_model=ExplainLawResponse)
async def explain_law(
    request: ExplainLawRequest,
    _: bool = Security(verify_api_key)
):
    """
    AI explanation of legal concepts.
    Supports Hinglish and English based on user preference.
    Uses conversational tone with "aap/tum" for Hinglish.
    """
    logger.info(f"Explain law request: {request.query}, language detection...")
    
    try:
        # Detect language preference (Hinglish vs English)
        language = detect_hinglish_preference(request.query)
        logger.info(f"Detected language preference: {language}")
        
        # Get act data if act_id provided
        act_data = None
        if request.act_id:
            act_data = firestore_client.get_act_by_id(request.act_id)
        
        # Build prompt based on language preference
        if language == "hinglish":
            system_prompt = """You are a helpful legal assistant. Explain legal concepts in Hinglish (Hindi-English mix) with a conversational, friendly tone. Use "aap" or "tum" naturally. Be easy to understand and helpful. Keep explanations clear and practical."""
            user_prompt = f"Kya aap iske baare mein explain kar sakte hain: {request.query}"
        else:
            system_prompt = """You are a helpful legal assistant. Explain legal concepts clearly and professionally in English. Be precise, accurate, and easy to understand."""
            user_prompt = f"Explain: {request.query}"
        
        # Add act context if available
        if act_data:
            act_name = act_data.get("act_name", "")
            act_text = act_data.get("text", "")[:500]  # Limit text length
            
            if language == "hinglish":
                user_prompt += f"\n\nRelevant Act: {act_name}\nText: {act_text}"
            else:
                user_prompt += f"\n\nRelevant Act: {act_name}\nText: {act_text}"
        
        # Use Gemini for explanation
        explanation = gemini_client.generate_response(
            prompt=user_prompt,
            system_instruction=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        return ExplainLawResponse(
            query=request.query,
            language=language,
            explanation=explanation,
            act_reference=act_data.get("act_name") if act_data else None
        )
        
    except Exception as e:
        logger.error(f"Error in explain-law: {str(e)}")
        # Fallback response
        fallback_msg = "I'm having trouble explaining this right now. Please try again later."
        if detect_hinglish_preference(request.query) == "hinglish":
            fallback_msg = "Mujhe iska explanation dene mein thoda problem ho raha hai. Kripya thodi der baad try karein."
        
        return ExplainLawResponse(
            query=request.query,
            language="english",
            explanation=fallback_msg,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.router_host,
        port=settings.router_port,
        log_level=settings.log_level.lower()
    )

