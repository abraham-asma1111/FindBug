"""
Simulation Subplatform - Bug Bounty Practice Environment
FREQ-23, FREQ-24, FREQ-25, FREQ-26, FREQ-27, FREQ-28
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints import simulation, challenges, scoring, targets, isolation

# Version and metadata
VERSION = "1.0.0"
APP_NAME = "Bug Bounty Simulation Platform"

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Bug Bounty Practice Environment - Isolated Simulation Platform",
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
app.include_router(simulation.router, prefix="/api/v1/simulation")
app.include_router(challenges.router, prefix="/api/v1/challenges")
app.include_router(scoring.router, prefix="/api/v1/scoring")
app.include_router(targets.router, prefix="/api/v1/targets")
app.include_router(isolation.router, prefix="/api/v1/isolation")

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
        "message": "Welcome to Bug Bounty Simulation Platform",
        "version": VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# Startup Event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🎯 {APP_NAME} v{VERSION} starting...")
    print("🔒 Isolated simulation environment initializing...")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("🔒 Simulation environment shutting down safely...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
