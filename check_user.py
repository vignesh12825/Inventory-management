#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create session
db = SessionLocal()

try:
    # Check admin user
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if admin_user:
        print(f"Admin user found:")
        print(f"  ID: {admin_user.id}")
        print(f"  Username: {admin_user.username}")
        print(f"  Email: {admin_user.email}")
        print(f"  Is Active: {admin_user.is_active}")
        print(f"  Role: {admin_user.role}")
    else:
        print("Admin user not found!")
    
    # Check all users
    print("\nAll users:")
    users = db.query(User).all()
    for user in users:
        print(f"  {user.id}: {user.username} ({user.email}) - Active: {user.is_active}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close() 