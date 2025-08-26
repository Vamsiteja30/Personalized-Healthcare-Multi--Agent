import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import APIRouter
from pydantic import BaseModel
from agno_agents.interrupt_agent import InterruptAgent

router = APIRouter(tags=["interrupt"])
agent = InterruptAgent()

class InterruptIn(BaseModel):
    query: str

@router.post("/interrupt")
def interrupt(inp: InterruptIn):
    # For now, use a default user_id of 1 since the frontend doesn't send user_id
    return agent.handle_query(1, inp.query)
