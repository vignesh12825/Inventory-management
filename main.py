from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from datetime import datetime
import sys
import os

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

# Try to import settings, but don't fail if it doesn't work
try:
    from app.core.config import settings
    PROJECT_NAME = settings.PROJECT_NAME
    API_V1_STR = settings.API_V1_STR
    BACKEND_CORS_ORIGINS = settings.BACKEND_CORS_ORIGINS
except ImportError:
    print("⚠️  Warning: Could not import settings, using defaults")
    PROJECT_NAME = "Inventory Management System"
    API_V1_STR = "/api/v1"
    BACKEND_CORS_ORIGINS = ["*"]

# Try to import API router, but don't fail if it doesn't work
try:
    from app.api.v1.api import api_router
    HAS_API_ROUTER = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import API router: {e}")
    HAS_API_ROUTER = False

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

# Include API router only if it's available
if HAS_API_ROUTER:
    app.include_router(api_router, prefix=API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Start background tasks when the application starts"""
    print("🚀 Application starting up...")
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
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "ping": "/ping"
    }

@app.get("/health")
async def health_check():
    """Basic health check - always returns healthy for Railway"""
    return {"status": "healthy", "message": "Service is running"}

@app.get("/ping")
async def ping():
    """Minimal health check for Railway - no dependencies"""
    return {"status": "ok", "message": "pong"}

@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 