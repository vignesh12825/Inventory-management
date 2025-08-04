#!/bin/bash

# Force Migration Script for Railway
echo "🚀 Force Migration Script Starting..."

# Set environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYTHONUNBUFFERED=1

# Wait for database
echo "⏳ Waiting for database..."
sleep 10

# Force run migrations
echo "📦 Running migrations..."
alembic upgrade head

# Verify tables
echo "🔍 Verifying tables..."
python3 -c "
import sys
sys.path.append('.')
from app.core.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' AND table_name = \'stock_alerts\'')
    if result.fetchone():
        print('✅ stock_alerts table exists')
    else:
        print('❌ stock_alerts table missing')
"

echo "✅ Migration script completed" 