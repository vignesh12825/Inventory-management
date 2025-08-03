# 🐳 Docker Setup for Inventory Management System

## Overview
This project uses Docker Compose to run both the frontend (React) and backend (FastAPI) services with your external Neon.tech PostgreSQL database.

## Quick Start

### 1. Build and Run
```bash
# Build and start all services
docker compose up --build

# Run in detached mode
docker compose up -d --build

# Stop services
docker compose down
```

### 2. View Logs
```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs frontend
docker compose logs backend

# Follow logs in real-time
docker compose logs -f
```

## Environment Variables

### Backend Environment Variables
The backend service uses these environment variables (configured in `docker-compose.yml`):

```env
DATABASE_URL=postgresql://neondb_owner:npg_F7JVLiacNCu0@ep-empty-glade-a1f1p80o-pooler.ap-southeast-1.aws.neon.tech/inventory_db?sslmode=require&channel_binding=require
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1
PROJECT_NAME=Inventory Management System
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend Environment Variables
The frontend service uses these environment variables:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## Service Architecture

### Frontend Service
- **Port**: 3000
- **Framework**: React with TypeScript
- **Build**: Production build with `serve`
- **Dependencies**: Node.js 18 Alpine

### Backend Service
- **Port**: 8000
- **Framework**: FastAPI
- **Database**: External Neon.tech PostgreSQL
- **Dependencies**: Python 3.10 with uvicorn

## Development vs Production

### Development
```bash
# For development with hot reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production
```bash
# For production deployment
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Platform Deployment

### Render.com
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Use the `docker-compose.yml` file
4. Set build command: `docker compose up --build`

### Railway
1. Connect your GitHub repository
2. Railway will automatically detect the `docker-compose.yml`
3. Set environment variables in Railway dashboard
4. Deploy automatically

### Heroku
1. Add `heroku.yml` file for container deployment
2. Set environment variables in Heroku dashboard
3. Deploy using Heroku container registry

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check if database is accessible
docker compose exec backend python -c "
import psycopg2
try:
    conn = psycopg2.connect('$DATABASE_URL')
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

#### 2. Frontend Build Issues
```bash
# Rebuild frontend only
docker compose build frontend

# Check frontend logs
docker compose logs frontend
```

#### 3. Backend API Issues
```bash
# Check backend logs
docker compose logs backend

# Test API endpoint
curl http://localhost:8000/api/v1/health
```

### Debug Commands

```bash
# Access frontend container
docker compose exec frontend sh

# Access backend container
docker compose exec backend bash

# Check service status
docker compose ps

# View resource usage
docker stats
```

## Performance Optimizations

### Build Optimizations
- **Layer Caching**: Package files copied first for better cache utilization
- **Multi-stage Builds**: Separate build and runtime stages
- **Alpine Images**: Smaller base images for reduced size

### Runtime Optimizations
- **Volume Mounts**: Development code changes reflected immediately
- **Network Isolation**: Services communicate via internal network
- **Resource Limits**: Configurable CPU and memory limits

## Security Considerations

### Environment Variables
- Never commit sensitive data to version control
- Use secrets management in production platforms
- Rotate database credentials regularly

### Container Security
- Run containers as non-root users in production
- Keep base images updated
- Scan images for vulnerabilities

## Monitoring

### Health Checks
```bash
# Frontend health check
curl http://localhost:3000

# Backend health check
curl http://localhost:8000/api/v1/health
```

### Logs
```bash
# Structured logging
docker compose logs --tail=100

# Real-time monitoring
docker compose logs -f
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend service
docker compose up --scale backend=3

# Scale frontend service
docker compose up --scale frontend=2
```

### Load Balancing
For production, consider using:
- Nginx reverse proxy
- Traefik for automatic SSL
- Cloud load balancers

---

**Note**: Remember to update the `DATABASE_URL` and `SECRET_KEY` for production deployments! 