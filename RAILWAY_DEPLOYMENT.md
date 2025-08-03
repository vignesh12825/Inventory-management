# Railway Deployment Guide

This guide explains how to deploy the Inventory Management System to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to GitHub
3. **Neon Database**: Your PostgreSQL database on Neon.tech

## Deployment Steps

### 1. Backend Deployment

1. **Connect to Railway**:
   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Choose the `backend` directory as the source

2. **Environment Variables**:
   Set these environment variables in Railway:
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_e6bOIDHrsf8T@ep-empty-glade-a1f1p80o-pooler.ap-southeast-1.aws.neon.tech/inventory_db?sslmode=require&channel_binding=require
   SECRET_KEY=your-super-secret-key-change-this-in-production
   DEBUG=False
   ENVIRONMENT=production
   ```

3. **Deploy**:
   - Railway will automatically detect the Python project
   - It will install dependencies from `requirements.txt`
   - The app will start using the `Procfile`

### 2. Frontend Deployment

1. **Create Second Service**:
   - In the same Railway project, click "New Service"
   - Choose "Deploy from GitHub repo"
   - Select the same repository but choose the `frontend` directory

2. **Environment Variables**:
   Set these environment variables for the frontend:
   ```
   REACT_APP_API_URL=https://your-backend-service-url.railway.app
   REACT_APP_API_VERSION=/api/v1
   ```

3. **Deploy**:
   - Railway will detect it's a Node.js project
   - It will run `npm install` and `npm start`

## Configuration Files

### Backend (`backend/`)

- `railway.toml`: Railway configuration
- `Procfile`: Process definition
- `requirements.txt`: Python dependencies
- `app/core/config.py`: Application configuration

### Frontend (`frontend/`)

- `railway.toml`: Railway configuration
- `package.json`: Node.js dependencies
- `src/services/api.ts`: API configuration

## Environment Variables

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon database connection string | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key` |
| `DEBUG` | Debug mode | `False` |
| `ENVIRONMENT` | Environment name | `production` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://backend.railway.app` |
| `REACT_APP_API_VERSION` | API version | `/api/v1` |

## Database Setup

1. **Run Migrations**:
   ```bash
   # Connect to your Railway backend service
   railway run --service backend alembic upgrade head
   ```

2. **Create Admin User**:
   ```bash
   railway run --service backend python create_admin_user.py
   ```

## Health Checks

- **Backend**: `/api/v1/health`
- **Frontend**: `/`

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Verify `DATABASE_URL` is correct
   - Check Neon database is accessible
   - Ensure SSL mode is set correctly

2. **Frontend Can't Connect to Backend**:
   - Verify `REACT_APP_API_URL` points to correct backend URL
   - Check CORS settings in backend
   - Ensure both services are deployed

3. **Build Failures**:
   - Check `requirements.txt` for backend
   - Check `package.json` for frontend
   - Verify all dependencies are listed

### Logs

View logs in Railway dashboard:
- Go to your service
- Click "Deployments" tab
- Click on latest deployment
- View logs for debugging

## Production Considerations

1. **Security**:
   - Change `SECRET_KEY` to a strong random string
   - Use environment variables for all secrets
   - Enable HTTPS (Railway handles this)

2. **Performance**:
   - Database connection pooling is handled by Neon
   - Railway auto-scales based on traffic
   - Consider CDN for static assets

3. **Monitoring**:
   - Railway provides basic monitoring
   - Set up custom alerts if needed
   - Monitor database performance on Neon

## Custom Domains

1. **Add Custom Domain**:
   - Go to Railway dashboard
   - Select your service
   - Go to "Settings" → "Domains"
   - Add your custom domain

2. **Update Environment Variables**:
   - Update `REACT_APP_API_URL` to use custom domain
   - Update CORS settings in backend

## Cost Optimization

- Railway charges based on usage
- Neon has a free tier for database
- Monitor usage in Railway dashboard
- Consider scaling down during low usage

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Neon Documentation: [neon.tech/docs](https://neon.tech/docs)
- Project Issues: Check GitHub repository 