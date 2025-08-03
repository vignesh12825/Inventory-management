#!/usr/bin/env python3
"""
Script to create a staff user for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_staff_user():
    """Create a staff user for testing"""
    db = SessionLocal()
    
    try:
        # List all existing users
        print("📋 Existing users:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.username} ({user.email}) - Role: {user.role}")
        
        # Check if staff user already exists
        existing_user = db.query(User).filter(User.email == "staff@example.com").first()
        if existing_user:
            print(f"✅ Staff user already exists: {existing_user.email} (Role: {existing_user.role})")
            return existing_user
        
        # Create staff user with unique username
        staff_user = User(
            email="staff@example.com",
            username="staffuser",  # Changed from "staff" to "staffuser"
            hashed_password=get_password_hash("password"),
            full_name="Staff User",
            role=UserRole.STAFF,
            department="Operations",
            phone="555-123-4567",
            is_active=True,
            is_superuser=False
        )
        
        db.add(staff_user)
        db.commit()
        db.refresh(staff_user)
        
        print(f"✅ Staff user created successfully!")
        print(f"   Email: {staff_user.email}")
        print(f"   Username: {staff_user.username}")
        print(f"   Role: {staff_user.role}")
        print(f"   Password: password")
        
        return staff_user
        
    except Exception as e:
        print(f"❌ Error creating staff user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_staff_user() 