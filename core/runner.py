import logging
from datetime import datetime, timedelta

from core import registry
from core.db import get_connection, get_history, store_prediction, register_model
from core.resolver import resolve_pending
from core.paper_trader import generate_daily_trade, store_trades, resolve_trades
from config import MARKETS

log = logging.getLogger(__name__)


def run_arena(target_date: str, markets: list[str] | None = None, db_path: str | None = None):
    conn = get_connection(db_path)
    models = registry.list_models()
    markets = markets or list(MARKETS.keys())

    for model in models:
        register_model(conn, model.id, model.name, model.description,
                        model.model_type, model.phase, model.get_config())

    total_predictions = 0
    all_trades = []

    for market_key in markets:
        market_cfg = MARKETS.get(market_key)
        if not market_cfg:
            log.warning(f"Unknown market: {market_key}")
            continue

        variable = market_cfg["variable"]
        locations = market_cfg["locations"]

        for location in locations:
            prev_date = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            history = get_history(conn, market_key, location, variable, prev_date, lookback_days=90)

            if not history:
                log.debug(f"No history for {market_key}/{location}, skipping")
                continue

            for model in models:
                try:
                    prediction = model.predict(history, target_date, variable, location)
                    store_prediction(
                        conn, model.id, market_key, location, target_date,
                        variable, prediction.value, prediction.confidence,
                        prediction.metadata,
                    )
                    total_predictions += 1

                    trade = generate_daily_trade(
                        model.id, market_key, location, target_date, prediction,
                    )
                    if trade is not None:
                        all_trades.append(trade)
                    else:
                        signal = prediction.trade.signal if prediction.trade else "hold"
                        log.debug(f"{model.id} {signal} on {target_date}")
                except Exception as e:
                    log.error(f"Model {model.id} failed on {market_key}/{location}: {e}")

    n_trades = store_trades(conn, all_trades)
    resolve_trades(conn)
    scored = resolve_pending(conn)
    log.info(f"Arena run for {target_date}: {total_predictions} predictions, {n_trades} trades, {scored} scored")
    conn.close()
    return total_predictions
