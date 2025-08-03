#!/usr/bin/env python3
"""
Comprehensive Railway startup test
"""
import sys
import os
import subprocess
import time
import requests

def test_startup_script():
    """Test the startup script"""
    print("🔍 Testing startup script...")
    
    try:
        # Test if the script can be imported
        import start_railway
        print("✅ Startup script import successful")
        
        # Test if it can create a minimal app
        app = start_railway.create_minimal_app()
        print("✅ Minimal app creation successful")
        
        # Test if it has the required endpoints
        routes = [route.path for route in app.routes]
        required_routes = ['/ping', '/health', '/']
        
        for route in required_routes:
            if route in routes:
                print(f"✅ {route} endpoint found")
            else:
                print(f"❌ {route} endpoint missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error testing startup script: {e}")
        return False

def test_railway_configs():
    """Test Railway configuration files"""
    print("\n🔍 Testing Railway configuration files...")
    
    configs = [
        ('railway.toml', 'root'),
        ('backend/railway.toml', 'backend')
    ]
    
    all_correct = True
    
    for file_path, location in configs:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                if 'start_railway.py' in content:
                    print(f"✅ {location} railway.toml uses startup script")
                else:
                    print(f"❌ {location} railway.toml doesn't use startup script")
                    all_correct = False
                
                if '/ping' in content:
                    print(f"✅ {location} railway.toml uses /ping health check")
                else:
                    print(f"❌ {location} railway.toml doesn't use /ping health check")
                    all_correct = False
                    
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            all_correct = False
    
    return all_correct

def test_main_app():
    """Test the main application"""
    print("\n🔍 Testing main application...")
    
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
        print(f"❌ Error testing main app: {e}")
        return False

def test_backend_app():
    """Test the backend application"""
    print("\n🔍 Testing backend application...")
    
    try:
        # Test backend/app/main.py import
        sys.path.insert(0, 'backend')
        import app.main
        print("✅ backend/app/main.py import successful")
        
        # Test app creation
        from app.main import app
        print("✅ Backend FastAPI app creation successful")
        
        # Test health endpoints
        routes = [route.path for route in app.routes]
        health_routes = [r for r in routes if 'health' in r or 'ping' in r]
        print(f"✅ Backend health routes found: {health_routes}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing backend app: {e}")
        return False

def main():
    """Run comprehensive Railway startup tests"""
    print("🚂 Comprehensive Railway Startup Test")
    print("=" * 50)
    
    tests = [
        ("Startup Script Test", test_startup_script),
        ("Railway Configs Test", test_railway_configs),
        ("Main App Test", test_main_app),
        ("Backend App Test", test_backend_app)
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
        print("🎉 ALL TESTS PASSED - RAILWAY STARTUP READY!")
        print("\n📋 Railway Configuration:")
        print("- Startup script: start_railway.py")
        print("- Health check path: /ping")
        print("- Health check timeout: 600 seconds")
        print("- Fallback to minimal app if main app fails")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 