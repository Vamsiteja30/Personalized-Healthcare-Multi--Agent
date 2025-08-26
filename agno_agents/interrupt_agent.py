import sys
import os
from pathlib import Path

# Add project root to path to import our base Agent class
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from agno_base import Agent
from typing import Dict, Any
import sqlite3
from datetime import datetime, timezone

class InterruptAgent(Agent):
    """Interrupt Agent (General Q&A Assistant): Handles unrelated questions and gracefully routes back to main flow"""
    
    EMERGENCY_KEYWORDS = [
        "emergency", "urgent", "help", "911", "ambulance", "chest pain", 
        "heart attack", "stroke", "bleeding", "unconscious", "severe pain",
        "difficulty breathing", "choking"
    ]
    
    HEALTH_KEYWORDS = [
        "diabetes", "glucose", "insulin", "blood sugar", "medication", "doctor",
        "symptoms", "side effects", "dosage", "prescription", "medical"
    ]
    
    def __init__(self):
        super().__init__(
            name="interrupt_agent",
            description="General Q&A assistant that handles unrelated queries and routes back to main flow",
            instructions=[
                "Accept free-form user queries at any point in conversation",
                "Detect emergency situations and provide immediate guidance",
                "Answer general health questions using LLM",
                "Gracefully route user back to main health tracking flow",
                "Maintain context of where user was in the flow"
            ],
        )
        self.db_path = Path(__file__).resolve().parents[1] / "data" / "healthcare.db"
    
    def handle_query(self, user_id: int, query: str, current_context: str = "general") -> Dict[str, Any]:
        """
        Handle general user queries and route back to main flow
        
        Args:
            user_id: User ID
            query: Free-form user query
            current_context: Current step in main flow (mood, cgm, food, etc.)
            
        Returns:
            Dict with answer and routing guidance
        """
        if not query or not query.strip():
            return {
                "success": False,
                "message": "❌ Please ask a specific question."
            }
        
        try:
            query_lower = query.lower().strip()
            
            # Check for emergency situations first
            emergency_response = self._handle_emergency_keywords(query_lower)
            if emergency_response:
                return emergency_response
            
            # Get user context for personalized responses
            user_context = self._get_user_context(user_id)
            
            # Generate response using LLM with context
            llm_response = self._generate_response(query, user_context, current_context)
            
            # Determine appropriate routing back to main flow
            routing_suggestion = self._get_routing_suggestion(query_lower, current_context)
            
            return {
                "success": True,
                "message": llm_response,
                "routing_suggestion": routing_suggestion,
                "query_type": self._classify_query(query_lower),
                "user_context": user_context,
                "next_step": "return_to_flow",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return self._fallback_response(query, current_context)
    
    def answer(self, user_id: int, query: str) -> Dict[str, Any]:
        """Legacy method for backward compatibility"""
        return self.handle_query(user_id, query)
    
    def _handle_emergency_keywords(self, query: str) -> Dict[str, Any]:
        """Handle emergency keywords with immediate response"""
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in query:
                return {
                    "success": True,
                    "message": f"🚨 EMERGENCY DETECTED: {query}\n\n⚠️ IMMEDIATE ACTION REQUIRED:\n• Call emergency services (911) immediately\n• Do not delay seeking medical attention\n• Stay calm and follow emergency protocols\n\nThis is a serious situation requiring immediate professional medical care.",
                    "query_type": "emergency",
                    "priority": "critical",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        return None
    
    def _get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get user context for personalized responses"""
        context = {
            "name": None,
            "dietary_preference": None,
            "medical_conditions": [],
            "recent_data": {}
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
                    context["name"] = f"{first_name} {last_name}"
                    context["dietary_preference"] = dietary_pref
                    
                    # Parse medical conditions
                    try:
                        import json
                        context["medical_conditions"] = json.loads(medical_conditions) if medical_conditions != '[]' else []
                    except:
                        context["medical_conditions"] = []
                
                # Get recent activity summary
                cur.execute("""
                    SELECT COUNT(*) FROM mood_logs 
                    WHERE user_id = ? AND date(timestamp) >= date('now', '-7 days')
                """, (user_id,))
                mood_count = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT COUNT(*) FROM cgm_logs 
                    WHERE user_id = ? AND date(timestamp) >= date('now', '-7 days')
                """, (user_id,))
                cgm_count = cur.fetchone()[0]
                
                context["recent_data"] = {
                    "mood_entries": mood_count,
                    "cgm_readings": cgm_count
                }
                
        except Exception as e:
            print(f"Error getting user context: {e}")
        
        return context
    
    def _generate_response(self, query: str, user_context: Dict[str, Any], current_context: str) -> str:
        """Generate LLM response with context"""
        try:
            from backend.services.llm import generate_text
            
            name = user_context.get("name", "Friend")
            dietary_pref = user_context.get("dietary_preference", "mixed")
            conditions = user_context.get("medical_conditions", [])
            
            prompt = f"""You are NOVA, a caring healthcare assistant. User {name} asked: "{query}"

CONTEXT:
- Current flow step: {current_context}
- Dietary preference: {dietary_pref}
- Medical conditions: {', '.join(conditions) if conditions else 'None'}

INSTRUCTIONS:
1. Provide a helpful, accurate, and empathetic response
2. Keep response concise (2-3 sentences)
3. After answering, gently guide them back to health tracking
4. Use warm, encouraging tone
5. If medical question, remind to consult professionals for serious concerns

RESPONSE FORMAT:
[Answer to their question]

[Gentle transition back to health tracking]"""

            response = generate_text(prompt)
            return response.strip()
            
        except Exception as e:
            return f"I understand you're asking about: {query}\n\nLet me help you with that, and then we can continue with your health tracking journey."
    
    def _get_routing_suggestion(self, query: str, current_context: str) -> str:
        """Get routing suggestion based on query and current context"""
        if "mood" in query or "feeling" in query:
            return "Let's log your mood first to track your emotional well-being."
        elif "glucose" in query or "blood sugar" in query or "cgm" in query:
            return "How about checking your glucose levels? Please share your latest CGM reading."
        elif "food" in query or "meal" in query or "eat" in query:
            return "Would you like to log your recent meal? Tell me what you ate."
        elif "plan" in query or "diet" in query:
            return "Ready to generate your personalized meal plan?"
        else:
            return "Let's continue with your health tracking. What would you like to log next?"
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        if any(keyword in query for keyword in self.EMERGENCY_KEYWORDS):
            return "emergency"
        elif any(keyword in query for keyword in self.HEALTH_KEYWORDS):
            return "health_question"
        elif any(word in query for word in ["how", "what", "why", "when", "where"]):
            return "information_request"
        elif any(word in query for word in ["help", "support", "assist"]):
            return "help_request"
        else:
            return "general_query"
    
    def _fallback_response(self, query: str, current_context: str) -> Dict[str, Any]:
        """Fallback response when LLM is unavailable"""
        return {
            "success": True,
            "message": f"I understand you're asking about: {query}\n\nI'm here to help! Let's continue with your health tracking journey.",
            "routing_suggestion": "Let's get back to tracking your health. What would you like to log?",
            "query_type": "general_query",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
