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

class CGMAgent(Agent):
    """CGM Agent: Logs Continuous Glucose Monitor readings (range 80–300 mg/dL)"""
    
    NORMAL_RANGE = (80, 180)
    TARGET_RANGE = (80, 140) 
    DIABETES_TARGET = (80, 180)
    
    def __init__(self):
        super().__init__(
            name="cgm_agent",
            description="Logs glucose readings and validates range with health alerts",
            instructions=[
                "Accept glucose readings in range 80-300 mg/dL",
                "Validate range and flag alerts if outside normal",
                "Provide health guidance based on readings"
            ],
        )
        self.db_path = Path(__file__).resolve().parents[1] / "data" / "healthcare.db"
    
    def log_reading(self, user_id: int, glucose_level: float) -> Dict[str, Any]:
        """
        Log glucose reading with validation and health alerts
        
        Args:
            user_id: User ID
            glucose_level: Glucose reading in mg/dL
            
        Returns:
            Dict with validation, alerts, and health guidance
        """
        try:
            # Validate range
            if glucose_level < 40 or glucose_level > 400:
                return {
                    "success": False,
                    "message": f"❌ Invalid glucose reading: {glucose_level} mg/dL. Please enter a value between 40-400 mg/dL.",
                    "valid_range": "40-400 mg/dL"
                }
            
            # Use real-time UTC timestamp
            timestamp = datetime.now(timezone.utc).isoformat()
            alert_level = self._get_alert_level(glucose_level)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO cgm_logs (user_id, glucose_level, alert_level, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (user_id, glucose_level, alert_level, timestamp))
                conn.commit()
            
            # Provide detailed feedback based on glucose level
            if glucose_level < 70:
                response = f"⚠️ LOW ALERT: Your glucose is {glucose_level} mg/dL (below normal). Consider having a quick snack with carbs and monitor closely."
            elif glucose_level < 80:
                response = f"⚡ BORDERLINE LOW: Your glucose is {glucose_level} mg/dL (on the lower side). Keep an eye on how you feel."
            elif glucose_level <= 140:
                response = f"✅ EXCELLENT: Your glucose is {glucose_level} mg/dL (in the healthy range)!"
            elif glucose_level <= 180:
                response = f"📈 ELEVATED: Your glucose is {glucose_level} mg/dL (slightly high). Consider light activity and monitor your next meal choices."
            elif glucose_level <= 250:
                response = f"🚨 HIGH ALERT: Your glucose is {glucose_level} mg/dL (significantly elevated). Please consult your healthcare provider if this persists."
            else:
                response = f"🆘 CRITICAL: Your glucose is {glucose_level} mg/dL (dangerously high). Please seek immediate medical attention if you feel unwell."
            
            # Get 7-day average
            avg_reading = self.get_average_reading(user_id, days=7)
            if avg_reading:
                response += f"\n📊 Your 7-day average: {avg_reading:.1f} mg/dL"
            
            return {
                "success": True,
                "message": f"{response}\n\n🍽️ Next step: Let's log your recent meal! What did you eat?",
                "glucose_level": glucose_level,
                "alert_level": alert_level,
                "average_reading": avg_reading,
                "next_step": "food_logging"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error logging glucose reading: {str(e)}"
            }
    
    def _get_alert_level(self, glucose_level: float) -> str:
        """Get alert level for glucose reading"""
        if glucose_level < 70 or glucose_level > 250:
            return "critical"
        elif glucose_level < 80 or glucose_level > 180:
            return "warning"
        elif glucose_level <= 140:
            return "normal"
        else:
            return "elevated"
    
    def get_average_reading(self, user_id: int, days: int = 7) -> float:
        """Get average glucose reading for past N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT AVG(glucose_level) FROM cgm_logs 
                    WHERE user_id = ? AND date(timestamp) >= date('now', '-{} days')
                """.format(days), (user_id,))
                result = cur.fetchone()[0]
                return float(result) if result else 0.0
        except:
            return 0.0
    
    def get_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get CGM history for charts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT glucose_level, alert_level, timestamp FROM cgm_logs 
                    WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
                """, (user_id, limit))
                return [
                    {"glucose_level": row[0], "alert_level": row[1], "timestamp": row[2]}
                    for row in cur.fetchall()
                ]
        except:
            return []
