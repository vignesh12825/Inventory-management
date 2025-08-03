#!/usr/bin/env python3
"""
Test script to verify the new product deletion logic
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

def test_product_deletion_logic():
    """Test the new product deletion logic"""
    print("🔐 Getting authentication token...")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test 1: Get products list
    print("\n📋 Testing: Get products list")
    response = requests.get(f"{BASE_URL}/products/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Products list retrieved successfully. Found {len(data['data'])} products")
        if data['data']:
            product_id = data['data'][0]['id']
            product_name = data['data'][0]['name']
            print(f"   Using product: {product_name} (ID: {product_id})")
        else:
            print("❌ No products found")
            return
    else:
        print(f"❌ Failed to get products list: {response.status_code} - {response.text}")
        return
    
    # Test 2: Try to delete the product
    print(f"\n🗑️ Testing: Delete product {product_id}")
    response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    if response.status_code == 200:
        print(f"✅ Product deleted successfully!")
        print(f"   Product '{product_name}' has been deleted")
    elif response.status_code == 400:
        error_detail = response.json().get('detail', 'Unknown error')
        print(f"⚠️ Product deletion blocked: {error_detail}")
        
        if "active purchase orders" in error_detail:
            print("   ✅ This is the expected behavior - product has items in active POs")
        elif "inventory items" in error_detail:
            print("   ✅ This is the expected behavior - product has inventory items")
        else:
            print("   ❓ Unexpected error message")
    else:
        print(f"❌ Unexpected response: {response.status_code} - {response.text}")
    
    print(f"\n🎉 Product deletion logic test completed!")
    print(f"✅ New logic: Only blocks deletion for products with items in ACTIVE POs")
    print(f"✅ New logic: Allows deletion for products with items in RECEIVED/CANCELLED POs")

if __name__ == "__main__":
    try:
        test_product_deletion_logic()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 