#!/usr/bin/env python3

"""
Simple test script to verify backend functionality
"""

import requests
import time
import sys

def test_backend():
    """Test the backend health endpoint"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing backend functionality...")
    
    # Test 1: Basic health check
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 3: API docs
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API docs accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API docs failed: {e}")
    
    print("🎉 Backend tests completed!")
    return True

if __name__ == "__main__":
    # Wait a bit for the server to start
    print("⏳ Waiting for backend to start...")
    time.sleep(5)
    
    success = test_backend()
    sys.exit(0 if success else 1) 