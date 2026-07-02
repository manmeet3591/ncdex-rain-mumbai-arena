#!/usr/bin/env python3
"""Run arena models against historical data for backtesting."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import logging
from datetime import datetime, timedelta

from core.runner import run_arena

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Backfill arena predictions")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--market", default=None, help="Market to backfill (default: all)")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")
    markets = [args.market] if args.market else None

    current = start
    total = 0
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        n = run_arena(date_str, markets)
        total += n
        current += timedelta(days=1)

    log.info(f"Backfill complete: {total} total predictions from {args.start} to {args.end}")


if __name__ == "__main__":
    main()
