import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import APIRouter, Query
from backend.services.db import get_mood_history, get_cgm_history, get_food_history

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/mood/{user_id}")
def mood_history(user_id: int, limit: int = Query(50, ge=1, le=500)):
    return get_mood_history(user_id, limit)

@router.get("/cgm/{user_id}")
def cgm_history(user_id: int, limit: int = Query(50, ge=1, le=500)):
    return get_cgm_history(user_id, limit)

@router.get("/food/{user_id}")
def food_history(user_id: int, limit: int = Query(50, ge=1, le=500)):
    return get_food_history(user_id, limit)
