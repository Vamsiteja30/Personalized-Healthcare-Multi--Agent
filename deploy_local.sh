#!/bin/bash
# HealthSync Local Deployment Script (Bash)
# Assignment: Personalized Healthcare Multi-Agent Demo

echo "🚀 HealthSync Local Deployment Starting..."
echo "================================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Python3 and Node.js found"

# Check environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set. Setting up demo mode..."
    export GEMINI_API_KEY="demo_mode"
else
    echo "✅ GEMINI_API_KEY configured"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data backups logs
echo "✅ Directories created"

# Start backend
echo "🐍 Starting backend..."
python3 run_backend.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 10

# Check backend health
echo "🔍 Checking backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend service healthy (http://localhost:8000)"
else
    echo "❌ Backend service not responding"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 15

# Check frontend health
echo "🔍 Checking frontend health..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend service healthy (http://localhost:3000)"
else
    echo "❌ Frontend service not responding"
fi

# Final status
echo "================================================"
echo "🎉 HealthSync Local Deployment Complete!"
echo ""
echo "📊 Access your application:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "🔧 Management Commands:"
echo "   Stop services: kill $BACKEND_PID $FRONTEND_PID"
echo "   View logs:     tail -f logs/*.log"
echo ""
echo "🏥 Demo Commands:"
echo "   Mood tracking: 'I'm feeling happy'"
echo "   CGM logging:   'My glucose is 120'"
echo "   Food logging:  'I ate rice and dal'"
echo "   Meal planning: 'Generate meal plan'"
echo "   Q&A:          'What is diabetes?'"
echo ""
echo "✨ HealthSync is ready for your assignment demo!"

# Keep script running
wait
