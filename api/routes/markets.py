from fastapi import APIRouter, Query
from core.db import get_connection

router = APIRouter(prefix="/api/markets", tags=["markets"])


@router.get("/actuals")
def get_actuals(
    market: str | None = None,
    location: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(default=100),
):
    conn = get_connection()
    where = "WHERE 1=1"
    params = []
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
        f"SELECT * FROM actuals {where} ORDER BY target_date DESC LIMIT ?",
        params + [limit],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/snapshots")
def get_snapshots(market: str | None = None, limit: int = Query(default=50)):
    conn = get_connection()
    where = "WHERE 1=1"
    params = []
    if market:
        where += " AND market = ?"
        params.append(market)
    rows = conn.execute(
        f"SELECT * FROM market_snapshots {where} ORDER BY fetched_at DESC LIMIT ?",
        params + [limit],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
