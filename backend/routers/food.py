import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import APIRouter
from pydantic import BaseModel
from agno_agents.food_agent import FoodIntakeAgent

router = APIRouter(tags=["food"])
agent = FoodIntakeAgent()

class FoodIn(BaseModel):
    user_id: int
    description: str

@router.post("/food")
def log_food(inp: FoodIn):
    return agent.log_food(inp.user_id, inp.description)
