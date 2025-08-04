#!/bin/bash

# Railway Startup Script with Database Migration
set -e

echo "🚀 Starting Inventory Management System on Railway..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYTHONUNBUFFERED=1

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Function to run migrations with retry logic
run_migrations() {
    echo "📦 Running database migrations..."
    
    # Try to run migrations with retry logic
    for i in {1..5}; do
        echo "Attempt $i of 5..."
        
        if alembic upgrade head; then
            echo "✅ Database migrations completed successfully!"
            return 0
        else
            echo "❌ Migration attempt $i failed"
            if [ $i -lt 5 ]; then
                echo "⏳ Waiting 10 seconds before retry..."
                sleep 10
            fi
        fi
    done
    
    echo "❌ All migration attempts failed"
    return 1
}

# Check if we can connect to the database
check_database() {
    echo "🔍 Checking database connection..."
    
    # Try to import and test database connection
    python3 -c "
import sys
sys.path.append('.')
try:
    from app.core.config import settings
    from app.core.database import engine
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"
}

# Main startup sequence
echo "🔧 Starting setup process..."

# Check database connection
if check_database; then
    echo "✅ Database connection verified"
else
    echo "❌ Cannot connect to database"
    exit 1
fi

# Run migrations
if run_migrations; then
    echo "✅ Setup completed successfully"
else
    echo "⚠️  Migration failed, but continuing with application startup..."
fi

# Start the application
echo "🚀 Starting FastAPI application..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT 