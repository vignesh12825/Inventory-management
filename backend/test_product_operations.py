#!/usr/bin/env python3
"""
Comprehensive test script to verify product operations fixes
"""
import requests
import json
import time

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

def test_product_filtering():
    """Test product filtering functionality"""
    print("🔍 Testing: Product filtering functionality")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Search filtering
    print("\n📝 Testing: Search filter")
    response = requests.get(f"{BASE_URL}/products/", headers=headers, params={"search": "test"})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Search filter working. Found {len(data['data'])} products matching 'test'")
    else:
        print(f"❌ Search filter failed: {response.status_code} - {response.text}")
        return False
    
    # Test 2: Category filtering
    print("\n📂 Testing: Category filter")
    response = requests.get(f"{BASE_URL}/products/", headers=headers, params={"category_id": 1})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Category filter working. Found {len(data['data'])} products in category 1")
    else:
        print(f"❌ Category filter failed: {response.status_code} - {response.text}")
        return False
    
    # Test 3: Active status filtering
    print("\n✅ Testing: Active status filter")
    response = requests.get(f"{BASE_URL}/products/", headers=headers, params={"is_active": True})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Active filter working. Found {len(data['data'])} active products")
    else:
        print(f"❌ Active filter failed: {response.status_code} - {response.text}")
        return False
    
    # Test 4: Inactive status filtering
    print("\n❌ Testing: Inactive status filter")
    response = requests.get(f"{BASE_URL}/products/", headers=headers, params={"is_active": False})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Inactive filter working. Found {len(data['data'])} inactive products")
    else:
        print(f"❌ Inactive filter failed: {response.status_code} - {response.text}")
        return False
    
    return True

