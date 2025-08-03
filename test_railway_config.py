#!/usr/bin/env python3
"""
Test script to verify Railway configuration
"""
import sys
import os

def test_railway_config():
    """Test Railway configuration files"""
    print("🔍 Testing Railway configuration...")
    
    # Test railway.toml
    try:
        with open('backend/railway.toml', 'r') as f:
            content = f.read()
            if 'main:app' in content:
                print("✅ railway.toml uses correct module path: main:app")
            else:
                print("❌ railway.toml still uses old module path")
                return False
    except Exception as e:
        print(f"❌ Error reading railway.toml: {e}")
        return False
    
    # Test start.sh
    try:
        with open('backend/start.sh', 'r') as f:
            content = f.read()
            if 'main:app' in content:
                print("✅ start.sh uses correct module path: main:app")
            else:
                print("❌ start.sh still uses old module path")
                return False
    except Exception as e:
        print(f"❌ Error reading start.sh: {e}")
        return False
    
    # Test Dockerfile
    try:
        with open('Dockerfile', 'r') as f:
            content = f.read()
            if 'main:app' in content:
                print("✅ Dockerfile uses correct module path: main:app")
            else:
                print("❌ Dockerfile still uses old module path")
                return False
    except Exception as e:
        print(f"❌ Error reading Dockerfile: {e}")
        return False
    
    return True

def test_module_import():
    """Test that the module can be imported correctly"""
    print("\n🔍 Testing module import...")
    
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

def main():
    """Run Railway configuration tests"""
    print("🚂 Railway Configuration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Railway Config Test", test_railway_config),
        ("Module Import Test", test_module_import)
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
        print("🎉 ALL TESTS PASSED - RAILWAY CONFIGURATION READY!")
        print("\n📋 Railway Configuration:")
        print("- Module path: main:app")
        print("- Health check: /ping")
        print("- Start command: python -m uvicorn main:app")
        print("- Docker CMD: main:app")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 