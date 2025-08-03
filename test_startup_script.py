#!/usr/bin/env python3
"""
Test the startup script functionality
"""
import sys
import os

def test_startup_script_import():
    """Test that the startup script can be imported"""
    print("🔍 Testing startup script import...")
    
    try:
        import start_railway
        print("✅ Startup script import successful")
        return True
    except Exception as e:
        print(f"❌ Error importing startup script: {e}")
        return False

def test_startup_script_functionality():
    """Test the startup script functionality"""
    print("\n🔍 Testing startup script functionality...")
    
    try:
        import start_railway
        
        # Test minimal app creation
        app = start_railway.create_minimal_app()
        print("✅ Minimal app creation successful")
        
        # Test endpoints
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
        print(f"❌ Error testing startup script functionality: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'start_railway.py',
        'main.py',
        'backend/app/main.py',
        'Dockerfile',
        'railway.toml',
        'backend/railway.toml'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run startup script tests"""
    print("🚀 Startup Script Test")
    print("=" * 50)
    
    tests = [
        ("File Structure Test", test_file_structure),
        ("Startup Script Import Test", test_startup_script_import),
        ("Startup Script Functionality Test", test_startup_script_functionality)
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
        print("🎉 ALL TESTS PASSED - STARTUP SCRIPT READY!")
        print("\n📋 Railway Configuration:")
        print("- Dockerfile uses startup script")
        print("- Health check path: /ping")
        print("- Fallback to minimal app if main app fails")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 