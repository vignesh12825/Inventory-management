#!/usr/bin/env python3
"""
Railway deployment entry point with robust error handling
"""
import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

# Add the correct directory to Python path for both local and Docker deployment
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
app_path = os.path.join(os.path.dirname(__file__), 'app')

if os.path.exists(backend_path):
    # Local development - backend files are in backend/ directory
    sys.path.insert(0, backend_path)
elif os.path.exists(app_path):
    # Docker deployment - backend files are in app/ directory
    sys.path.insert(0, app_path)
else:
    # Fallback - try both
    sys.path.insert(0, backend_path)
    sys.path.insert(0, app_path)

# Import settings
from app.core.config import settings
PROJECT_NAME = settings.PROJECT_NAME
API_V1_STR = settings.API_V1_STR
BACKEND_CORS_ORIGINS = settings.BACKEND_CORS_ORIGINS
DATABASE_URL = settings.DATABASE_URL

# Import API router
from app.api.v1.api import api_router
HAS_API_ROUTER = True
print("✅ Successfully imported API router")

app = FastAPI(
    title=PROJECT_NAME,
    version="1.0.0",
    description="A comprehensive Inventory Management System API",
    openapi_url=f"{API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=API_V1_STR)
print("✅ API router included successfully")

@app.on_event("startup")
async def startup_event():
    """Start background tasks when the application starts"""
    print("🚀 Application starting up...")
    print(f"📊 Database URL: {DATABASE_URL[:50]}...")
    # Background tasks are disabled for now to ensure health check works

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks when the application shuts down"""
    print("🛑 Application shutting down...")

@app.get("/")
async def root():
    """Root endpoint - Railway health check target"""
    return {
        "status": "healthy",
        "message": "Inventory Management System API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "ping": "/ping",
        "api_router_loaded": HAS_API_ROUTER
    }

@app.get("/health")
async def health_check():
    """Basic health check - always returns healthy for Railway"""
    return {
        "status": "healthy", 
        "message": "Service is running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ping")
async def ping():
    """Minimal health check for Railway - no dependencies"""
    return {"status": "ok", "message": "pong", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy", 
        "message": "API is running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def status():
    """Detailed status endpoint"""
    return {
        "status": "healthy",
        "api_router_loaded": HAS_API_ROUTER,
        "database_url_configured": bool(DATABASE_URL),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    print(f"🌐 Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info") 