"""
Agno Framework Orchestrator for NOVA Multi-Agent System
Follows the exact specifications from the assignment instructions
"""
import yaml
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.services.db import get_user
from agno_agents.greeting_agent import GreetingAgent
from agno_agents.mood_agent import MoodTrackerAgent
from agno_agents.cgm_agent import CGMAgent
from agno_agents.food_agent import FoodIntakeAgent
from agno_agents.meal_planner_agent import MealPlannerAgent
from agno_agents.interrupt_agent import InterruptAgent

@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    data: Dict[str, Any]
    message: str
    next_step: Optional[str] = None

class AgnoOrchestrator:
    """
    Agno Framework Orchestrator following exact specifications:
    
    5. Greeting Agent: Inputs: user ID, Action: validate user ID against dataset
    6. Mood Tracker Agent: Inputs: mood label, Action: store in memory, compute rolling average
    7. CGM Agent: Inputs: glucose reading, Action: validate range, flag alerts if outside 80–300
    8. Food Intake Agent: Inputs: meal description + timestamp, Action: categorize nutrients via LLM
    9. Meal Planner Agent: Inputs: dietary preference + medical conditions + latest mood/CGM, Action: call LLM for 3-meal plan
    10. Interrupt Agent: Inputs: free-form user query, Action: intercepts unrelated questions, answers via LLM, routes back
    """
    
    def __init__(self):
        """Initialize Agno workspace and all agents"""
        self.config = self._load_agno_config()
        self.agents = self._initialize_agents()
        self.current_flow = "health_tracking_flow"
        self.current_step = "greeting_agent"
        self.user_context = {}
    
    def _load_agno_config(self) -> Dict[str, Any]:
        """Load Agno workspace configuration"""
        config_path = Path(__file__).parent / "agno.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents as per Agno framework"""
        return {
            "greeting_agent": GreetingAgent(),
            "mood_tracker_agent": MoodTrackerAgent(),
            "cgm_agent": CGMAgent(),
            "food_intake_agent": FoodIntakeAgent(),
            "meal_planner_agent": MealPlannerAgent(),
            "interrupt_agent": InterruptAgent()
        }
    
    def process(self, user_id: int, text: str = "") -> AgentResult:
        """
        Main processing method following Agno framework flow
        
        Args:
            user_id: User ID to validate
            text: User input text
            
        Returns:
            AgentResult with response and next step
        """
        # Step 1: Validate user ID (Greeting Agent responsibility)
        if not self._validate_user(user_id):
            return AgentResult(
                success=False,
                data={"error": "invalid_user"},
                message="Invalid user ID. Please enter a valid user ID (1-100) to continue.",
                next_step="greeting_agent"
            )
        
        # Step 2: Handle first interaction (Greeting)
        if not text.strip():
            return self._execute_greeting_agent(user_id)
        
        # Step 3: Check for interrupt (General Q&A)
        if self._is_general_query(text):
            return self._execute_interrupt_agent(user_id, text)
        
        # Step 4: Route to appropriate agent based on current flow
        return self._route_to_agent(user_id, text)
    
    def _validate_user(self, user_id: int) -> bool:
        """Validate user ID against dataset (Greeting Agent responsibility)"""
        user = get_user(user_id)
        return user is not None
    
    def _execute_greeting_agent(self, user_id: int) -> AgentResult:
        """Execute Greeting Agent: validate user ID, retrieve name/city, greet"""
        try:
            result = self.agents["greeting_agent"].greet(user_id)
            self.user_context["user_id"] = user_id
            self.current_step = "mood_tracker_agent"
            
            return AgentResult(
                success=True,
                data=result,
                message=result.get("message", "Welcome!"),
                next_step="mood_tracker_agent"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data={"error": str(e)},
                message="Error in greeting agent",
                next_step="greeting_agent"
            )
    
    def _is_general_query(self, text: str) -> bool:
        """Check if text is a general query (not health-related)"""
        text_lower = text.lower()
        health_keywords = ["mood", "glucose", "cgm", "food", "meal", "plan", "blood", "sugar"]
        return not any(keyword in text_lower for keyword in health_keywords)
    
    def _execute_interrupt_agent(self, user_id: int, query: str) -> AgentResult:
        """
        Execute Interrupt Agent: 
        - Inputs: free-form user query
        - Action: intercepts unrelated questions, answers via LLM, routes back
        """
        try:
            result = self.agents["interrupt_agent"].handle_query(user_id, query)
            
            return AgentResult(
                success=True,
                data=result,
                message=result.get("message", "Here's your answer"),
                next_step=self.current_step  # Return to previous task
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data={"error": str(e)},
                message="Error in interrupt agent",
                next_step=self.current_step
            )
    
    def _route_to_agent(self, user_id: int, text: str) -> AgentResult:
        """Route to appropriate agent based on input and current flow"""
        text_lower = text.lower()
        
        # Mood Tracker Agent
        if text_lower.startswith("mood:") or "mood" in text_lower:
            mood = text.split(":", 1)[1].strip() if ":" in text else text
            return self._execute_mood_agent(user_id, mood)
        
        # CGM Agent
        elif text_lower.startswith("cgm:") or any(word in text_lower for word in ["glucose", "blood sugar"]):
            try:
                if ":" in text:
                    reading = float(text.split(":", 1)[1].strip())
                else:
                    # Extract number from text
                    import re
                    numbers = re.findall(r'\d+', text)
                    reading = float(numbers[0]) if numbers else 0
                
                return self._execute_cgm_agent(user_id, reading)
            except ValueError:
                return AgentResult(
                    success=False,
                    data={"error": "invalid_reading"},
                    message="Invalid glucose reading. Please enter a number.",
                    next_step="cgm_agent"
                )
        
        # Food Intake Agent
        elif text_lower.startswith("food:") or any(word in text_lower for word in ["ate", "eat", "meal", "snack"]):
            description = text.split(":", 1)[1].strip() if ":" in text else text
            return self._execute_food_agent(user_id, description)
        
        # Meal Planner Agent
        elif "plan" in text_lower or "meal plan" in text_lower:
            return self._execute_meal_planner_agent(user_id)
        
        # Default to interrupt agent for unrecognized input
        else:
            return self._execute_interrupt_agent(user_id, text)
    
    def _execute_mood_agent(self, user_id: int, mood: str) -> AgentResult:
        """
        Execute Mood Tracker Agent:
        - Inputs: mood label (happy, sad, excited, tired, etc.)
        - Action: store in memory, compute rolling average
        """
        try:
            result = self.agents["mood_tracker_agent"].log_mood(user_id, mood)
            self.current_step = "cgm_agent"
            
            return AgentResult(
                success=True,
                data=result,
                message=result.get("message", "Mood logged successfully"),
                next_step="cgm_agent"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data={"error": str(e)},
                message="Error logging mood",
                next_step="mood_tracker_agent"
            )
    
    def _execute_cgm_agent(self, user_id: int, reading: float) -> AgentResult:
        """
        Execute CGM Agent:
        - Inputs: glucose reading
        - Action: validate range, flag alerts if outside 80–300
        """
        try:
            result = self.agents["cgm_agent"].log_reading(user_id, reading)
            self.current_step = "food_intake_agent"
            
            return AgentResult(
                success=True,
                data=result,
                message=result.get("message", "CGM reading logged"),
                next_step="food_intake_agent"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data={"error": str(e)},
                message="Error logging CGM reading",
                next_step="cgm_agent"
            )
    
    def _execute_food_agent(self, user_id: int, description: str) -> AgentResult:
        """
        Execute Food Intake Agent:
        - Inputs: meal description (free-text) + timestamp (optional)
        - Action: categorize nutrients (carbs/protein/fat) via LLM prompt
        """
        try:
            result = self.agents["food_intake_agent"].log_food(user_id, description)
            self.current_step = "meal_planner_agent"
            
            return AgentResult(
                success=True,
                data=result,
                message=result.get("message", "Food logged successfully"),
                next_step="meal_planner_agent"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data={"error": str(e)},
                message="Error logging food",
                next_step="food_intake_agent"
            )
    
    def _execute_meal_planner_agent(self, user_id: int) -> AgentResult:
        """
        Execute Meal Planner Agent:
        - Inputs: dietary preference + medical conditions + latest mood/CGM
        - Action: call LLM to generate 3-meal plan per day (with macros)
        """
        try:
            result = self.agents["meal_planner_agent"].plan(user_id)
            self.current_step = "complete"
            
            return AgentResult(
                success=True,
                data=result,
                message=result.get("message", "Meal plan generated"),
                next_step="complete"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data={"error": str(e)},
                message="Error generating meal plan",
                next_step="meal_planner_agent"
            )
    
    def get_current_flow_status(self) -> Dict[str, Any]:
        """Get current flow status for debugging"""
        return {
            "current_flow": self.current_flow,
            "current_step": self.current_step,
            "user_context": self.user_context
        }
