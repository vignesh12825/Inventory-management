import pytest
from fastapi import status
from app.core.security import verify_password, get_password_hash, create_password_reset_token, verify_password_reset_token

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success_with_email(self, client, admin_user):
        """Test successful login with email"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_user.email,
                "password": "admin123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_success_with_username(self, client, admin_user):
        """Test successful login with username"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_user.username,
                "password": "admin123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@test.com",
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email/username or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user"""
        from app.models.user import User, UserRole
        
        # Create inactive user
        inactive_user = User(
            email="inactive@test.com",
            username="inactive_test",
            hashed_password=get_password_hash("password123"),
            full_name="Inactive User",
            role=UserRole.STAFF,
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": inactive_user.email,
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in response.json()["detail"]
    
    def test_register_success(self, client):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "newpassword123",
            "full_name": "New Test User",
            "role": "staff",  # Use lowercase to match enum values
            "department": "Testing",
            "phone": "+1234567899",
            "is_active": True
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        if response.status_code != status.HTTP_200_OK:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["role"] == user_data["role"]
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(self, client, admin_user):
        """Test registration with duplicate email"""
        user_data = {
            "email": admin_user.email,  # Duplicate email
            "username": "differentuser",
            "password": "password123",
            "full_name": "Different User",
            "role": "staff"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email already exists" in response.json()["detail"]
    
    def test_register_duplicate_username(self, client, admin_user):
        """Test registration with duplicate username"""
        user_data = {
            "email": "different@test.com",
            "username": admin_user.username,  # Duplicate username
            "password": "password123",
            "full_name": "Different User",
            "role": "staff"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username already exists" in response.json()["detail"]
    
    def test_forgot_password_success(self, client, admin_user):
        """Test successful forgot password request"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": admin_user.email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Password reset link has been sent" in data["message"]
        assert "reset_token" in data
        assert "note" in data
    
    def test_forgot_password_nonexistent_email(self, client):
        """Test forgot password with nonexistent email"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@test.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "If the email exists" in data["message"]
    
    def test_forgot_password_inactive_user(self, client, db_session):
        """Test forgot password with inactive user"""
        from app.models.user import User, UserRole
        
        # Create inactive user
        inactive_user = User(
            email="inactive@test.com",
            username="inactive_test",
            hashed_password=get_password_hash("password123"),
            full_name="Inactive User",
            role=UserRole.STAFF,
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": inactive_user.email}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in response.json()["detail"]
    
    def test_reset_password_success(self, client, admin_user):
        """Test successful password reset"""
        # First get reset token
        reset_response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": admin_user.email}
        )
        reset_token = reset_response.json()["reset_token"]
        
        # Reset password
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": admin_user.email,
                "token": reset_token,
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "Password has been reset successfully" in response.json()["message"]
        
        # Verify new password works
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_user.email,
                "password": "newpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_reset_password_invalid_token(self, client, admin_user):
        """Test password reset with invalid token"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": admin_user.email,
                "token": "invalid_token",
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired reset token" in response.json()["detail"]
    
    def test_reset_password_nonexistent_user(self, client):
        """Test password reset with nonexistent user"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": "nonexistent@test.com",
                "token": "some_token",
                "new_password": "newpassword123"
            }
        )
        
        # The endpoint checks token validity first, so it returns 400 for invalid token
        # rather than 404 for nonexistent user (for security reasons)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired reset token" in response.json()["detail"]

class TestSecurityFunctions:
    """Test security utility functions"""
    
    def test_password_hashing_and_verification(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_password_reset_token_creation_and_verification(self):
        """Test password reset token creation and verification"""
        email = "test@example.com"
        token = create_password_reset_token(email)
        
        # Verify token
        verified_email = verify_password_reset_token(token)
        assert verified_email == email
        
        # Test invalid token
        invalid_email = verify_password_reset_token("invalid_token")
        assert invalid_email is None 