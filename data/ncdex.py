import logging
from data.open_meteo import fetch_historical_precipitation
from config import MUMBAI_LAT, MUMBAI_LON, NCDEX_ANCHOR_CDR

log = logging.getLogger(__name__)

_LPA_CACHE: dict[str, float] | None = None


def compute_daily_lpa_table() -> dict[str, float]:
    """Compute daily LPA (Long Period Average) for Mumbai Jun 1 - Sep 30.

    Uses Open-Meteo 1991-2020 historical archive as a proxy for IMD station data.
    Returns dict mapping "MM-DD" → average daily precipitation in mm.
    """
    global _LPA_CACHE
    if _LPA_CACHE is not None:
        return _LPA_CACHE

    from collections import defaultdict
    daily_sums = defaultdict(list)

    for year in range(1991, 2021):
        try:
            records = fetch_historical_precipitation(
                MUMBAI_LAT, MUMBAI_LON,
                f"{year}-06-01", f"{year}-09-30",
            )
            for r in records:
                mmdd = r["date"][5:]  # "YYYY-MM-DD" → "MM-DD"
                if r["value"] is not None:
                    daily_sums[mmdd].append(r["value"])
        except Exception as e:
            log.warning(f"Failed to fetch LPA data for {year}: {e}")
            continue

    lpa = {}
    for mmdd, values in sorted(daily_sums.items()):
        lpa[mmdd] = sum(values) / len(values) if values else 0.0

    _LPA_CACHE = lpa
    log.info(f"Computed daily LPA table: {len(lpa)} days, season avg={sum(lpa.values()) / len(lpa):.1f} mm/day")
    return lpa


def compute_cdr(daily_actuals: list[dict], lpa_table: dict[str, float]) -> float:
    """Compute Cumulative Departure from normal (CDR) from daily rainfall actuals.

    daily_actuals: list of {"date": "YYYY-MM-DD", "value": float} sorted chronologically
    Returns CDR value (starting from NCDEX anchor of 2206.7 mm on June 1).
    """
    cdr = NCDEX_ANCHOR_CDR
    for rec in daily_actuals:
        mmdd = rec["date"][5:]
        lpa_val = lpa_table.get(mmdd, 0.0)
        actual_val = rec["value"] if rec["value"] is not None else 0.0
        cdr += actual_val - lpa_val
    return cdr


def get_daily_lpa(date_str: str, lpa_table: dict[str, float] | None = None) -> float:
    if lpa_table is None:
        lpa_table = compute_daily_lpa_table()
    mmdd = date_str[5:]  # "YYYY-MM-DD" → "MM-DD"
    return lpa_table.get(mmdd, 0.0)
