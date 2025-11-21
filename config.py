"""Configuration management for Legal Search & Legal-ai system."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # GCP Configuration
    gcp_project_id: str = ""
    gcp_region: str = "us-central1"
    
    # Data Source Configuration
    data_source: str = "firestore"  # "bigquery" or "firestore"
    
    # BigQuery Configuration
    bigquery_dataset: str = "legal_data"
    bigquery_case_table: str = "legal_cases"
    bigquery_statute_table: str = "statutes"
    
    # Firestore Configuration
    firestore_cases_collection: str = "legal_cases"
    firestore_statutes_collection: str = "statutes"
    firestore_acts_collection: str = "acts"  # For existing backend integration
    
    # Vertex AI Configuration
    vertex_ai_location: str = "us-central1"
    vertex_ai_index_endpoint: Optional[str] = None
    
    # Gemini API Configuration
    gemini_api_key: Optional[str] = None
    gemini_model_flash: str = "gemini-1.5-flash"
    gemini_model_pro: str = "gemini-1.5-pro"
    
    # Service URLs
    legal_search_agent_url: str = "http://localhost:8001"
    legal_ai_agent_url: str = "http://localhost:8002"
    
    # Authentication
    api_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    # Router Configuration
    router_port: int = 8000
    router_host: str = "0.0.0.0"
    
    # Agent Configuration
    search_agent_port: int = 8001
    search_agent_host: str = "0.0.0.0"
    ai_agent_port: int = 8002
    ai_agent_host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

