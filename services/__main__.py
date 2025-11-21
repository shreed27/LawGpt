"""Main entry point for services - allows running as module."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    service_name = sys.argv[1] if len(sys.argv) > 1 else "main_router"
    
    if service_name == "main_router":
        from services.main_router import app
        import uvicorn
        from config import settings
        uvicorn.run(app, host=settings.router_host, port=settings.router_port)
    elif service_name == "legal_search_agent":
        from services.legal_search_agent import app
        import uvicorn
        from config import settings
        uvicorn.run(app, host=settings.search_agent_host, port=settings.search_agent_port)
    elif service_name == "legal_ai_agent":
        from services.legal_ai_agent import app
        import uvicorn
        from config import settings
        uvicorn.run(app, host=settings.ai_agent_host, port=settings.ai_agent_port)
    else:
        print(f"Unknown service: {service_name}")
        sys.exit(1)

