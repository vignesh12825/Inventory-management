#!/usr/bin/env python3
"""
Test script to verify product deletion for Product 4 (Pencil) with received PO
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

def test_pencil_deletion():
    """Test deletion of Product 4 (Pencil) which has PO items in received status"""
    print("🔐 Getting authentication token...")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test deletion of Product 4 (Pencil)
    product_id = 4
    print(f"\n🗑️ Testing: Delete Product 4 (Pencil)")
    print("   This product has PO items in RECEIVED status")
    print("   According to new logic, this should be deletable")
    
    response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    if response.status_code == 200:
        print(f"✅ SUCCESS! Product deleted successfully!")
        print(f"   This confirms the new logic is working correctly")
        print(f"   Products with items in RECEIVED POs can now be deleted")
    elif response.status_code == 400:
        error_detail = response.json().get('detail', 'Unknown error')
        print(f"❌ Product deletion still blocked: {error_detail}")
        
        if "active purchase orders" in error_detail:
            print("   ❌ This is NOT expected - the PO is in received status")
        elif "inventory items" in error_detail:
            print("   ✅ This is expected - product has inventory items")
        else:
            print("   ❓ Unexpected error message")
    else:
        print(f"❌ Unexpected response: {response.status_code} - {response.text}")
    
    print(f"\n🎉 Test completed!")
    print(f"✅ New logic should allow deletion of products with items in RECEIVED/CANCELLED POs")

if __name__ == "__main__":
    try:
        test_pencil_deletion()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 