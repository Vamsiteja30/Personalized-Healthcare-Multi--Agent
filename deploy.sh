#!/bin/bash
# HealthSync Docker Deployment Script
# Assignment: Personalized Healthcare Multi-Agent Demo

echo "🚀 HealthSync Docker Deployment Starting..."
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Check environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set. Setting up demo mode..."
    export GEMINI_API_KEY="demo_mode"
else
    echo "✅ GEMINI_API_KEY configured"
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Remove old images and containers
echo "🧹 Cleaning up old images and containers..."
docker system prune -f
docker builder prune -f

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check backend health
echo "🔍 Checking backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend service healthy (http://localhost:8000)"
else
    echo "❌ Backend service not responding"
    docker-compose logs backend
    exit 1
fi

# Check frontend health
echo "🔍 Checking frontend health..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend service healthy (http://localhost:3000)"
else
    echo "❌ Frontend service not responding"
    docker-compose logs frontend
fi

# Final status
echo "================================================"
echo "🎉 HealthSync Docker Deployment Complete!"
echo ""
echo "📊 Access your application:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "🏥 Demo Commands:"
echo "   Mood tracking: 'I'm feeling happy'"
echo "   CGM logging:   'My glucose is 120'"
echo "   Food logging:  'I ate rice and dal'"
echo "   Meal planning: 'Generate meal plan'"
echo "   Q&A:          'What is diabetes?'"
echo ""
echo "✨ HealthSync is ready for your assignment demo!"
