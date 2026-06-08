#!/usr/bin/env python3
"""Convert Bloch angles (theta, phi) in degrees to Cartesian components (rx, ry, rz).

Features:
- Robust parsing: supports labeled or unlabeled inputs, degree symbols, and extra whitespace.
- Optional normalization of angles.
- Zero-clamps tiny values to avoid -0.000.
- Writes strict, signed, three-decimal output.

Usage:
    python scripts/bloch_vector.py --input /root/input.txt --output /root/output.txt [--normalize] [--epsilon 1e-12] [--strict]

Options:
    --normalize  Normalize phi to [0, 360) and theta to [0, 180].
    --epsilon    Threshold for zero-clamping; abs(value) < epsilon -> 0.0 (default: 1e-12).
    --strict     Enforce pre-round magnitude ~ 1 check; exit nonzero if violated.
"""

import argparse
import math
import re
import sys
from typing import Tuple, Optional

LABEL_THETA = re.compile(r"(?i)\b(theta|θ|ϑ)\b")
LABEL_PHI = re.compile(r"(?i)\b(phi|φ)\b")
FLOAT_RE = re.compile(r"[-+]?((?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][-+]?\d+)?")


def _find_labeled_value(text: str, label_re: re.Pattern) -> Optional[float]:
    # Look for label followed by separators and a number
    # e.g., "theta: 90", "phi = 45°"
    pattern = re.compile(label_re.pattern + r"\s*[:=]?\s*" + FLOAT_RE.pattern)
    m = pattern.search(text)
    if m:
        # The last group matches the numeric literal; extract via FLOAT_RE
        num_match = re.search(FLOAT_RE, m.group(0))
        if num_match:
            return float(num_match.group(0))
    return None


def parse_angles(text: str) -> Tuple[float, float]:
    """Parse theta and phi (degrees) from text.

    Strategy:
    - Prefer labeled values if both present.
    - Otherwise, take the first two numeric literals as theta, phi.
    """
    theta = _find_labeled_value(text, LABEL_THETA)
    phi = _find_labeled_value(text, LABEL_PHI)

    if theta is not None and phi is not None:
        return theta, phi

    nums = [float(m.group(0)) for m in FLOAT_RE.finditer(text)]
    if len(nums) < 2:
        raise ValueError("Could not find two numeric values for theta and phi in input.")
    return nums[0], nums[1]


def normalize_angles(theta_deg: float, phi_deg: float) -> Tuple[float, float]:
    # Map phi to [0, 360); map theta to [0, 180]
    phi = phi_deg % 360.0
    t = theta_deg % 360.0
    if t > 180.0:
        t = 360.0 - t
    return t, phi


def compute_components(theta_deg: float, phi_deg: float) -> Tuple[float, float, float]:
    th = math.radians(theta_deg)
    ph = math.radians(phi_deg)
    rx = math.sin(th) * math.cos(ph)
    ry = math.sin(th) * math.sin(ph)
    rz = math.cos(th)
    return rx, ry, rz


def zero_clamp(x: float, eps: float) -> float:
    return 0.0 if abs(x) < eps else x


def verify_unit_length(rx: float, ry: float, rz: float, tol: float = 1e-12) -> bool:
    r2 = rx * rx + ry * ry + rz * rz
    return abs(r2 - 1.0) <= tol


def format_components(rx: float, ry: float, rz: float) -> str:
    return f"rx: {rx:+.3f}\nry: {ry:+.3f}\nrz: {rz:+.3f}\n"


def main():
    ap = argparse.ArgumentParser(description="Bloch vector from angles (degrees)")
    ap.add_argument("--input", required=True, help="Path to input file containing theta, phi in degrees")
    ap.add_argument("--output", required=True, help="Path to write output components")
    ap.add_argument("--normalize", action="store_true", help="Normalize angles (phi to [0,360), theta to [0,180])")
    ap.add_argument("--epsilon", type=float, default=1e-12, help="Zero-clamp threshold (default: 1e-12)")
    ap.add_argument("--strict", action="store_true", help="Fail if pre-round vector magnitude deviates from 1 beyond tolerance")
    args = ap.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: failed to read input: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        theta_deg, phi_deg = parse_angles(content)
    except Exception as e:
        print(f"ERROR: failed to parse angles: {e}", file=sys.stderr)
        sys.exit(1)

    if args.normalize:
        theta_deg, phi_deg = normalize_angles(theta_deg, phi_deg)

    rx, ry, rz = compute_components(theta_deg, phi_deg)

    if args.strict and not verify_unit_length(rx, ry, rz):
        print("ERROR: vector magnitude deviates from 1 beyond tolerance", file=sys.stderr)
        sys.exit(1)

    rx = zero_clamp(rx, args.epsilon)
    ry = zero_clamp(ry, args.epsilon)
    rz = zero_clamp(rz, args.epsilon)

    out_text = format_components(rx, ry, rz)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_text)
    except Exception as e:
        print(f"ERROR: failed to write output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
