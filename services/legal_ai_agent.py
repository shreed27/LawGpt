"""Legal-ai Analysis Agent - Deep legal analysis service."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from config import settings
from utils.logger import setup_logger
from utils.bigquery_client import BigQueryClient
from utils.firestore_client import FirestoreClient
from utils.vertex_ai_client import VertexAIClient
from utils.gemini_client import GeminiClient
import json

logger = setup_logger(__name__)

app = FastAPI(title="Legal-ai Analysis Agent")

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
gemini_client = GeminiClient(model_name=settings.gemini_model_pro)


class ProcessRequest(BaseModel):
    """Process request model."""
    query: str
    topics: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    complexity: str = "medium"
    context: Optional[Dict[str, Any]] = None


class ProcessResponse(BaseModel):
    """Process response model."""
    analysis: Dict[str, Any]
    summary: str
    sources: List[str]
    depth: str


def build_analysis_prompt(
    query: str,
    cases: List[Dict[str, Any]],
    statutes: List[Dict[str, Any]],
    jurisdictions: List[str],
    complexity: str
) -> str:
    """Build comprehensive analysis prompt for Gemini Pro."""
    
    # Format cases
    cases_text = ""
    for i, case in enumerate(cases[:15], 1):  # Limit to top 15 cases
        cases_text += f"""
Case {i}: {case.get('case_title', 'N/A')}
Court: {case.get('court', 'N/A')}
Year: {case.get('year', 'N/A')}
Citations: {case.get('citation_count', 0)}
Articles: {', '.join(case.get('articles', []))}
Sections: {', '.join(case.get('sections', []))}
Summary: {case.get('summary', 'N/A')[:200]}...
"""
    
    # Format statutes
    statutes_text = ""
    for i, statute in enumerate(statutes[:10], 1):
        statutes_text += f"""
Statute {i}: {statute.get('act_name', 'N/A')} - Section {statute.get('section_number', 'N/A')}
Title: {statute.get('section_title', 'N/A')}
Text: {statute.get('section_text', 'N/A')[:300]}...
Jurisdiction: {statute.get('jurisdiction', 'N/A')}
"""
    
    system_instruction = """You are Legal-ai, an emotionless, highly analytical legal assistant used by judges and senior lawyers. 
Your responses must be exhaustive, cite every legal basis, and provide balanced conclusions.

You must analyze every aspect of the legal question with:
1. Complete factual analysis
2. All applicable laws, articles, sections, and statutes
3. Comparative case law analysis
4. Multi-jurisdictional perspective (if applicable)
5. Legal test applications (proportionality, strict scrutiny, etc.)
6. Risk assessment
7. Practical implications
8. Balanced conclusion with reasoning

Be thorough, precise, and leave no legal angle unexplored. This is for real-world legal practice."""

    prompt = f"""
{system_instruction}

USER QUERY: {query}

RELEVANT JURISDICTIONS: {', '.join(jurisdictions) if jurisdictions else 'Not specified - analyze all applicable'}

COMPLEXITY LEVEL: {complexity.upper()}

RELEVANT CASES FOUND:
{cases_text}

RELEVANT STATUTES:
{statutes_text}

Provide a comprehensive legal analysis in the following structured format:

## EXECUTIVE SUMMARY
[2-3 sentence overview of legal posture]

## FACTS & ASSUMPTIONS
[Clarify what facts are known and what assumptions are being made]

## ISSUES PRESENTED
[Enumerate all legal questions that need to be addressed]

## APPLICABLE LAW
### Primary Legislation
[List all relevant acts, sections, articles with full citations]

### Secondary Legislation & Regulations
[Subordinate legislation, rules, circulars]

### Constitutional Provisions
[If applicable - articles, fundamental rights, etc.]

### International Law
[If applicable - treaties, conventions, cross-border implications]

## COMPARATIVE CASE ANALYSIS
[For each relevant case, explain:
- How it applies to the current situation
- Precedential value
- Distinguishing factors
- Citation count and authority]

