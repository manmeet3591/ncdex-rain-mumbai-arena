import json
import re
import time
import logging
from datetime import datetime, timezone

import requests
from config import POLYMARKET_EVENTS_URL

log = logging.getLogger(__name__)


def fetch_weather_markets() -> list[dict]:
    all_events = []
    for offset in range(0, 200, 50):
        params = {
            "tag_slug": "temperature",
            "limit": 50,
            "offset": offset,
            "order": "endDate",
            "ascending": "false",
        }
        try:
            resp = requests.get(POLYMARKET_EVENTS_URL, params=params, timeout=15)
            resp.raise_for_status()
            events = resp.json()
            if not events:
                break
            all_events.extend(events)
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Failed to fetch markets (offset={offset}): {e}")
            break

    active = []
    for ev in all_events:
        if ev.get("closed"):
            continue
        markets = [m for m in ev.get("markets", []) if not m.get("closed")]
        if markets:
            ev["markets"] = markets
            active.append(ev)
    log.info(f"Found {len(active)} active weather events")
    return active


def parse_market_brackets(event: dict) -> dict | None:
    title = event.get("title", "")

    city_match = re.search(r"in (.+?) on", title)
    if not city_match:
        return None
    city = city_match.group(1).strip()

    date_match = re.search(r"on (\w+ \d+)", title)
    if not date_match:
        return None
    date_str = date_match.group(1)

    end_date = event.get("endDate", "")
    year = end_date[:4] if end_date else str(datetime.now(timezone.utc).year)
    try:
        target_date = datetime.strptime(f"{date_str} {year}", "%B %d %Y")
    except ValueError:
        return None

    brackets = []
    for m in event.get("markets", []):
        q = m.get("question", "")
        prices = json.loads(m.get("outcomePrices", "[]"))
        yes_price = float(prices[0]) if prices else 0

        unit = "F" if "°F" in q else "C"

        lower, upper = None, None
        below_match = re.search(r"be (\d+)°[FC] or below", q)
        between_match = re.search(r"between (\d+)[–-](\d+)°[FC]", q)
        above_match = re.search(r"be (\d+)°[FC] or higher", q)
        exact_match = re.search(r"be (\d+)°([FC]) on", q)

        if below_match:
            upper = int(below_match.group(1))
            lower = -999
        elif between_match:
            lower = int(between_match.group(1))
            upper = int(between_match.group(2))
        elif above_match:
            lower = int(above_match.group(1))
            upper = 999
        elif exact_match and not below_match and not above_match:
            val = int(exact_match.group(1))
            if "or below" in q:
                lower, upper = -999, val
            elif "or higher" in q:
                lower, upper = val, 999
            else:
                lower, upper = val, val
        else:
            continue

        brackets.append({
            "question": q,
            "yes_price": yes_price,
            "lower": lower,
            "upper": upper,
            "market_id": m.get("id", ""),
            "condition_id": m.get("conditionId", ""),
            "token_ids": m.get("clobTokenIds", "[]"),
            "unit": unit,
        })

    if not brackets:
        return None

    return {
        "city": city,
        "date": target_date.strftime("%Y-%m-%d"),
        "target_date": target_date,
        "unit": brackets[0]["unit"],
        "brackets": sorted(brackets, key=lambda b: (b["lower"], b["upper"])),
        "event_slug": event.get("slug", ""),
        "event_title": title,
    }
