from dataclasses import dataclass
from typing import Any, Dict
from datetime import datetime
from backend.services.db import get_db, get_user

# Import all agents
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.greeting_agent import GreetingAgent
from agents.mood_agent import MoodAgent
from agents.cgm_agent import CGMAgent
from agents.food_agent import FoodIntakeAgent
from agents.meal_planner_agent import MealPlannerAgent
from agents.interrupt_agent import InterruptAgent

@dataclass
class OrchestratorResult:
    step: str
    result: Dict[str, Any]
    prompt: str

class Orchestrator:
    def __init__(self):
        # Initialize all agents
        self.greeting_agent = GreetingAgent()
        self.mood_agent = MoodAgent()
        self.cgm_agent = CGMAgent()
        self.food_agent = FoodIntakeAgent()
        self.meal_planner_agent = MealPlannerAgent()
        self.interrupt_agent = InterruptAgent()
    
    def process(self, user_id: int, text: str) -> OrchestratorResult:
        text = (text or "").strip()
        
        # Validate user exists
        user = get_user(user_id)
        if not user:
            return OrchestratorResult(
                "error", 
                {"error": "invalid_user"}, 
                "Invalid user ID. Please enter a valid user ID (1-100) to continue."
            )
        
        if not text:
            # First interaction - greet user
            result = self.greeting_agent.greet(user_id)
            return OrchestratorResult("greeting", result, result.get("message", "Welcome!"))
        
        # Parse command structure
        text_lower = text.lower()
        
        # Check for structured commands first
        if ":" in text and any(prefix in text_lower for prefix in ["mood:", "cgm:", "food:"]):
            return self._handle_structured_command(user_id, text)
        elif "plan" in text_lower or "meal" in text_lower:
            return self._handle_meal_plan(user_id)
        else:
            # Handle as general query through interrupt agent
            return self._handle_general_query(user_id, text)
    
    def _handle_structured_command(self, user_id: int, text: str) -> OrchestratorResult:
        """Handle structured commands like 'mood: happy', 'cgm: 120', 'food: rice'"""
        text_lower = text.lower()
        
        if text_lower.startswith("mood:"):
            mood = text.split(":", 1)[1].strip()
            result = self.mood_agent.log_mood(user_id, mood)
            return OrchestratorResult("mood", result, result.get("message", "Mood logged"))
        
        elif text_lower.startswith("cgm:"):
            reading_str = text.split(":", 1)[1].strip()
            try:
                reading = float(reading_str)
                result = self.cgm_agent.log_reading(user_id, reading)
                return OrchestratorResult("cgm", result, result.get("message", "CGM logged"))
            except ValueError:
                return OrchestratorResult("cgm", {"ok": False}, "Invalid glucose reading. Please enter a number.")
        
        elif text_lower.startswith("food:"):
            description = text.split(":", 1)[1].strip()
            result = self.food_agent.log_food(user_id, description)
            return OrchestratorResult("food", result, result.get("message", "Food logged"))
        
        else:
            return self._handle_general_query(user_id, text)
    
    def _handle_meal_plan(self, user_id: int) -> OrchestratorResult:
        """Handle meal plan generation"""
        result = self.meal_planner_agent.plan(user_id)
        return OrchestratorResult("meal_plan", result, result.get("message", "Meal plan generated"))
    
    def _handle_general_query(self, user_id: int, text: str) -> OrchestratorResult:
        """Handle general queries through interrupt agent"""
        result = self.interrupt_agent.handle_query(user_id, text)
        return OrchestratorResult("general", result, result.get("message", ""))
    
    def get_user_greeting(self, user_id: int) -> OrchestratorResult:
        """Get personalized greeting for a user"""
        result = self.greeting_agent.greet(user_id)
        return OrchestratorResult("greeting", result, result.get("message", "Welcome!"))
