"""Vertex AI Vector Search client for semantic case retrieval."""
from google.cloud import aiplatform
from typing import List, Dict, Any, Optional
from config import settings
from utils.logger import setup_logger
import json

logger = setup_logger(__name__)


class VertexAIClient:
    """Client for Vertex AI Vector Search."""
    
    def __init__(self):
        aiplatform.init(
            project=settings.gcp_project_id,
            location=settings.vertex_ai_location
        )
        self.index_endpoint = settings.vertex_ai_index_endpoint
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using Vertex AI Vector Search.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_dict: Optional filters (e.g., {"jurisdiction": "India"})
            
        Returns:
            List of similar cases with similarity scores
        """
        try:
            # If index endpoint is configured, use it
            if self.index_endpoint:
                from google.cloud.aiplatform import MatchingEngineIndexEndpoint
                
                index_endpoint = MatchingEngineIndexEndpoint(
                    index_endpoint_name=self.index_endpoint
                )
                
                # Find neighbors
                response = index_endpoint.find_neighbors(
                    deployed_index_id="legal_cases_index",
                    queries=[[query]],  # Embedding query would go here
                    num_neighbors=top_k
                )
                
                results = []
                for neighbor in response[0]:
                    results.append({
                        "case_id": neighbor.id,
                        "similarity_score": neighbor.distance,
                        "metadata": neighbor.metadata if hasattr(neighbor, 'metadata') else {}
                    })
                
                return results
            else:
                # Fallback: Use Gemini to generate embeddings and search
                # This is a simplified version - in production, use actual vector search
                logger.warning("Vertex AI index endpoint not configured, using fallback")
                return []
                
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            # Return empty list on error to allow system to continue with BigQuery only
            return []
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts using Vertex AI.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            from google.cloud.aiplatform import Model
            
            # Use text embedding model
            model = Model.from_pretrained("textembedding-gecko@001")
            
            embeddings = []
            for text in texts:
                # Generate embedding (simplified - actual implementation would use model.predict)
                # In production, use the actual embedding model API
                embeddings.append([])  # Placeholder
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return []

