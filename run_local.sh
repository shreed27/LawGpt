#!/bin/bash
# Script to run all services locally for development

echo "Starting Legal Search & Legal-ai services locally..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create one from .env.example"
fi

# Start services in background
echo "Starting Main Router on port 8000..."
python -m services.main_router &
ROUTER_PID=$!

sleep 2

echo "Starting Legal Search Agent on port 8001..."
python -m services.legal_search_agent &
SEARCH_PID=$!

sleep 2

echo "Starting Legal-ai Agent on port 8002..."
python -m services.legal_ai_agent &
AI_PID=$!

echo ""
echo "All services started!"
echo "Main Router: http://localhost:8000"
echo "Legal Search Agent: http://localhost:8001"
echo "Legal-ai Agent: http://localhost:8002"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $ROUTER_PID $SEARCH_PID $AI_PID; exit" INT
wait