## DETAILED LEGAL ANALYSIS
### Issue 1: [First legal question]
[Apply relevant legal tests, analyze facts, cite authorities]

### Issue 2: [Second legal question]
[Continue for all issues]

## MULTI-JURISDICTIONAL PERSPECTIVE
[If multiple jurisdictions are involved, compare approaches]

## LEGAL TESTS APPLIED
[Explicitly state which tests are being applied (proportionality, legitimate aim, etc.) and how facts satisfy/fail each prong]

## RISK ASSESSMENT
[Legal risks, regulatory risks, practical risks with severity levels]

## PRACTICAL IMPLICATIONS
[Compliance requirements, procedural steps, deadlines, enforcement likelihood]

## REMEDIES & RECOMMENDATIONS
[Available remedies, recommended actions, mitigation strategies]

## CONCLUSION
[Balanced conclusion with clear reasoning, acknowledging uncertainties if any]

## SOURCES CITED
[Complete list of all cases, statutes, articles referenced]
"""
    
    return prompt


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "legal_ai_agent"
    }


@app.post("/process", response_model=ProcessResponse)
async def process_query(request: ProcessRequest):
    """
    Process deep legal analysis query.
    Returns comprehensive legal analysis.
    """
    logger.info(f"Processing legal analysis query: {request.query}")
    
    try:
        # Step 1: Gather context from BigQuery
        main_topic = request.query
        if request.topics:
            main_topic = " ".join(request.topics)
        
        jurisdiction = request.jurisdictions[0] if request.jurisdictions else None
        
        # Get cases
        cases = data_client.search_cases(
            topic=main_topic,
            jurisdiction=jurisdiction,
            limit=20  # More cases for deep analysis
        )
        
        # Get statutes
        statutes = data_client.get_statutes(
            topic=main_topic,
            jurisdiction=jurisdiction,
            limit=15
        )
        
        # Step 2: Enhance with semantic search
        semantic_results = vertex_client.semantic_search(
            query=request.query,
            top_k=15
        )
        
        # Step 3: Build comprehensive prompt
        jurisdictions_list = request.jurisdictions or []
        if not jurisdictions_list and jurisdiction:
            jurisdictions_list = [jurisdiction]
        
        prompt = build_analysis_prompt(
            query=request.query,
            cases=cases,
            statutes=statutes,
            jurisdictions=jurisdictions_list,
            complexity=request.complexity
        )
        
        # Step 4: Generate analysis with Gemini Pro
        logger.info("Generating comprehensive legal analysis with Gemini Pro...")
        analysis_text = gemini_client.generate_response(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for analytical precision
            max_tokens=8000  # Allow for comprehensive responses
        )
        
        # Step 5: Structure the analysis
        # In production, you might parse the structured response or use function calling
        analysis = {
            "full_analysis": analysis_text,
            "cases_referenced": len(cases),
            "statutes_referenced": len(statutes),
            "jurisdictions_analyzed": jurisdictions_list,
            "complexity": request.complexity
        }
        
        # Extract summary (first paragraph or executive summary)
        summary = analysis_text.split("\n\n")[0] if analysis_text else "Analysis completed."
        if len(summary) > 500:
            summary = summary[:500] + "..."
        
        # Collect sources
        sources = []
        for case in cases:
            if case.get("full_text_url"):
                sources.append(case["full_text_url"])
        for statute in statutes:
            sources.append(f"Statute: {statute.get('act_name')} Section {statute.get('section_number')}")
        
        return ProcessResponse(
            analysis=analysis,
            summary=summary,
            sources=list(set(sources)),
            depth="maximum" if request.complexity == "high" else "standard"
        )
        
    except Exception as e:
        logger.error(f"Error processing legal analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing analysis: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.ai_agent_host,
        port=settings.ai_agent_port,
        log_level=settings.log_level.lower()
    )

