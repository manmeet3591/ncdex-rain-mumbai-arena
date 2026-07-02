from fastapi import APIRouter, Query
from core.db import get_connection
from core.runner import run_arena
from api.schemas import RunArenaRequest

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("")
def get_predictions(
    model_id: str | None = None,
    market: str | None = None,
    location: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(default=100),
):
    conn = get_connection()
    where = "WHERE 1=1"
    params = []
    if model_id:
        where += " AND model_id = ?"
        params.append(model_id)
    if market:
        where += " AND market = ?"
        params.append(market)
    if location:
        where += " AND location = ?"
        params.append(location)
    if date_from:
        where += " AND target_date >= ?"
        params.append(date_from)
    if date_to:
        where += " AND target_date <= ?"
        params.append(date_to)

    rows = conn.execute(
        f"SELECT * FROM predictions {where} ORDER BY target_date DESC LIMIT ?",
        params + [limit],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/latest")
def get_latest_predictions():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.* FROM predictions p
        INNER JOIN (
            SELECT model_id, market, location, variable, MAX(target_date) as max_date
            FROM predictions GROUP BY model_id, market, location, variable
        ) latest ON p.model_id = latest.model_id
                AND p.market = latest.market
                AND p.location = latest.location
                AND p.variable = latest.variable
                AND p.target_date = latest.max_date
        ORDER BY p.target_date DESC, p.model_id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("/run")
def run_predictions(req: RunArenaRequest):
    n = run_arena(req.target_date, req.markets)
    return {"target_date": req.target_date, "predictions_generated": n}
