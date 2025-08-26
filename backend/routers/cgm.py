import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import APIRouter
from pydantic import BaseModel
from agno_agents.cgm_agent import CGMAgent

router = APIRouter(tags=["cgm"])
agent = CGMAgent()

class CGMIn(BaseModel):
    user_id: int
    reading: float

@router.post("/cgm")
def log_cgm(inp: CGMIn):
    result = agent.log_reading(inp.user_id, inp.reading)
    return result
