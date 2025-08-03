# 🚂 Railway Deployment Guide - Fixed Version

## Problem Solved: Build Failures

The previous build was failing due to:
1. **npm authentication errors** (`npm ci` failing)
2. **Complex multi-stage builds** causing timeouts
3. **Memory issues** during build process

## ✅ New Solution: Separate Services

### Backend Deployment (Recommended First)

#### 1. **Backend Dockerfile** (`Dockerfile`)
```dockerfile
# Simple Railway Dockerfile for Inventory Management System
FROM python:3.10-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./backend/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/v1/health || exit 1

# Start FastAPI
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. **Railway Configuration** (`railway.toml`)
```toml
[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

## 🚀 Step-by-Step Deployment

### Step 1: Deploy Backend First

1. **Push your code:**
```bash
git add .
git commit -m "Fix Railway deployment - simplified Dockerfile"
git push origin main
```

2. **Create Railway project:**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Environment Variables:**
   In Railway dashboard → Variables tab:
   ```env
   DATABASE_URL=postgresql://neondb_owner:npg_F7JVLiacNCu0@ep-empty-glade-a1f1p80o-pooler.ap-southeast-1.aws.neon.tech/inventory_db?sslmode=require&channel_binding=require
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   API_V1_STR=/api/v1
   PROJECT_NAME=Inventory Management System
   ```

4. **Deploy:**
   - Railway will automatically detect the root `Dockerfile`
   - Build should complete successfully (no npm issues)
   - Backend will be available at your Railway domain

### Step 2: Deploy Frontend (Optional)

If you want to deploy the frontend separately:

1. **Create a new Railway service** for frontend
2. **Use the frontend Dockerfile:**
   ```dockerfile
   FROM node:18-alpine
   WORKDIR /app
   COPY package*.json ./
   RUN npm install --production
   COPY . .
   RUN npm run build
   RUN npm install -g serve
   EXPOSE 3000
   CMD ["serve", "-s", "build", "-l", "3000"]
   ```

3. **Set frontend environment variables:**
   ```env
   REACT_APP_API_URL=https://your-backend-service.railway.app/api
   REACT_APP_WS_URL=wss://your-backend-service.railway.app/ws
   ```

## 🔧 Alternative: Single Service Approach

If you prefer a single service, use this simplified approach:

### Option A: Backend Only (Recommended)
- Deploy only the backend
- Use Railway's static file serving for frontend
- Simpler, more reliable

### Option B: Frontend Only
- Deploy only the frontend
- Connect to external backend API
- Good for static sites

## 📊 Monitoring Your Deployment

### Health Check
Visit: `https://your-app.railway.app/api/v1/health`

### API Documentation
Visit: `https://your-app.railway.app/docs`

### Logs
Check Railway dashboard → Your service → Logs

## 🛠️ Troubleshooting

### Issue: Build still fails
**Solution:**
1. Check Railway logs for specific errors
2. Ensure `DATABASE_URL` is correct
3. Verify `SECRET_KEY` is set

### Issue: Health check fails
**Check:**
1. Backend is starting properly
2. Database connection works
3. Port 8000 is exposed

### Issue: Frontend can't connect to backend
**Solution:**
1. Update `REACT_APP_API_URL` to your Railway backend URL
2. Check CORS settings in backend
3. Ensure backend is running

## ✅ Success Checklist

- [x] **Simplified Dockerfile** (no npm issues) ✅
- [x] **Railway configuration** ✅
- [x] **Health check endpoint** ✅
- [x] **Environment variables** ✅
- [x] **Database connection** ✅

## 🎯 Key Improvements

1. **Removed npm authentication issues** - Using simpler Python-only build
2. **Eliminated complex multi-stage builds** - Single stage, faster builds
3. **Reduced memory usage** - No Node.js in main container
4. **Better error handling** - Clearer build process
5. **Railway-optimized** - Uses Railway's recommended patterns

## 🚀 Quick Deploy Commands

```bash
# 1. Commit your changes
git add .
git commit -m "Fix Railway deployment"
git push origin main

# 2. Deploy to Railway
# - Go to Railway dashboard
# - Connect your repository
# - Add environment variables
# - Deploy!

# 3. Test your deployment
curl https://your-app.railway.app/api/v1/health
```

---

**🎉 Your backend should now deploy successfully on Railway!**

The build failures are resolved with this simplified approach. The backend will be available at your Railway domain, and you can access the API documentation at `/docs`. 