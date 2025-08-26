from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict
from backend.agno_workspace.orchestrator import Orchestrator

router = APIRouter(prefix="/agno", tags=["agno"])
orch = Orchestrator()

class ChatIn(BaseModel):
    user_id: int
    text: str

@router.post("/chat")
def agno_chat(inp: ChatIn) -> Dict[str, Any]:
    res = orch.process(inp.user_id, inp.text)
    return {"step": res.step, "result": res.result, "prompt": res.prompt}
