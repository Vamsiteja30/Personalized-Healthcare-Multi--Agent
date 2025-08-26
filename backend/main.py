# backend/main.py
from __future__ import annotations
import pathlib
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
# from backend.routers import agno



# Import DB module; it runs ensure_tables() on import
from backend.services import db

# Routers (module style keeps it simple)
from backend.routers import greet, mood, cgm, food, mealplan, interrupt, history, flow, users, voice

# Load .env from project root
env_path = pathlib.Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path, override=True)

app = FastAPI(
    title="NOVA - Next-Gen Optimized Virtual Assessment",
    description="""
    # 🌟 NOVA - Next-Gen Optimized Virtual Assessment
    
    A comprehensive healthcare management platform featuring AI-powered agents for personalized health tracking and recommendations.
    
    ## 🤖 Multi-Agent Architecture
    
    - **👋 Greeting Agent**: User validation and personalized welcome
    - **😊 Mood Tracker**: Emotional well-being monitoring with trends
    - **📊 CGM Monitor**: Continuous glucose monitoring with alerts
    - **🍽️ Food Logger**: Nutritional analysis and meal tracking
    - **🧠 Meal Planner**: AI-powered personalized meal planning
    - **🆘 Interrupt Agent**: General Q&A and emergency detection
    
    ## 💡 Key Features
    
    - **Real-time Chat Interface**: Natural language health tracking
    - **Smart Health Monitoring**: CGM alerts, mood analysis, food insights
    - **Personalized Recommendations**: Based on medical conditions & preferences
    - **Emergency Detection**: Automatic routing for urgent queries
    - **Synthetic Dataset**: 100 diverse user profiles for testing
    
    ## 🚀 Quick Start
    
    1. **Chat**: Use `/chat` endpoint for conversational interface
    2. **Commands**: `mood: happy`, `cgm: 120`, `food: chicken salad`, `plan`
    3. **Users**: Get user list from `/users` (ID 1-100)
    4. **Health Data**: Access trends via `/history/*` endpoints
    
    **Built with:** FastAPI, Google Gemini AI, SQLite, React
    """,
    version="1.0.0",
    contact={
        "name": "NOVA Team",
        "url": "https://github.com/your-repo/nova",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# (Optional) call again on startup; harmless if already done on import
@app.on_event("startup")
def _startup() -> None:
    try:
        db.ensure_tables()
        db.initialize_with_sample_data()
        print("✅ Database tables and sample data ensured successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        # Don't fail startup, just log the issue

@app.get("/health")
def health():
    """Health check endpoint with database and LLM status"""
    try:
        # Check database
        db_status = "ok"
        try:
            db.ensure_tables()
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Check LLM
        llm_status = "ok"
        try:
            from backend.services.llm import get_llm_client
            get_llm_client()
        except Exception as e:
            llm_status = f"error: {str(e)}"
        
        return {
            "status": "ok" if db_status == "ok" and llm_status == "ok" else "warning",
            "database": db_status,
            "llm": llm_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {
        "ok": True, 
        "message": "🌟 NOVA - Next-Gen Optimized Virtual Assessment", 
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Mount routers
app.include_router(greet.router)
app.include_router(mood.router)
app.include_router(cgm.router)
app.include_router(food.router)
app.include_router(mealplan.router)
app.include_router(interrupt.router)
app.include_router(history.router)
app.include_router(flow.router)
app.include_router(users.router)
app.include_router(voice.router)
# app.include_router(agno.router)