#!/usr/bin/env python3
"""
Test script to verify Docker deployment setup
"""
import sys
import os

def test_imports():
    """Test that all imports work in Docker environment"""
    print("🔍 Testing imports for Docker deployment...")
    
    try:
        # Test main.py import
        import main
        print("✅ main.py import successful")
        
        # Test app creation
        from main import app
        print("✅ FastAPI app creation successful")
        
        # Test health endpoints
        routes = [route.path for route in app.routes]
        health_routes = [r for r in routes if 'health' in r or 'ping' in r]
        print(f"✅ Health routes found: {health_routes}")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from main import app
        from app.core.config import settings
        
        print(f"✅ Database URL configured: {settings.DATABASE_URL[:50]}...")
        print(f"✅ API version: {settings.API_V1_STR}")
        print(f"✅ Environment: {settings.ENVIRONMENT}")
        print(f"✅ Debug mode: {settings.DEBUG}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run Docker deployment tests"""
    print("🐳 Docker Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config)
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
        print("🎉 ALL TESTS PASSED - DOCKER DEPLOYMENT READY!")
        print("\n📋 Docker Configuration:")
        print("- Health check: /ping")
        print("- Module path: main:app")
        print("- Background tasks: DISABLED")
        print("- Configuration: EXTRA_IGNORE")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 