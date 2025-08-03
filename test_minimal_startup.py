#!/usr/bin/env python3
"""
Minimal startup test for Railway deployment
"""
import sys
import os

def test_minimal_app():
    """Test creating a minimal FastAPI app"""
    print("🔍 Testing minimal FastAPI app...")
    
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        # Create minimal app
        app = FastAPI()
        
        @app.get("/ping")
        async def ping():
            return {"status": "ok", "message": "pong"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "message": "Service is running"}
        
        print("✅ Minimal FastAPI app created successfully")
        print("✅ /ping endpoint added")
        print("✅ /health endpoint added")
        
        return True
    except Exception as e:
        print(f"❌ Error creating minimal app: {e}")
        return False

def test_imports():
    """Test basic imports"""
    print("\n🔍 Testing basic imports...")
    
    try:
        import fastapi
        print("✅ FastAPI import successful")
        
        import uvicorn
        print("✅ Uvicorn import successful")
        
        import pydantic
        print("✅ Pydantic import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_railway_config():
    """Test Railway configuration"""
    print("\n🔍 Testing Railway configuration...")
    
    try:
        # Check if we can read the config files
        with open('railway.toml', 'r') as f:
            content = f.read()
            if '/ping' in content:
                print("✅ Root railway.toml uses /ping")
            else:
                print("❌ Root railway.toml doesn't use /ping")
                return False
        
        with open('backend/railway.toml', 'r') as f:
            content = f.read()
            if 'main:app' in content:
                print("✅ Backend railway.toml uses main:app")
            else:
                print("❌ Backend railway.toml doesn't use main:app")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error reading config files: {e}")
        return False

def main():
    """Run minimal startup tests"""
    print("🚀 Minimal Railway Startup Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports Test", test_imports),
        ("Minimal App Test", test_minimal_app),
        ("Railway Config Test", test_railway_config)
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
        print("🎉 ALL TESTS PASSED - MINIMAL STARTUP READY!")
        print("\n📋 Next Steps:")
        print("- Railway should use /ping for health checks")
        print("- Application should start with minimal dependencies")
        print("- All basic imports working")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 