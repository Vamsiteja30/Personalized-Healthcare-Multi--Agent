from typing import Dict, Any, List
from backend.services.db import get_latest_cgm_for_user, get_user, get_mood_history, get_food_history
from backend.services.llm import get_llm_client
import json

class MealPlannerAgent:
    def plan(self, user_id: int) -> Dict[str, Any]:
        try:
            # Gather user context
            user = get_user(user_id)
            if not user:
                return {"ok": False, "error": "User not found"}
            
            latest_cgm = get_latest_cgm_for_user(user_id)
            recent_mood = self._get_recent_mood(user_id)
            recent_foods = self._get_recent_foods(user_id)
            
            # Parse medical conditions
            try:
                medical_conditions = json.loads(user.get('medical_conditions', '[]'))
            except:
                medical_conditions = []
            
            # Create comprehensive prompt
            prompt = self._create_meal_plan_prompt(
                user, latest_cgm, recent_mood, recent_foods, medical_conditions
            )
            
            # Generate meal plan using LLM
            llm = get_llm_client()
            response = llm.generate_content(prompt)
            
            # Parse response
            return self._parse_meal_plan_response(response.text, latest_cgm)
            
        except Exception as e:
            return {"ok": False, "error": f"Meal planning error: {str(e)}"}
    
    def _get_recent_mood(self, user_id: int) -> str:
        """Get the most recent mood entry"""
        mood_history = get_mood_history(user_id, limit=1)
        if mood_history:
            return mood_history[0].get('mood', 'neutral')
        return 'neutral'
    
    def _get_recent_foods(self, user_id: int) -> List[str]:
        """Get recent food entries"""
        food_history = get_food_history(user_id, limit=5)
        return [entry.get('description', '') for entry in food_history if entry.get('description')]
    
    def _create_meal_plan_prompt(self, user: Dict, cgm: float, mood: str, foods: List[str], conditions: List[str]) -> str:
        """Create a comprehensive meal planning prompt"""
        
        first_name = user.get('first_name', 'Friend')
        dietary_pref = user.get('dietary_preference', 'mixed')
        city = user.get('city', 'India')
        
        prompt = f"""You are a expert nutritionist and meal planner specializing in personalized healthcare. 
Create a meal plan for {first_name} with the following context:

PERSONAL INFO:
- Name: {first_name}
- Location: {city}
- Dietary Preference: {dietary_pref}
- Medical Conditions: {', '.join(conditions) if conditions else 'None'}
- Current Mood: {mood}

HEALTH DATA:
- Latest Glucose Reading: {cgm if cgm else 'Not available'} mg/dL
- Recent Foods: {', '.join(foods[-3:]) if foods else 'No recent entries'}

MEAL PLANNING REQUIREMENTS:
1. Suggest 3 personalized meals for the next day (breakfast, lunch, dinner)
2. Consider the glucose level for meal timing and composition
3. Respect dietary preferences and medical conditions
4. Include local/regional foods from {city} area
5. Provide estimated macronutrients for each meal

GLUCOSE LEVEL GUIDELINES:
- If CGM > 180: Focus on low glycemic index foods, high fiber
- If CGM 140-180: Balanced meals with moderate carbs
- If CGM 80-140: Normal balanced nutrition
- If CGM < 80: Include quick-acting carbs for next meal

RESPONSE FORMAT (JSON):
{{
  "personalized_message": "Brief encouraging message about the meal plan",
  "glucose_analysis": "Brief analysis of current glucose level and recommendations",
  "suggestions": [
    {{
      "meal_type": "Breakfast/Lunch/Dinner",
      "meal": "Detailed meal description with preparation notes",
      "macros": {{"carb": number, "protein": number, "fat": number, "calories": number}},
      "benefits": "Why this meal is good for the user's current condition",
      "timing": "Suggested eating time"
    }}
  ]
}}

Please provide ONLY the JSON response, no additional text."""

        return prompt
    
    def _parse_meal_plan_response(self, response_text: str, latest_cgm: float) -> Dict[str, Any]:
        """Parse and validate the LLM response"""
        try:
            # Clean up the response
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            # Validate structure
            if 'suggestions' not in data:
                raise ValueError("No suggestions in response")
            
            # Ensure we have the required fields
            result = {
                "ok": True,
                "latest_cgm": latest_cgm,
                "suggestions": data.get('suggestions', []),
                "personalized_message": data.get('personalized_message', ''),
                "glucose_analysis": data.get('glucose_analysis', '')
            }
            
            return result
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract meal suggestions from text
            return self._fallback_parse(response_text, latest_cgm)
        except Exception as e:
            return {
                "ok": False,
                "error": f"Response parsing error: {str(e)}",
                "raw": response_text,
                "latest_cgm": latest_cgm
            }
    
    def _fallback_parse(self, text: str, latest_cgm: float) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses"""
        lines = text.split('\n')
        suggestions = []
        
        meal_keywords = ['breakfast', 'lunch', 'dinner', 'snack']
        current_meal = None
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in meal_keywords):
                if current_meal:
                    suggestions.append({"meal": current_meal})
                current_meal = line
            elif line and current_meal:
                current_meal += " " + line
        
        if current_meal:
            suggestions.append({"meal": current_meal})
        
        return {
            "ok": True,
            "latest_cgm": latest_cgm,
            "suggestions": suggestions[:3],  # Limit to 3 meals
            "raw": text
        }
