#!/usr/bin/env python3
"""IMC PI tuning for first-order thermal processes.

Formulas (no dead time):
  Kp = tau / (K * lambda)
  Ki = 1 / (K * lambda)  (equivalently: Ki = Kp / tau)
  Kd = 0

Provide K, tau, and either lambda or a target settling time Ts (approx Ts ≈ 4*lambda).
Outputs tuned_gains.json with {Kp, Ki, Kd, lambda}.
"""

import argparse
import json


def main():
    ap = argparse.ArgumentParser(description="IMC PI tuner for first-order plants")
    ap.add_argument("--K", type=float, required=True, help="Process gain (units per % power)")
    ap.add_argument("--tau", type=float, required=True, help="Time constant (seconds)")
    ap.add_argument("--lambda", dest="lam", type=float, default=None, help="Closed-loop time constant lambda (seconds)")
    ap.add_argument("--target-settling-s", type=float, default=None, help="Desired settling time (seconds)")
    ap.add_argument("--out", required=True, help="Output JSON path for tuned gains")
    args = ap.parse_args()

    if args.K <= 0 or args.tau <= 0:
        raise ValueError("K and tau must be positive")

    lam = args.lam
    if lam is None and args.target_settling_s is not None:
        lam = max(1e-6, args.target_settling_s / 4.0)
    if lam is None:
        # Default heuristic: moderately fast but robust
        lam = max(1e-6, 0.6 * args.tau)

    Kp = args.tau / (args.K * lam)
    Ki = 1.0 / (args.K * lam)
    Kd = 0.0

    tuned = {
        "Kp": round(Kp, 6),
        "Ki": round(Ki, 6),
        "Kd": round(Kd, 6),
        "lambda": round(lam, 6),
    }

    with open(args.out, "w") as f:
        json.dump(tuned, f, indent=2)

    print(f"Tuned gains written to {args.out}")


if __name__ == "__main__":
    main()
