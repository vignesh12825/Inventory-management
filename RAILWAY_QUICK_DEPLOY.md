# 🚂 Quick Railway Deployment Guide

## Problem Solved: "Dockerfile does not exist"

Railway was looking for a `Dockerfile` in the root directory, but we had separate Dockerfiles in `frontend/` and `backend/` directories.

## ✅ Solution Implemented

### 1. **Root Dockerfile Created** (`Dockerfile`)
- Multi-stage build that builds both frontend and backend
- Includes both services in a single container
- Optimized for Railway deployment

### 2. **Railway Configuration** (`railway.toml`)
```toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "docker compose -f docker-compose.railway.yml up --build"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### 3. **Railway-Specific Docker Compose** (`docker-compose.railway.yml`)
- Simplified configuration for Railway
- Only includes backend service (Railway handles frontend separately)
- Proper health checks and environment variables

## 🚀 Quick Deploy Steps

### Step 1: Push Your Code
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 2: Connect to Railway
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### Step 3: Add Environment Variables
In Railway dashboard → Variables tab:

**Required:**
```env
DATABASE_URL=postgresql://neondb_owner:npg_F7JVLiacNCu0@ep-empty-glade-a1f1p80o-pooler.ap-southeast-1.aws.neon.tech/inventory_db?sslmode=require&channel_binding=require
SECRET_KEY=your-super-secret-key-change-this-in-production
```

**Optional:**
```env
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1
PROJECT_NAME=Inventory Management System
```

### Step 4: Deploy
Railway will automatically:
- ✅ Detect the root `Dockerfile`
- ✅ Build the application
- ✅ Deploy to Railway's infrastructure
- ✅ Set up health checks

## 🔧 Alternative Approaches

### Option A: Use Root Dockerfile (Recommended)
- Uses the `Dockerfile` in the root directory
- Builds both frontend and backend in one container
- Simpler deployment

### Option B: Use Docker Compose
- Uses `docker-compose.railway.yml`
- More flexible for complex setups
- Better for microservices

## 📊 Monitoring

### Check Deployment Status
1. Go to Railway dashboard
2. Click on your project
3. Check the "Deployments" tab

### View Logs
1. Click on your service
2. Go to "Logs" tab
3. Monitor real-time logs

### Health Check
Visit: `https://your-app.railway.app/api/v1/health`

## 🛠️ Troubleshooting

### Issue: "Dockerfile does not exist"
**Solution**: ✅ Fixed - Root `Dockerfile` created

### Issue: Build fails
**Check**:
1. Environment variables are set correctly
2. `DATABASE_URL` is valid
3. `SECRET_KEY` is provided

### Issue: Health check fails
**Check**:
1. Backend is starting properly
2. Database connection is working
3. Port 8000 is exposed

### Issue: Frontend not accessible
**Solution**: Railway will serve the frontend separately. The backend API will be available at your Railway domain.

## 🎯 Key Files for Railway

1. **`Dockerfile`** - Root Dockerfile for Railway
2. **`railway.toml`** - Railway configuration
3. **`docker-compose.railway.yml`** - Railway-specific compose
4. **`backend/app/main.py`** - Health check endpoint
5. **`.dockerignore`** - Optimizes build

## ✅ Success Checklist

- [ ] Root `Dockerfile` exists ✅
- [ ] `railway.toml` configured ✅
- [ ] Environment variables set
- [ ] Health check endpoint working ✅
- [ ] Database connection tested
- [ ] Deployment successful

---

**🎉 Your app should now deploy successfully on Railway!** 