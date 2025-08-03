import pytest
from fastapi import status

class TestUsersEndpoints:
    """Test users endpoints"""
    
    def test_get_current_user_success(self, client, admin_headers, admin_user):
        """Test getting current user successfully"""
        response = client.get("/api/v1/users/me", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == admin_user.email
        assert data["username"] == admin_user.username
        assert data["full_name"] == admin_user.full_name
        assert data["role"] == admin_user.role.value
        assert data["is_active"] == admin_user.is_active
        assert "can_manage_users" in data
        assert "can_approve_po" in data
        assert "can_view_reports" in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_users_admin_access(self, client, admin_headers):
        """Test admin can get all users"""
        response = client.get("/api/v1/users/", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_users_staff_access_denied(self, client, staff_headers):
        """Test staff cannot get all users"""
        response = client.get("/api/v1/users/", headers=staff_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_get_users_viewer_access_denied(self, client, viewer_headers):
        """Test viewer cannot get all users"""
        response = client.get("/api/v1/users/", headers=viewer_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_get_user_by_id_admin(self, client, admin_headers, staff_user):
        """Test admin can get user by ID"""
        response = client.get(f"/api/v1/users/{staff_user.id}", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == staff_user.id
        assert data["email"] == staff_user.email
    
    def test_get_user_by_id_own_profile(self, client, staff_headers, staff_user):
        """Test user can get their own profile"""
        response = client.get(f"/api/v1/users/{staff_user.id}", headers=staff_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == staff_user.id
        assert data["email"] == staff_user.email
    
    def test_get_user_by_id_unauthorized(self, client, staff_headers, admin_user):
        """Test user cannot get other user's profile without permissions"""
        response = client.get(f"/api/v1/users/{admin_user.id}", headers=staff_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_get_user_by_id_not_found(self, client, admin_headers):
        """Test getting non-existent user"""
        response = client.get("/api/v1/users/99999", headers=admin_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
    
    def test_create_user_admin_success(self, client, admin_headers):
        """Test admin can create new user"""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New Test User",
            "role": "staff",
            "department": "Testing",
            "phone": "+1234567899",
            "is_active": True
        }
        
        response = client.post("/api/v1/users/", json=user_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["role"] == user_data["role"]
        assert "hashed_password" not in data
    
    def test_create_user_staff_denied(self, client, staff_headers):
        """Test staff cannot create users"""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New Test User",
            "role": "staff"
        }
        
        response = client.post("/api/v1/users/", json=user_data, headers=staff_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_create_user_duplicate_email(self, client, admin_headers, admin_user):
        """Test creating user with duplicate email"""
        user_data = {
            "email": admin_user.email,  # Duplicate email
            "username": "differentuser",
            "password": "password123",
            "full_name": "Different User",
            "role": "staff"
        }
        
        response = client.post("/api/v1/users/", json=user_data, headers=admin_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_update_user_admin_success(self, client, admin_headers, staff_user):
        """Test admin can update user"""
        update_data = {
            "full_name": "Updated Name",
            "department": "Updated Department",
            "phone": "+9876543210"
        }
        
        response = client.put(
            f"/api/v1/users/{staff_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["department"] == update_data["department"]
        assert data["phone"] == update_data["phone"]
    
    def test_update_user_own_profile(self, client, staff_headers, staff_user):
        """Test user can update their own profile"""
        update_data = {
            "full_name": "My Updated Name",
            "phone": "+1111111111"
        }
        
        response = client.put(
            f"/api/v1/users/{staff_user.id}",
            json=update_data,
            headers=staff_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["phone"] == update_data["phone"]
    
    def test_update_user_unauthorized(self, client, staff_headers, admin_user):
        """Test user cannot update other user's profile without permissions"""
        update_data = {"full_name": "Unauthorized Update"}
        
        response = client.put(
            f"/api/v1/users/{admin_user.id}",
            json=update_data,
            headers=staff_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_update_user_password(self, client, admin_headers, staff_user):
        """Test updating user password"""
        update_data = {
            "password": "newpassword123"
        }
        
        response = client.put(
            f"/api/v1/users/{staff_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password was changed by trying to login
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": staff_user.email,
                "password": "newpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_delete_user_admin_success(self, client, admin_headers, staff_user):
        """Test admin can delete user"""
        response = client.delete(f"/api/v1/users/{staff_user.id}", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert "User deleted successfully" in response.json()["message"]
    
    def test_delete_user_staff_denied(self, client, staff_headers, admin_user):
        """Test staff cannot delete users"""
        response = client.delete(f"/api/v1/users/{admin_user.id}", headers=staff_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_delete_user_not_found(self, client, admin_headers):
        """Test deleting non-existent user"""
        response = client.delete("/api/v1/users/99999", headers=admin_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
    
    def test_get_available_roles(self, client, admin_headers):
        """Test getting available roles"""
        response = client.get("/api/v1/users/roles/available", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert "admin" in data
        assert "manager" in data
        assert "staff" in data
        assert "viewer" in data
    
    def test_change_password_success(self, client, admin_headers, admin_user):
        """Test successful password change"""
        password_data = {
            "current_password": "admin123",
            "new_password": "newadminpassword123"
        }
        
        response = client.post(
            "/api/v1/users/change-password",
            json=password_data,
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "Password changed successfully" in response.json()["message"]
        
        # Verify new password works
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_user.email,
                "password": "newadminpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_current_password(self, client, admin_headers):
        """Test password change with wrong current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        response = client.post(
            "/api/v1/users/change-password",
            json=password_data,
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_change_password_unauthorized(self, client):
        """Test password change without authentication"""
        password_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/v1/users/change-password", json=password_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"] 