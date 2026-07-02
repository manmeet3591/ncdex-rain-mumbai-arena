#!/usr/bin/env python3
"""Initialize database and backfill historical actuals.

Uses GHCND Santacruz station as primary source (real IMD station data),
then fills the recent gap with Open-Meteo gridded data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from datetime import datetime, timedelta

from core.db import init_db, get_connection, store_actual
from data.ghcnd import fetch_mumbai_rainfall
from data.open_meteo import fetch_historical_precipitation
from config import MUMBAI_LAT, MUMBAI_LON

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def seed_mumbai_rainfall(conn, start_date="2020-01-01"):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 1. GHCND Santacruz — real station data (primary)
    log.info(f"Fetching GHCND Santacruz rainfall {start_date} onwards...")
    ghcnd_records = fetch_mumbai_rainfall(start_date)
    ghcnd_count = 0
    ghcnd_last_date = start_date
    for r in ghcnd_records:
        if r["value"] is not None:
            store_actual(conn, "rainfall_mumbai", "mumbai", r["date"],
                         "precipitation_mm", r["value"], "ghcnd_santacruz")
            ghcnd_count += 1
            ghcnd_last_date = r["date"]
    log.info(f"GHCND Santacruz: {ghcnd_count} records (up to {ghcnd_last_date})")

    # 2. Open-Meteo — fill the gap from GHCND's last date to yesterday
    gap_start = (datetime.strptime(ghcnd_last_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    if gap_start <= yesterday:
        log.info(f"Filling gap with Open-Meteo: {gap_start} to {yesterday}...")
        om_records = fetch_historical_precipitation(MUMBAI_LAT, MUMBAI_LON, gap_start, yesterday)
        om_count = 0
        for r in om_records:
            if r["value"] is not None:
                store_actual(conn, "rainfall_mumbai", "mumbai", r["date"],
                             "precipitation_mm", r["value"], "open_meteo")
                om_count += 1
        log.info(f"Open-Meteo gap fill: {om_count} records")

    return ghcnd_count


def main():
    log.info("Initializing database...")
    init_db()
    conn = get_connection()

    seed_mumbai_rainfall(conn)

    row_count = conn.execute("SELECT COUNT(*) as n FROM actuals WHERE market='rainfall_mumbai'").fetchone()["n"]
    sources = conn.execute(
        "SELECT source, COUNT(*) as n, MIN(target_date) as first, MAX(target_date) as last "
        "FROM actuals WHERE market='rainfall_mumbai' GROUP BY source"
    ).fetchall()
    log.info(f"Total Mumbai rainfall records: {row_count}")
    for s in sources:
        log.info(f"  {s['source']}: {s['n']} records ({s['first']} to {s['last']})")
    conn.close()


if __name__ == "__main__":
    main()
