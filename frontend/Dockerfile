# Frontend Dockerfile for Inventory Management System
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Clear any existing npm configuration and set up for public registry only
RUN npm config delete registry
RUN npm config delete _auth
RUN npm config delete _authToken
RUN npm config delete username
RUN npm config delete password
RUN npm config delete email
RUN npm config set registry https://registry.npmjs.org/
RUN npm config set strict-ssl false

# Install dependencies with explicit public registry
RUN npm install --omit=dev --no-audit --no-fund --registry=https://registry.npmjs.org/

# Copy source code
COPY . .

# Build the React app
RUN npm run build

# Install serve globally with explicit registry
RUN npm install -g serve --registry=https://registry.npmjs.org/

# Create non-root user
RUN adduser -D appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 3000

# Start the app
CMD ["serve", "-s", "build", "-l", "3000"] 