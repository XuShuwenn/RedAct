#!/usr/bin/env python3
"""Validate an events CSV file for seismic phase association outputs.

Checks:
- presence of a 'time' column
- ISO 8601 parsing with no timezone (naive datetime)
- sorted ascending by time
- no near-duplicate events within a specified tolerance

Usage:
  python scripts/validate_events_csv.py --file results.csv [--max-dup-sec 5] [--fail-on-unsorted]

Exit codes:
  0 on success, 1 on validation failure
"""
import argparse
import csv
import sys
from datetime import datetime


def parse_args():
    p = argparse.ArgumentParser(description="Validate events CSV time column and basic integrity")
    p.add_argument("--file", required=True, help="Path to events CSV with at least a 'time' column")
    p.add_argument("--max-dup-sec", type=float, default=5.0,
                   help="Maximum allowed time difference (seconds) to consider two events duplicates")
    p.add_argument("--fail-on-unsorted", action="store_true",
                   help="Fail if events are not sorted ascending by time")
    return p.parse_args()


def read_times(path):
    times = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if "time" not in (reader.fieldnames or []):
            raise ValueError("Missing required 'time' column")
        for i, row in enumerate(reader, start=1):
            tstr = (row.get("time") or "").strip()
            if not tstr:
                raise ValueError(f"Empty time value at row {i}")
            try:
                dt = datetime.fromisoformat(tstr)
            except Exception as e:
                raise ValueError(f"Row {i} has non-ISO time '{tstr}': {e}")
            if dt.tzinfo is not None:
                raise ValueError(f"Row {i} has timezone-aware time; expected naive ISO without timezone: '{tstr}'")
            times.append(dt)
    if not times:
        raise ValueError("No data rows found")
    return times


def check_sorted(times, fail_on_unsorted=False):
    is_sorted = all(times[i] <= times[i+1] for i in range(len(times)-1))
    if fail_on_unsorted and not is_sorted:
        raise ValueError("Events are not sorted ascending by time")
    return is_sorted


def check_duplicates(times, max_dup_sec):
    # assume sorted or near-sorted; check neighbors for near-duplicates
    from datetime import timedelta
    max_dt = timedelta(seconds=max_dup_sec)
    dups = 0
    for i in range(len(times)-1):
        if (times[i+1] - times[i]) <= max_dt:
            dups += 1
    return dups


def main():
    args = parse_args()
    try:
        times = read_times(args.file)
        is_sorted = check_sorted(times, args.fail_on_unsorted)
        dups = check_duplicates(times, args.max_dup_sec)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {len(times)} events found")
    print(f"Sorted: {'yes' if is_sorted else 'no (not failing)'}")
    print(f"Near-duplicates (<= {args.max_dup_sec}s): {dups}")
    if dups > 0:
        print("WARNING: Near-duplicate events detected; consider deduplication.")
    sys.exit(0)


if __name__ == "__main__":
    main()
