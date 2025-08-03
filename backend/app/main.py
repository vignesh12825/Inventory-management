from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from datetime import datetime

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine
from app.models import Base
from app.core.background_tasks import background_task_manager

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
    await background_task_manager.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks when the application shuts down"""
    await background_task_manager.stop()

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

@app.get("/api/v1/health")
async def api_health_check():
    """Comprehensive health check for Railway deployment"""
    try:
        # Check if background task manager is running
        background_status = "running" if background_task_manager.is_running else "stopped"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "background_tasks": background_status,
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
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 