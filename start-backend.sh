#!/bin/bash

# Startup script for Railway deployment
echo "🚀 Starting Inventory Management System Backend..."

# Set environment variables
export PYTHONPATH=/app/backend
export PYTHONUNBUFFERED=1

# Change to backend directory
cd /app/backend

# Test database connection
echo "🔍 Testing database connection..."
python -c "
import os
from sqlalchemy import create_engine
from app.core.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Start the application
echo "🔧 Starting FastAPI application..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info 