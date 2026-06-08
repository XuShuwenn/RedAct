#!/usr/bin/env python3
"""Noise-tolerant performance metrics for closed-loop thermal control.

Input: control_log.json (expects {"phase":"control","setpoint":<sp>,"data":[{time,temperature,setpoint,heater_power,error},...]})
- If setpoint is not present at top-level, pass via --setpoint.

Metrics:
- rise_time: time from 10% to 90% of the step
- overshoot: (max(filtered_temp) - setpoint) / step_magnitude
- settling_time: earliest time after which filtered temps remain within ±band
- steady_state_error: mean |temp - setpoint| over last ss_seconds
- max_temp: max observed temperature (raw)

Filtering: moving average over ~ma_seconds to mitigate sensor noise.
"""

import argparse
import json
import numpy as np


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values.copy()
    kernel = np.ones(window) / window
    return np.convolve(values, kernel, mode='valid')


def interp_time_at_level(times, values, target):
    for i in range(1, len(values)):
        y0, y1 = values[i-1], values[i]
        if (y0 - target) <= 0 <= (y1 - target):
            t0, t1 = times[i-1], times[i]
            if y1 == y0:
                return t1
            frac = (target - y0) / (y1 - y0)
            return t0 + np.clip(frac, 0, 1) * (t1 - t0)
    return None


def earliest_sustained_in_band(times, values, center, band, min_count):
    # Find earliest index from which all remaining samples are in band
    for i in range(len(values)):
        if np.all(np.abs(values[i:] - center) <= band):
            return times[i]
    # Fallback: sustained window of min_count
    for i in range(len(values) - min_count + 1):
        if np.all(np.abs(values[i:i+min_count] - center) <= band):
            return times[i]
    return times[-1]


def main():
    ap = argparse.ArgumentParser(description="Compute noise-tolerant control metrics")
    ap.add_argument("--control", required=True, help="Path to control_log.json")
    ap.add_argument("--out", required=True, help="Path to write metrics.json")
    ap.add_argument("--setpoint", type=float, default=None, help="Setpoint if not provided in control log")
    ap.add_argument("--band", type=float, default=0.5, help="Absolute settling band (e.g., 0.5 C)")
    ap.add_argument("--ma-seconds", type=float, default=10.0, help="Moving average window (seconds)")
    ap.add_argument("--ss-seconds", type=float, default=30.0, help="Seconds for steady-state error averaging")
    args = ap.parse_args()

    with open(args.control, "r") as f:
        log = json.load(f)

    setpoint = log.get("setpoint", args.setpoint)
    if setpoint is None:
        raise ValueError("Setpoint must be provided either in control log or via --setpoint")

    data = log.get("data", [])
    if not data:
        raise ValueError("No control data found")

    times = np.array([float(d["time"]) for d in data], dtype=float)
    temps = np.array([float(d["temperature"]) for d in data], dtype=float)

    # Step magnitude based on initial temperature
    T0 = temps[0]
    step_mag = setpoint - T0

    # Rise time (10%->90% of step)
    t10 = t90 = None
    if abs(step_mag) > 1e-9:
        y10 = T0 + 0.1 * step_mag
        y90 = T0 + 0.9 * step_mag
        t10 = interp_time_at_level(times, temps, y10)
        t90 = interp_time_at_level(times, temps, y90)
    rise_time = (t90 - t10) if (t10 is not None and t90 is not None and t90 >= t10) else None

    # Moving average filter
    dt_est = np.median(np.diff(times)) if len(times) > 1 else 0.5
    win = max(1, int(round(args.ma_seconds / max(dt_est, 1e-6))))
    ftemps = moving_average(temps, win)
    ftimes = times[win - 1:] if win > 1 else times

    # Overshoot on filtered temps
    max_f = float(np.max(ftemps))
    overshoot = 0.0
    if abs(step_mag) > 1e-9:
        overshoot = max(0.0, (max_f - setpoint) / abs(step_mag))

    # Settling time (absolute band on filtered temps)
    sustain_count = max(1, int(round(10.0 / max(dt_est, 1e-6))))  # ~10 seconds of samples
    settle_time = earliest_sustained_in_band(ftimes, ftemps, setpoint, args.band, sustain_count)
    settling_time = float(settle_time - times[0])

    # Steady-state error over last ss_seconds
    ss_start_time = times[-1] - args.ss_seconds
    ss_mask = times >= ss_start_time
    if not np.any(ss_mask):
        ss_mask = np.ones_like(times, dtype=bool)
    sse = float(abs(np.mean(temps[ss_mask]) - setpoint))

    metrics = {
        "rise_time": None if rise_time is None else float(round(rise_time, 4)),
        "overshoot": float(round(overshoot, 6)),
        "settling_time": float(round(settling_time, 4)),
        "steady_state_error": float(round(sse, 6)),
        "max_temp": float(round(float(np.max(temps)), 6))
    }

    with open(args.out, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Metrics written to {args.out}")


if __name__ == "__main__":
    main()
