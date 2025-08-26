import sys
import os
from pathlib import Path

# Add project root to path to import our base Agent class
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from agno_base import Agent
from typing import Dict, Any, List, Optional
import sqlite3
from datetime import datetime, timezone, timedelta
import json

class MealPlannerAgent(Agent):
    """Meal Planner Agent: Generates adaptive meal plans respecting dietary preferences and medical constraints"""
    
    def __init__(self):
        super().__init__(
            name="meal_planner_agent",
            description="Generates personalized meal plans based on user profile and health data",
            instructions=[
                "Consider dietary preferences and medical conditions",
                "Factor in latest mood and CGM readings",
                "Generate 3 meals per day with macronutrient information",
                "Provide specific guidance for glucose management"
            ],
        )
        self.db_path = Path(__file__).resolve().parents[1] / "data" / "healthcare.db"
    
    def plan(self, user_id: int, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate adaptive meal plan based on user profile and health data
        
        Args:
            user_id: User ID
            preferences: Optional dietary preferences override
            
        Returns:
            Dict with meal plan suggestions and health guidance
        """
        try:
            # Gather comprehensive user context
            user_context = self._gather_user_context(user_id)
            
            if not user_context["user_profile"]:
                return {
                    "success": False,
                    "message": "❌ User profile not found. Please ensure you have a valid user ID."
                }
            
            # Override preferences if provided
            if preferences:
                user_context.update(preferences)
            
            # Debug: Print user context for verification
            print(f"🔍 Meal Planner Debug - User {user_id}:")
            print(f"   Name: {user_context['user_profile']['name']}")
            print(f"   Dietary: {user_context['user_profile']['dietary_preference']}")
            print(f"   Conditions: {user_context['user_profile']['medical_conditions']}")
            print(f"   CGM: {user_context['latest_cgm']}")
            print(f"   Mood: {user_context['recent_mood']}")
            
            # Create detailed meal plan prompt
            meal_plan_prompt = self._create_meal_plan_prompt(user_context)
            
            # Generate meal plan using LLM with user context for fallback
            meal_plan_response = self._generate_meal_plan_with_context(meal_plan_prompt, user_context)
            
            # Parse and structure the response
            structured_plan = self._parse_meal_plan_response(meal_plan_response)
            
            if structured_plan["success"]:
                # Add timestamp for when plan was generated
                structured_plan["generated_at"] = datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
                
                # Check if we're using fallback (LLM failed)
                if "⚠️ **LLM Quota Exceeded**" in structured_plan.get("glucose_analysis", ""):
                    structured_plan["message"] += f"\n\n⚠️ **LLM Quota Exceeded**: Using personalized fallback meals due to API limitations."
                
                structured_plan["message"] += f"\n\n📅 Plan generated at: {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y-%m-%d %H:%M IST')}"
                
                # Add user context info for verification
                structured_plan["user_context"] = {
                    "user_id": user_id,
                    "name": user_context["user_profile"]["name"],
                    "dietary_preference": user_context["user_profile"]["dietary_preference"],
                    "medical_conditions": user_context["user_profile"]["medical_conditions"]
                }
            
            return structured_plan
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error generating meal plan: {str(e)}"
            }
    
    def _gather_user_context(self, user_id: int) -> Dict[str, Any]:
        """Gather comprehensive user context for meal planning"""
        context = {
            "user_profile": None,
            "latest_cgm": None,
            "recent_mood": None,
            "recent_foods": []
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                
                # Get user profile
                cur.execute("""
                    SELECT first_name, last_name, dietary_preference, medical_conditions
                    FROM users WHERE id = ?
                """, (user_id,))
                user_row = cur.fetchone()
                
                if user_row:
                    first_name, last_name, dietary_pref, medical_conditions = user_row
                    try:
                        conditions = json.loads(medical_conditions) if medical_conditions != '[]' else []
                    except:
                        conditions = []
                    
                    context["user_profile"] = {
                        "name": f"{first_name} {last_name}",
                        "dietary_preference": dietary_pref,
                        "medical_conditions": conditions
                    }
                
                # Get latest CGM reading (within last 24 hours)
                cur.execute("""
                    SELECT glucose_level FROM cgm_logs 
                    WHERE user_id = ? AND date(timestamp) >= date('now', '-1 day')
                    ORDER BY timestamp DESC LIMIT 1
                """, (user_id,))
                cgm_row = cur.fetchone()
                if cgm_row:
                    context["latest_cgm"] = cgm_row[0]
                
                # Get recent mood (within last 24 hours)
                cur.execute("""
                    SELECT mood FROM mood_logs 
                    WHERE user_id = ? AND date(timestamp) >= date('now', '-1 day')
                    ORDER BY timestamp DESC LIMIT 1
                """, (user_id,))
                mood_row = cur.fetchone()
                if mood_row:
                    context["recent_mood"] = mood_row[0]
                
                # Get recent foods (last 3 meals)
                cur.execute("""
                    SELECT meal_description FROM food_logs 
                    WHERE user_id = ? ORDER BY timestamp DESC LIMIT 3
                """, (user_id,))
                food_rows = cur.fetchall()
                context["recent_foods"] = [row[0] for row in food_rows]
                
        except Exception as e:
            print(f"Error gathering user context: {e}")
        
        return context
    
    def _create_meal_plan_prompt(self, context: Dict[str, Any]) -> str:
        """Create comprehensive meal planning prompt"""
        user = context["user_profile"]
        if not user:
            return "Generate a general healthy meal plan."
        
        name = user["name"]
        dietary_pref = user["dietary_preference"]
        conditions = user["medical_conditions"]
        cgm = context["latest_cgm"]
        mood = context["recent_mood"]
        
        # Simplified but effective prompt
        prompt = f"""Create a personalized meal plan for {name}.

User Profile:
- Dietary: {dietary_pref}
- Medical Conditions: {', '.join(conditions) if conditions else 'None'}
- Glucose Level: {cgm if cgm else 'Not available'} mg/dL
- Mood: {mood if mood else 'Not available'}

Requirements:
1. Create 3 meals (breakfast, lunch, dinner)
2. Respect {dietary_pref} diet
3. Consider medical conditions: {', '.join(conditions) if conditions else 'None'}
4. Include specific ingredients and macros

Return ONLY valid JSON:
{{
  "personalized_message": "Brief message for {name}",
  "glucose_analysis": "Brief glucose analysis",
  "suggestions": [
    {{
      "meal_type": "Breakfast",
      "meal": "Specific meal description",
      "macros": {{"carb": 30, "protein": 12, "fat": 10, "calories": 280}},
      "benefits": "Why this meal is good for {name}",
      "timing": "7:00 AM"
    }},
    {{
      "meal_type": "Lunch",
      "meal": "Specific meal description", 
      "macros": {{"carb": 35, "protein": 25, "fat": 12, "calories": 320}},
      "benefits": "Why this meal is good for {name}",
      "timing": "12:30 PM"
    }},
    {{
      "meal_type": "Dinner",
      "meal": "Specific meal description",
      "macros": {{"carb": 40, "protein": 30, "fat": 15, "calories": 380}},
      "benefits": "Why this meal is good for {name}",
      "timing": "7:00 PM"
    }}
  ]
}}"""

        return prompt
    
    def _generate_meal_plan(self, prompt: str) -> str:
        """Generate meal plan using LLM with improved error handling"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                from backend.services.llm import generate_text
                response = generate_text(prompt)
                
                # Validate response is not empty
                if not response or response.strip() == "":
                    print(f"Attempt {attempt + 1}: Empty LLM response")
                    continue
                
                # Try to parse JSON to validate response
                import json
                try:
                    parsed = json.loads(response.strip())
                    print(f"✅ LLM generation successful on attempt {attempt + 1}")
                    return response
                except json.JSONDecodeError as e:
                    print(f"Attempt {attempt + 1}: JSON parsing failed: {e}")
                    # If JSON parsing fails, try to clean the response
                    cleaned_response = self._clean_llm_response(response)
                    try:
                        json.loads(cleaned_response)  # Validate cleaned response
                        print(f"✅ LLM generation successful after cleaning on attempt {attempt + 1}")
                        return cleaned_response
                    except json.JSONDecodeError:
                        print(f"Attempt {attempt + 1}: Cleaned response still invalid")
                        continue
                        
            except Exception as e:
                print(f"Attempt {attempt + 1}: LLM generation failed: {e}")
                if attempt == max_retries - 1:
                    break
        
        print("❌ All LLM attempts failed, using fallback")
        return self._generate_personalized_fallback()
    
    def _generate_meal_plan_with_context(self, prompt: str, user_context: Dict[str, Any]) -> str:
        """Generate meal plan using LLM with user context for personalized fallback"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                from backend.services.llm import generate_text
                response = generate_text(prompt)
                
                # Validate response is not empty
                if not response or response.strip() == "":
                    print(f"Attempt {attempt + 1}: Empty LLM response")
                    continue
                
                # Try to parse JSON to validate response
                import json
                try:
                    parsed = json.loads(response.strip())
                    print(f"✅ LLM generation successful on attempt {attempt + 1}")
                    return response
                except json.JSONDecodeError as e:
                    print(f"Attempt {attempt + 1}: JSON parsing failed: {e}")
                    # If JSON parsing fails, try to clean the response
                    cleaned_response = self._clean_llm_response(response)
                    try:
                        json.loads(cleaned_response)  # Validate cleaned response
                        print(f"✅ LLM generation successful after cleaning on attempt {attempt + 1}")
                        return cleaned_response
                    except json.JSONDecodeError:
                        print(f"Attempt {attempt + 1}: Cleaned response still invalid")
                        continue
                        
            except Exception as e:
                print(f"Attempt {attempt + 1}: LLM generation failed: {e}")
                if attempt == max_retries - 1:
                    break
        
        print("❌ All LLM attempts failed, using personalized fallback")
        return self._generate_personalized_fallback(user_context)
    
    def _clean_llm_response(self, response: str) -> str:
        """Clean LLM response to extract valid JSON"""
        # Remove markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        
        # Remove any text before the first {
        start_idx = response.find("{")
        if start_idx != -1:
            response = response[start_idx:]
        
        # Remove any text after the last }
        end_idx = response.rfind("}")
        if end_idx != -1:
            response = response[:end_idx + 1]
        
        return response.strip()
    
    def _generate_personalized_fallback(self, user_context: Dict[str, Any] = None) -> str:
        """Generate personalized fallback meals based on user context"""
        if not user_context:
            return self._generate_generic_fallback()
        
        user = user_context.get("user_profile", {})
        dietary_pref = user.get("dietary_preference", "vegetarian")
        conditions = user.get("medical_conditions", [])
        name = user.get("name", "User")
        
        # Generate personalized meals based on dietary preference and conditions
        meals = self._get_personalized_meals(dietary_pref, conditions)
        
        return json.dumps({
            "personalized_message": f"Hello {name}, here's your personalized meal plan based on your {dietary_pref} diet and health conditions!",
            "glucose_analysis": f"⚠️ **LLM Quota Exceeded**: Unable to generate AI-powered meal plans. Using personalized fallback meals based on your health profile ({', '.join(conditions) if conditions else 'general wellness'}). These meals are designed to support your specific needs.",
            "suggestions": meals
        })
    
    def _get_personalized_meals(self, dietary_pref: str, conditions: list) -> list:
        """Get personalized meals based on dietary preference and medical conditions"""
        
        # Base meals for different dietary preferences
        base_meals = {
            "vegetarian": {
                "breakfast": {
                    "meal": "Greek yogurt with honey and mixed berries",
                    "macros": {"carb": 25, "protein": 15, "fat": 8, "calories": 220}
                },
                "lunch": {
                    "meal": "Quinoa bowl with roasted vegetables and chickpeas",
                    "macros": {"carb": 40, "protein": 12, "fat": 10, "calories": 280}
                },
                "dinner": {
                    "meal": "Lentil curry with brown rice and spinach",
                    "macros": {"carb": 45, "protein": 18, "fat": 12, "calories": 320}
                }
            },
            "non-vegetarian": {
                "breakfast": {
                    "meal": "Scrambled eggs with whole grain toast and avocado",
                    "macros": {"carb": 30, "protein": 20, "fat": 15, "calories": 320}
                },
                "lunch": {
                    "meal": "Grilled chicken breast with mixed greens and olive oil dressing",
                    "macros": {"carb": 15, "protein": 35, "fat": 12, "calories": 280}
                },
                "dinner": {
                    "meal": "Baked salmon with quinoa and steamed broccoli",
                    "macros": {"carb": 35, "protein": 30, "fat": 18, "calories": 380}
                }
            },
            "vegan": {
                "breakfast": {
                    "meal": "Oatmeal with almond milk, chia seeds, and banana",
                    "macros": {"carb": 35, "protein": 8, "fat": 6, "calories": 220}
                },
                "lunch": {
                    "meal": "Chickpea and vegetable stir-fry with brown rice",
                    "macros": {"carb": 45, "protein": 12, "fat": 8, "calories": 280}
                },
                "dinner": {
                    "meal": "Tofu and vegetable curry with quinoa",
                    "macros": {"carb": 40, "protein": 15, "fat": 10, "calories": 300}
                }
            }
        }
        
        # Get base meals for dietary preference
        meals = base_meals.get(dietary_pref, base_meals["vegetarian"])
        
        # Customize based on medical conditions
        if "Type 2 Diabetes" in conditions:
            meals["breakfast"]["meal"] = "Steel-cut oats with cinnamon and walnuts (low glycemic)"
            meals["breakfast"]["macros"]["carb"] = 20
            meals["lunch"]["meal"] = "Grilled chicken with non-starchy vegetables"
            meals["lunch"]["macros"]["carb"] = 10
            meals["dinner"]["meal"] = "Baked fish with cauliflower rice and green beans"
            meals["dinner"]["macros"]["carb"] = 15
        
        if "Hypertension" in conditions:
            meals["breakfast"]["meal"] += " (low sodium)"
            meals["lunch"]["meal"] += " (no added salt)"
            meals["dinner"]["meal"] += " (herbs instead of salt)"
        
        if "Arthritis" in conditions:
            meals["breakfast"]["meal"] += " with anti-inflammatory turmeric"
            meals["lunch"]["meal"] += " with omega-3 rich ingredients"
            meals["dinner"]["meal"] += " with ginger and garlic"
        
        if "Depression" in conditions:
            meals["breakfast"]["meal"] += " with mood-boosting berries"
            meals["lunch"]["meal"] += " with serotonin-rich foods"
            meals["dinner"]["meal"] += " with complex carbohydrates"
        
        # Convert to required format
        return [
            {
                "meal_type": "Breakfast",
                "meal": meals["breakfast"]["meal"],
                "macros": meals["breakfast"]["macros"],
                "benefits": f"Tailored for {dietary_pref} diet and {', '.join(conditions) if conditions else 'general health'}",
                "timing": "7:00 AM"
            },
            {
                "meal_type": "Lunch",
                "meal": meals["lunch"]["meal"],
                "macros": meals["lunch"]["macros"],
                "benefits": f"Designed for {dietary_pref} diet and {', '.join(conditions) if conditions else 'general health'}",
                "timing": "12:30 PM"
            },
            {
                "meal_type": "Dinner",
                "meal": meals["dinner"]["meal"],
                "macros": meals["dinner"]["macros"],
                "benefits": f"Optimized for {dietary_pref} diet and {', '.join(conditions) if conditions else 'general health'}",
                "timing": "7:00 PM"
            }
        ]
    
    def _generate_generic_fallback(self) -> str:
        """Generate generic fallback meals"""
        return json.dumps({
            "personalized_message": "Here's your personalized meal plan based on your health profile!",
            "glucose_analysis": "Based on your health profile, these meals are designed to support your specific conditions.",
            "suggestions": [
                {
                    "meal_type": "Breakfast",
                    "meal": "Personalized breakfast based on your dietary preferences and health conditions",
                    "macros": {"carb": 30, "protein": 12, "fat": 10, "calories": 280},
                    "benefits": "Tailored to support your specific health needs",
                    "timing": "7:00 AM"
                },
                {
                    "meal_type": "Lunch",
                    "meal": "Personalized lunch based on your dietary preferences and health conditions",
                    "macros": {"carb": 35, "protein": 25, "fat": 12, "calories": 320},
                    "benefits": "Designed to support your medical conditions and dietary requirements",
                    "timing": "12:30 PM"
                },
                {
                    "meal_type": "Dinner",
                    "meal": "Personalized dinner based on your dietary preferences and health conditions",
                    "macros": {"carb": 40, "protein": 30, "fat": 15, "calories": 380},
                    "benefits": "Optimized for your health profile and nutritional needs",
                    "timing": "7:00 PM"
                }
            ]
        })
    
    def _parse_meal_plan_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            meal_plan = json.loads(cleaned_text)
            
            return {
                "success": True,
                "message": meal_plan.get("personalized_message", "Your personalized meal plan is ready!"),
                "glucose_analysis": meal_plan.get("glucose_analysis", ""),
                "suggestions": meal_plan.get("suggestions", []),
                "total_calories": sum(meal.get("macros", {}).get("calories", 0) for meal in meal_plan.get("suggestions", [])),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error parsing meal plan: {str(e)}",
                "suggestions": [],
                "total_calories": 0
            }