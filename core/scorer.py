import math


def compute_leaderboard(conn, market: str | None = None, days: int = 30) -> list[dict]:
    where = "WHERE 1=1"
    params = []
    if market:
        where += " AND s.market = ?"
        params.append(market)
    if days:
        where += " AND s.target_date >= date('now', ?)"
        params.append(f"-{days} days")

    rows = conn.execute(f"""
        SELECT s.model_id,
               m.name,
               m.model_type,
               COUNT(*) as n_predictions,
               ROUND(AVG(s.abs_error), 3) as mae,
               ROUND(SQRT(AVG(s.squared_error)), 3) as rmse,
               ROUND(AVG(s.error), 3) as bias,
               MIN(s.target_date) as first_date,
               MAX(s.target_date) as last_date
        FROM scores s
        JOIN models m ON s.model_id = m.id
        {where}
        GROUP BY s.model_id
        ORDER BY mae ASC
    """, params).fetchall()

    return [dict(r) for r in rows]


def compute_model_scores(conn, model_id: str, market: str | None = None, days: int = 30) -> list[dict]:
    where = "WHERE s.model_id = ?"
    params = [model_id]
    if market:
        where += " AND s.market = ?"
        params.append(market)
    if days:
        where += " AND s.target_date >= date('now', ?)"
        params.append(f"-{days} days")

    rows = conn.execute(f"""
        SELECT s.target_date, s.market, s.location, s.variable,
               s.predicted_value, s.actual_value, s.error, s.abs_error
        FROM scores s
        {where}
        ORDER BY s.target_date DESC
    """, params).fetchall()

    return [dict(r) for r in rows]


def compute_trade_summary(conn, model_id: str | None = None, market: str | None = None) -> list[dict]:
    where = "WHERE status = 'resolved'"
    params = []
    if model_id:
        where += " AND model_id = ?"
        params.append(model_id)
    if market:
        where += " AND market = ?"
        params.append(market)

    rows = conn.execute(f"""
        SELECT model_id,
               COUNT(*) as total_trades,
               SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
               ROUND(SUM(pnl), 2) as total_pnl,
               ROUND(AVG(pnl), 2) as avg_pnl,
               ROUND(SUM(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END) / COUNT(*), 3) as win_rate
        FROM trades
        {where}
        GROUP BY model_id
        ORDER BY total_pnl DESC
    """, params).fetchall()

    return [dict(r) for r in rows]
