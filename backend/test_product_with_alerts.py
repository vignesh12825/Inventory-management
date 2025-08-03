#!/usr/bin/env python3
"""
Test script to verify product deletion for products with stock alerts
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_token():
    """Get authentication token"""
    login_data = {
        "username": "admin@example.com",
        "password": "password"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

def test_product_with_alerts():
    """Test deletion of products with stock alerts"""
    print("🔐 Getting authentication token...")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test deletion of Product 1 (Laptop) which has stock alerts
    product_id = 1
    print(f"\n🗑️ Testing: Delete Product 1 (Laptop)")
    print("   This product has stock alerts (acknowledged/dismissed)")
    print("   According to new logic, stock alerts should NOT block deletion")
    
    response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    if response.status_code == 200:
        print(f"✅ SUCCESS! Product deleted successfully!")
        print(f"   This confirms stock alerts no longer block deletion")
    elif response.status_code == 400:
        error_detail = response.json().get('detail', 'Unknown error')
        print(f"❌ Product deletion blocked: {error_detail}")
        
        if "stock alerts" in error_detail:
            print("   ❌ This is NOT expected - stock alerts should not block deletion")
        elif "inventory items" in error_detail:
            print("   ✅ This is expected - product has inventory items")
        elif "active purchase orders" in error_detail:
            print("   ✅ This is expected - product has items in active POs")
        else:
            print("   ❓ Unexpected error message")
    else:
        print(f"❌ Unexpected response: {response.status_code} - {response.text}")
    
    print(f"\n🎉 Test completed!")
    print(f"✅ Stock alerts should NOT block product deletion (they're just notifications)")

if __name__ == "__main__":
    try:
        test_product_with_alerts()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 