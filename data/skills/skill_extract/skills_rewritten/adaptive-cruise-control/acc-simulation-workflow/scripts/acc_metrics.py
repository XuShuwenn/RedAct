#!/usr/bin/env python3
"""
ACC metrics calculator for simulation_results.csv.

Computes speed rise time, overshoot, steady-state errors, and minimum distance.
Designed for generic ACC logs with columns:
  time, ego_speed, acceleration_cmd, mode, distance_error, distance, ttc

Usage example:
  python3 scripts/acc_metrics.py \
      --csv simulation_results.csv \
      --set-speed 30.0 \
      --time-headway 1.5 \
      --min-gap 10.0 \
      --ss-window 20 \
      --rise-low-frac 0.1 \
      --rise-high-frac 0.9 \
      --min-distance-threshold 5.0

Notes:
- Distance SSE is computed only on rows with mode == 'follow' and a valid distance.
- TTC is not required for metrics but can be reported separately if needed.
"""

import argparse
import csv
import math
from typing import List, Optional


def parse_float(x: str) -> Optional[float]:
    if x is None:
        return None
    s = str(x).strip()
    if s == '' or s.lower() == 'nan':
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_rows(path: str):
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            row = {
                'time': parse_float(r.get('time')),
                'ego_speed': parse_float(r.get('ego_speed')),
                'acceleration_cmd': parse_float(r.get('acceleration_cmd')),
                'mode': (r.get('mode') or '').strip(),
                'distance_error': parse_float(r.get('distance_error')),
                'distance': parse_float(r.get('distance')),
                'ttc': parse_float(r.get('ttc')),
            }
            rows.append(row)
        return rows


def find_rise_time(times: List[float], speeds: List[float], set_speed: float, low_frac: float, high_frac: float) -> Optional[float]:
    if not times:
        return None
    low = set_speed * low_frac
    high = set_speed * high_frac
    t_low = None
    t_high = None

    # Detect first crossing of low and high thresholds from below
    for i in range(1, len(times)):
        s_prev, s_curr = speeds[i - 1], speeds[i]
        t_prev, t_curr = times[i - 1], times[i]
        if s_prev is None or s_curr is None:
            continue
        # Low crossing
        if t_low is None and s_prev < low <= s_curr:
            # Linear interpolate crossing time
            frac = (low - s_prev) / max(s_curr - s_prev, 1e-12)
            t_low = t_prev + frac * (t_curr - t_prev)
        # High crossing
        if s_prev < high <= s_curr:
            frac = (high - s_prev) / max(s_curr - s_prev, 1e-12)
            t_high = t_prev + frac * (t_curr - t_prev)
            # Allow t_high before t_low if initial speed already above low
            if t_low is None:
                t_low = times[0]
            break

    if t_low is None or t_high is None:
        return None
    return max(0.0, t_high - t_low)


def overshoot_pct(speeds: List[Optional[float]], set_speed: float) -> float:
    valid = [s for s in speeds if s is not None]
    if not valid:
        return 0.0
    max_s = max(valid)
    if set_speed <= 0:
        return 0.0
    return max(0.0, (max_s - set_speed) / set_speed * 100.0)


def steady_state_error_speed(times: List[float], speeds: List[Optional[float]], set_speed: float, window_s: float) -> Optional[float]:
    if not times:
        return None
    t_end = times[-1]
    t_start = t_end - window_s
    errs = []
    for t, s in zip(times, speeds):
        if t is None or s is None:
            continue
        if t >= t_start:
            errs.append(abs(s - set_speed))
    if not errs:
        return None
    return sum(errs) / len(errs)


def steady_state_error_distance(times: List[float], distances: List[Optional[float]], ego_speeds: List[Optional[float]], modes: List[str], min_gap: float, time_headway: float, window_s: float) -> Optional[float]:
    if not times:
        return None
    t_end = times[-1]
    t_start = t_end - window_s
    errs = []
    for t, d, v, m in zip(times, distances, ego_speeds, modes):
        if t is None or d is None or v is None:
            continue
        if m != 'follow':
            continue
        if t >= t_start:
            desired = min_gap + time_headway * v
            errs.append(abs(d - desired))
    if not errs:
        return None
    return sum(errs) / len(errs)


