#!/usr/bin/env python3
"""
Final Railway deployment test
"""
import sys
import os
import requests
import time

def test_railway_configs():
    """Test all Railway configuration files"""
    print("🔍 Testing Railway configuration files...")
    
    configs = [
        ('railway.toml', 'root'),
        ('backend/railway.toml', 'backend'),
        ('frontend/railway.toml', 'frontend')
    ]
    
    all_correct = True
    
    for file_path, location in configs:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                if location == 'root':
                    if '/ping' in content and '/api/v1/health' not in content:
                        print(f"✅ {location} railway.toml uses correct health check: /ping")
                    else:
                        print(f"❌ {location} railway.toml still uses old health check")
                        all_correct = False
                        
                elif location == 'backend':
                    if 'main:app' in content:
                        print(f"✅ {location} railway.toml uses correct module path: main:app")
                    else:
                        print(f"❌ {location} railway.toml still uses old module path")
                        all_correct = False
                        
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            all_correct = False
    
    return all_correct

def test_health_endpoints():
    """Test all health check endpoints"""
    print("\n🔍 Testing health endpoints...")
    
    # Start a test server
    import subprocess
    import signal
    
    try:
        # Start the server in background
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        base_url = "http://localhost:8004"
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
        
        # Kill the process
        process.terminate()
        process.wait()
        
        return all_working
        
    except Exception as e:
        print(f"❌ Error testing health endpoints: {e}")
        return False

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

def test_dockerfile():
    """Test Dockerfile configuration"""
    print("\n🔍 Testing Dockerfile...")
    
    try:
        with open('Dockerfile', 'r') as f:
            content = f.read()
            
            if 'main:app' in content:
                print("✅ Dockerfile uses correct module path: main:app")
            else:
                print("❌ Dockerfile still uses old module path")
                return False
                
            if '/ping' in content:
                print("✅ Dockerfile uses correct health check: /ping")
            else:
                print("❌ Dockerfile still uses old health check")
                return False
                
            return True
    except Exception as e:
        print(f"❌ Error reading Dockerfile: {e}")
        return False

def main():
    """Run final Railway deployment tests"""
    print("🚂 Final Railway Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        ("Railway Configs Test", test_railway_configs),
        ("Module Import Test", test_module_import),
        ("Dockerfile Test", test_dockerfile),
        ("Health Endpoints Test", test_health_endpoints)
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
        print("🎉 ALL TESTS PASSED - RAILWAY DEPLOYMENT READY!")
        print("\n📋 Railway Configuration:")
        print("- Health check path: /ping")
        print("- Module path: main:app")
        print("- Health check timeout: 600 seconds")
        print("- All config files updated")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 