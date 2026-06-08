#!/usr/bin/env python3
"""Estimate an association time window from station geometry and a uniform velocity model.

Approach:
- Read station coordinates from CSV with columns including 'latitude' and 'longitude'.
- Compute an approximate network diagonal distance using a bounding-box diagonal (haversine).
- Recommend a time window based on vs (slowest phase of interest) and a safety multiplier.

Usage:
  python scripts/estimate_assoc_window.py --stations stations.csv \
      --vp-km-s 6.0 --vs-km-s 3.4286 --safety 1.3

Outputs:
- Prints recommended window in seconds for association configuration.
"""
import argparse
import csv
import math
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Estimate association time window from station layout and velocities")
    p.add_argument("--stations", required=True, help="Path to station CSV")
    p.add_argument("--vp-km-s", type=float, default=6.0, help="P-wave velocity in km/s")
    p.add_argument("--vs-km-s", type=float, default=None, help="S-wave velocity in km/s (default vp/1.75)")
    p.add_argument("--safety", type=float, default=1.3, help="Safety multiplier for the time window")
    return p.parse_args()


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def read_bbox(station_csv):
    lat_min = float('inf'); lat_max = float('-inf')
    lon_min = float('inf'); lon_max = float('-inf')
    with open(station_csv, newline="") as f:
        reader = csv.DictReader(f)
        if 'latitude' not in reader.fieldnames or 'longitude' not in reader.fieldnames:
            raise ValueError("stations CSV must have 'latitude' and 'longitude' columns")
        rows = 0
        for row in reader:
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
            except Exception:
                continue
            rows += 1
            lat_min = min(lat_min, lat); lat_max = max(lat_max, lat)
            lon_min = min(lon_min, lon); lon_max = max(lon_max, lon)
    if rows == 0:
        raise ValueError("No valid station rows found")
    return lat_min, lon_min, lat_max, lon_max


def main():
    args = parse_args()
    vs = args.vs_km_s if args.vs_km_s is not None else (args.vp_km_s / 1.75)
    try:
        lat_min, lon_min, lat_max, lon_max = read_bbox(args.stations)
        diag_km = haversine_km(lat_min, lon_min, lat_max, lon_max)
        # If bbox collapses (single station), set a minimal diagonal
        diag_km = max(diag_km, 0.1)
        base_window = diag_km / max(vs, 0.1)
        recommended = base_window * max(args.safety, 1.0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Stations bbox diagonal: {diag_km:.3f} km")
    print(f"vp: {args.vp_km_s:.3f} km/s, vs: {vs:.3f} km/s, safety: {args.safety:.2f}")
    print(f"Recommended association window: {recommended:.2f} s")
    sys.exit(0)


if __name__ == "__main__":
    main()
