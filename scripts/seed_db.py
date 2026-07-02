#!/usr/bin/env python3
"""Initialize database and backfill historical actuals from Open-Meteo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from datetime import datetime, timedelta

from core.db import init_db, get_connection, store_actual
from data.open_meteo import fetch_historical_precipitation, fetch_historical_temperature
from config import MUMBAI_LAT, MUMBAI_LON, POLYMARKET_CITY_COORDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def seed_mumbai_rainfall(conn, start_date="2020-01-01"):
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    log.info(f"Fetching Mumbai rainfall {start_date} to {end_date}...")
    records = fetch_historical_precipitation(MUMBAI_LAT, MUMBAI_LON, start_date, end_date)
    count = 0
    for r in records:
        if r["value"] is not None:
            store_actual(conn, "rainfall_mumbai", "mumbai", r["date"],
                         "precipitation_mm", r["value"], "open_meteo")
            count += 1
    log.info(f"Inserted {count} Mumbai rainfall records")
    return count


def seed_polymarket_temperatures(conn, cities=None, start_date="2024-01-01"):
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cities = cities or ["New York City", "Chicago", "Miami", "London", "Tokyo"]
    total = 0
    for city in cities:
        coords = POLYMARKET_CITY_COORDS.get(city)
        if not coords:
            log.warning(f"No coords for {city}, skipping")
            continue
        log.info(f"Fetching temperature for {city} {start_date} to {end_date}...")
        try:
            records = fetch_historical_temperature(coords["lat"], coords["lon"], start_date, end_date)
            count = 0
            for r in records:
                if r["value"] is not None:
                    store_actual(conn, "temperature_polymarket", city, r["date"],
                                 "temperature_max_c", r["value"], "open_meteo")
                    count += 1
            log.info(f"  {city}: {count} records")
            total += count
        except Exception as e:
            log.error(f"  {city}: failed - {e}")
    log.info(f"Inserted {total} temperature records total")
    return total


def main():
    log.info("Initializing database...")
    init_db()
    conn = get_connection()

    rainfall_count = seed_mumbai_rainfall(conn)
    temp_count = seed_polymarket_temperatures(conn)

    row_count = conn.execute("SELECT COUNT(*) as n FROM actuals").fetchone()["n"]
    log.info(f"Database seeded. Total actuals: {row_count}")
    conn.close()


if __name__ == "__main__":
    main()
