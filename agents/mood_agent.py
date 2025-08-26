from datetime import datetime, timezone
from backend.services.db import insert_mood, get_mood_history
from typing import List, Dict, Any

class MoodAgent:
    VALID_MOODS = {
        'happy': 4, 'great': 4, 'excellent': 4, 'amazing': 4, 'fantastic': 4,
        'good': 3, 'ok': 3, 'okay': 3, 'fine': 3, 'neutral': 3, 'alright': 3,
        'sad': 2, 'down': 2, 'low': 2, 'disappointed': 2, 'upset': 2,
        'awful': 1, 'terrible': 1, 'depressed': 1, 'angry': 1, 'frustrated': 1
    }
    
    def log_mood(self, user_id: int, mood: str):
        mood = mood.lower().strip()
        
        # Validate mood
        if mood not in self.VALID_MOODS:
            available_moods = list(self.VALID_MOODS.keys())
            return {
                "ok": False, 
                "message": f"Please enter a valid mood. Available options: {', '.join(available_moods[:10])}..."
            }
        
        # Use real-time UTC timestamp
        ts = datetime.now(timezone.utc).isoformat()
        insert_mood(user_id, mood, ts)
        
        # Provide encouraging response based on mood
        mood_score = self.VALID_MOODS[mood]
        if mood_score >= 4:
            response = f"🌟 Wonderful! I'm glad you're feeling {mood}!"
        elif mood_score >= 3:
            response = f"👍 Thanks for sharing. Feeling {mood} is perfectly normal."
        elif mood_score >= 2:
            response = f"💙 I understand you're feeling {mood}. Remember, it's okay to have these feelings."
        else:
            response = f"🫂 I'm here for you while you're feeling {mood}. Your feelings are valid."
        
        return {
            "ok": True, 
            "message": response,
            "mood_logged": mood,
            "mood_score": mood_score,
            "ts": ts
        }
    
    def get_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        return get_mood_history(user_id, limit)
    
    def get_rolling_average(self, user_id: int, days: int = 7) -> float:
        """Calculate rolling average mood score for the past N days"""
        history = self.get_history(user_id, limit=days * 24)  # Assume max 24 entries per day
        if not history:
            return 3.0  # Default neutral
            
        total_score = 0
        count = 0
        for entry in history:
            mood = entry.get('mood', '').lower()
            if mood in self.VALID_MOODS:
                total_score += self.VALID_MOODS[mood]
                count += 1
                
        return total_score / count if count > 0 else 3.0
