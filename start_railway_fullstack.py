#!/usr/bin/env python3
"""
Railway Full-Stack Startup Script
Serves both frontend and backend together
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import uvicorn
        import fastapi
        print("✅ Backend dependencies available")
    except ImportError as e:
        print(f"❌ Backend dependency missing: {e}")
        return False
    
    # Check if frontend build exists
    frontend_build = Path("frontend/build")
    if frontend_build.exists():
        print("✅ Frontend build found")
    else:
        print("❌ Frontend build not found")
        return False
    
    return True

def start_nginx():
    """Start nginx to serve frontend static files"""
    try:
        # Start nginx in background
        subprocess.Popen([
            "nginx", "-g", "daemon off;"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Nginx started for frontend")
        return True
    except Exception as e:
        print(f"❌ Failed to start nginx: {e}")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    try:
        # Get port from environment or use default
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")
        
        print(f"🚀 Starting backend server on {host}:{port}")
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", host, 
            "--port", str(port),
            "--log-level", "info"
        ])
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🚀 Starting Inventory Management System (Full-Stack)")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependencies check failed")
        sys.exit(1)
    
    # Start nginx for frontend
    if not start_nginx():
        print("❌ Failed to start nginx")
        sys.exit(1)
    
    # Wait a moment for nginx to start
    time.sleep(2)
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    main() 