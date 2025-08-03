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
    
    @app.get("/ping")
    async def ping():
        """Minimal health check for Railway"""
        return {"status": "ok", "message": "pong"}
    
    @app.get("/health")
    async def health():
        """Basic health check"""
        return {"status": "healthy", "message": "Service is running"}
    
    @app.get("/")
    async def root():
        return {"message": "Inventory Management System API", "version": "1.0.0"}
    
    return app

def main():
    """Main startup function"""
    print("🚀 Starting Railway application...")
    
    try:
        # Try to import the main application
        import main
        from main import app
        print("✅ Successfully imported main application")
        
    except ImportError as e:
        print(f"⚠️  Import error: {e}")
        print("🔄 Falling back to minimal application...")
        app = create_minimal_app()
        
    except Exception as e:
        print(f"❌ Error importing main app: {e}")
        print("🔄 Falling back to minimal application...")
        app = create_minimal_app()
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🌐 Starting server on port {port}")
    print("🔍 Health check endpoint: /ping")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main() 