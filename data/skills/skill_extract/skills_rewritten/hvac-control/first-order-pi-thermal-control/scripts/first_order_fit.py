#!/usr/bin/env python3
"""
First-order model identification for thermal step tests.

Reads a calibration JSON log with entries like:
{
  "phase": "calibration",
  "data": [
    {"time": <float>, "temperature": <float>, "heater_power": <float>},
    ...
  ]
}

Outputs estimated_params.json with keys:
{
  "K": <float>,
  "tau": <float>,
  "r_squared": <float>,
  "fitting_error": <float>
}

Usage:
  python3 scripts/first_order_fit.py --input calibration_log.json --output estimated_params.json

This script:
- Detects the largest actuator step.
- Computes K as Δy/Δu using pre/post means.
- Estimates tau using the 63.2% method; falls back to slope-based tau if needed.
- Computes fit diagnostics (R^2 and RMSE) on post-step data.
"""

import argparse
import json
import math
import statistics
from typing import List, Tuple


def _moving_average(vals: List[float], window: int) -> List[float]:
    if window <= 1:
        return vals[:]
    out = []
    s = 0.0
    q = []
    for v in vals:
        q.append(v)
        s += v
        if len(q) > window:
            s -= q.pop(0)
        out.append(s / len(q))
    return out


def _detect_step(u: List[float]) -> int:
    # Return index where the largest absolute step occurs (between i and i+1)
    if len(u) < 2:
        return 0
    diffs = [abs(u[i+1] - u[i]) for i in range(len(u) - 1)]
    idx = max(range(len(diffs)), key=lambda i: diffs[i])
    return idx + 1  # index of first sample after the step


def _mean_segment(x: List[float], start: int, end: int) -> float:
    start = max(0, start)
    end = min(len(x), end)
    if end <= start:
        return x[start] if start < len(x) else (x[-1] if x else 0.0)
    return sum(x[start:end]) / (end - start)


def fit_first_order(t: List[float], y: List[float], u: List[float]) -> Tuple[float, float, float, float]:
    # Identify step
    i_step = _detect_step(u)
    if i_step <= 0:
        i_step = 1

    # Pre/post windows
    pre_end = max(1, i_step)
    pre_start = 0
    post_start = i_step
    post_end = len(t)

    # Compute means
    y0 = _mean_segment(y, pre_start, pre_end)
    u0 = _mean_segment(u, pre_start, pre_end)
    y_inf = _mean_segment(y, max(post_start, int(0.9 * len(y))), len(y))
    u1 = _mean_segment(u, max(post_start, int(0.9 * len(u))), len(u))

    du = u1 - u0
    if abs(du) < 1e-6:
        raise ValueError("Detected actuator step is too small to estimate gain.")
    dy = y_inf - y0
    K = dy / du

    # Estimate tau via 63.2% method
    target = y0 + 0.632 * dy
    tau = None
    # Find first crossing of target after step
    for j in range(post_start, len(t)):
        if dy >= 0 and y[j] >= target or dy < 0 and y[j] <= target:
            # Linear interpolation for better tau estimate
            if j == 0:
                tau = max(t[j] - t[post_start], 1e-6)
            else:
                t1, y1 = t[j-1], y[j-1]
                t2, y2 = t[j], y[j]
                if y2 == y1:
                    tau = t[j] - t[post_start]
                else:
                    frac = (target - y1) / (y2 - y1)
                    tcross = t1 + max(0.0, min(1.0, frac)) * (t2 - t1)
                    tau = max(tcross - t[post_start], 1e-6)
            break

    # Fallback: slope-based tau near step
    if tau is None or not math.isfinite(tau) or tau <= 0:
        # Use first ~10% of post-step data for slope
        post_len = max(1, len(t) - post_start)
        span = max(2, min(post_len, int(0.1 * post_len)))
        ts = t[post_start:post_start + span]
        ys = y[post_start:post_start + span]
        if len(ts) >= 2:
            # Simple linear regression for slope
            t_mean = sum(ts) / len(ts)
            y_mean = sum(ys) / len(ys)
            num = sum((ti - t_mean) * (yi - y_mean) for ti, yi in zip(ts, ys))
            den = sum((ti - t_mean) ** 2 for ti in ts)
            slope = num / den if den != 0 else 0.0
            if abs(slope) > 1e-9:
                tau = abs(dy / slope)
            else:
                tau = 1.0
        else:
            tau = 1.0

    # Build prediction for post-step and compute diagnostics
    y_hat = []
    y_obs = []
    t0 = t[post_start]
    for j in range(post_start, len(t)):
        y_pred = y0 + K * du * (1.0 - math.exp(-(t[j] - t0) / tau))
        y_hat.append(y_pred)
        y_obs.append(y[j])

    if len(y_obs) >= 2:
        y_mean = sum(y_obs) / len(y_obs)
        sst = sum((yo - y_mean) ** 2 for yo in y_obs)
        sse = sum((yo - yh) ** 2 for yo, yh in zip(y_obs, y_hat))
        r2 = 1.0 - (sse / sst) if sst > 0 else 1.0
        rmse = math.sqrt(sse / len(y_obs))
    else:
        r2 = 1.0
        rmse = 0.0

    return (float(K), float(tau), float(r2), float(rmse))


def main():
    ap = argparse.ArgumentParser(description="First-order model fit from calibration step test.")
    ap.add_argument("--input", default="calibration_log.json", help="Calibration JSON path")
    ap.add_argument("--output", default="estimated_params.json", help="Output JSON path")
    args = ap.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    samples = data.get("data", [])
    if not samples:
        raise SystemExit("No calibration samples found in input.")

    t = [float(s.get("time", 0.0)) for s in samples]
    y = [float(s.get("temperature", 0.0)) for s in samples]
    u = [float(s.get("heater_power", 0.0)) for s in samples]

    # Optional light smoothing for robustness
    if len(t) > 5:
        y = _moving_average(y, window=max(1, len(t) // 100))

    K, tau, r2, rmse = fit_first_order(t, y, u)

    out = {
        "K": round(K, 6),
        "tau": round(tau, 6),
        "r_squared": round(r2, 6),
        "fitting_error": round(rmse, 6),
    }
    with open(args.output, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
