from backend.services.db import get_user
import json

class GreetingAgent:
    def greet(self, user_id: int):
        user = get_user(user_id)
        if not user:
            return {"ok": False, "message": "Invalid user ID. Please enter a valid user ID (1-100) to continue."}
        
        # Parse medical conditions and dietary preferences
        first_name = user.get('first_name', 'Friend')
        last_name = user.get('last_name', '')
        city = user.get('city', 'your city')
        dietary_pref = user.get('dietary_preference', 'mixed')
        
        try:
            medical_conditions = json.loads(user.get('medical_conditions', '[]'))
        except:
            medical_conditions = []
            
        full_name = f"{first_name} {last_name}".strip()
        
        # Create personalized greeting
        greeting = f"🌟 Welcome to NOVA, {first_name}!"
        
        if medical_conditions:
            conditions_str = ", ".join(medical_conditions)
            greeting += f"\n\nI see you're managing {conditions_str}. I'm here to help you track your health and provide personalized recommendations."
        
        greeting += f"\n\n📍 Location: {city}"
        greeting += f"\n🍽️ Dietary Preference: {dietary_pref.title()}"
        
        return {
            "ok": True, 
            "message": greeting,
            "user_data": {
                "name": full_name,
                "first_name": first_name,
                "city": city,
                "dietary_preference": dietary_pref,
                "medical_conditions": medical_conditions
            }
        }
