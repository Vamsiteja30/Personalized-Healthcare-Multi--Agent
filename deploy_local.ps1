# HealthSync Local Deployment Script (PowerShell)
# Assignment: Personalized Healthcare Multi-Agent Demo

Write-Host "🚀 HealthSync Local Deployment Starting..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Check Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js 18+ first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Python and Node.js found" -ForegroundColor Green

# Check environment variables
if (-not $env:GEMINI_API_KEY) {
    Write-Host "⚠️  GEMINI_API_KEY not set. Setting up demo mode..." -ForegroundColor Yellow
    $env:GEMINI_API_KEY = "demo_mode"
} else {
    Write-Host "✅ GEMINI_API_KEY configured" -ForegroundColor Green
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" }
if (-not (Test-Path "backups")) { New-Item -ItemType Directory -Path "backups" }
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }
Write-Host "✅ Directories created" -ForegroundColor Green

# Start backend
Write-Host "🐍 Starting backend..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python run_backend.py
} | Out-Null

# Wait for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check backend health
Write-Host "🔍 Checking backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend service healthy (http://localhost:8000)" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend service not responding properly" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Backend service not responding" -ForegroundColor Red
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    exit 1
}

# Start frontend
Write-Host "🎨 Starting frontend..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python run_frontend.py
} | Out-Null

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check frontend health
Write-Host "🔍 Checking frontend health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend service healthy (http://localhost:3000)" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend service not responding properly" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend service not responding" -ForegroundColor Red
}

# Final status
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🎉 HealthSync Local Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Access your application:" -ForegroundColor White
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor White
Write-Host "   Stop services: Get-Job | Stop-Job" -ForegroundColor Yellow
Write-Host "   View logs:     Get-Job | Receive-Job" -ForegroundColor Yellow
Write-Host "   Clean up:      Get-Job | Remove-Job" -ForegroundColor Yellow
Write-Host ""
Write-Host "🏥 Demo Commands:" -ForegroundColor White
Write-Host "   Mood tracking: 'I'm feeling happy'" -ForegroundColor Green
Write-Host "   CGM logging:   'My glucose is 120'" -ForegroundColor Green
Write-Host "   Food logging:  'I ate rice and dal'" -ForegroundColor Green
Write-Host "   Meal planning: 'Generate meal plan'" -ForegroundColor Green
Write-Host "   Q&A:          'What is diabetes?'" -ForegroundColor Green
Write-Host ""
Write-Host "✨ HealthSync is ready for your assignment demo!" -ForegroundColor Green
