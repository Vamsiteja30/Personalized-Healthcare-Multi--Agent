import sys
import os
from pathlib import Path

# Add project root to path to import our base Agent class
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from agno_base import Agent
from typing import Dict, Any, List, Optional
import sqlite3
from datetime import datetime, timezone
import json

class FoodIntakeAgent(Agent):
    """Food Intake Agent: Records meals/snacks with timestamps and nutritional analysis"""
    
    def __init__(self):
        super().__init__(
            name="food_intake_agent", 
            description="Records meals and snacks with LLM-powered nutritional categorization",
            instructions=[
                "Accept meal descriptions in free-text format",
                "Add timestamp (current time if not provided)",
                "Categorize nutrients (carbs/protein/fat) via LLM prompt"
            ],
        )
        self.db_path = Path(__file__).resolve().parents[1] / "data" / "healthcare.db"
    
    def log_food(self, user_id: int, meal_description: str, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Log food intake with nutritional analysis
        
        Args:
            user_id: User ID
            meal_description: Free-text meal description
            timestamp: Optional timestamp (uses current time if not provided)
            
        Returns:
            Dict with logging confirmation and nutrition analysis
        """
        if not meal_description or not meal_description.strip():
            return {
                "success": False,
                "message": "❌ Please provide a description of your food intake."
            }
        
        try:
            # Use real-time UTC timestamp if not provided
            if not timestamp:
                timestamp = datetime.now(timezone.utc).isoformat()
            
            # Analyze nutrition using LLM
            nutrition_analysis = self._analyze_nutrition(meal_description)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO food_logs (user_id, meal_description, nutrition_analysis, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (user_id, meal_description, json.dumps(nutrition_analysis), timestamp))
                conn.commit()
            
            # Create response message
            response_msg = f"🍽️ Food logged: {meal_description}"
            
            if nutrition_analysis and nutrition_analysis.get("analysis"):
                analysis_text = nutrition_analysis["analysis"]
                response_msg += f"\n\n📊 Nutritional Analysis:\n{analysis_text}"
            
            response_msg += f"\n\n🍽️ Ready for meal planning? Let's generate a personalized meal plan based on your health profile!"
            
            return {
                "success": True,
                "message": response_msg,
                "meal_description": meal_description,
                "nutrition_analysis": nutrition_analysis,
                "timestamp": timestamp,
                "next_step": "meal_planning"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error logging food: {str(e)}"
            }
    
    def _analyze_nutrition(self, meal_description: str) -> Dict[str, Any]:
        """Analyze nutrition using LLM prompt"""
        try:
            from backend.services.llm import generate_text
            
            prompt = f"""
            Analyze the nutritional content of this meal/snack: "{meal_description}"
            
            Provide a brief analysis including:
            1. Primary macronutrients (carbs, protein, fat)
            2. Estimated calorie range
            3. Health benefits or concerns
            4. Meal timing recommendations
            
            Keep the response concise and practical for someone tracking their health.
            Format as plain text, not JSON.
            """
            
            analysis = generate_text(prompt)
            
            # Extract key info for structured storage
            return {
                "description": meal_description,
                "analysis": analysis,
                "estimated_calories": self._extract_calories(analysis),
                "primary_macros": self._extract_macros(analysis),
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            # Fallback analysis
            return {
                "description": meal_description,
                "analysis": f"Nutritional analysis for: {meal_description}\n\nEstimated calories: 300-500\nMacros: Balanced meal\nBenefits: Provides energy and nutrients",
                "estimated_calories": "300-500",
                "primary_macros": "balanced",
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
    
    def _extract_calories(self, analysis: str) -> str:
        """Extract calorie estimate from analysis text"""
        try:
            import re
            calorie_match = re.search(r'(\d+)-?(\d+)?\s*calories?', analysis.lower())
            if calorie_match:
                return f"{calorie_match.group(1)}-{calorie_match.group(2) or calorie_match.group(1)}"
        except:
            pass
        return "300-500"
    
    def _extract_macros(self, analysis: str) -> str:
        """Extract primary macronutrients from analysis text"""
        try:
            if any(word in analysis.lower() for word in ["protein", "meat", "fish", "chicken"]):
                return "protein-rich"
            elif any(word in analysis.lower() for word in ["carbs", "rice", "bread", "pasta"]):
                return "carb-rich"
            elif any(word in analysis.lower() for word in ["fat", "oil", "nuts", "avocado"]):
                return "fat-rich"
        except:
            pass
        return "balanced"
    
    def get_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get food history for charts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT meal_description, nutrition_analysis, timestamp FROM food_logs 
                    WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
                """, (user_id, limit))
                return [
                    {
                        "meal_description": row[0], 
                        "nutrition_analysis": json.loads(row[1]) if row[1] else {},
                        "timestamp": row[2]
                    }
                    for row in cur.fetchall()
                ]
        except:
            return []
