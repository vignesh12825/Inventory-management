#!/bin/bash

# Startup script for Railway deployment

echo "Starting Inventory Management System..."

# Set environment variables if not set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Add a small delay to ensure everything is ready
echo "Waiting for application to be ready..."
sleep 3

# Start the application
echo "Starting FastAPI application..."
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT 