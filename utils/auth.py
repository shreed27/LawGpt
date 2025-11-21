"""Authentication utilities."""
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> bool:
    """Verify API key."""
    if not settings.api_key:
        # No API key configured, allow all (for development)
        return True
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide X-API-Key header."
        )
    
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return True

