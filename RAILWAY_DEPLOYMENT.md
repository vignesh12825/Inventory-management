# 🚂 Railway Deployment Guide

## Overview
This guide will help you deploy your Inventory Management System to Railway using Docker containers.

## Prerequisites
- Railway account
- GitHub repository with your code
- Neon.tech PostgreSQL database

## Step-by-Step Deployment

### 1. Connect Your Repository
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 2. Configure Environment Variables
In your Railway project dashboard, go to the "Variables" tab and add these environment variables:

#### Required Variables:
```env
DATABASE_URL=postgresql://neondb_owner:npg_F7JVLiacNCu0@ep-empty-glade-a1f1p80o-pooler.ap-southeast-1.aws.neon.tech/inventory_db?sslmode=require&channel_binding=require
SECRET_KEY=your-super-secret-key-change-this-in-production
```

#### Optional Variables (with defaults):
```env
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1
PROJECT_NAME=Inventory Management System
BACKEND_CORS_ORIGINS=["https://your-app-name.railway.app"]
REACT_APP_API_URL=https://your-app-name.railway.app/api
REACT_APP_WS_URL=wss://your-app-name.railway.app/ws
```

### 3. Configure Deployment Settings

#### Option A: Use Railway's Docker Compose Detection
Railway will automatically detect your `docker-compose.yml` file.

#### Option B: Manual Configuration
If automatic detection doesn't work:

1. Go to your project settings
2. Set the following:
   - **Build Command**: `docker compose build`
   - **Start Command**: `docker compose up`
   - **Health Check Path**: `/api/v1/health`

### 4. Deploy

#### Method 1: Automatic Deployment
1. Railway will automatically deploy when you push to your main branch
2. Monitor the deployment in the Railway dashboard

#### Method 2: Manual Deployment
1. Push your changes to GitHub
2. Go to Railway dashboard
3. Click "Deploy" button

## Troubleshooting Common Issues

### Issue 1: Nixpacks Build Failed
**Solution**: Railway is trying to use Nixpacks instead of Docker.

**Fix**:
1. Add `railway.toml` file to your project root:
```toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "docker compose up"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### Issue 2: Database Connection Failed
**Solution**: Check your DATABASE_URL format.

**Fix**:
1. Ensure your Neon.tech connection string is correct
2. Add SSL parameters: `?sslmode=require&channel_binding=require`
3. Test the connection locally first

### Issue 3: Frontend Can't Connect to Backend
**Solution**: Update CORS and API URLs.

**Fix**:
1. Set `BACKEND_CORS_ORIGINS` to include your Railway domain
2. Update `REACT_APP_API_URL` to use your Railway domain
3. Use HTTPS for production URLs

### Issue 4: Build Timeout
**Solution**: Optimize Docker builds.

**Fix**:
1. Use `.dockerignore` files (already included)
2. Ensure `requirements.txt` is copied before source code
3. Use multi-stage builds if needed

## Railway-Specific Optimizations

### 1. Use Railway Compose File
Create `railway-compose.yml` for Railway-specific settings:

```yaml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.railway
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8000:8000"
```

### 2. Health Checks
Add health check endpoint to your FastAPI app:

```python
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### 3. Environment Variables
Railway automatically provides these variables:
- `RAILWAY_PUBLIC_DOMAIN`: Your app's public domain
- `RAILWAY_STATIC_URL`: Static file serving URL
- `PORT`: Port to bind to (Railway sets this)

## Monitoring and Debugging

### View Logs
1. Go to Railway dashboard
2. Click on your service
3. Go to "Logs" tab
4. View real-time logs

### Debug Commands
```bash
# Check if containers are running
railway status

# View logs
railway logs

# Access container shell
railway shell

# Check environment variables
railway variables
```

## Production Considerations

### 1. Security
- Change `SECRET_KEY` to a strong random string
- Use environment variables for all sensitive data
- Enable HTTPS (Railway provides this automatically)

### 2. Performance
- Use Railway's auto-scaling features
- Monitor resource usage in Railway dashboard
- Set up alerts for high resource usage

### 3. Database
- Use connection pooling for PostgreSQL
- Monitor database performance
- Set up automated backups

## Custom Domain (Optional)
1. Go to Railway dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## SSL Certificate
Railway automatically provides SSL certificates for:
- `*.railway.app` domains
- Custom domains (after DNS verification)

## Scaling
Railway supports automatic scaling:
1. Go to service settings
2. Enable "Auto-scaling"
3. Set minimum and maximum instances
4. Configure scaling rules

## Backup and Recovery
1. **Database**: Use Neon.tech's built-in backup features
2. **Code**: Your GitHub repository serves as backup
3. **Environment Variables**: Export from Railway dashboard

## Cost Optimization
1. Use Railway's free tier for development
2. Monitor usage in Railway dashboard
3. Set up usage alerts
4. Consider Railway's paid plans for production

---

## Quick Deploy Checklist

- [ ] Repository connected to Railway
- [ ] Environment variables configured
- [ ] `railway.toml` file added
- [ ] `railway-compose.yml` created (optional)
- [ ] Health check endpoint implemented
- [ ] CORS settings updated
- [ ] Database connection tested
- [ ] SSL certificate verified
- [ ] Custom domain configured (if needed)

## Support
If you encounter issues:
1. Check Railway's [documentation](https://docs.railway.app/)
2. Review logs in Railway dashboard
3. Test locally with Docker Compose
4. Contact Railway support if needed

---

**Note**: Remember to update your `DATABASE_URL` and `SECRET_KEY` for production deployment! 