#!/usr/bin/env python3
"""Daily arena run: fetch data, run models, resolve predictions, generate trades."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import logging
from datetime import datetime, timedelta

from core.db import init_db, get_connection, store_actual
from core.runner import run_arena
from core.paper_trader import resolve_trades
from data.open_meteo import fetch_historical_precipitation, fetch_historical_temperature
from config import MUMBAI_LAT, MUMBAI_LON, POLYMARKET_CITY_COORDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def update_actuals(conn):
    """Fetch yesterday's actual weather data."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    log.info(f"Fetching Mumbai rainfall for {two_days_ago} to {yesterday}...")
    try:
        records = fetch_historical_precipitation(MUMBAI_LAT, MUMBAI_LON, two_days_ago, yesterday)
        for r in records:
            if r["value"] is not None:
                store_actual(conn, "rainfall_mumbai", "mumbai", r["date"],
                             "precipitation_mm", r["value"], "open_meteo")
        log.info(f"  Updated {len(records)} rainfall records")
    except Exception as e:
        log.error(f"  Failed: {e}")

    cities = ["New York City", "Chicago", "Miami", "London", "Tokyo"]
    for city in cities:
        coords = POLYMARKET_CITY_COORDS.get(city)
        if not coords:
            continue
        try:
            records = fetch_historical_temperature(coords["lat"], coords["lon"], two_days_ago, yesterday)
            for r in records:
                if r["value"] is not None:
                    store_actual(conn, "temperature_polymarket", city, r["date"],
                                 "temperature_max_c", r["value"], "open_meteo")
        except Exception as e:
            log.error(f"  {city} temperature fetch failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Daily arena run")
    parser.add_argument("--date", default=None, help="Target date YYYY-MM-DD (default: tomorrow)")
    args = parser.parse_args()

    target_date = args.date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    init_db()
    conn = get_connection()

    log.info("=== Step 1: Update actuals ===")
    update_actuals(conn)

    log.info(f"=== Step 2: Run arena for {target_date} ===")
    n_pred = run_arena(target_date)

    log.info("=== Step 3: Resolve trades ===")
    n_resolved = resolve_trades(conn)

    log.info(f"=== Done: {n_pred} predictions, {n_resolved} trades resolved ===")
    conn.close()


if __name__ == "__main__":
    main()
