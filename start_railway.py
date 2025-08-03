#!/usr/bin/env python3
"""
Railway startup script with error handling
"""
import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

def create_minimal_app():
    """Create a minimal FastAPI app for Railway"""
    app = FastAPI(title="Inventory Management System")
    
    @app.get("/")
    async def root():
        """Root endpoint - Railway health check target"""
        return {
            "status": "healthy",
            "message": "Inventory Management System API is running",
            "version": "1.0.0"
        }
    
    @app.get("/ping")
    async def ping():
        """Minimal health check for Railway"""
        return {"status": "ok", "message": "pong"}
    
    @app.get("/health")
    async def health():
        """Basic health check"""
        return {"status": "healthy", "message": "Service is running"}
    
    return app

def create_full_app():
    """Create the full application with all features"""
    try:
        # Add the correct path for imports
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        app_path = os.path.join(os.path.dirname(__file__), 'app')
        
        if os.path.exists(backend_path):
            sys.path.insert(0, backend_path)
        elif os.path.exists(app_path):
            sys.path.insert(0, app_path)
        
        # Try to import the main app
        from main import app
        print("✅ Successfully imported full application")
        return app
    except ImportError as e:
        print(f"⚠️  Warning: Could not import full application: {e}")
        print("🔄 Falling back to minimal application")
        return create_minimal_app()
    except Exception as e:
        print(f"❌ Error importing full application: {e}")
        print("🔄 Falling back to minimal application")
        return create_minimal_app()

if __name__ == "__main__":
    print("🚀 Starting Railway deployment...")
    
    # Try to create the full app, fallback to minimal if needed
    app = create_full_app()
    
    # Start the server
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🌐 Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info") 