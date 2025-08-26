import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import APIRouter, Path
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from agno_agents.greeting_agent import GreetingAgent

router = APIRouter(prefix="/greet", tags=["👋 Greeting Agent"])
agent = GreetingAgent()

class GreetingResponse(BaseModel):
    """Personalized greeting response"""
    ok: bool = Field(..., description="Success status")
    message: str = Field(..., description="Personalized greeting message")
    user_data: Dict[str, Any] = Field(None, description="User profile data")

@router.get("/{user_id}", response_model=GreetingResponse)
def greet(
    user_id: int = Path(..., description="User ID to greet", example=1, ge=1, le=100)
) -> GreetingResponse:
    """
    👋 **Get Personalized Greeting**
    
    Returns a personalized welcome message for the specified user, including:
    - User's name and location
    - Dietary preferences
    - Medical conditions awareness
    - Encouraging health tracking message
    
    **User ID Range:** 1-100 (from synthetic dataset)
    """
    result = agent.greet(user_id)
    return GreetingResponse(
        ok=result.get("success", False),
        message=result.get("message", ""),
        user_data=result.get("user_info", {})
    )
