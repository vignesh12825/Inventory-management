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

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine
from app.models import Base

# Temporarily disable background tasks to isolate health check issue
# from app.core.background_tasks import background_task_manager

# Note: Database tables are created via init.sql script
# Base.metadata.create_all(bind=engine)  # Commented out to avoid conflicts

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="A comprehensive Inventory Management System API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Start background tasks when the application starts"""
    # Temporarily disabled to isolate health check issue
    # try:
    #     await background_task_manager.start()
    # except Exception as e:
    #     print(f"Warning: Background task manager failed to start: {e}")
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks when the application shuts down"""
    # Temporarily disabled to isolate health check issue
    # try:
    #     await background_task_manager.stop()
    # except Exception as e:
    #     print(f"Warning: Background task manager failed to stop: {e}")
    pass

@app.get("/")
async def root():
    return {
        "message": "Welcome to Inventory Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.get("/ping")
async def ping():
    """Minimal health check for Railway - no dependencies"""
    return {"status": "ok", "message": "pong"}

@app.get("/api/v1/health")
async def api_health_check():
    """Simple health check for Railway deployment"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "message": "Inventory Management System API is running"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "Service is experiencing issues"
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 