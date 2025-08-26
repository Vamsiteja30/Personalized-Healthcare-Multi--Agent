# NOVA Docker Setup Guide

This guide explains how to deploy the NOVA Healthcare Multi-Agent application using Docker.

##  Prerequisites requried 

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- 5GB free disk space

##  Quick Start to do 

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd healthcare-multi-agent-starter
```

### 2. Set Environment Variables (Optional)
Create a `.env` file in the root directory:
```bash
# Google Gemini API Key (optional - demo mode available)
GEMINI_API_KEY=your_gemini_api_key_here

# Database settings
DATABASE_PATH=/app/data/healthcare.db

# Model settings
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Build and Run
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

##  Project Structure

```
healthcare-multi-agent-starter/
├── Dockerfile.backend          # Backend container definition
├── Dockerfile.frontend         # Frontend container definition
├── docker-compose.yml          # Multi-service orchestration
├── nginx.conf                  # Nginx configuration
├── .dockerignore              # Files to exclude from build
├── backend/                   # FastAPI backend code
├── frontend/                  # React frontend code
├── agents/                    # AI agent implementations
└── data/                      # Persistent data storage
```

##  Docker Services

### Backend Service (`NOVA-backend`)
- **Image**: Python 3.11-slim
- **Port**: 8000
- **Features**:
  - FastAPI application
  - SQLite database
  - AI agents (Mood, CGM, Food, Meal Planner)
  - Google Gemini integration
  - Health check endpoint

### Frontend Service (`NOVA-frontend`)
- **Image**: Node.js 18 + Nginx
- **Port**: 3000 (mapped to nginx port 80)
- **Features**:
  - React application
  - Power BI-style dashboard
  - Nginx reverse proxy
  - Static file serving
  - API proxy to backend

##  Docker Commands ##

### Build Services
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Run Services
```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# Start specific service
docker-compose up backend
docker-compose up frontend
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### View Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Health Checks
```bash
# Check service status
docker-compose ps

# Check health status
docker inspect healthsync-backend | grep Health -A 10
docker inspect healthsync-frontend | grep Health -A 10
```

##  Troubleshooting 

### Common Issues 

#### 1. Port Already in Use
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000

# Kill processes if needed
kill -9 <PID>
```

#### 2. Build Failures
```bash
# Clean build cache
docker-compose build --no-cache

# Remove all containers and images
docker-compose down --rmi all
docker system prune -a
```

#### 3. Database Issues
```bash
# Reset database
docker-compose down
rm -rf data/
docker-compose up --build
```

#### 4. Frontend Not Loading
```bash
# Check nginx logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up frontend
```

### Debug Mode
```bash
# Run with debug logging
docker-compose up --build --verbose

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

##  Security Considerations

### Environment Variables
- Never commit API keys to version control
- Use `.env` files for sensitive data
- Consider using Docker secrets for production

### Network Security
- Services communicate via internal Docker network
- Only necessary ports are exposed
- Nginx provides rate limiting and security headers

### Data Persistence
- Database files are stored in `./data/` directory
- Volumes are mounted for data persistence
- Regular backups recommended

##  Monitoring

### Health Checks
Both services include health check endpoints:
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000/health`

### Logs
```bash
# View real-time logs
docker-compose logs -f

# Export logs
docker-compose logs > app.log
```

### Resource Usage
```bash
# Monitor resource usage
docker stats

# Check disk usage
docker system df
```

##  Production Deployment

### Environment Setup
```bash
# Create production environment file
cp .env.example .env.prod

# Set production variables
GEMINI_API_KEY=your_production_key
NODE_ENV=production
```

### Production Commands
```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Scaling
```bash
# Scale backend service
docker-compose up --scale backend=3

# Scale with load balancer
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

##  Updates and Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### Database Migrations
```bash
# Backup current data
cp -r data/ data_backup_$(date +%Y%m%d)

# Run migrations (if any)
docker-compose exec backend python -m alembic upgrade head
```

### Cleanup
```bash
# Remove unused containers, networks, images
docker system prune

# Remove all unused data
docker system prune -a --volumes
```

##  Support

For issues related to:
- **Docker setup**: Check this guide and troubleshooting section
- **Application features**: Refer to main README.md
- **API documentation**: Visit http://localhost:8000/docs


