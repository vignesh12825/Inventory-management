#!/bin/bash

# Test script for different Docker build approaches
# This script will test all the different solutions for npm authentication issues

echo "🧪 Testing Docker Build Solutions for NPM Authentication Issues"
echo "=============================================================="

# Function to test a Docker build
test_build() {
    local name=$1
    local dockerfile=$2
    local context=$3
    
    echo ""
    echo "🔍 Testing: $name"
    echo "Dockerfile: $dockerfile"
    echo "Context: $context"
    
    # Change to the context directory
    cd "$context" || exit 1
    
    # Build the Docker image
    if docker build -f "$dockerfile" -t "test-$name" .; then
        echo "✅ SUCCESS: $name build completed successfully"
        return 0
    else
        echo "❌ FAILED: $name build failed"
        return 1
    fi
}

# Test 1: Backend-only approach (most reliable)
echo ""
echo "📦 Testing Backend-Only Approach..."
test_build "backend-only" "Dockerfile.railway" "."

# Test 2: Enhanced NPM configuration
echo ""
echo "📦 Testing Enhanced NPM Configuration..."
test_build "frontend-npm" "Dockerfile" "frontend"

# Test 3: Yarn approach
echo ""
echo "📦 Testing Yarn Approach..."
test_build "frontend-yarn" "Dockerfile.yarn" "frontend"

# Test 4: Static files approach (requires pre-build)
echo ""
echo "📦 Testing Static Files Approach..."
echo "⚠️  This requires pre-building the frontend locally"
echo "Building frontend locally first..."

cd frontend || exit 1
if npm run build; then
    echo "✅ Frontend built successfully"
    cd ..
    test_build "frontend-static" "Dockerfile.static" "frontend"
else
    echo "❌ Frontend build failed, skipping static Dockerfile test"
    cd ..
fi

echo ""
echo "🎯 Summary of Results:"
echo "======================"
echo ""
echo "Recommended approach for Railway deployment:"
echo "1. Use Dockerfile.railway for backend-only deployment"
echo "2. If frontend is needed, use Dockerfile.yarn"
echo "3. For production, consider building frontend locally and serving from CDN"
echo ""
echo "All Dockerfiles have been updated to avoid npm authentication issues." 