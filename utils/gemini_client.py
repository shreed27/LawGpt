"""Gemini API client for LLM interactions."""
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GeminiClient:
    """Client for interacting with Gemini models."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
        
        self.model_name = model_name
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            logger.warning(f"Could not initialize Gemini model {model_name}: {e}")
            self.model = None
    
    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response using Gemini model.
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        if not self.model:
            return "Error: Gemini model not initialized. Please check API key configuration."
        
        try:
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            raise
    
    def detect_intent(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Detect user intent and classify query type.
        
        Args:
            query: User query
            
        Returns:
            Intent classification with mode and required agents
        """
        intent_prompt = f"""
        Analyze the following legal query and classify it:
        
        Query: "{query}"
        
        Determine:
        1. Mode: "case_retrieval" (simple case lookup) or "deep_analysis" (complex legal analysis)
        2. Complexity: "low", "medium", or "high"
        3. Required agents: List which agents are needed (case_search, analysis, compliance, drafting)
        4. Jurisdictions: Extract mentioned jurisdictions (India, EU, US, etc.)
        5. Topics: Extract main legal topics
        
        Respond in JSON format:
        {{
            "mode": "case_retrieval" or "deep_analysis",
            "complexity": "low" or "medium" or "high",
            "required_agents": ["case_search", "analysis"],
            "jurisdictions": ["India"],
            "topics": ["privacy", "data protection"]
        }}
        """
        
        try:
            response = self.generate_response(
                intent_prompt,
                temperature=0.3,  # Lower temperature for classification
                max_tokens=500
            )
            
            # Parse JSON response
            import json
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            intent_data = json.loads(response)
            return intent_data
            
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            # Default fallback
            return {
                "mode": "deep_analysis",
                "complexity": "medium",
                "required_agents": ["case_search", "analysis"],
                "jurisdictions": [],
                "topics": []
            }

