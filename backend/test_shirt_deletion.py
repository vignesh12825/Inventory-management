#!/usr/bin/env python3
"""
Test script to verify product deletion for Product 3 (Shirt) with no PO items
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

def test_shirt_deletion():
    """Test deletion of Product 3 (Shirt) which has no PO items"""
    print("🔐 Getting authentication token...")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test deletion of Product 3 (Shirt)
    product_id = 3
    print(f"\n🗑️ Testing: Delete Product 3 (Shirt)")
    print("   This product has NO PO items")
    print("   According to new logic, this should be deletable")
    
    response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    if response.status_code == 200:
        print(f"✅ SUCCESS! Product deleted successfully!")
        print(f"   This confirms the new logic is working correctly")
        print(f"   Products with no PO items can be deleted")
    elif response.status_code == 400:
        error_detail = response.json().get('detail', 'Unknown error')
        print(f"❌ Product deletion blocked: {error_detail}")
        
        if "active purchase orders" in error_detail:
            print("   ❌ This is NOT expected - the product has no PO items")
        elif "inventory items" in error_detail:
            print("   ✅ This is expected - product has inventory items")
        elif "stock alerts" in error_detail:
            print("   ✅ This is expected - product has stock alerts")
        else:
            print("   ❓ Unexpected error message")
    else:
        print(f"❌ Unexpected response: {response.status_code} - {response.text}")
    
    print(f"\n🎉 Test completed!")
    print(f"✅ New logic should allow deletion of products with no PO items")

if __name__ == "__main__":
    try:
        test_shirt_deletion()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 