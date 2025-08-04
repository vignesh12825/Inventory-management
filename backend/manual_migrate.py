#!/usr/bin/env python3
"""
Manual Database Migration Script for Railway
This script can be run directly in Railway's terminal to force run migrations.
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

def check_environment():
    """Check if we're in the right environment"""
    print("🔍 Checking environment...")
    
    # Check if we're in the right directory
    if not Path("alembic.ini").exists():
        print("❌ Error: alembic.ini not found. Please run this script from the backend directory.")
        return False
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable is not set.")
        return False
    
    print(f"✅ Environment check passed")
    print(f"📊 Database URL: {database_url[:20]}...")
    return True

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
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

def run_migrations_with_retry():
    """Run migrations with retry logic"""
    print("📦 Running database migrations with retry logic...")
    
    for attempt in range(1, 6):
        print(f"\n🔄 Attempt {attempt} of 5...")
        
        # Check current migration status
        success, output = run_command("alembic current", f"Checking current migration (attempt {attempt})")
        if success:
            print(f"Current migration: {output.strip()}")
        
        # Run migrations
        success = run_command("alembic upgrade head", f"Running migrations (attempt {attempt})")
        if success:
            print("✅ Migrations completed successfully!")
            return True
        else:
            print(f"❌ Migration attempt {attempt} failed")
            if attempt < 5:
                print("⏳ Waiting 10 seconds before retry...")
                time.sleep(10)
    
    print("❌ All migration attempts failed")
    return False

def verify_tables():
    """Verify that key tables were created"""
    print("\n📋 Verifying table creation...")
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from app.core.database import engine
        
        with engine.connect() as conn:
            # Check key tables
            tables_to_check = [
                'users', 'products', 'categories', 'locations', 
                'inventory', 'purchase_orders', 'suppliers', 'stock_alerts'
            ]
            
            existing_tables = []
            missing_tables = []
            
            for table in tables_to_check:
                result = conn.execute(f"""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = '{table}'
                """)
                if result.fetchone():
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)
            
            print(f"✅ Existing tables: {', '.join(existing_tables)}")
            if missing_tables:
                print(f"❌ Missing tables: {', '.join(missing_tables)}")
                return False
            else:
                print("✅ All key tables exist")
                return True
                
    except Exception as e:
        print(f"❌ Table verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Manual Database Migration for Railway")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        print("❌ Cannot connect to database. Please check your DATABASE_URL.")
        sys.exit(1)
    
    # Run migrations with retry
    if run_migrations_with_retry():
        print("\n✅ Migration process completed successfully!")
        
        # Verify tables
        if verify_tables():
            print("🎉 All tables created successfully!")
            print("✅ Your database is ready for use")
        else:
            print("⚠️  Migrations ran but some tables may be missing")
    else:
        print("\n❌ Migration process failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 