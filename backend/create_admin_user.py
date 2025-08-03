#!/usr/bin/env python3
"""
Script to create an admin user for testing the role-based system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_admin_user():
    """Create an admin user for testing"""
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@inventory.com").first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            email="admin@inventory.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            department="IT",
            phone="+1234567890",
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("Email: admin@inventory.com")
        print("Password: admin123")
        print("Role: ADMIN")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

def create_test_users():
    """Create test users with different roles"""
    db = SessionLocal()
    
    try:
        # Create Manager user
        manager_user = User(
            email="manager@inventory.com",
            username="manager",
            hashed_password=get_password_hash("manager123"),
            full_name="John Manager",
            role=UserRole.MANAGER,
            department="Operations",
            phone="+1234567891",
            is_active=True,
            is_superuser=False
        )
        
        # Create Staff user
        staff_user = User(
            email="staff@inventory.com",
            username="staff",
            hashed_password=get_password_hash("staff123"),
            full_name="Jane Staff",
            role=UserRole.STAFF,
            department="Warehouse",
            phone="+1234567892",
            is_active=True,
            is_superuser=False
        )
        
        # Create Viewer user
        viewer_user = User(
            email="viewer@inventory.com",
            username="viewer",
            hashed_password=get_password_hash("viewer123"),
            full_name="Bob Viewer",
            role=UserRole.VIEWER,
            department="Sales",
            phone="+1234567893",
            is_active=True,
            is_superuser=False
        )
        
        db.add_all([manager_user, staff_user, viewer_user])
        db.commit()
        
        print("✅ Test users created successfully!")
        print("\nTest Users:")
        print("1. Manager - manager@inventory.com / manager123")
        print("2. Staff - staff@inventory.com / staff123")
        print("3. Viewer - viewer@inventory.com / viewer123")
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating users for Inventory Management System...")
    print("=" * 50)
    
    create_admin_user()
    print()
    create_test_users()
    
    print("\n" + "=" * 50)
    print("🎉 User creation completed!")
    print("You can now log in with any of these accounts to test role-based functionality.") 