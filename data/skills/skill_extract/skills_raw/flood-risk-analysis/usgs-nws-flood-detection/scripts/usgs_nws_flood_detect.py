#!/usr/bin/env python3
"""
USGS–NWS Flood Detection

Compare USGS IV gage-height (00065) to NWS flood-stage thresholds to count
calendar days with flooding (>= threshold) for a list of stations and a date range.

Usage:
  python scripts/usgs_nws_flood_detect.py \
      --stations /path/to/stations.txt \
      --start 2025-04-01 \
      --end 2025-04-07 \
      --out /path/to/flood_results.csv

Notes:
- Requires 'pandas' and 'dataretrieval' Python packages.
- NWS thresholds are retrieved from the bulk CSV and matched to station IDs via
  normalized numeric forms (digits-only, zero-padded to 8 when needed).
"""

import sys
import os
import io
import csv
import time
import argparse
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional

import pandas as pd
from dataretrieval import nwis
import urllib.request


NWS_CSV_URL = "https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv"
PARAM_CODE = "00065"  # USGS gage height, feet


def log(msg: str):
    print(msg, file=sys.stderr)


def read_station_ids(path: str) -> List[str]:
    ids = []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            ids.append(s)
    return ids


def normalize_usgs_id(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    if s == "" or s.lower() == "nan":
        return None
    # Remove decimal artifacts like '12345678.0'
    if s.endswith(".0"):
        s = s[:-2]
    if "." in s:
        s = s.split(".")[0]
    digits = "".join(ch for ch in s if ch.isdigit())
    if digits == "":
        return None
    # USGS site numbers are often 8+ digits; zero-pad to 8 for robust matching
    if len(digits) < 8:
        digits = digits.zfill(8)
    return digits


def daterange_inclusive(start_str: str, end_str: str) -> List[date]:
    start_dt = datetime.fromisoformat(start_str).date()
    end_dt = datetime.fromisoformat(end_str).date()
    if end_dt < start_dt:
        raise ValueError("end date is before start date")
    days = []
    cur = start_dt
    while cur <= end_dt:
        days.append(cur)
        cur = cur + timedelta(days=1)
    return days


def fetch_nws_thresholds(input_station_ids: List[str], timeout: int = 30) -> Dict[str, float]:
    """Return map of original station_id -> flood stage (feet).

    Matching uses a normalized ID map built from the NWS CSV.
    """
    station_map = {sid: normalize_usgs_id(sid) for sid in input_station_ids}
    norm_to_original = {v: k for k, v in station_map.items() if v is not None}

    log(f"Downloading NWS thresholds from {NWS_CSV_URL} ...")
    with urllib.request.urlopen(NWS_CSV_URL, timeout=timeout) as resp:
        content = resp.read().decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(content))
    try:
        headers = next(reader)
    except StopIteration:
        raise RuntimeError("NWS CSV appears empty")

    rows = []
    for row in reader:
        if not row:
            continue
        # Truncate to header length to handle known inconsistencies
        rows.append(row[:len(headers)])

    df = pd.DataFrame(rows, columns=headers)

    # Required columns
    if "usgs id" not in df.columns or "flood stage" not in df.columns:
        raise RuntimeError("NWS CSV missing expected columns 'usgs id' and/or 'flood stage'")

    # Normalize IDs and coerce flood stage
    df["usgs_id_norm"] = df["usgs id"].apply(normalize_usgs_id)
    df["flood stage"] = pd.to_numeric(df["flood stage"], errors="coerce")

    # Build normalized map, skip invalid/sentinel values
    norm_threshold_map: Dict[str, float] = {}
    for _, row in df.iterrows():
        nid = row.get("usgs_id_norm")
        fs = row.get("flood stage")
        if nid is None or pd.isna(fs):
            continue
        try:
            fsv = float(fs)
        except Exception:
            continue
        if fsv == -9999:
            continue
        norm_threshold_map[nid] = fsv

    # Translate normalized thresholds back to original input station IDs
    thresholds: Dict[str, float] = {}
    for original, nid in station_map.items():
        if nid and nid in norm_threshold_map:
            thresholds[original] = norm_threshold_map[nid]

    log(f"Found thresholds for {len(thresholds)} of {len(input_station_ids)} stations")
    return thresholds


