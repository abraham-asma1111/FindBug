#!/bin/bash

# Bug Bounty Platform - Development Server Startup Script
# This script starts the FastAPI development server on localhost

echo "🚀 Starting Bug Bounty Platform Development Server..."
echo "📚 API Documentation: http://127.0.0.1:8001/docs"
echo "❤️  Health Check: http://127.0.0.1:8001/health"
echo "🔒 Server listening on localhost only (127.0.0.1:8001)"
echo "🔄 Auto-reload enabled for development"
echo "----------------------------------------"

# Change to backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Start the server
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload