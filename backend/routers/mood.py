import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any
from agno_agents.mood_agent import MoodTrackerAgent

router = APIRouter(tags=["😊 Mood Tracking"])
agent = MoodTrackerAgent()

class MoodIn(BaseModel):
    """Mood logging input"""
    user_id: int = Field(..., description="User ID", example=1)
    mood: str = Field(..., description="User's current mood", example="happy")

class MoodResponse(BaseModel):
    """Mood logging response"""
    ok: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    mood_logged: str = Field(None, description="Logged mood")
    mood_score: int = Field(None, description="Mood score (1-4)")
    next_step: str = Field(None, description="Suggested next action")

@router.post("/mood", response_model=MoodResponse)
def log_mood(inp: MoodIn) -> MoodResponse:
    """
    😊 **Log User Mood**
    
    Record the user's current emotional state with validation and scoring.
    
    **Valid Moods:**
    - **Excellent (4):** happy, great, excellent, amazing, fantastic
    - **Good (3):** good, ok, okay, fine, neutral, alright  
    - **Low (2):** sad, down, low, disappointed, upset
    - **Poor (1):** awful, terrible, depressed, angry, frustrated
    
    **Example:** `{"user_id": 1, "mood": "happy"}`
    """
    result = agent.log_mood(inp.user_id, inp.mood)
    return MoodResponse(
        ok=result.get("success", False),
        message=result.get("message", ""),
        mood_logged=inp.mood,
        mood_score=result.get("mood_score", 0),
        next_step=result.get("next_step", "")
    )
