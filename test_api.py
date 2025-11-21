"""Test script for the Legal Search & Legal-ai API."""
import requests
import json

ROUTER_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    response = requests.get(f"{ROUTER_URL}/health")
    print("Health Check:", response.json())
    print()

def test_legal_search():
    """Test Legal Search mode."""
    payload = {
        "query": "right to privacy data protection cases",
        "mode": "legal_search"
    }
    
    response = requests.post(
        f"{ROUTER_URL}/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print("Legal Search Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_legal_ai():
    """Test Legal-ai Analysis mode."""
    payload = {
        "query": "Am I legally bound to not buy land from an Adivasi in MP?",
        "mode": "legal_ai"
    }
    
    response = requests.post(
        f"{ROUTER_URL}/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print("Legal-ai Analysis Response:")
    result = response.json()
    print(f"Summary: {result.get('response', 'N/A')[:200]}...")
    print(f"Mode: {result.get('mode', 'N/A')}")
    print(f"Cases found: {len(result.get('cases', []))}")
    print(f"Sources: {len(result.get('sources', []))}")
    print()

if __name__ == "__main__":
    print("Testing Legal Search & Legal-ai API\n")
    print("=" * 50)
    
    try:
        test_health()
        test_legal_search()
        test_legal_ai()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to services. Make sure they are running.")
        print("Run: bash run_local.sh")
    except Exception as e:
        print(f"Error: {e}")

