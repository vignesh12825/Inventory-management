#!/bin/bash

# Start both backend and frontend services
# This script runs both services in the same container for Railway deployment

echo "🚀 Starting Inventory Management System..."

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start backend service
echo "🔧 Starting FastAPI backend..."
cd /app/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend service
echo "🎨 Starting React frontend..."
cd /app/frontend
serve -s build -l 3000 &
FRONTEND_PID=$!

echo "✅ Both services started!"
echo "📊 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 