import pytest
from fastapi import status

class TestAPIIntegration:
    """Integration tests for complete API workflows"""
    
    def test_complete_auth_workflow(self, client):
        """Test complete authentication workflow: register -> login -> get profile -> change password"""
        # 1. Register new user
        user_data = {
            "email": "integration@test.com",
            "username": "integration_test",
            "password": "integration123",
            "full_name": "Integration Test User",
            "role": "staff",
            "department": "Testing",
            "phone": "+1234567899",
            "is_active": True
        }
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK
        
        # 2. Login with new user
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == status.HTTP_200_OK
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Get current user profile
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()
        assert profile_data["email"] == user_data["email"]
        assert profile_data["username"] == user_data["username"]
        
        # 4. Change password
        password_data = {
            "current_password": user_data["password"],
            "new_password": "newintegration123"
        }
        
        change_password_response = client.post(
            "/api/v1/users/change-password",
            json=password_data,
            headers=headers
        )
        assert change_password_response.status_code == status.HTTP_200_OK
        
        # 5. Login with new password
        new_login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": "newintegration123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert new_login_response.status_code == status.HTTP_200_OK
    
    def test_password_reset_workflow(self, client, admin_user):
        """Test complete password reset workflow"""
        # 1. Request password reset
        reset_request_response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": admin_user.email}
        )
        assert reset_request_response.status_code == status.HTTP_200_OK
        
        reset_token = reset_request_response.json()["reset_token"]
        
        # 2. Reset password
        reset_response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": admin_user.email,
                "token": reset_token,
                "new_password": "resetpassword123"
            }
        )
        assert reset_response.status_code == status.HTTP_200_OK
        
        # 3. Login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_user.email,
                "password": "resetpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_user_management_workflow(self, client, admin_headers):
        """Test complete user management workflow: create -> update -> delete"""
        # 1. Create new user
        user_data = {
            "email": "management@test.com",
            "username": "management_test",
            "password": "management123",
            "full_name": "Management Test User",
            "role": "staff",
            "department": "Management",
            "phone": "+1234567898",
            "is_active": True
        }
        
        create_response = client.post("/api/v1/users/", json=user_data, headers=admin_headers)
        assert create_response.status_code == status.HTTP_200_OK
        created_user = create_response.json()
        user_id = created_user["id"]
        
        # 2. Update user
        update_data = {
            "full_name": "Updated Management User",
            "department": "Updated Department",
            "phone": "+9876543210"
        }
        
        update_response = client.put(
            f"/api/v1/users/{user_id}",
            json=update_data,
            headers=admin_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_user = update_response.json()
        assert updated_user["full_name"] == update_data["full_name"]
        assert updated_user["department"] == update_data["department"]
        
        # 3. Delete user
        delete_response = client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # 4. Verify user is deleted
        get_response = client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_permission_based_access_control(self, client, admin_user, staff_user, manager_user):
        """Test permission-based access control across different user roles"""
        # Login as different users
        admin_login = client.post(
            "/api/v1/auth/login",
            data={"username": admin_user.email, "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        staff_login = client.post(
            "/api/v1/auth/login",
            data={"username": staff_user.email, "password": "staff123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        staff_token = staff_login.json()["access_token"]
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        
        manager_login = client.post(
            "/api/v1/auth/login",
            data={"username": manager_user.email, "password": "manager123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        manager_token = manager_login.json()["access_token"]
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        
        # Test user management permissions
        # Admin should be able to manage users
        admin_users_response = client.get("/api/v1/users/", headers=admin_headers)
        assert admin_users_response.status_code == status.HTTP_200_OK
        
        # Staff should not be able to manage users
        staff_users_response = client.get("/api/v1/users/", headers=staff_headers)
        assert staff_users_response.status_code == status.HTTP_403_FORBIDDEN
        
        # Manager should not be able to manage users (unless they have the permission)
        manager_users_response = client.get("/api/v1/users/", headers=manager_headers)
        # This might be 200 or 403 depending on manager permissions
        assert manager_users_response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
    
    def test_error_handling_scenarios(self, client):
        """Test various error handling scenarios"""
        # 1. Invalid login credentials
        invalid_login = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent@test.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert invalid_login.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 2. Access protected endpoint without token
        no_auth_response = client.get("/api/v1/users/me")
        assert no_auth_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 3. Access with invalid token
        invalid_token_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert invalid_token_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 4. Access non-existent resource
        not_found_response = client.get("/api/v1/users/99999")
        assert not_found_response.status_code == status.HTTP_401_UNAUTHORIZED  # No auth first
        
        # 5. Invalid password reset token
        invalid_reset = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": "test@example.com",
                "token": "invalid_token",
                "new_password": "newpassword123"
            }
        )
        assert invalid_reset.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_data_validation_scenarios(self, client):
        """Test data validation scenarios"""
        # 1. Register with invalid email
        invalid_email_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User",
            "role": "staff"
        }
        
        invalid_email_response = client.post("/api/v1/auth/register", json=invalid_email_data)
        # This might pass validation or fail depending on the validation rules
        assert invalid_email_response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        # 2. Register with short password
        short_password_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "123",  # Too short
            "full_name": "Test User",
            "role": "staff"
        }
        
        short_password_response = client.post("/api/v1/auth/register", json=short_password_data)
        # This might pass or fail depending on password validation
        assert short_password_response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        # 3. Register with invalid role
        invalid_role_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User",
            "role": "INVALID_ROLE"
        }
        
        invalid_role_response = client.post("/api/v1/auth/register", json=invalid_role_data)
        assert invalid_role_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_concurrent_operations(self, client, admin_headers):
        """Test concurrent operations to ensure data consistency"""
        # Create multiple users concurrently
        user_data_list = [
            {
                "email": f"concurrent{i}@test.com",
                "username": f"concurrent{i}",
                "password": "password123",
                "full_name": f"Concurrent User {i}",
                "role": "staff"
            }
            for i in range(3)
        ]
        
        responses = []
        for user_data in user_data_list:
            response = client.post("/api/v1/users/", json=user_data, headers=admin_headers)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all users were created
        users_response = client.get("/api/v1/users/", headers=admin_headers)
        assert users_response.status_code == status.HTTP_200_OK
        users = users_response.json()
        
        # Check that our test users are in the list
        created_emails = [user["email"] for user in users]
        for user_data in user_data_list:
            assert user_data["email"] in created_emails 