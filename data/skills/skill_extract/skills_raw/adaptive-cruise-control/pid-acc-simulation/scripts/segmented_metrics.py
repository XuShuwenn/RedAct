#!/usr/bin/env python3
"""Segmented ACC metrics from simulation_results.csv

Assumptions:
- CSV columns (exact order not required by this script):
  time, ego_speed, acceleration_cmd, mode, distance_error, distance, ttc
- Modes: 'cruise', 'follow', 'emergency' (strings)
- Missing numeric fields are blank or not-a-number; this script coerces as needed.

Metrics:
- rise_time_90: time to reach 90% of set_speed (from t0 upward)
- overshoot_pct_cruise: overshoot computed on cruise-only rows
- speed_ss_error_cruise: mean |ego_set - ego_speed| on the last window of the longest cruise segment
- distance_ss_error_follow: mean |distance_error| on the last window of the longest follow segment (excluding emergency)
- min_distance: minimum distance over all valid rows
- basic validations: monotonic time, uniform dt (within tolerance)

Usage:
  python3 scripts/segmented_metrics.py --csv simulation_results.csv --set-speed 30 --dt 0.1 \
      --cruise-ss-window 5 --follow-stable-window 10 --time-tol 1e-3

"""
import argparse
import csv
import json
from typing import List, Tuple, Optional


def read_rows(path: str) -> List[dict]:
    rows: List[dict] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def to_float(s: str) -> Optional[float]:
    if s is None:
        return None
    s = str(s).strip()
    if s == "" or s.lower() == "nan":
        return None
    try:
        return float(s)
    except Exception:
        return None


def segments_by_mode(times: List[float], modes: List[str], target: str) -> List[Tuple[int, int]]:
    segs: List[Tuple[int, int]] = []
    start: Optional[int] = None
    for i, m in enumerate(modes):
        if m == target:
            if start is None:
                start = i
        else:
            if start is not None:
                segs.append((start, i - 1))
                start = None
    if start is not None:
        segs.append((start, len(modes) - 1))
    return segs


def longest_segment(segs: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
    if not segs:
        return None
    segs = sorted(segs, key=lambda ab: (ab[1] - ab[0] + 1), reverse=True)
    return segs[0]


def window_tail(times: List[float], idx0: int, idx1: int, window_s: float) -> Tuple[int, int]:
    # select tail subrange of segment totaling window_s seconds if possible
    if idx0 >= idx1:
        return idx0, idx1
    t_end = times[idx1]
    t_start = t_end - window_s
    # find first index >= t_start
    j0 = idx0
    for j in range(idx0, idx1 + 1):
        if times[j] >= t_start:
            j0 = j
            break
    return j0, idx1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--set-speed", required=True, type=float)
    ap.add_argument("--dt", required=True, type=float)
    ap.add_argument("--cruise-ss-window", type=float, default=5.0, help="seconds")
    ap.add_argument("--follow-stable-window", type=float, default=10.0, help="seconds")
    ap.add_argument("--time-tol", type=float, default=1e-3)
    args = ap.parse_args()

    rows = read_rows(args.csv)

    times = [to_float(r.get("time")) or 0.0 for r in rows]
    speeds = [to_float(r.get("ego_speed")) for r in rows]
    modes = [str(r.get("mode", "")).strip() for r in rows]
    dist_errs = [to_float(r.get("distance_error")) for r in rows]
    distances = [to_float(r.get("distance")) for r in rows]

    # Basic validations
    valid_monotonic = all(times[i] <= times[i+1] + args.time_tol for i in range(len(times)-1))
    dts = [times[i+1] - times[i] for i in range(len(times)-1)]
    mean_dt = sum(dts)/len(dts) if dts else args.dt
    valid_dt = abs(mean_dt - args.dt) <= max(args.time_tol, 0.1*args.dt)

    # Rise time: time to reach 90% of set_speed from start
    target90 = 0.9 * args.set_speed
    rise_time_90 = None
    for t, s in zip(times, speeds):
        if s is not None and s >= target90:
            rise_time_90 = t
            break

    # Cruise-only segments
    cruise_segs = segments_by_mode(times, modes, "cruise")
    best_cruise = longest_segment(cruise_segs)

    overshoot_pct_cruise = None
    speed_ss_error_cruise = None
    if best_cruise is not None:
        c0, c1 = best_cruise
        max_cruise_speed = max([s for s in speeds[c0:c1+1] if s is not None] or [0.0])
        overshoot_pct_cruise = max(0.0, (max_cruise_speed - args.set_speed) / args.set_speed * 100.0)
        # tail window for steady-state
        w0, w1 = window_tail(times, c0, c1, args.cruise_ss_window)
        ss_vals = [abs(args.set_speed - s) for s in speeds[w0:w1+1] if s is not None]
        speed_ss_error_cruise = (sum(ss_vals)/len(ss_vals)) if ss_vals else None

    # Follow-only segments (exclude emergency by mode filtering at source)
    follow_segs = segments_by_mode(times, modes, "follow")
    best_follow = longest_segment(follow_segs)

    distance_ss_error_follow = None
    if best_follow is not None:
        f0, f1 = best_follow
        # take a tail window and average |distance_error|
        w0, w1 = window_tail(times, f0, f1, args.follow_stable_window)
        de_vals = [abs(de) for de in dist_errs[w0:w1+1] if de is not None]
        distance_ss_error_follow = (sum(de_vals)/len(de_vals)) if de_vals else None

    # Minimum distance over valid rows
    dist_vals = [d for d in distances if d is not None]
    min_distance = min(dist_vals) if dist_vals else None

    out = {
        "valid_monotonic_time": bool(valid_monotonic),
        "valid_dt": bool(valid_dt),
        "rise_time_90": rise_time_90,
        "overshoot_pct_cruise": overshoot_pct_cruise,
        "speed_ss_error_cruise": speed_ss_error_cruise,
        "distance_ss_error_follow": distance_ss_error_follow,
        "min_distance": min_distance,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