def fetch_usgs_iv(station_id: str, start: str, end: str, param: str = PARAM_CODE):
    """Fetch USGS IV data for a station and return DataFrame (or None).

    To ensure inclusive end-day coverage, this function requests one extra day
    beyond 'end' and the caller should filter back to [start, end] inclusive.
    """
    # Request through the next day to ensure full coverage of the end date
    end_plus_one = (datetime.fromisoformat(end) + timedelta(days=1)).date().isoformat()
    try:
        result = nwis.get_iv(sites=station_id, start=start, end=end_plus_one, parameterCd=param)
    except Exception as e:
        log(f"  {station_id}: get_iv error: {e}")
        return None

    # Handle possible (df, metadata) tuple from dataretrieval
    if isinstance(result, tuple):
        df, _meta = result
    else:
        df = result

    if df is None or len(df) == 0:
        return None

    # Ensure datetime index
    try:
        df.index = pd.to_datetime(df.index)
    except Exception:
        pass
    return df


def select_gage_height_column(df: pd.DataFrame, param: str = PARAM_CODE) -> Optional[str]:
    candidates = [c for c in df.columns if (param in str(c)) and ("_cd" not in str(c))]
    if not candidates:
        return None
    return candidates[0]


def count_flood_days(df: pd.DataFrame, gage_col: str, threshold_ft: float, start: str, end: str) -> int:
    # Convert to numeric values
    s = pd.to_numeric(df[gage_col], errors="coerce")
    s = s.dropna()
    if s.empty:
        return 0

    # Group to daily maxima by calendar date
    dates = pd.to_datetime(s.index)
    daily_max = s.groupby(dates.date).max()

    # Restrict to inclusive date range
    target_days = set(daterange_inclusive(start, end))
    flood_days = 0
    for d, v in daily_max.items():
        if d in target_days and v >= threshold_ft:
            flood_days += 1
    return int(flood_days)


def main():
    ap = argparse.ArgumentParser(description="USGS–NWS flood day counter")
    ap.add_argument("--stations", required=True, help="Path to text file with one USGS station ID per line")
    ap.add_argument("--start", required=True, help="Start date (YYYY-MM-DD), inclusive")
    ap.add_argument("--end", required=True, help="End date (YYYY-MM-DD), inclusive")
    ap.add_argument("--out", required=True, help="Output CSV path (station_id,flood_days)")
    ap.add_argument("--sleep", type=float, default=0.1, help="Seconds to sleep between station requests")
    args = ap.parse_args()

    stations = read_station_ids(args.stations)
    if not stations:
        log("No station IDs found in input file")
        # Still write an empty CSV with header
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["station_id", "flood_days"])
            writer.writeheader()
        sys.exit(0)

    log(f"Loaded {len(stations)} station IDs")

    # Fetch NWS thresholds
    try:
        thresholds = fetch_nws_thresholds(stations)
    except Exception as e:
        log(f"Failed to download/parse NWS thresholds: {e}")
        thresholds = {}

    results = []
    processed = 0
    with_threshold = 0
    for sid in stations:
        processed += 1
        thr = thresholds.get(sid)
        if thr is None:
            continue
        with_threshold += 1

        df = fetch_usgs_iv(sid, args.start, args.end, PARAM_CODE)
        if df is None or len(df) == 0:
            time.sleep(args.sleep)
            continue

        gcol = select_gage_height_column(df, PARAM_CODE)
        if not gcol:
            time.sleep(args.sleep)
            continue

        days = count_flood_days(df, gcol, thr, args.start, args.end)
        if days > 0:
            results.append({"station_id": sid, "flood_days": int(days)})

        if args.sleep > 0:
            time.sleep(args.sleep)

    # Sort and write output
    results.sort(key=lambda x: (-x["flood_days"], x["station_id"]))
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["station_id", "flood_days"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    log(f"Processed stations: {processed}")
    log(f"With thresholds: {with_threshold}")
    log(f"Stations with flooding: {len(results)}")
    log(f"Wrote results to: {args.out}")


if __name__ == "__main__":
    main()
