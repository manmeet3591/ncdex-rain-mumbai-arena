from fastapi import APIRouter, Query
from core.db import get_connection
from core.scorer import compute_leaderboard, compute_model_scores

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
def get_leaderboard(market: str | None = None, days: int = Query(default=30)):
    conn = get_connection()
    result = compute_leaderboard(conn, market, days)
    conn.close()
    return result


@router.get("/{model_id}")
def get_model_detail(model_id: str, market: str | None = None, days: int = Query(default=30)):
    conn = get_connection()
    scores = compute_model_scores(conn, model_id, market, days)
    conn.close()
    return scores
