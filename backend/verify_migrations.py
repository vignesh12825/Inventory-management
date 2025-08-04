#!/usr/bin/env python3
"""
Database Migration Verification Script
This script checks if all migrations have been applied and verifies table existence.
"""

import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} successful")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False, e.stderr

def check_migration_status():
    """Check current migration status"""
    print("📊 Checking Migration Status")
    print("=" * 40)
    
    # Check current migration
    success, output = run_command("alembic current", "Current migration")
    if success:
        print(f"Current migration: {output.strip()}")
    
    # Check migration history
    success, output = run_command("alembic history", "Migration history")
    if success:
        print(f"Migration history:\n{output}")
    
    return success

def check_database_tables():
    """Check if key tables exist"""
    print("\n📋 Checking Database Tables")
    print("=" * 40)
    
    # Import database components
    try:
        sys.path.append(str(Path(__file__).parent))
        from app.core.database import engine
        
        # Test connection and check tables
        with engine.connect() as conn:
            # Check stock_alerts table
            result = conn.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'stock_alerts'
            """)
            stock_alerts_exists = result.fetchone() is not None
            
            # Check other key tables
            tables_to_check = [
                'users', 'products', 'categories', 'locations', 
                'inventory', 'purchase_orders', 'suppliers'
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
            else:
                print("✅ All key tables exist")
            
            # Specific check for stock_alerts
            if stock_alerts_exists:
                print("✅ stock_alerts table exists")
            else:
                print("❌ stock_alerts table is missing")
            
            return stock_alerts_exists and len(missing_tables) == 0
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Database Migration Verification")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("alembic.ini").exists():
        print("❌ Error: alembic.ini not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    # Check migration status
    migration_ok = check_migration_status()
    
    # Check database tables
    tables_ok = check_database_tables()
    
    print("\n" + "=" * 50)
    if migration_ok and tables_ok:
        print("🎉 VERIFICATION PASSED!")
        print("✅ All migrations applied successfully")
        print("✅ All required tables exist")
        print("✅ Your database is ready for use")
    else:
        print("❌ VERIFICATION FAILED!")
        if not migration_ok:
            print("❌ Migration status check failed")
        if not tables_ok:
            print("❌ Database tables check failed")
        print("\n💡 To fix this, run:")
        print("   python run_migrations.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 