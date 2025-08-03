#!/usr/bin/env python3
"""
Comprehensive deployment test for Railway
"""
import sys
import os
import requests
import time

def test_imports():
    """Test that all imports work without errors"""
    print("🔍 Testing imports...")
    try:
        import app.main
        print("✅ Main app import successful")
        
        from app.core.config import settings
        print("✅ Config import successful")
        
        from app.core.database import engine
        print("✅ Database import successful")
        
        from app.api.v1.api import api_router
        print("✅ API router import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_health_endpoints():
    """Test all health check endpoints"""
    print("\n🔍 Testing health endpoints...")
    
    base_url = "http://localhost:8000"
    endpoints = [
        ("/ping", "Minimal health check"),
        ("/health", "Basic health check"),
        ("/api/v1/health", "API health check")
    ]
    
    all_working = True
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} ({endpoint}) - Status: {response.status_code}")
            else:
                print(f"❌ {description} ({endpoint}) - Status: {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"❌ {description} ({endpoint}) - Error: {e}")
            all_working = False
    
    return all_working

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_application_startup():
    """Test that the application can start without errors"""
    print("\n🔍 Testing application startup...")
    try:
        # Test that we can create the FastAPI app
        from app.main import app
        print("✅ FastAPI app creation successful")
        
        # Test that all routes are registered
        routes = [route.path for route in app.routes]
        health_routes = [r for r in routes if 'health' in r or 'ping' in r]
        print(f"✅ Health routes registered: {health_routes}")
        
        return True
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 Railway Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Application Startup", test_application_startup),
        ("Health Endpoints", test_health_endpoints),
        ("Database Connection", test_database_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - READY FOR RAILWAY DEPLOYMENT!")
        print("\n📋 Railway Configuration:")
        print("- Health check path: /ping")
        print("- Health check timeout: 600 seconds")
        print("- Background tasks: DISABLED (temporarily)")
        print("- Database: Connected to Neon")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 