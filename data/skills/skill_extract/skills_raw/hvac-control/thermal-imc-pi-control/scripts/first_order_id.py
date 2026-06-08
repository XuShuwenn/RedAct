#!/usr/bin/env python3
"""First-order thermal system identification from an open-loop step test.

- Input: calibration_log.json (format: {"phase": "calibration", "heater_power_test": <u>, "data": [{time,temperature,heater_power}, ...]})
- Output: estimated_params.json (keys: K, tau, r_squared, fitting_error)

This script does not require SciPy and uses robust heuristics:
- Baseline T0 from pre-step samples
- Gain K from final average response
- Time constant tau from t_63 (63.2% of the step)
- R^2 and RMSE computed from the analytical step model
"""

import argparse
import json
import math
from statistics import mean
from typing import List, Dict


def _interp_time_at_value(t0: float, y0: float, t1: float, y1: float, y_target: float) -> float:
    if y1 == y0:
        return t1
    frac = (y_target - y0) / (y1 - y0)
    return t0 + max(0.0, min(1.0, frac)) * (t1 - t0)


def identify_first_order(cal: Dict) -> Dict:
    data = cal.get("data", [])
    if not data:
        raise ValueError("No calibration data found")

    # Find step onset (first index where heater turns on)
    step_idx = None
    for i, d in enumerate(data):
        if float(d.get("heater_power", 0.0)) > 0.0:
            step_idx = i
            break
    if step_idx is None:
        raise ValueError("No step input found (heater_power never > 0)")

    # Baseline T0 (mean of pre-step temps if available)
    pre = data[:step_idx]
    if pre:
        T0 = mean(float(p["temperature"]) for p in pre)
    else:
        T0 = float(data[0]["temperature"])  # fallback

    # Constant input u (assume constant during step)
    u = float(cal.get("heater_power_test", data[step_idx].get("heater_power", 0.0)))
    if u <= 0:
        raise ValueError("Heater power test value must be > 0")

    # Step response arrays referenced to step onset
    step = data[step_idx:]
    t = [float(d["time"]) - float(step[0]["time"]) for d in step]
    y = [float(d["temperature"]) for d in step]

    if len(t) < 3:
        raise ValueError("Insufficient post-step samples for identification")

    # Final average (last N points) for steady-state estimate
    N_tail = min(10, len(y))
    y_ss = mean(y[-N_tail:])

    # Gain estimate
    delta = y_ss - T0
    K = delta / u if u != 0 else 0.0
    if K <= 0:
        # Fallback: ensure positive gain; use minimal positive guess
        K = max(1e-6, abs(delta) / max(u, 1e-6))

    # Time constant from 63.2% point (linear interpolation)
    target = T0 + 0.632 * (y_ss - T0)
    tau = None
    for i in range(1, len(y)):
        if (y[i-1] - target) <= 0 <= (y[i] - target):
            tau = _interp_time_at_value(t[i-1], y[i-1], t[i], y[i], target)
            break
    if tau is None:
        # Fallback: half of the test duration if not reached
        tau = max(1e-6, t[-1] / 2.0)

    # Predicted response and fit quality
    # T(t) = T_ss - (T_ss - T0) * exp(-t/tau), T_ss = T0 + K*u
    T_ss = T0 + K * u
    y_pred = [T_ss - (T_ss - T0) * math.exp(-ti / max(tau, 1e-9)) for ti in t]

    # R^2 and RMSE
    y_mean = mean(y)
    ss_res = sum((yi - yp) ** 2 for yi, yp in zip(y, y_pred))
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    rmse = (ss_res / len(y)) ** 0.5 if y else 0.0

    return {
        "K": round(K, 6),
        "tau": round(tau, 6),
        "r_squared": round(r2, 6),
        "fitting_error": round(rmse, 6),
    }


def main():
    ap = argparse.ArgumentParser(description="Identify first-order thermal parameters from a step test")
    ap.add_argument("--calibration", required=True, help="Path to calibration_log.json")
    ap.add_argument("--out", required=True, help="Path to write estimated_params.json")
    args = ap.parse_args()

    with open(args.calibration, "r") as f:
        cal = json.load(f)
    params = identify_first_order(cal)

    with open(args.out, "w") as f:
        json.dump(params, f, indent=2)

    print(f"Estimated parameters written to {args.out}")


if __name__ == "__main__":
    main()
