#!/usr/bin/env python3
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_me_endpoint_detailed():
    print("🔍 Detailed /me API Debugging")
    print("=" * 60)
    
    # Test 1: Check if endpoint exists without auth
    print("1. Testing /me endpoint without authentication:")
    try:
        response = requests.get(f"{BASE_URL}/users/me")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Login to get token
    print("2. Testing login to get token:")
    login_data = {
        "username": "admin@example.com",
        "password": "password"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"   ✅ Token received: {token[:20]}...")
            print()
            
            # Test 3: Test /me with token
            print("3. Testing /me endpoint with token:")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{BASE_URL}/users/me", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            print(f"   Request Headers: {headers}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ Success! User: {user_data.get('username')} ({user_data.get('email')})")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                
        else:
            print(f"   ❌ Login failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 4: Test with different token formats
    print("4. Testing different token formats:")
    
    # Test with malformed token
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers={"Authorization": "Bearer invalid_token"})
        print(f"   Invalid token - Status: {response.status_code}")
    except Exception as e:
        print(f"   Invalid token - Error: {e}")
    
    # Test without Bearer prefix
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers={"Authorization": token})
        print(f"   No Bearer prefix - Status: {response.status_code}")
    except Exception as e:
        print(f"   No Bearer prefix - Error: {e}")
    
    # Test with extra spaces
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers={"Authorization": f"Bearer  {token}"})
        print(f"   Extra spaces - Status: {response.status_code}")
    except Exception as e:
        print(f"   Extra spaces - Error: {e}")
    
    print()
    
    # Test 5: Check backend logs
    print("5. Backend Configuration Check:")
    print("   - CORS should allow localhost:3000")
    print("   - JWT secret should be configured")
    print("   - Database connection should be working")
    print("   - User 'admin' should exist and be active")

def test_frontend_simulation():
    print("\n🌐 Frontend Simulation Test")
    print("=" * 60)
    
    # Simulate what the frontend does
    print("1. Simulating frontend login flow:")
    
    # Step 1: Login
    login_data = {
        "username": "admin@example.com",
        "password": "password"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"   ✅ Login successful, token: {token[:20]}...")
            
            # Step 2: Simulate frontend API call
            print("2. Simulating frontend /me API call:")
            
            # Simulate axios interceptor behavior
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.get(f"{BASE_URL}/users/me", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                print("   ✅ Frontend simulation successful!")
            else:
                print("   ❌ Frontend simulation failed!")
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")

def check_backend_health():
    print("\n🏥 Backend Health Check")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health endpoint: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Root endpoint: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Root check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting /me API Debugging")
    print("=" * 60)
    
    check_backend_health()
    test_me_endpoint_detailed()
    test_frontend_simulation()
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("If all tests pass, the issue is likely in the frontend.")
    print("If tests fail, the issue is in the backend configuration.")
    print("Check the output above for specific error messages.") 