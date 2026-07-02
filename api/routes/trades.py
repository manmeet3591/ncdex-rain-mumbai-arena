from fastapi import APIRouter, Query
from core.db import get_connection
from core.scorer import compute_trade_summary
from core.paper_trader import get_equity_curves

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.get("")
def get_trades(
    model_id: str | None = None,
    market: str | None = None,
    status: str | None = None,
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
    if status:
        where += " AND status = ?"
        params.append(status)

    rows = conn.execute(
        f"SELECT * FROM trades {where} ORDER BY created_at DESC LIMIT ?",
        params + [limit],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/summary")
def get_trade_summary(model_id: str | None = None, market: str | None = None):
    conn = get_connection()
    result = compute_trade_summary(conn, model_id, market)
    conn.close()
    return result


@router.get("/equity")
def get_equity():
    conn = get_connection()
    curves = get_equity_curves(conn)
    conn.close()
    return curves
