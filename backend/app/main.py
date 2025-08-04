from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from datetime import datetime
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine
from app.models import Base

# Temporarily disable background tasks to isolate health check issue
# from app.core.background_tasks import background_task_manager

# Create database tables if they don't exist
try:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")
    # Continue without tables for now

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
    """Basic health check - always returns healthy for Railway"""
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

@app.get("/api/v1/debug/db")
async def debug_database():
    """Debug database connection"""
    try:
        from app.core.config import settings
        from app.core.database import engine
        from sqlalchemy import text
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            
        return {
            "database_url": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
            "database_name": db_info[0] if db_info else "unknown",
            "database_user": db_info[1] if db_info else "unknown",
            "status": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database_url": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL
        }

@app.get("/api/v1/debug/env")
async def debug_environment():
    """Debug environment variables"""
    import os
    return {
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "database_url_length": len(os.getenv("DATABASE_URL", "")),
        "database_url_preview": os.getenv("DATABASE_URL", "")[:50] + "..." if len(os.getenv("DATABASE_URL", "")) > 50 else os.getenv("DATABASE_URL", ""),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "debug": os.getenv("DEBUG", "unknown")
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 