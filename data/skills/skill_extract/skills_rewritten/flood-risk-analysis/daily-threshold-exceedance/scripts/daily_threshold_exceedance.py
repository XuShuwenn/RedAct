#!/usr/bin/env python3
"""
Compute per-station daily exceedance counts within a date window.

Inputs:
  - Observations CSV with columns: station_id, timestamp, value
  - Thresholds CSV with columns: station_id, threshold[, units]
Outputs:
  - CSV with columns: station_id, flood_days (count of days with daily_max >= threshold)

Usage:
  python3 daily_threshold_exceedance.py \
    --observations observations.csv \
    --thresholds thresholds.csv \
    --start-date 2025-04-01 \
    --end-date 2025-04-07 \
    --output flood_results.csv \
    --data-units ft \
    --threshold-units ft \
    [--station-col station_id] [--timestamp-col timestamp] [--value-col value] \
    [--threshold-col threshold] [--threshold-units-col units] [--timezone UTC]

Notes:
  - Station IDs are treated as strings end-to-end to preserve leading zeros.
  - Date window is inclusive of both start and end dates.
  - If data and threshold units differ, supports ft↔m conversion.
"""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime, date
from typing import Dict, Tuple, Optional

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # Fallback if not available; timestamps will be treated as naive


def parse_args():
    p = argparse.ArgumentParser(description="Daily threshold exceedance counter")
    p.add_argument("--observations", required=True, help="Path to observations CSV")
    p.add_argument("--thresholds", required=True, help="Path to thresholds CSV")
    p.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    p.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    p.add_argument("--output", required=True, help="Output CSV path")

    p.add_argument("--station-col", default="station_id", help="Observations station id column")
    p.add_argument("--timestamp-col", default="timestamp", help="Observations timestamp column")
    p.add_argument("--value-col", default="value", help="Observations value column")

    p.add_argument("--threshold-col", default="threshold", help="Threshold value column name")
    p.add_argument("--threshold-units-col", default="units", help="Threshold units column name (optional)")

    p.add_argument("--data-units", default=None, help="Units for observation values (e.g., ft or m)")
    p.add_argument("--threshold-units", default=None, help="Units for thresholds (e.g., ft or m)")

    p.add_argument("--timezone", default="UTC", help="Timezone for day boundaries (e.g., UTC or America/New_York)")
    return p.parse_args()


def to_zone(dt: datetime, tzname: str) -> datetime:
    if tzname and ZoneInfo is not None:
        tz = ZoneInfo(tzname)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=tz)
        return dt.astimezone(tz)
    # Fallback: no zoneinfo available; return as-is
    return dt


def parse_dt(val: str) -> Optional[datetime]:
    val = val.strip()
    # Try ISO 8601 parsing (handles 'YYYY-MM-DDTHH:MM:SS' and offsets)
    try:
        # Replace 'Z' with '+00:00' for fromisoformat compatibility
        if val.endswith('Z'):
            val = val[:-1] + '+00:00'
        return datetime.fromisoformat(val)
    except Exception:
        # Try common fallback format
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(val, fmt)
            except Exception:
                continue
    return None


def convert_units(value: float, from_units: Optional[str], to_units: Optional[str]) -> float:
    if not from_units or not to_units:
        return value
    fu = from_units.lower().strip()
    tu = to_units.lower().strip()
    if fu == tu:
        return value
    # Normalize synonyms
    if fu in {"ft", "feet"}:
        fu = "ft"
    if fu in {"m", "meter", "meters"}:
        fu = "m"
    if tu in {"ft", "feet"}:
        tu = "ft"
    if tu in {"m", "meter", "meters"}:
        tu = "m"
    # ft <-> m
    if fu == "ft" and tu == "m":
        return value * 0.3048
    if fu == "m" and tu == "ft":
        return value / 0.3048
    # Unknown conversion; return as-is with warning
    print(f"WARN: Unknown unit conversion from '{from_units}' to '{to_units}'. Assuming same units.", file=sys.stderr)
    return value


def load_thresholds(path: str, units_arg: Optional[str], station_col: str, thresh_col: str, units_col: str) -> Dict[str, Tuple[float, Optional[str]]]:
    mapping: Dict[str, Tuple[float, Optional[str]]] = {}
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = str(row.get(station_col, "")).strip()
            if not sid:
                continue
            tval_raw = row.get(thresh_col, "").strip()
            if not tval_raw:
                continue
            try:
                tval = float(tval_raw)
            except Exception:
                continue
            tunits = units_arg if units_arg else (row.get(units_col, "").strip() or None)
            mapping[sid] = (tval, tunits)
    return mapping


def load_daily_maxima(obs_path: str, station_col: str, ts_col: str, val_col: str, start_d: date, end_d: date, tzname: str) -> Dict[str, Dict[date, float]]:
    daily_max: Dict[str, Dict[date, float]] = defaultdict(dict)
    with open(obs_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = str(row.get(station_col, "")).strip()
            if not sid:
                continue
            ts_raw = row.get(ts_col, "").strip()
            val_raw = row.get(val_col, "").strip()
            if not ts_raw or not val_raw:
                continue
            dt = parse_dt(ts_raw)
            if dt is None:
                continue
            dt = to_zone(dt, tzname)
            d = dt.date()
            if d < start_d or d > end_d:
                continue
            try:
                v = float(val_raw)
            except Exception:
                continue
            prev = daily_max[sid].get(d)
            if prev is None or v > prev:
                daily_max[sid][d] = v
    return daily_max


def main():
    args = parse_args()

    try:
        start_d = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end_d = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    except Exception:
        print("ERROR: start-date and end-date must be in YYYY-MM-DD format", file=sys.stderr)
        sys.exit(1)
    if end_d < start_d:
        print("ERROR: end-date is before start-date", file=sys.stderr)
        sys.exit(1)

    # Load thresholds
    thresh_map = load_thresholds(
        path=args.thresholds,
        units_arg=args.threshold_units,
        station_col=args.station_col,
        thresh_col=args.threshold_col,
        units_col=args.threshold_units_col,
    )
    if not thresh_map:
        print("ERROR: No thresholds loaded.", file=sys.stderr)
        sys.exit(1)

    # Load daily maxima from observations
    daily_max = load_daily_maxima(
        obs_path=args.observations,
        station_col=args.station_col,
        ts_col=args.timestamp_col,
        val_col=args.value_col,
        start_d=start_d,
        end_d=end_d,
        tzname=args.timezone,
    )

    # Count exceedance days per station
    n_days = (end_d - start_d).days + 1
    results: Dict[str, int] = {}

    for sid, day_map in daily_max.items():
        if sid not in thresh_map:
            # No threshold -> skip
            continue
        tval, tunits = thresh_map[sid]
        # Convert threshold into data units if necessary
        conv_tval = convert_units(tval, tunits, args.data_units)
        cnt = 0
        for d, v in day_map.items():
            if v >= conv_tval:
                cnt += 1
        if cnt > n_days:
            # Clamp and warn
            print(f"WARN: Computed exceedance days ({cnt}) exceeds window days ({n_days}) for station {sid}. Clamping.", file=sys.stderr)
            cnt = n_days
        if cnt >= 1:
            results[sid] = cnt

    # Write output CSV
    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["station_id", "flood_days"])
        for sid in sorted(results.keys()):
            writer.writerow([sid, results[sid]])

    # Basic summary to stderr
    print(f"Wrote {len(results)} stations with >=1 exceedance to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
