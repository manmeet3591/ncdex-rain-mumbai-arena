"""Fetch daily precipitation from NOAA GHCN-Daily for Mumbai stations.

Santacruz: IN012070800 (1949-present, updated regularly)
Colaba:    IN012070300 (1901-1970, no longer updated)

GHCND .dly format: fixed-width, each row = one station + year-month + element,
followed by 31 daily values. Each value is 5 chars (tenths of mm for PRCP),
-9999 = missing. See https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt
"""

import logging
import requests

log = logging.getLogger(__name__)

GHCND_BASE = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all"
SANTACRUZ_ID = "IN012070800"
COLABA_ID = "IN012070300"


def _parse_dly_line(line: str) -> list[dict] | None:
    station = line[0:11]
    year = int(line[11:15])
    month = int(line[15:17])
    element = line[17:21]

    if element != "PRCP":
        return None

    records = []
    for day in range(1, 32):
        offset = 21 + (day - 1) * 8
        val_str = line[offset:offset + 5].strip()
        flag = line[offset + 5:offset + 6]

        try:
            val = int(val_str)
        except ValueError:
            continue

        if val == -9999:
            continue

        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
            import datetime
            datetime.date.fromisoformat(date_str)
        except ValueError:
            continue

        records.append({
            "date": date_str,
            "value": val / 10.0,  # tenths of mm → mm
            "station": station,
        })

    return records


def fetch_ghcnd_precipitation(station_id: str = SANTACRUZ_ID,
                               start_date: str | None = None,
                               end_date: str | None = None) -> list[dict]:
    url = f"{GHCND_BASE}/{station_id}.dly"
    log.info(f"Fetching GHCND data from {url}...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    records = []
    for line in resp.text.splitlines():
        if len(line) < 269:
            continue
        parsed = _parse_dly_line(line)
        if parsed:
            records.extend(parsed)

    if start_date:
        records = [r for r in records if r["date"] >= start_date]
    if end_date:
        records = [r for r in records if r["date"] <= end_date]

    log.info(f"GHCND {station_id}: {len(records)} precipitation records"
             f" ({records[0]['date']} to {records[-1]['date']})" if records else "")
    return records


def fetch_mumbai_rainfall(start_date: str | None = None,
                           end_date: str | None = None) -> list[dict]:
    """Fetch Santacruz station rainfall as the primary Mumbai ground truth."""
    return fetch_ghcnd_precipitation(SANTACRUZ_ID, start_date, end_date)
