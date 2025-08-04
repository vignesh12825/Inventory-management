#!/usr/bin/env python3
"""
Database Migration Script for Inventory Management System
This script runs Alembic migrations to ensure the database schema is up to date.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    print("🔍 Checking database connection...")
    
    # Try to import and test database connection
    try:
        sys.path.append(str(Path(__file__).parent))
        from app.core.config import settings
        from app.core.database import engine
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting Database Migration Process")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("alembic.ini").exists():
        print("❌ Error: alembic.ini not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot connect to database. Please check your DATABASE_URL environment variable.")
        sys.exit(1)
    
    # Run migrations
    print("\n📦 Running database migrations...")
    success = run_command("alembic upgrade head", "Database migrations")
    
    if success:
        print("\n✅ Migration process completed successfully!")
        print("🎉 Your database schema is now up to date.")
    else:
        print("\n❌ Migration process failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 