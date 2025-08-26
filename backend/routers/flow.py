"""
Chat Flow Router using Agno Framework
Follows exact specifications from assignment instructions
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from agno_workspace.orchestrator import AgnoOrchestrator, AgentResult

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize Agno orchestrator
agno_orchestrator = AgnoOrchestrator()

class ChatIn(BaseModel):
    """Input model for chat requests"""
    user_id: int
    message: Optional[str] = ""

class ChatResponse(BaseModel):
    """Response model for chat requests"""
    step: str
    result: Dict[str, Any]
    prompt: str
    message: str
    next_step: Optional[str] = None

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(chat_input: ChatIn):
    """
    Main chat endpoint using Agno Framework
    
    Follows exact agent specifications:
    - Greeting Agent: Inputs: user ID, Action: validate user ID against dataset
    - Mood Tracker Agent: Inputs: mood label, Action: store in memory, compute rolling average
    - CGM Agent: Inputs: glucose reading, Action: validate range, flag alerts if outside 80–300
    - Food Intake Agent: Inputs: meal description + timestamp, Action: categorize nutrients via LLM
    - Meal Planner Agent: Inputs: dietary preference + medical conditions + latest mood/CGM, Action: call LLM for 3-meal plan
    - Interrupt Agent: Inputs: free-form user query, Action: intercepts unrelated questions, answers via LLM, routes back
    """
    try:
        # Process through Agno orchestrator
        result: AgentResult = agno_orchestrator.process(
            user_id=chat_input.user_id,
            text=chat_input.message or ""
        )
        
        # Convert to response format
        return ChatResponse(
            step=result.next_step or "unknown",
            result=result.data,
            prompt=result.message,
            message=result.message,
            next_step=result.next_step
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Agno orchestrator: {str(e)}")

@router.get("/status")
async def get_flow_status():
    """Get current Agno flow status for debugging"""
    try:
        status = agno_orchestrator.get_current_flow_status()
        return {
            "status": "ok",
            "agno_framework": "active",
            "current_flow": status["current_flow"],
            "current_step": status["current_step"],
            "user_context": status["user_context"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting flow status: {str(e)}")
