#!/usr/bin/env python3
"""
Test script to simulate frontend purchase order request and identify 422 errors
"""
import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000/api/v1"

def get_token(username="staff@example.com", password="password"):
    """Get authentication token for staff user"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed for {username}: {response.status_code} - {response.text}")
        return None

def test_frontend_po_request():
    """Test the exact request format that frontend might send"""
    print("🔐 Getting authentication token for staff user...")
    token = get_token("staff@example.com", "password")
    
    if not token:
        print("❌ Could not get token for staff user")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test 1: Get suppliers and products
    print("\n🏢 Testing: Get suppliers and products")
    response = requests.get(f"{BASE_URL}/suppliers/", headers=headers)
    if response.status_code == 200:
        suppliers = response.json()['data']
        supplier_id = suppliers[0]['id'] if suppliers else None
        print(f"   Using supplier ID: {supplier_id}")
    else:
        print(f"❌ Failed to get suppliers: {response.status_code}")
        return
    
    response = requests.get(f"{BASE_URL}/products/?supplier_id={supplier_id}", headers=headers)
    if response.status_code == 200:
        products = response.json()['data']
        product_id = products[0]['id'] if products else None
        print(f"   Using product ID: {product_id}")
    else:
        print(f"❌ Failed to get products: {response.status_code}")
        return
    
    # Test 2: Simulate frontend request with potential issues
    print(f"\n📋 Testing: Frontend-style purchase order creation")
    
    # Test case 1: Valid request
    po_data_valid = {
        "supplier_id": supplier_id,
        "order_date": date.today().isoformat(),
        "expected_delivery_date": "2024-12-31",
        "payment_terms": "Net 30",
        "shipping_address": "123 Test Street",
        "billing_address": "123 Test Street",
        "notes": "Test purchase order",
        "items": [
            {
                "product_id": product_id,
                "quantity": 5,
                "unit_price": 100.0,
                "supplier_sku": "TEST-SKU-001",
                "notes": "Test item"
            }
        ],
        "tax_amount": 50.0,
        "shipping_amount": 25.0
    }
    
    print(f"   Test 1: Valid request")
    response = requests.post(f"{BASE_URL}/purchase-orders/", headers=headers, json=po_data_valid)
    if response.status_code == 200:
        print(f"   ✅ Valid request successful")
    else:
        print(f"   ❌ Valid request failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test case 2: Missing required fields
    po_data_missing = {
        "supplier_id": supplier_id,
        "order_date": date.today().isoformat(),
        "items": []  # Empty items array
    }
    
    print(f"\n   Test 2: Missing required fields")
    response = requests.post(f"{BASE_URL}/purchase-orders/", headers=headers, json=po_data_missing)
    if response.status_code == 422:
        print(f"   ✅ Correctly rejected missing fields: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error details: {error_data}")
        except:
            print(f"   Raw error: {response.text}")
    else:
        print(f"   ❌ Unexpected response: {response.status_code}")
    
    # Test case 3: Invalid data types
    po_data_invalid_types = {
        "supplier_id": "invalid",  # Should be int
        "order_date": "invalid-date",  # Should be valid date
        "items": [
            {
                "product_id": "invalid",  # Should be int
                "quantity": "invalid",  # Should be int
                "unit_price": "invalid"  # Should be float
            }
        ]
    }
    
    print(f"\n   Test 3: Invalid data types")
    response = requests.post(f"{BASE_URL}/purchase-orders/", headers=headers, json=po_data_invalid_types)
    if response.status_code == 422:
        print(f"   ✅ Correctly rejected invalid types: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error details: {error_data}")
        except:
            print(f"   Raw error: {response.text}")
    else:
        print(f"   ❌ Unexpected response: {response.status_code}")
    
    # Test case 4: Frontend-style request (with potential issues)
    po_data_frontend = {
        "supplier_id": supplier_id,
        "order_date": date.today().isoformat(),
        "expected_delivery_date": "2024-12-31",
        "payment_terms": "Net 30",
        "shipping_address": "123 Test Street",
        "billing_address": "123 Test Street",
        "notes": "Test purchase order from frontend",
        "items": [
            {
                "product_id": product_id,
                "quantity": 5,
                "unit_price": 100.0,
                "supplier_sku": "",
                "notes": ""
            }
        ],
        "tax_amount": 0,
        "shipping_amount": 0
    }
    
    print(f"\n   Test 4: Frontend-style request")
    response = requests.post(f"{BASE_URL}/purchase-orders/", headers=headers, json=po_data_frontend)
    if response.status_code == 200:
        print(f"   ✅ Frontend-style request successful")
    else:
        print(f"   ❌ Frontend-style request failed: {response.status_code}")
        print(f"   Response: {response.text}")
        try:
            error_data = response.json()
            print(f"   Error details: {error_data}")
        except:
            print(f"   Raw error: {response.text}")
    
    print(f"\n🎉 Frontend request simulation completed!")

if __name__ == "__main__":
    try:
        test_frontend_po_request()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 