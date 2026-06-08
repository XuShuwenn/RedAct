#!/usr/bin/env python3
"""
Noise-robust performance metrics for setpoint tracking.

Reads a control JSON log with entries like:
{
  "phase": "control",
  "setpoint": <float>,  # optional (can also be per-sample)
  "data": [
    {"time": <float>, "temperature": <float>, "heater_power": <float>, "setpoint": <float>},
    ...
  ]
}

Outputs metrics.json with keys:
{
  "rise_time": <float>,
  "overshoot": <float>,    # fraction of step (e.g., 0.08 for 8%)
  "settling_time": <float>,
  "steady_state_error": <float>,
  "max_temp": <float>
}

Usage:
  python3 scripts/noise_robust_metrics.py --input control_log.json --output metrics.json --band 0.5 --dwell 5.0 --smooth 2.0

- band: settling band in degrees (e.g., 0.5 means ±0.5° around setpoint)
- dwell: time that the response must remain in band to be considered settled
- smooth: moving-average window in seconds for metrics (not for control)
"""

import argparse
import json
import math
from typing import List, Tuple


def _moving_average_time(t: List[float], x: List[float], window_sec: float) -> List[float]:
    if len(t) < 2 or window_sec <= 0:
        return x[:]
    # approximate window length in samples using median dt
    dts = [t[i+1] - t[i] for i in range(len(t)-1)]
    dt = sorted(dts)[len(dts)//2] if dts else 1.0
    win = max(1, int(round(window_sec / max(dt, 1e-6))))
    buf = []
    s = 0.0
    out = []
    for v in x:
        buf.append(v)
        s += v
        if len(buf) > win:
            s -= buf.pop(0)
        out.append(s / len(buf))
    return out


def _first_time_cross(t: List[float], y: List[float], y0: float, y1: float, frac: float) -> float:
    # Time to reach y0 + frac*(y1 - y0) in the direction of the step
    target = y0 + frac * (y1 - y0)
    rising = (y1 - y0) >= 0
    for i in range(1, len(t)):
        if rising and y[i-1] < target <= y[i] or (not rising and y[i-1] > target >= y[i]):
            # linear interpolation
            y1p, y2p = y[i-1], y[i]
            if y2p == y1p:
                return t[i]
            alpha = (target - y1p) / (y2p - y1p)
            alpha = max(0.0, min(1.0, alpha))
            return t[i-1] + alpha * (t[i] - t[i-1])
    return float('nan')


def compute_metrics(t: List[float], y: List[float], sp_series: List[float], band: float, dwell: float, smooth: float) -> dict:
    # Use a smoothed temperature trace for metrics only
    yf = _moving_average_time(t, y, smooth)

    sp = sp_series[-1] if sp_series and all(abs(s - sp_series[0]) < 1e-9 for s in sp_series) else sp_series[-1] if sp_series else None
    if sp is None:
        raise ValueError("Setpoint not found in input; provide a top-level or per-sample setpoint.")

    y0 = y[0]
    step_amp = sp - y0
    duration = t[-1] - t[0] if t else 0.0

    # Rise time (10% to 90%) on smoothed signal
    t10 = _first_time_cross(t, yf, y0, sp, 0.10)
    t90 = _first_time_cross(t, yf, y0, sp, 0.90)
    rise_time = t90 - t10 if (not math.isnan(t10) and not math.isnan(t90) and t90 >= t10) else float('nan')

    # Overshoot normalized by step amplitude
    max_temp = max(y) if y else float('nan')
    overshoot = 0.0
    if abs(step_amp) > 1e-9:
        overshoot = max(0.0, (max_temp - sp) / abs(step_amp))

    # Settling time with band and dwell on smoothed signal
    # Identify first time index where all following samples in the next dwell seconds are within band
    # If not found, return duration
    settle_time = duration
    if t:
        # Build in-band boolean
        in_band = [abs(yf[i] - sp) <= band for i in range(len(yf))]
        # dwell window in samples
        dts = [t[i+1] - t[i] for i in range(len(t)-1)]
        dt = sorted(dts)[len(dts)//2] if dts else 1.0
        dwell_n = max(1, int(round(dwell / max(dt, 1e-6))))
        for i in range(len(t)):
            j_end = min(len(t), i + dwell_n)
            if all(in_band[k] for k in range(i, j_end)):
                settle_time = t[i] - t[0]
                break

    # Steady-state error as mean absolute error over the last window
    last_window = max(1.0, min(15.0, 0.1 * duration))
    # Gather samples in the last window for smoothed signal
    idx0 = 0
    for i in range(len(t)):
        if t[-1] - t[i] <= last_window:
            idx0 = i
            break
    if t:
        ss_err = sum(abs(yf[i] - sp) for i in range(idx0, len(t))) / max(1, len(t) - idx0)
    else:
        ss_err = float('nan')

    return {
        "rise_time": 0.0 if math.isnan(rise_time) else float(rise_time),
        "overshoot": float(overshoot),
        "settling_time": float(settle_time),
        "steady_state_error": float(ss_err),
        "max_temp": float(max_temp)
    }


def main():
    ap = argparse.ArgumentParser(description="Compute noise-robust performance metrics from control log.")
    ap.add_argument("--input", default="control_log.json", help="Control JSON path")
    ap.add_argument("--output", default="metrics.json", help="Output metrics JSON path")
    ap.add_argument("--band", type=float, default=0.5, help="Settling band (±band around setpoint)")
    ap.add_argument("--dwell", type=float, default=5.0, help="Dwell time in seconds for settling")
    ap.add_argument("--smooth", type=float, default=2.0, help="Moving-average window in seconds (metrics only)")
    args = ap.parse_args()

    with open(args.input, "r") as f:
        obj = json.load(f)

    samples = obj.get("data", [])
    if not samples:
        raise SystemExit("No control samples found in input.")

    t = [float(s.get("time", 0.0)) for s in samples]
    y = [float(s.get("temperature", 0.0)) for s in samples]

    # Setpoint can be top-level or per-sample; build a series for convenience
    top_sp = obj.get("setpoint", None)
    sp_series = []
    for s in samples:
        if "setpoint" in s:
            sp_series.append(float(s.get("setpoint")))
        elif top_sp is not None:
            sp_series.append(float(top_sp))
        else:
            sp_series.append(float('nan'))

    if any(math.isnan(v) for v in sp_series):
        raise SystemExit("Setpoint not found in top-level or per-sample entries.")

    metrics = compute_metrics(t, y, sp_series, args.band, args.dwell, args.smooth)

    with open(args.output, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
