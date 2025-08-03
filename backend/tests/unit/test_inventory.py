import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.main import app
from app.core.database import get_db
from app.models.inventory import Inventory, StockMovement, StockMovementType, Location
from app.models.product import Product
from app.models.user import User, UserRole
from app.core.security import create_access_token

class TestInventoryEndpoints:
    """Test inventory endpoints with authentication"""
    
    @pytest.fixture
    def test_data(self, client, db_session, admin_user, admin_headers):
        """Create test data for inventory tests"""
        
        # Create test product
        product = Product(
            name="Test Product",
            sku="TEST001",
            description="Test product description",
            category_id=1,
            supplier_id=1,
            price=10.0,
            min_stock_level=5,
            reorder_point=10
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        # Create test location
        location = Location(
            name="Test Location",
            code="TEST-LOC",
            address="Test Address",
            warehouse_type="main"
        )
        db_session.add(location)
        db_session.commit()
        db_session.refresh(location)
        
        # Create test inventory item
        inventory_item = Inventory(
            product_id=product.id,
            location_id=location.id,
            quantity=100,
            reserved_quantity=10,
            available_quantity=90,
            unit_cost=8.0
        )
        db_session.add(inventory_item)
        db_session.commit()
        db_session.refresh(inventory_item)
        
        return {
            "client": client,
            "admin_headers": admin_headers,
            "admin_user": admin_user,
            "product": product,
            "location": location,
            "inventory_item": inventory_item
        }
    
    def test_get_inventory_list_success(self, test_data):
        """Test getting inventory list with authentication"""
        response = test_data["client"].get("/api/v1/inventory/", headers=test_data["admin_headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert len(data["data"]) >= 1
        
        # Check if our test inventory item is in the list
        inventory_ids = [item["id"] for item in data["data"]]
        assert test_data["inventory_item"].id in inventory_ids
    
    def test_get_inventory_list_unauthorized(self, client):
        """Test getting inventory list without authentication"""
        response = client.get("/api/v1/inventory/")
        assert response.status_code == 401
    
    def test_get_inventory_list_with_filters(self, test_data):
        """Test getting inventory list with product and location filters"""
        
        # Filter by product
        response = test_data["client"].get(
            f"/api/v1/inventory/?product_id={test_data['product'].id}",
            headers=test_data["admin_headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["product_id"] == test_data["product"].id
        
        # Filter by location
        response = test_data["client"].get(
            f"/api/v1/inventory/?location_id={test_data['location'].id}",
            headers=test_data["admin_headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["location_id"] == test_data["location"].id
    
    def test_get_inventory_item_success(self, test_data):
        """Test getting single inventory item"""
        response = test_data["client"].get(
            f"/api/v1/inventory/{test_data['inventory_item'].id}",
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_data["inventory_item"].id
        assert data["product_id"] == test_data["product"].id
        assert data["location_id"] == test_data["location"].id
        assert data["quantity"] == 100
    
    def test_get_inventory_item_not_found(self, client, admin_headers):
        """Test getting non-existent inventory item"""
        response = client.get("/api/v1/inventory/99999", headers=admin_headers)
        assert response.status_code == 404
    
    def test_create_inventory_item_success(self, test_data):
        """Test creating new inventory item"""
        
        # Create another product and location for new inventory
        product2 = Product(
            name="Test Product 2",
            sku="TEST002",
            description="Test product 2 description",
            category_id=1,
            supplier_id=1,
            price=15.0
        )
        test_data["client"].app.dependency_overrides[get_db]().__next__().add(product2)
        test_data["client"].app.dependency_overrides[get_db]().__next__().commit()
        test_data["client"].app.dependency_overrides[get_db]().__next__().refresh(product2)
        
        location2 = Location(
            name="Test Location 2",
            code="TEST-LOC2",
            address="Test Address 2"
        )
        test_data["client"].app.dependency_overrides[get_db]().__next__().add(location2)
        test_data["client"].app.dependency_overrides[get_db]().__next__().commit()
        test_data["client"].app.dependency_overrides[get_db]().__next__().refresh(location2)
        
        inventory_data = {
            "product_id": product2.id,
            "location_id": location2.id,
            "quantity": 50,
            "unit_cost": 12.0,
            "notes": "Test inventory item"
        }
        
        response = test_data["client"].post(
            "/api/v1/inventory/",
            json=inventory_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == product2.id
        assert data["location_id"] == location2.id
        assert data["quantity"] == 50
        assert data["unit_cost"] == 12.0
    
    def test_create_inventory_item_duplicate(self, test_data):
        """Test creating inventory item that already exists"""
        inventory_data = {
            "product_id": test_data["product"].id,
            "location_id": test_data["location"].id,
            "quantity": 25,
            "unit_cost": 9.0
        }
        
        response = test_data["client"].post(
            "/api/v1/inventory/",
            json=inventory_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_update_inventory_item_success(self, test_data):
        """Test updating inventory item"""
        update_data = {
            "quantity": 150,
            "unit_cost": 9.5,
            "notes": "Updated inventory item"
        }
        
        response = test_data["client"].put(
            f"/api/v1/inventory/{test_data['inventory_item'].id}",
            json=update_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 150
        assert data["unit_cost"] == 9.5
        assert data["notes"] == "Updated inventory item"
        assert data["available_quantity"] == 140  # 150 - 10 (reserved)
    
    def test_update_inventory_item_not_found(self, client, admin_headers):
        """Test updating non-existent inventory item"""
        update_data = {"quantity": 150}
        
        response = client.put(
            "/api/v1/inventory/99999",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 404
    
    def test_delete_inventory_item_success(self, test_data):
        """Test deleting inventory item"""
        response = test_data["client"].delete(
            f"/api/v1/inventory/{test_data['inventory_item'].id}",
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify item is deleted
        response = test_data["client"].get(
            f"/api/v1/inventory/{test_data['inventory_item'].id}",
            headers=test_data["admin_headers"]
        )
        assert response.status_code == 404
    
    def test_delete_inventory_item_not_found(self, client, admin_headers):
        """Test deleting non-existent inventory item"""
        response = client.delete("/api/v1/inventory/99999", headers=admin_headers)
        assert response.status_code == 404
    
    def test_create_stock_movement_in_success(self, test_data):
        """Test creating stock movement (stock in)"""
        movement_data = {
            "movement_type": "in",
            "quantity": 25,
            "notes": "Stock in movement"
        }
        
        response = test_data["client"].post(
            f"/api/v1/inventory/{test_data['inventory_item'].id}/stock-movement",
            json=movement_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["movement_type"] == "in"
        assert data["quantity"] == 25
        assert data["inventory_item_id"] == test_data["inventory_item"].id
        
        # Verify inventory quantity is updated
        inventory_response = test_data["client"].get(
            f"/api/v1/inventory/{test_data['inventory_item'].id}",
            headers=test_data["admin_headers"]
        )
        updated_inventory = inventory_response.json()
        assert updated_inventory["quantity"] == 125  # 100 + 25
    
    def test_create_stock_movement_out_success(self, test_data):
        """Test creating stock movement (stock out)"""
        movement_data = {
            "movement_type": "out",
            "quantity": 15,
            "notes": "Stock out movement"
        }
        
        response = test_data["client"].post(
            f"/api/v1/inventory/{test_data['inventory_item'].id}/stock-movement",
            json=movement_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["movement_type"] == "out"
        assert data["quantity"] == 15
        
        # Verify inventory quantity is updated
        inventory_response = test_data["client"].get(
            f"/api/v1/inventory/{test_data['inventory_item'].id}",
            headers=test_data["admin_headers"]
        )
        updated_inventory = inventory_response.json()
        assert updated_inventory["quantity"] == 85  # 100 - 15
    
    def test_create_stock_movement_insufficient_stock(self, test_data):
        """Test creating stock movement with insufficient stock"""
        movement_data = {
            "movement_type": "out",
            "quantity": 200,  # More than available (100)
            "notes": "Stock out movement"
        }
        
        response = test_data["client"].post(
            f"/api/v1/inventory/{test_data['inventory_item'].id}/stock-movement",
            json=movement_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]
    
    def test_get_stock_movements_success(self, test_data):
        """Test getting stock movements for inventory item"""
        
        # First create a movement
        movement_data = {
            "movement_type": "in",
            "quantity": 10,
            "notes": "Test movement"
        }
        test_data["client"].post(
            f"/api/v1/inventory/{test_data['inventory_item'].id}/stock-movement",
            json=movement_data,
            headers=test_data["admin_headers"]
        )
        
        # Get movements
        response = test_data["client"].get(
            f"/api/v1/inventory/{test_data['inventory_item'].id}/stock-movements",
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_adjust_stock_success(self, test_data):
        """Test adjusting stock quantity"""
        adjustment_data = {
            "quantity_change": 30,
            "notes": "Manual stock adjustment"
        }
        
        response = test_data["client"].post(
            f"/api/v1/inventory/{test_data['inventory_item'].id}/adjust-stock",
            json=adjustment_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "adjusted by 30" in data["message"]
        assert data["new_quantity"] == 130  # 100 + 30
        
        # Verify inventory is updated
        inventory_response = test_data["client"].get(
            f"/api/v1/inventory/{test_data['inventory_item'].id}",
            headers=test_data["admin_headers"]
        )
        updated_inventory = inventory_response.json()
        assert updated_inventory["quantity"] == 130
    
    def test_adjust_stock_negative_success(self, test_data):
        """Test adjusting stock with negative quantity"""
        adjustment_data = {
            "quantity_change": -20,
            "notes": "Manual stock reduction"
        }
        
        response = test_data["client"].post(
            f"/api/v1/inventory/{test_data['inventory_item'].id}/adjust-stock",
            json=adjustment_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "adjusted by -20" in data["message"]
        assert data["new_quantity"] == 80  # 100 - 20
    
    def test_adjust_stock_below_zero(self, test_data):
        """Test adjusting stock below zero (should clamp to 0)"""
        adjustment_data = {
            "quantity_change": -150,  # More than available (100)
            "notes": "Manual stock reduction"
        }
        
        response = test_data["client"].post(
            f"/api/v1/inventory/{test_data['inventory_item'].id}/adjust-stock",
            json=adjustment_data,
            headers=test_data["admin_headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["new_quantity"] == 0  # Should clamp to 0
    
    def test_get_low_stock_items(self, test_data):
        """Test getting low stock items"""
        
        # Update product to have reorder point
        test_data["product"].reorder_point = 50
        test_data["client"].app.dependency_overrides[get_db]().__next__().commit()
        
        # Update inventory to be below reorder point
        test_data["inventory_item"].quantity = 30
        test_data["client"].app.dependency_overrides[get_db]().__next__().commit()
        
        response = test_data["client"].get("/api/v1/inventory/low-stock", headers=test_data["admin_headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should include our test item since quantity (30) <= reorder_point (50)
        inventory_ids = [item["id"] for item in data]
        assert test_data["inventory_item"].id in inventory_ids
    
    def test_get_out_of_stock_items(self, test_data):
        """Test getting out of stock items"""
        
        # Update inventory to be out of stock
        test_data["inventory_item"].quantity = 0
        test_data["client"].app.dependency_overrides[get_db]().__next__().commit()
        
        response = test_data["client"].get("/api/v1/inventory/out-of-stock", headers=test_data["admin_headers"])
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should include our test item since quantity is 0
        inventory_ids = [item["id"] for item in data]
        assert test_data["inventory_item"].id in inventory_ids 