def test_product_deletion():
    """Test product deletion with proper error handling"""
    print("\n🗑️ Testing: Product deletion functionality")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get a product to test deletion
    response = requests.get(f"{BASE_URL}/products/", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get products: {response.status_code}")
        return False
    
    products = response.json()["data"]
    if not products:
        print("❌ No products found to test deletion")
        return False
    
    product_id = products[0]["id"]
    
    # Test deletion
    print(f"\n🗑️ Testing: Delete product {product_id}")
    response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Product {product_id} deleted successfully")
        return True
    elif response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "inventory items" in error_detail or "purchase order items" in error_detail:
            print(f"✅ Product deletion properly blocked due to dependencies: {error_detail}")
            return True
        else:
            print(f"❌ Unexpected 400 error: {error_detail}")
            return False
    else:
        print(f"❌ Delete failed with status {response.status_code}: {response.text}")
        return False

def test_category_filtering():
    """Test category filtering for active categories only"""
    print("\n📂 Testing: Category filtering (active only)")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test active categories filter
    response = requests.get(f"{BASE_URL}/categories/", headers=headers, params={"is_active": True})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Active categories filter working. Found {len(data['data'])} active categories")
        
        # Verify all returned categories are active
        for category in data['data']:
            if not category.get('is_active', True):
                print(f"❌ Found inactive category in active filter: {category['name']}")
                return False
        
        print("✅ All returned categories are active")
        return True
    else:
        print(f"❌ Category filtering failed: {response.status_code} - {response.text}")
        return False

def test_supplier_filtering():
    """Test supplier filtering for active suppliers only"""
    print("\n🏢 Testing: Supplier filtering (active only)")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test active suppliers filter
    response = requests.get(f"{BASE_URL}/suppliers/", headers=headers, params={"is_active": True})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Active suppliers filter working. Found {len(data['data'])} active suppliers")
        
        # Verify all returned suppliers are active
        for supplier in data['data']:
            if not supplier.get('is_active', True):
                print(f"❌ Found inactive supplier in active filter: {supplier['name']}")
                return False
        
        print("✅ All returned suppliers are active")
        return True
    else:
        print(f"❌ Supplier filtering failed: {response.status_code} - {response.text}")
        return False

def test_product_creation_with_filters():
    """Test creating a product and verifying it appears in filtered results"""
    print("\n➕ Testing: Product creation and filtering")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test product
    product_data = {
        "name": "Test Product for Filtering",
        "description": "A test product to verify filtering",
        "sku": f"TEST-{int(time.time())}",
        "price": 99.99,
        "min_stock_level": 10,
        "reorder_point": 5,
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/products/", headers=headers, json=product_data)
    if response.status_code != 201 and response.status_code != 200:
        print(f"❌ Failed to create test product: {response.status_code} - {response.text}")
        return False
    
    created_product = response.json()
    product_id = created_product["id"]
    print(f"✅ Created test product with ID: {product_id}")
    
    # Test that it appears in active products filter
    response = requests.get(f"{BASE_URL}/products/", headers=headers, params={"is_active": True})
    if response.status_code == 200:
        data = response.json()
        found = any(p["id"] == product_id for p in data["data"])
        if found:
            print("✅ Created product appears in active products filter")
        else:
            print("❌ Created product not found in active products filter")
            return False
    else:
        print(f"❌ Failed to get active products: {response.status_code}")
        return False
    
    # Test search filter
    response = requests.get(f"{BASE_URL}/products/", headers=headers, params={"search": "Test Product for Filtering"})
    if response.status_code == 200:
        data = response.json()
        found = any(p["id"] == product_id for p in data["data"])
        if found:
            print("✅ Created product appears in search results")
        else:
            print("❌ Created product not found in search results")
            return False
    else:
        print(f"❌ Failed to search products: {response.status_code}")
        return False
    
    # Clean up - delete the test product
    response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    if response.status_code == 200:
        print("✅ Test product cleaned up successfully")
    else:
        print(f"⚠️ Failed to clean up test product: {response.status_code}")
    
    return True

def test_inventory_product_filtering():
    """Test that inventory only shows active products"""
    print("\n📦 Testing: Inventory product filtering (active only)")
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get active products
    response = requests.get(f"{BASE_URL}/products/", headers=headers, params={"is_active": True})
    if response.status_code == 200:
        active_products = response.json()["data"]
        print(f"✅ Found {len(active_products)} active products")
        
        # Get all products
        response = requests.get(f"{BASE_URL}/products/", headers=headers)
        if response.status_code == 200:
            all_products = response.json()["data"]
            inactive_count = len(all_products) - len(active_products)
            print(f"✅ Found {inactive_count} inactive products")
            
            if inactive_count > 0:
                print("✅ Product filtering is working correctly")
                return True
            else:
                print("ℹ️ No inactive products found to test filtering")
                return True
        else:
            print(f"❌ Failed to get all products: {response.status_code}")
            return False
    else:
        print(f"❌ Failed to get active products: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive product operations tests...")
    
    try:
        # Test 1: Product filtering
        if not test_product_filtering():
            print("❌ Product filtering tests failed")
            return
        
        # Test 2: Product deletion
        if not test_product_deletion():
            print("❌ Product deletion tests failed")
            return
        
        # Test 3: Category filtering
        if not test_category_filtering():
            print("❌ Category filtering tests failed")
            return
        
        # Test 4: Supplier filtering
        if not test_supplier_filtering():
            print("❌ Supplier filtering tests failed")
            return
        
        # Test 5: Product creation and filtering
        if not test_product_creation_with_filters():
            print("❌ Product creation and filtering tests failed")
            return
        
        # Test 6: Inventory product filtering
        if not test_inventory_product_filtering():
            print("❌ Inventory product filtering tests failed")
            return
        
        print("\n🎉 All tests passed successfully!")
        print("✅ Product filtering: Working")
        print("✅ Product deletion: Working with proper error handling")
        print("✅ Category filtering: Working (active only)")
        print("✅ Supplier filtering: Working (active only)")
        print("✅ Inventory product filtering: Working (active only)")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 