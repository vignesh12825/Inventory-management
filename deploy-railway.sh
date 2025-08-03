#!/bin/bash

# Railway Deployment Script for Inventory Management System

echo "🚂 Railway Deployment Script"
echo "=============================="

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please login first:"
    echo "railway login"
    exit 1
fi

echo "✅ Railway CLI is ready"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Project structure looks good"

# Check if railway.toml exists
if [ ! -f "railway.toml" ]; then
    echo "⚠️  railway.toml not found. Creating it..."
    cat > railway.toml << EOF
[build]
builder = "dockerfile"

[deploy]
startCommand = "docker compose up"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
EOF
    echo "✅ Created railway.toml"
fi

echo ""
echo "📋 Deployment Checklist:"
echo "1. ✅ Railway CLI installed"
echo "2. ✅ Logged in to Railway"
echo "3. ✅ Project structure verified"
echo "4. ✅ railway.toml configured"
echo ""
echo "🔧 Next Steps:"
echo "1. Go to Railway Dashboard: https://railway.app/dashboard"
echo "2. Create a new project"
echo "3. Connect your GitHub repository"
echo "4. Add environment variables:"
echo "   - DATABASE_URL (your Neon.tech URL)"
echo "   - SECRET_KEY (generate a strong secret)"
echo "5. Deploy!"
echo ""
echo "📚 For detailed instructions, see: RAILWAY_DEPLOYMENT.md"
echo ""
echo "🚀 Ready to deploy!" 