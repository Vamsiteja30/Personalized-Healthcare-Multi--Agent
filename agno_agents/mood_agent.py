import sys
import os
from pathlib import Path

# Add project root to path to import our base Agent class
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from agno_base import Agent
from typing import Dict, Any, List
import sqlite3
from datetime import datetime, timezone

class MoodTrackerAgent(Agent):
    """Mood Tracker Agent: Captures user mood for each session"""
    
    VALID_MOODS = {
        "happy": 5,
        "excited": 5, 
        "content": 4,
        "calm": 4,
        "neutral": 3,
        "tired": 2,
        "sad": 2,
        "stressed": 1,
        "anxious": 1,
        "angry": 1
    }
    
    def __init__(self):
        super().__init__(
            name="mood_tracker_agent",
            description="Captures user mood and computes rolling averages",
            instructions=[
                "Accept mood labels: happy, sad, excited, tired, etc.",
                "Store in database with timestamp",
                "Compute rolling average for trends"
            ],
        )
        self.db_path = Path(__file__).resolve().parents[1] / "data" / "healthcare.db"
    
    def log_mood(self, user_id: int, mood: str) -> Dict[str, Any]:
        """
        Log user mood and provide feedback
        
        Args:
            user_id: User ID
            mood: Mood label (happy, sad, excited, etc.)
            
        Returns:
            Dict with success status and encouragement
        """
        mood_lower = mood.lower().strip()
        
        if mood_lower not in self.VALID_MOODS:
            valid_moods = ", ".join(self.VALID_MOODS.keys())
            return {
                "success": False,
                "message": f"❌ Invalid mood '{mood}'. Please choose from: {valid_moods}",
                "valid_moods": list(self.VALID_MOODS.keys())
            }
        
        try:
            score = self.VALID_MOODS[mood_lower]
            # Use real-time UTC timestamp
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO mood_logs (user_id, mood, score, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (user_id, mood_lower, score, timestamp))
                conn.commit()
            
            # Get encouraging response based on mood
            if score >= 4:
                response = f"🌟 Wonderful! You're feeling {mood_lower}! That's fantastic energy for your health journey today!"
            elif score == 3:
                response = f"😊 You're feeling {mood_lower} - that's a good baseline! Let's see how we can boost your wellness."
            else:
                response = f"💙 I understand you're feeling {mood_lower}. Remember, taking care of your health can help improve your mood. You've got this!"
            
            # Get rolling average
            rolling_avg = self.get_rolling_average(user_id, days=7)
            if rolling_avg:
                response += f"\n📊 Your 7-day mood average: {rolling_avg:.1f}/5.0"
            
            return {
                "success": True,
                "message": f"{response}\n\n🩸 Next step: Let's check your glucose levels! Please share your latest CGM reading.",
                "mood_score": score,
                "rolling_average": rolling_avg,
                "next_step": "cgm_logging"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error logging mood: {str(e)}"
            }
    
    def get_rolling_average(self, user_id: int, days: int = 7) -> float:
        """Get rolling average mood score"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT AVG(score) FROM mood_logs 
                    WHERE user_id = ? AND date(timestamp) >= date('now', '-{} days')
                """.format(days), (user_id,))
                result = cur.fetchone()[0]
                return float(result) if result else 0.0
        except:
            return 0.0
    
    def get_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get mood history for charts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT mood, score, timestamp FROM mood_logs 
                    WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
                """, (user_id, limit))
                return [
                    {"mood": row[0], "score": row[1], "timestamp": row[2]}
                    for row in cur.fetchall()
                ]
        except:
            return []
