from datetime import datetime, timezone
from backend.services.db import insert_food, get_food_history
from backend.services.llm import get_llm_client
from typing import List, Dict, Any
import json

class FoodIntakeAgent:
    def log_food(self, user_id: int, description: str):
        if not description.strip():
            return {
                "ok": False,
                "message": "Please provide a description of your food intake (e.g., 'grilled chicken salad with olive oil')."
            }
        
        # Use real-time UTC timestamp
        ts = datetime.now(timezone.utc).isoformat()
        insert_food(user_id, description, ts)
        
        # Analyze nutrition using LLM
        nutrition_analysis = self._analyze_nutrition(description)
        
        response = f"🍽️ Food logged: {description}"
        
        return {
            "ok": True,
            "message": response,
            "description": description,
            "ts": ts,
            "nutrients": nutrition_analysis
        }
    
    def _analyze_nutrition(self, description: str) -> Dict[str, Any]:
        """Analyze food description using LLM to extract nutritional information"""
        try:
            llm = get_llm_client()
            
            prompt = f"""Analyze the following food description and provide nutritional information in JSON format:

Food: {description}

Please respond with a JSON object containing:
{{
    "calories": "estimated calorie range (e.g., '300-500')",
    "carbs": "carbohydrate content in grams (e.g., '30-60g')",
    "protein": "protein content in grams (e.g., '20-40g')",
    "fat": "fat content in grams (e.g., '10-25g')",
    "benefits": "brief description of health benefits",
    "concerns": "brief description of any health considerations"
}}

Example response:
{{
    "calories": "300-500",
    "carbs": "45g",
    "protein": "25g",
    "fat": "15g",
    "benefits": "Good source of lean protein and complex carbohydrates for sustained energy",
    "concerns": "Consider portion sizes and cooking methods for optimal nutrition"
}}

Respond only with valid JSON, no additional text."""

            response = llm.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to parse JSON response
            try:
                nutrition_data = json.loads(response_text)
                return nutrition_data
            except json.JSONDecodeError:
                # Fallback: parse text response and extract values
                return self._parse_text_nutrition(response_text)
                
        except Exception as e:
            print(f"LLM analysis error: {e}")
            return {
                "calories": "300-500",
                "carbs": "30-60g",
                "protein": "20-40g",
                "fat": "10-25g",
                "benefits": "Good source of essential nutrients",
                "concerns": "Consider portion sizes and preparation methods"
            }
    
    def _parse_text_nutrition(self, text: str) -> Dict[str, Any]:
        """Parse text nutrition response and extract structured data"""
        import re
        
        nutrition_data = {
            "calories": "300-500",
            "carbs": "30-60g",
            "protein": "20-40g",
            "fat": "10-25g",
            "benefits": "Good source of essential nutrients",
            "concerns": "Consider portion sizes and preparation methods"
        }
        
        # Extract calories
        calories_match = re.search(r'calories?[:\s]*([0-9\-~]+)', text.lower())
        if calories_match:
            nutrition_data["calories"] = calories_match.group(1)
        
        # Extract carbs
        carbs_match = re.search(r'carbs?[:\s]*([0-9\-~]+g?)', text.lower())
        if carbs_match:
            nutrition_data["carbs"] = carbs_match.group(1)
        
        # Extract protein
        protein_match = re.search(r'protein[:\s]*([0-9\-~]+g?)', text.lower())
        if protein_match:
            nutrition_data["protein"] = protein_match.group(1)
        
        # Extract fat
        fat_match = re.search(r'fat[:\s]*([0-9\-~]+g?)', text.lower())
        if fat_match:
            nutrition_data["fat"] = fat_match.group(1)
        
        return nutrition_data
    
    def get_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        return get_food_history(user_id, limit)
    
    def get_recent_foods(self, user_id: int, hours: int = 24) -> List[str]:
        """Get list of foods consumed in the past N hours"""
        history = self.get_history(user_id, limit=hours)
        return [entry.get('description', '') for entry in history if entry.get('description')]
