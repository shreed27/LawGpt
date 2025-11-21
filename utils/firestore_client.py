"""Firestore client for querying legal data."""
from google.cloud import firestore
from typing import List, Dict, Any, Optional
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FirestoreClient:
    """Client for interacting with Firestore legal data."""
    
    def __init__(self):
        self.db = firestore.Client(project=settings.gcp_project_id)
        self.cases_collection = "legal_cases"
        self.statutes_collection = "statutes"
        self.acts_collection = getattr(settings, 'firestore_acts_collection', 'acts')
    
    def search_cases(
        self,
        topic: str,
        jurisdiction: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for legal cases by topic in Firestore.
        
        Args:
            topic: Search topic/keywords
            jurisdiction: Optional jurisdiction filter
            limit: Maximum number of results
            
        Returns:
            List of case records with metadata
        """
        try:
            cases_ref = self.db.collection(self.cases_collection)
            
            # Build query
            query = cases_ref
            
            # Filter by jurisdiction if provided
            if jurisdiction:
                query = query.where("jurisdiction", "==", jurisdiction)
            
            # Get all documents (Firestore doesn't support full-text search natively)
            # We'll filter in memory for topic matching
            docs = query.stream()
            
            cases = []
            topic_lower = topic.lower()
            
            for doc in docs:
                if len(cases) >= limit:
                    break
                
                case_data = doc.to_dict()
                case_id = doc.id
                
                # Check if topic matches in title, summary, articles, or sections
                title = case_data.get("case_title", "").lower()
                summary = case_data.get("summary", "").lower()
                articles = case_data.get("articles", "").lower()
                sections = case_data.get("sections", "").lower()
                
                if (topic_lower in title or 
                    topic_lower in summary or 
                    topic_lower in articles or 
                    topic_lower in sections):
                    
                    # Format case data
                    case = {
                        "case_id": case_id,
                        "case_title": case_data.get("case_title", ""),
                        "court": case_data.get("court", ""),
                        "year": case_data.get("year"),
                        "citation_count": case_data.get("citation_count", 0),
                        "articles": case_data.get("articles", "").split(",") if isinstance(case_data.get("articles"), str) else case_data.get("articles", []),
                        "sections": case_data.get("sections", "").split(",") if isinstance(case_data.get("sections"), str) else case_data.get("sections", []),
                        "summary": case_data.get("summary", ""),
                        "full_text_url": case_data.get("full_text_url", ""),
                        "jurisdiction": case_data.get("jurisdiction", ""),
                        "case_type": case_data.get("case_type", ""),
                        "parties": case_data.get("parties", ""),
                        "judgment_date": str(case_data.get("judgment_date")) if case_data.get("judgment_date") else None
                    }
                    
                    cases.append(case)
            
            # Sort by citation count and year
            cases.sort(key=lambda x: (x.get("citation_count", 0), x.get("year", 0)), reverse=True)
            
            logger.info(f"Retrieved {len(cases)} cases from Firestore for topic: {topic}")
            return cases[:limit]
            
        except Exception as e:
            logger.error(f"Error querying Firestore: {str(e)}")
            raise
    
    def get_statutes(
        self,
        topic: str,
        jurisdiction: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for statutes/acts by topic in Firestore.
        
        Args:
            topic: Search topic/keywords
            jurisdiction: Optional jurisdiction filter
            limit: Maximum number of results
            
        Returns:
            List of statute records
        """
        try:
            statutes_ref = self.db.collection(self.statutes_collection)
            
            # Build query
            query = statutes_ref
            
            if jurisdiction:
                query = query.where("jurisdiction", "==", jurisdiction)
            
            docs = query.stream()
            
            statutes = []
            topic_lower = topic.lower()
            
            for doc in docs:
                if len(statutes) >= limit:
                    break
                
                statute_data = doc.to_dict()
                statute_id = doc.id
                
                # Check if topic matches
                act_name = statute_data.get("act_name", "").lower()
                section_text = statute_data.get("section_text", "").lower()
                section_title = statute_data.get("section_title", "").lower()
                
                if (topic_lower in act_name or 
                    topic_lower in section_text or 
                    topic_lower in section_title):
                    
                    statute = {
                        "statute_id": statute_id,
                        "act_name": statute_data.get("act_name", ""),
                        "section_number": statute_data.get("section_number", ""),
                        "section_title": statute_data.get("section_title", ""),
                        "section_text": statute_data.get("section_text", ""),
                        "jurisdiction": statute_data.get("jurisdiction", ""),
                        "effective_date": str(statute_data.get("effective_date")) if statute_data.get("effective_date") else None,
                        "related_cases": statute_data.get("related_cases", "").split(",") if isinstance(statute_data.get("related_cases"), str) else statute_data.get("related_cases", []),
                        "amendments": statute_data.get("amendments", "").split(",") if isinstance(statute_data.get("amendments"), str) else statute_data.get("amendments", [])
                    }
                    
                    statutes.append(statute)
            
            logger.info(f"Retrieved {len(statutes)} statutes from Firestore for topic: {topic}")
            return statutes[:limit]
            
        except Exception as e:
            logger.error(f"Error querying Firestore for statutes: {str(e)}")
            raise
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get full case details by case ID."""
        try:
            doc_ref = self.db.collection(self.cases_collection).document(case_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error fetching case by ID from Firestore: {str(e)}")
            raise
    
    def get_all_cases(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all cases (useful for migration or bulk operations)."""
        try:
            cases_ref = self.db.collection(self.cases_collection)
            docs = cases_ref.limit(limit).stream()
            
            cases = []
            for doc in docs:
                case_data = doc.to_dict()
                case_data["case_id"] = doc.id
                cases.append(case_data)
            
            return cases
            
        except Exception as e:
            logger.error(f"Error fetching all cases: {str(e)}")
            raise
    
    def search_acts(
        self,
        keywords: List[str],
        limit: int = 20,
        max_scan: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Search for legal acts by keywords.
        Matches existing /search-law functionality.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of results to return (default: 20)
            max_scan: Maximum documents to scan (default: 2000)
            
        Returns:
            List of act records matching keywords
        """
        try:
            acts_ref = self.db.collection(self.acts_collection)
            docs = acts_ref.limit(max_scan).stream()
            
            acts = []
            keywords_lower = [kw.lower() for kw in keywords]
            
            for doc in docs:
                if len(acts) >= limit:
                    break
                
                act_data = doc.to_dict()
                act_id = doc.id
                
                # Check if keywords match in act_name, title, or text
                act_name = act_data.get("act_name", "").lower()
                title = act_data.get("title", "").lower()
                text = act_data.get("text", "").lower()
                
                # Match if any keyword is found in any field
                matches = False
                match_score = 0
                
                for keyword in keywords_lower:
                    if keyword in act_name:
                        matches = True
                        match_score += 3  # Higher weight for act_name
                    if keyword in title:
                        matches = True
                        match_score += 2  # Medium weight for title
                    if keyword in text:
                        matches = True
                        match_score += 1  # Lower weight for text
                
                if matches:
                    act = {
                        "act_id": act_id,
                        "act_name": act_data.get("act_name", ""),
                        "title": act_data.get("title", ""),
                        "page_no": act_data.get("page_no", ""),
                        "text": act_data.get("text", ""),
                        "match_score": match_score
                    }
                    acts.append(act)
            
            # Sort by match score (higher is better)
            acts.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            
            logger.info(f"Retrieved {len(acts)} acts from Firestore for keywords: {keywords}")
            return acts[:limit]
            
        except Exception as e:
            logger.error(f"Error searching acts: {str(e)}")
            # Return empty list on error (fallback behavior)
            return []
    
    def get_act_by_id(self, act_id: str) -> Optional[Dict[str, Any]]:
        """Get act details by act ID."""
        try:
            doc_ref = self.db.collection(self.acts_collection).document(act_id)
            doc = doc_ref.get()
            
            if doc.exists:
                act_data = doc.to_dict()
                act_data["act_id"] = doc.id
                return act_data
            return None
            
        except Exception as e:
            logger.error(f"Error fetching act by ID from Firestore: {str(e)}")
            return None

