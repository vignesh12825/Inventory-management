# Simple Railway Dockerfile for Inventory Management System
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first for caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application files to app directory
COPY backend/ ./app/

# Copy main.py to root
COPY main.py .

# Copy startup script to root
COPY start_railway.py .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port (Railway will set the PORT environment variable)
EXPOSE $PORT

# Health check - use /ping for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ping || exit 1

# Start the FastAPI application using the startup script
CMD ["python", "start_railway.py"] 