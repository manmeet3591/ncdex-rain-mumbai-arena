import json
import logging

log = logging.getLogger(__name__)

STARTING_CAPITAL = 10_000.0
BET_SIZE = 200.0
MAX_DAILY_PNL = 500.0


def generate_daily_trade(model_id: str, market: str, location: str,
                          target_date: str, predicted_value: float,
                          yesterday_value: float) -> dict:
    """Every model bets on direction of change vs yesterday.

    Long if prediction > yesterday, short if prediction < yesterday.
    P&L resolved later against actual change.
    """
    direction = "long" if predicted_value >= yesterday_value else "short"
    return {
        "model_id": model_id,
        "market": market,
        "location": location,
        "target_date": target_date,
        "direction": direction,
        "entry_price": yesterday_value,
        "predicted_value": predicted_value,
        "position_size": BET_SIZE,
        "shares": 1.0,
        "trade_metadata": json.dumps({
            "yesterday_value": round(yesterday_value, 2),
            "predicted_change": round(predicted_value - yesterday_value, 2),
        }),
    }


def store_trades(conn, trades: list[dict]) -> int:
    count = 0
    for t in trades:
        try:
            conn.execute(
                """INSERT OR IGNORE INTO trades
                   (model_id, market, location, target_date, direction,
                    entry_price, predicted_value, position_size, shares, trade_metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (t["model_id"], t["market"], t["location"], t["target_date"],
                 t["direction"], t["entry_price"], t["predicted_value"],
                 t["position_size"], t["shares"], t.get("trade_metadata")),
            )
            count += 1
        except Exception as e:
            log.error(f"Failed to store trade: {e}")
    conn.commit()
    return count


def resolve_trades(conn, market: str | None = None) -> int:
    """Resolve open trades against actuals.

    P&L = direction_sign × actual_change × bet_multiplier, capped at ±MAX_DAILY_PNL.
    Bet multiplier scales $BET_SIZE relative to typical daily changes.
    """
    where = "WHERE t.status = 'open'"
    params = []
    if market:
        where += " AND t.market = ?"
        params.append(market)

    open_trades = conn.execute(f"""
        SELECT t.id, t.model_id, t.market, t.location, t.target_date,
               t.direction, t.entry_price, t.shares, t.position_size,
               t.trade_metadata,
               a.value as actual_value
        FROM trades t
        JOIN actuals a ON t.market = a.market
                     AND t.location = a.location
                     AND t.target_date = a.target_date
        {where}
    """, params).fetchall()

    resolved = 0
    for trade in open_trades:
        actual = trade["actual_value"]
        entry = trade["entry_price"]
        actual_change = actual - entry
        direction_sign = 1.0 if trade["direction"] == "long" else -1.0

        scale = 20.0 if "rainfall" in trade["market"] else 5.0
        pnl = direction_sign * actual_change * (BET_SIZE / scale)
        pnl = max(-MAX_DAILY_PNL, min(MAX_DAILY_PNL, pnl))

        conn.execute(
            """UPDATE trades SET status = 'resolved', exit_price = ?, pnl = ?,
               resolved_at = datetime('now') WHERE id = ?""",
            (actual, round(pnl, 2), trade["id"]),
        )
        resolved += 1

    conn.commit()
    if resolved:
        log.info(f"Resolved {resolved} trades")
    return resolved


def get_equity_curves(conn, market: str = "rainfall_mumbai") -> dict[str, list[dict]]:
    """Compute cumulative account value over time for each model.

    Returns {model_id: [{"date": ..., "account_value": ...}, ...]}.
    """
    rows = conn.execute("""
        SELECT model_id, target_date, SUM(pnl) as daily_pnl
        FROM trades
        WHERE status = 'resolved' AND pnl IS NOT NULL AND market = ?
        GROUP BY model_id, target_date
        ORDER BY target_date
    """, (market,)).fetchall()

    curves = {}
    for row in rows:
        mid = row["model_id"]
        if mid not in curves:
            curves[mid] = []
        curves[mid].append({
            "date": row["target_date"],
            "daily_pnl": row["daily_pnl"],
        })

    if not curves:
        return curves

    from datetime import datetime, timedelta
    earliest = min(e[0]["date"] for e in curves.values())
    start_date = (datetime.strptime(earliest, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

    for mid, entries in curves.items():
        entries.insert(0, {"date": start_date, "daily_pnl": 0, "account_value": STARTING_CAPITAL})
        balance = STARTING_CAPITAL
        for e in entries[1:]:
            balance += e["daily_pnl"]
            e["account_value"] = round(balance, 2)

    return curves
