#!/usr/bin/env python3
"""
Association input sanity checker and normalizer for seismic phase association.

- Validates and normalizes pick timestamps to pandas datetime with UTC
- Normalizes station and pick IDs to a consistent format: 'NET.STA.'
- Projects station lon/lat to local x/y in km (equirectangular fallback)
- Writes normalized picks/stations on request for direct GaMMA use

Usage:
  python assoc_sanity_check.py --picks picks.csv --stations stations.csv \
    [--out-picks picks_norm.csv] [--out-stations stations_gamma.csv]

Expected columns:
  picks.csv: id, timestamp, type, prob (others ignored)
  stations.csv: network, station, longitude, latitude, elevation_m (others ignored)

This script is deterministic and does not depend on SeisBench or GaMMA.
"""

import argparse
import sys
from typing import Tuple

import numpy as np
import pandas as pd


def _equirectangular_xy(lon: np.ndarray, lat: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Project lon/lat (deg) to local km using equirectangular approximation."""
    if len(lon) == 0:
        return np.array([]), np.array([])
    lon0 = float(np.nanmean(lon))
    lat0 = float(np.nanmean(lat))
    km_per_deg_lat = 110.574
    km_per_deg_lon = 111.320 * np.cos(np.deg2rad(lat0))
    x = (lon - lon0) * km_per_deg_lon
    y = (lat - lat0) * km_per_deg_lat
    return x, y


def _normalize_station_ids(sta: pd.DataFrame) -> pd.DataFrame:
    out = sta.copy()
    # Build id as 'NET.STA.' (two parts plus trailing dot)
    out['id'] = out['network'].astype(str) + '.' + out['station'].astype(str) + '.'
    return out


def _normalize_pick_ids(picks: pd.DataFrame) -> pd.DataFrame:
    out = picks.copy()
    # Derive 'NET.STA.' from arbitrary trace_id forms
    def to_net_sta_dot(x: str) -> str:
        parts = str(x).split('.')
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}."
        return str(x)
    out['id'] = out['id'].astype(str).map(to_net_sta_dot)
    return out


def _ensure_datetime_utc(picks: pd.DataFrame) -> pd.DataFrame:
    out = picks.copy()
    out['timestamp'] = pd.to_datetime(out['timestamp'], utc=True, errors='coerce')
    return out


def main():
    ap = argparse.ArgumentParser(description="Sanity check and normalize inputs for GaMMA association")
    ap.add_argument('--picks', required=True, help='Path to picks CSV')
    ap.add_argument('--stations', required=True, help='Path to stations CSV')
    ap.add_argument('--out-picks', help='Optional path to write normalized picks CSV')
    ap.add_argument('--out-stations', help='Optional path to write projected stations CSV')
    args = ap.parse_args()

    # Load
    try:
        picks = pd.read_csv(args.picks)
    except Exception as e:
        print(f"ERROR: Failed to read picks CSV: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        stations_raw = pd.read_csv(args.stations)
    except Exception as e:
        print(f"ERROR: Failed to read stations CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Basic column checks
    for col in ['id', 'timestamp']:
        if col not in picks.columns:
            print(f"ERROR: picks is missing required column '{col}'", file=sys.stderr)
            sys.exit(1)
    for col in ['network', 'station', 'longitude', 'latitude', 'elevation_m']:
        if col not in stations_raw.columns:
            print(f"ERROR: stations is missing required column '{col}'", file=sys.stderr)
            sys.exit(1)

    # Normalize
    picks_norm = _ensure_datetime_utc(picks)
    picks_norm = _normalize_pick_ids(picks_norm)

    stations_u = stations_raw.drop_duplicates(subset=['network', 'station']).copy()
    stations_u = _normalize_station_ids(stations_u)

    # Projection
    x, y = _equirectangular_xy(stations_u['longitude'].to_numpy(), stations_u['latitude'].to_numpy())
    stations_gamma = pd.DataFrame({
        'id': stations_u['id'].values,
        'x(km)': x,
        'y(km)': y,
        'z(km)': -stations_u['elevation_m'].to_numpy() / 1000.0,
    })

    # Report alignment
    pid = set(picks_norm['id'].dropna().astype(str).unique())
    sid = set(stations_gamma['id'].dropna().astype(str).unique())
    inter = pid & sid

    print("Sanity check summary:")
    print(f"  Picks: {len(picks_norm)} rows | unique ids: {len(pid)}")
    print(f"  Stations: {len(stations_gamma)} rows | unique ids: {len(sid)}")
    print(f"  ID intersection: {len(inter)}")
    if len(inter) == 0:
        print("WARNING: No overlapping station IDs between picks and stations after normalization.")
        print("         Verify the id format (e.g., ensure both use 'NET.STA.' style).")

    # Timestamp dtype
    if str(picks_norm['timestamp'].dtype).startswith('datetime64'):
        print("  Timestamp dtype: OK (datetime64)")
    else:
        print(f"  Timestamp dtype: {picks_norm['timestamp'].dtype} (EXPECTED datetime64 with UTC)")

    # Optional writes
    if args.out_picks:
        picks_norm.to_csv(args.out_picks, index=False)
        print(f"Wrote normalized picks to: {args.out_picks}")
    if args.out_stations:
        stations_gamma.to_csv(args.out_stations, index=False)
        print(f"Wrote projected stations to: {args.out_stations}")


if __name__ == '__main__':
    main()
