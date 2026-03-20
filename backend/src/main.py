"""
Bug Bounty Platform - Main Application
FastAPI Backend Server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api/v1/endpoints import auth, profile, domain, sso, programs, reports, triage, bounty, reputation, notifications, ptaas, code_review, integration, ai_red_teaming, messages, subscription, financial

# Version and metadata
VERSION = "1.0.0"
APP_NAME = "Bug Bounty Platform API"

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Production-grade Bug Bounty and Simulation Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(domain.router, prefix="/api/v1")
app.include_router(sso.router, prefix="/api/v1")
app.include_router(programs.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(triage.router, prefix="/api/v1")
app.include_router(bounty.router, prefix="/api/v1")
app.include_router(reputation.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(ptaas.router, prefix="/api/v1")
app.include_router(code_review.router, prefix="/api/v1")
app.include_router(integration.router, prefix="/api/v1")
app.include_router(ai_red_teaming.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(subscription.router, prefix="/api/v1")
app.include_router(financial.router, prefix="/api/v1")


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": VERSION,
        "environment": "development"
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Bug Bounty Platform API",
        "version": VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Startup Event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 {APP_NAME} v{VERSION} starting...")
    print(f"📚 API Documentation: http://localhost:8001/docs")
    print(f"❤️  Health Check: http://localhost:8001/health")


# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print(f"👋 {APP_NAME} shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
