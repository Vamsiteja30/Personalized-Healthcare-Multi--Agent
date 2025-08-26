import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from agno_agents.meal_planner_agent import MealPlannerAgent

router = APIRouter(tags=["🍽️ Meal Planning"])
agent = MealPlannerAgent()

class MealIn(BaseModel):
    """Meal plan request input"""
    user_id: int = Field(..., description="User ID", example=1)

class MealSuggestion(BaseModel):
    """Individual meal suggestion"""
    meal_type: str = Field(None, description="Type of meal", example="Breakfast")
    meal: str = Field(..., description="Meal description", example="Oatmeal with berries and nuts")
    macros: Optional[Dict[str, int]] = Field(None, description="Nutritional information")
    benefits: str = Field(None, description="Health benefits")
    timing: str = Field(None, description="Suggested eating time")

class MealPlanResponse(BaseModel):
    """Meal plan response"""
    ok: bool = Field(..., description="Success status")
    latest_cgm: Optional[float] = Field(None, description="Latest glucose reading")
    personalized_message: str = Field(None, description="Personalized message")
    glucose_analysis: str = Field(None, description="Glucose level analysis")
    suggestions: List[MealSuggestion] = Field(default=[], description="Meal suggestions")

@router.post("/mealplan", response_model=MealPlanResponse)
def mealplan(inp: MealIn) -> MealPlanResponse:
    """
    🍽️ **Generate Personalized Meal Plan**
    
    Creates a customized meal plan based on:
    - **User Profile:** Dietary preferences, medical conditions
    - **Health Data:** Latest glucose readings, mood state  
    - **Food History:** Recent meals and patterns
    
    **Algorithm considers:**
    - Glucose levels (adjusts carbs/glycemic index)
    - Medical conditions (diabetes, hypertension, etc.)
    - Dietary restrictions (vegetarian, vegan, etc.)
    - Mood state (comfort foods vs. energy foods)
    - Local cuisine preferences
    
    **Returns:** 3 personalized meal suggestions with nutritional info
    """
    result = agent.plan(inp.user_id)
    return MealPlanResponse(
        ok=result.get("success", False),
        latest_cgm=result.get("latest_cgm", None),
        personalized_message=result.get("message", ""),
        glucose_analysis=result.get("glucose_analysis", ""),
        suggestions=result.get("suggestions", [])
    )
