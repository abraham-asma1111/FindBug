#!/usr/bin/env python3
"""
Development server runner
Run this script to start the FastAPI development server
"""

import uvicorn
import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("🚀 Starting Bug Bounty Platform Development Server...")
    print("📚 API Documentation will be available at: http://127.0.0.1:8001/docs")
    print("❤️  Health Check will be available at: http://127.0.0.1:8001/health")
    print("🔄 Auto-reload is enabled for development")
    print("🔒 Server listening on localhost only (127.0.0.1)")
    print("-" * 60)
    
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info",
        reload_dirs=["src"]
    )