from datetime import datetime, timezone
from backend.services.db import insert_cgm, get_cgm_history
from typing import List, Dict, Any

class CGMAgent:
    NORMAL_RANGE = (80, 300)  # mg/dL
    TARGET_RANGE = (80, 140)  # mg/dL for general population
    DIABETES_TARGET = (80, 180)  # mg/dL for people with diabetes
    
    def log_reading(self, user_id: int, reading: float):
        try:
            reading = float(reading)
        except (ValueError, TypeError):
            return {
                "ok": False,
                "message": "Invalid glucose reading. Please enter a number between 80-300 mg/dL."
            }
        
        # Validate range
        if not (self.NORMAL_RANGE[0] <= reading <= self.NORMAL_RANGE[1]):
            return {
                "ok": False,
                "message": f"Glucose reading must be between {self.NORMAL_RANGE[0]}-{self.NORMAL_RANGE[1]} mg/dL. Please check your reading."
            }
        
        # Use real-time UTC timestamp
        ts = datetime.now(timezone.utc).isoformat()
        insert_cgm(user_id, reading, ts)
        
        # Analyze reading and provide feedback
        feedback = self._analyze_reading(reading)
        response = f"📊 Glucose level logged: {reading} mg/dL\n\n{feedback}"
        
        return {
            "ok": True,
            "message": response,
            "reading": reading,
            "ts": ts,
            "alert_level": self._get_alert_level(reading)
        }
    
    def _analyze_reading(self, reading: float) -> str:
        """Analyze glucose reading and provide appropriate feedback"""
        if reading < 70:
            return "⚠️ LOW ALERT: Your glucose is below normal. Consider having a quick snack with carbs and monitor closely."
        elif reading < 80:
            return "⚡ BORDERLINE LOW: Your glucose is on the lower side. Keep an eye on how you feel."
        elif reading <= 140:
            return "✅ EXCELLENT: Your glucose is in the healthy range!"
        elif reading <= 180:
            return "📈 ELEVATED: Your glucose is slightly high. Consider light activity and monitor your next meal choices."
        elif reading <= 250:
            return "🚨 HIGH ALERT: Your glucose is significantly elevated. Please consult your healthcare provider if this persists."
        else:
            return "🆘 CRITICAL: Your glucose is dangerously high. Please seek immediate medical attention if you feel unwell."
    
    def _get_alert_level(self, reading: float) -> str:
        """Get alert level for the reading"""
        if reading < 70 or reading > 250:
            return "critical"
        elif reading < 80 or reading > 180:
            return "warning"
        elif reading <= 140:
            return "normal"
        else:
            return "elevated"
    
    def get_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        return get_cgm_history(user_id, limit)
    
    def get_average_reading(self, user_id: int, hours: int = 24) -> float:
        """Calculate average glucose reading for the past N hours"""
        history = self.get_history(user_id, limit=hours)
        if not history:
            return 0.0
            
        total = sum(float(entry.get('reading', 0)) for entry in history)
        return total / len(history) if history else 0.0
