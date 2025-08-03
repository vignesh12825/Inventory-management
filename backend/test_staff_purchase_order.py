#!/usr/bin/env python3
"""
Test script to verify staff user purchase order creation and identify 422 errors
"""
import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000/api/v1"

def get_token(username="staff@inventory.com", password="password"):
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

def test_staff_purchase_order_creation():
    """Test staff user purchase order creation"""
    print("🔐 Getting authentication token for staff user...")
    
    # Try different staff users
    staff_users = [
        ("staff@inventory.com", "password"),
        ("staff@example.com", "password"),
        ("vicky@gmail.com", "password"),
        ("test@example.com", "password")
    ]
    
    token = None
    for username, password in staff_users:
        print(f"   Trying {username}...")
        token = get_token(username, password)
        if token:
            print(f"   ✅ Successfully logged in as {username}")
            break
    
    if not token:
        print("❌ Could not get token for any staff user. Trying admin...")
        token = get_token("admin@example.com", "password")
        if not token:
            print("❌ Could not get token for any user")
            return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test 1: Get current user info
    print("\n👤 Testing: Get current user info")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ User info retrieved successfully")
        print(f"   Username: {user_data['username']}")
        print(f"   Role: {user_data['role']}")
        print(f"   Email: {user_data['email']}")
    else:
        print(f"❌ Failed to get user info: {response.status_code} - {response.text}")
        return
    
    # Test 2: Get suppliers
    print("\n🏢 Testing: Get suppliers")
    response = requests.get(f"{BASE_URL}/suppliers/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        suppliers = data['data']
        print(f"✅ Suppliers retrieved successfully. Found {len(suppliers)} suppliers")
        
        if not suppliers:
            print("❌ No suppliers found. Cannot test purchase order creation.")
            return
        
        supplier_id = suppliers[0]['id']
        print(f"   Using supplier ID: {supplier_id} ({suppliers[0]['name']})")
    else:
        print(f"❌ Failed to get suppliers: {response.status_code} - {response.text}")
        return
    
    # Test 3: Get products for the supplier
    print(f"\n📦 Testing: Get products for supplier {supplier_id}")
    response = requests.get(f"{BASE_URL}/products/?supplier_id={supplier_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        products = data['data']
        print(f"✅ Products retrieved successfully. Found {len(products)} products for supplier")
        
        if not products:
            print("❌ No products found for this supplier. Cannot test purchase order creation.")
            return
        
        product_id = products[0]['id']
        print(f"   Using product ID: {product_id} ({products[0]['name']})")
    else:
        print(f"❌ Failed to get products: {response.status_code} - {response.text}")
        return
    
    # Test 4: Create purchase order
    print(f"\n📋 Testing: Create purchase order")
    po_data = {
        "supplier_id": supplier_id,
        "order_date": date.today().isoformat(),
        "expected_delivery_date": "2024-12-31",
        "payment_terms": "Net 30",
        "shipping_address": "123 Test Street",
        "billing_address": "123 Test Street",
        "notes": "Test purchase order from staff user",
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
    
    print(f"   Sending PO data: {json.dumps(po_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/purchase-orders/", headers=headers, json=po_data)
    if response.status_code == 200:
        po_result = response.json()
        print(f"✅ Purchase order created successfully!")
        print(f"   PO Number: {po_result['po_number']}")
        print(f"   Status: {po_result['status']}")
        print(f"   Total Amount: ${po_result['total_amount']}")
    else:
        print(f"❌ Failed to create purchase order: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Try to parse error details
        try:
            error_data = response.json()
            if 'detail' in error_data:
                print(f"   Error detail: {error_data['detail']}")
        except:
            print(f"   Raw error: {response.text}")
    
    # Test 5: Get purchase orders to verify creation
    print(f"\n📋 Testing: Get purchase orders")
    response = requests.get(f"{BASE_URL}/purchase-orders/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        purchase_orders = data['data']
        print(f"✅ Purchase orders retrieved successfully. Found {len(purchase_orders)} POs")
        
        for po in purchase_orders:
            print(f"   - {po['po_number']}: {po['status']} (${po['total_amount']})")
    else:
        print(f"❌ Failed to get purchase orders: {response.status_code} - {response.text}")
    
    print(f"\n🎉 Staff user purchase order test completed!")

if __name__ == "__main__":
    try:
        test_staff_purchase_order_creation()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 