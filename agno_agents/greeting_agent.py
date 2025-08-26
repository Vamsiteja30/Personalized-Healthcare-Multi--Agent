import sys
import os
from pathlib import Path

# Add project root to path to import our base Agent class
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from agno_base import Agent
from typing import Dict, Any
import sqlite3

class GreetingAgent(Agent):
    """Greeting Agent: Greets users personally by name"""
    
    def __init__(self):
        super().__init__(
            name="greeting_agent",
            description="Greets users personally by name and validates user ID",
            instructions=[
                "Validate user ID against dataset",
                "If invalid, prompt user to re-enter a valid ID",
                "If valid, retrieve name/city and greet personally"
            ],
        )
        self.db_path = Path(__file__).resolve().parents[1] / "data" / "healthcare.db"
    
    def greet(self, user_id: int) -> Dict[str, Any]:
        """
        Greet user by validating ID and retrieving personal info
        
        Args:
            user_id: User ID to validate and greet
            
        Returns:
            Dict with greeting message and user info
        """
        try:
            # Validate user ID against dataset
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT first_name, last_name, city, dietary_preference, medical_conditions
                    FROM users WHERE id = ?
                """, (user_id,))
                user = cur.fetchone()
                
                if not user:
                    return {
                        "success": False,
                        "message": f"❌ Invalid user ID: {user_id}. Please enter a valid ID between 1-100.",
                        "action_required": "re_enter_user_id"
                    }
                
                first_name, last_name, city, dietary_preference, medical_conditions = user
                
                # Parse medical conditions
                try:
                    import json
                    conditions = json.loads(medical_conditions) if medical_conditions != '[]' else []
                except:
                    conditions = []
                
                greeting_msg = f"🎉 Hello {first_name} {last_name}! Welcome to NOVA!"
                details_msg = f"📍 Location: {city}\n🥗 Diet: {dietary_preference.title()}"
                
                if conditions:
                    conditions_str = ", ".join(conditions)
                    details_msg += f"\n🏥 Health Focus: {conditions_str}"
                
                return {
                    "success": True,
                    "message": f"{greeting_msg}\n\n{details_msg}\n\n💡 Ready to start your health journey today? Let's begin by checking your current mood! 😊",
                    "user_info": {
                        "id": user_id,
                        "name": f"{first_name} {last_name}",
                        "city": city,
                        "dietary_preference": dietary_preference,
                        "medical_conditions": conditions
                    },
                    "next_step": "mood_tracking"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error accessing user data: {str(e)}",
                "action_required": "retry"
            }
