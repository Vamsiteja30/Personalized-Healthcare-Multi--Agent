from typing import Dict, Any
from backend.services.llm import get_llm_client
from backend.services.db import get_user
import json

class InterruptAgent:
    def handle_query(self, user_id: int, query: str) -> Dict[str, Any]:
        """Handle general user queries and route back to main flow"""
        try:
            # Check for emergency keywords first
            emergency_response = self.handle_emergency_keywords(query)
            if emergency_response:
                return emergency_response
            
            # Get user context for personalized responses
            user = get_user(user_id)
            first_name = user.get('first_name', 'Friend') if user else 'Friend'
            
            # Create context-aware prompt
            prompt = self._create_interrupt_prompt(query, first_name)
            
            # Generate response using LLM
            llm = get_llm_client()
            response = llm.generate_content(prompt)
            
            # Parse and format response
            return self._format_response(response.text, user_id)
            
        except Exception as e:
            return self._fallback_response(query, user_id)
    
    def answer(self, query: str):
        """Legacy method for backward compatibility"""
        return self.handle_query(1, query)  # Default to user 1
    
    def _create_interrupt_prompt(self, query: str, first_name: str) -> str:
        """Create a context-aware prompt for general queries"""
        prompt = f"""You are NOVA, a caring and knowledgeable healthcare assistant. A user named {first_name} has asked you a question while using the health tracking app.

User's Question: "{query}"

INSTRUCTIONS:
1. Provide a helpful, accurate, and empathetic response to their question
2. Keep the response concise but informative (2-4 sentences)
3. After answering, gently guide them back to their health tracking journey
4. Use a warm, encouraging tone
5. If it's a medical question, remind them to consult healthcare professionals for serious concerns

ROUTING OPTIONS after answering:
- If they haven't logged mood today → suggest "Let's log your mood first"
- If they haven't logged glucose → suggest "How about checking your glucose level?"
- If they haven't logged food → suggest "Would you like to log your recent meal?"
- If they've done the basics → suggest "Ready to generate your personalized meal plan?"
- For general continuation → suggest "Let's continue with your health tracking"

RESPONSE FORMAT:
[Answer to their question]

[Gentle transition back to health tracking]

Please provide a natural, conversational response."""

        return prompt
    
    def _format_response(self, llm_response: str, user_id: int) -> Dict[str, Any]:
        """Format the LLM response for the user"""
        response_text = llm_response.strip()
        
        # Add routing suggestion based on app flow
        routing_message = self._get_routing_suggestion(user_id)
        
        if routing_message:
            response_text += f"\n\n{routing_message}"
        
        return {
            "ok": True,
            "message": response_text,
            "type": "general_query",
            "source": "llm"
        }
    
    def _get_routing_suggestion(self, user_id: int) -> str:
        """Suggest next steps in the health tracking flow"""
        # In a real implementation, you'd check what data has been logged today
        # For now, provide a general suggestion
        return "💡 Ready to continue with your health tracking? You can log your mood, glucose reading, food intake, or generate a meal plan!"
    
    def _fallback_response(self, query: str, user_id: int) -> Dict[str, Any]:
        """Provide a fallback response when LLM fails"""
        return {
            "ok": True,
            "message": f"Thank you for your question about '{query}'. While I'd love to help with that, I'm specialized in health tracking and meal planning. Let's continue with logging your health data - would you like to record your mood, glucose level, or food intake?",
            "type": "fallback",
            "source": "fallback"
        }
    
    def is_health_related_query(self, query: str) -> bool:
        """Check if the query is related to health/nutrition"""
        health_keywords = [
            'health', 'nutrition', 'diet', 'glucose', 'diabetes', 'blood sugar',
            'meal', 'food', 'exercise', 'medication', 'doctor', 'symptom',
            'calories', 'carbs', 'protein', 'vitamin', 'mood', 'stress',
            'weight', 'bp', 'pressure', 'heart', 'cholesterol'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in health_keywords)
    
    def handle_emergency_keywords(self, query: str) -> Dict[str, Any]:
        """Handle potential emergency keywords"""
        emergency_keywords = [
            'emergency', 'urgent', 'help', 'chest pain', 'heart attack',
            'stroke', 'unconscious', 'seizure', 'severe', 'critical'
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in emergency_keywords):
            return {
                "ok": True,
                "message": "🚨 If this is a medical emergency, please call emergency services immediately (911/108) or go to the nearest hospital. I'm a health tracking assistant and cannot provide emergency medical care. Your safety is the top priority!",
                "type": "emergency_alert",
                "priority": "high"
            }
        
        return None