def min_distance(distances: List[Optional[float]]) -> Optional[float]:
    vals = [d for d in distances if d is not None]
    return min(vals) if vals else None


def main():
    ap = argparse.ArgumentParser(description='Compute ACC metrics from simulation_results.csv')
    ap.add_argument('--csv', required=True, help='Path to simulation_results.csv')
    ap.add_argument('--set-speed', type=float, required=True, help='Target cruise speed (m/s)')
    ap.add_argument('--time-headway', type=float, required=True, help='Time headway for desired gap (s)')
    ap.add_argument('--min-gap', type=float, required=True, help='Minimum standstill gap (m)')
    ap.add_argument('--ss-window', type=float, default=20.0, help='Steady-state window length in seconds (from end)')
    ap.add_argument('--rise-low-frac', type=float, default=0.1, help='Lower fraction of set speed for rise time')
    ap.add_argument('--rise-high-frac', type=float, default=0.9, help='Upper fraction of set speed for rise time')
    # Optional thresholds for simple pass/fail flags
    ap.add_argument('--rise-time-threshold', type=float, default=None, help='Max allowed rise time (s)')
    ap.add_argument('--overshoot-threshold', type=float, default=None, help='Max allowed overshoot (%)')
    ap.add_argument('--speed-sse-threshold', type=float, default=None, help='Max allowed speed steady-state error (m/s)')
    ap.add_argument('--distance-sse-threshold', type=float, default=None, help='Max allowed distance steady-state error (m)')
    ap.add_argument('--min-distance-threshold', type=float, default=None, help='Min allowed following distance (m)')
    args = ap.parse_args()

    rows = load_rows(args.csv)
    if not rows:
        print('ERROR: No rows parsed from CSV')
        return

    times = [r['time'] for r in rows]
    ego_speeds = [r['ego_speed'] for r in rows]
    modes = [r['mode'] for r in rows]
    distances = [r['distance'] for r in rows]

    rt = find_rise_time(times, ego_speeds, args.set_speed, args.rise_low_frac, args.rise_high_frac)
    ov = overshoot_pct(ego_speeds, args.set_speed)
    sse_v = steady_state_error_speed(times, ego_speeds, args.set_speed, args.ss_window)
    sse_d = steady_state_error_distance(times, distances, ego_speeds, modes, args.min_gap, args.time_headway, args.ss_window)
    dmin = min_distance(distances)

    print('Metrics:')
    print(f"  Rise time (fraction {args.rise_low_frac:.2f}->{args.rise_high_frac:.2f}): {rt:.3f} s" if rt is not None else '  Rise time: N/A')
    print(f"  Overshoot: {ov:.3f} %")
    print(f"  Speed steady-state error (last {args.ss_window:.1f}s): {sse_v:.4f} m/s" if sse_v is not None else f"  Speed steady-state error: N/A")
    print(f"  Distance steady-state error (follow-only, last {args.ss_window:.1f}s): {sse_d:.4f} m" if sse_d is not None else f"  Distance steady-state error: N/A")
    print(f"  Minimum distance: {dmin:.3f} m" if dmin is not None else "  Minimum distance: N/A")

    # Optional pass/fail flags
    if args.rise_time_threshold is not None and rt is not None:
        print(f"  Rise time pass: {rt <= args.rise_time_threshold}")
    if args.overshoot_threshold is not None:
        print(f"  Overshoot pass: {ov <= args.overshoot_threshold}")
    if args.speed_sse_threshold is not None and sse_v is not None:
        print(f"  Speed SSE pass: {sse_v <= args.speed_sse_threshold}")
    if args.distance_sse_threshold is not None and sse_d is not None:
        print(f"  Distance SSE pass: {sse_d <= args.distance_sse_threshold}")
    if args.min_distance_threshold is not None and dmin is not None:
        print(f"  Minimum distance pass: {dmin >= args.min_distance_threshold}")


if __name__ == '__main__':
    main()
