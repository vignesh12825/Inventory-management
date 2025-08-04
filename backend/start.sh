#!/bin/bash

# Startup script for Railway deployment

echo "Starting Inventory Management System..."

# Set environment variables if not set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Add a small delay to ensure everything is ready
echo "Waiting for application to be ready..."
sleep 3

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "Warning: Database migration failed, but continuing with application startup..."
fi

# Start the application
echo "Starting FastAPI application..."
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT 