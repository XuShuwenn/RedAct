#!/usr/bin/env python3
"""
Compute Reynolds number for internal pipe flow and classify regime.

Usage examples:
  - From CLI values:
      python scripts/reynolds_pipe.py --rho 1000 --mu 0.001 --D 0.05 --v 1.0
  - From input file (keys may include rho/\u03c1, mu/\u00b5/\u03bc, D/diameter, v/velocity):
      python scripts/reynolds_pipe.py --in input.txt
  - Write to an output file in two-line format:
      python scripts/reynolds_pipe.py --in input.txt --out output.txt

If both an input file and CLI values are provided, CLI values override file values.
"""

import argparse
import os
import re
import sys
from typing import Dict, Optional

FLOAT_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")

KEY_MAP = {
    # density
    'rho': 'rho', 'p': 'rho', 'density': 'rho', '\u03c1': 'rho',
    # dynamic viscosity
    'mu': 'mu', '\u03bc': 'mu', '\u00b5': 'mu', 'viscosity': 'mu', 'dynamic_viscosity': 'mu',
    # diameter
    'd': 'D', 'diameter': 'D', 'pipe_diameter': 'D', 'D': 'D',
    # velocity
    'v': 'v', 'u': 'v', 'velocity': 'v', 'flow_velocity': 'v',
}

REQUIRED_KEYS = {'rho', 'mu', 'D', 'v'}


def first_float(text: str) -> Optional[float]:
    match = FLOAT_RE.search(text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def normalize_key(key: str) -> Optional[str]:
    k = key.strip()
    # Preserve uppercase D; others lowercased for mapping
    if k == 'D':
        return 'D'
    k_low = k.lower()
    return KEY_MAP.get(k_low) or KEY_MAP.get(k)


def parse_kv_line(line: str) -> Optional[tuple]:
    # Remove comments
    line = line.split('#', 1)[0].split('//', 1)[0].strip()
    if not line:
        return None
    # Try separators: ':', '=', whitespace
    for sep in (':', '='):
        if sep in line:
            left, right = line.split(sep, 1)
            key = normalize_key(left.strip())
            val = first_float(right)
            if key and val is not None:
                return (key, val)
            return None
    # Fallback: whitespace split
    parts = line.split()
    if len(parts) >= 2:
        key = normalize_key(parts[0])
        val = first_float(' '.join(parts[1:]))
        if key and val is not None:
            return (key, val)
    return None


def parse_input_file(path: str) -> Dict[str, float]:
    values: Dict[str, float] = {}
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            kv = parse_kv_line(raw)
            if not kv:
                continue
            k, v = kv
            values[k] = v
    return values


def validate(values: Dict[str, float]) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in values]
    if missing:
        raise ValueError(f"Missing required keys: {', '.join(sorted(missing))}")
    rho = values['rho']
    mu = values['mu']
    D = values['D']
    v = values['v']
    if mu <= 0:
        raise ValueError("Dynamic viscosity (mu) must be > 0.")
    if D <= 0:
        raise ValueError("Pipe diameter (D) must be > 0.")
    if rho <= 0:
        raise ValueError("Density (rho) must be > 0.")
    if v < 0:
        raise ValueError("Velocity (v) must be >= 0.")


def compute_re(rho: float, mu: float, D: float, v: float) -> float:
    return (rho * v * D) / mu


def classify_regime(re_unrounded: float) -> str:
    if re_unrounded < 2300:
        return 'laminar'
    elif re_unrounded < 4000:
        return 'transitional'
    else:
        return 'turbulent'


def format_output(re_value: float, regime: str) -> str:
    return f"Reynolds number: {re_value:.1f}\nFlow regime: {regime}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Reynolds number and flow regime for internal pipe flow")
    parser.add_argument('--in', dest='inp', help='Path to input file with key-value pairs')
    parser.add_argument('--out', dest='out', help='Path to write two-line output')
    parser.add_argument('--rho', type=float, help='Density (kg/m^3)')
    parser.add_argument('--mu', type=float, help='Dynamic viscosity (Pa·s)')
    parser.add_argument('--D', type=float, help='Pipe diameter (m)')
    parser.add_argument('--v', type=float, help='Average velocity (m/s)')
    args = parser.parse_args()

    values: Dict[str, float] = {}

    if args.inp:
        if not os.path.exists(args.inp):
            print(f"ERROR: Input file not found: {args.inp}", file=sys.stderr)
            return 1
        try:
            values.update(parse_input_file(args.inp))
        except Exception as e:
            print(f"ERROR: Failed to parse input file: {e}", file=sys.stderr)
            return 1

    # CLI overrides
    if args.rho is not None:
        values['rho'] = args.rho
    if args.mu is not None:
        values['mu'] = args.mu
    if args.D is not None:
        values['D'] = args.D
    if args.v is not None:
        values['v'] = args.v

    try:
        validate(values)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    rho = values['rho']
    mu = values['mu']
    D = values['D']
    v = values['v']

    re_unrounded = compute_re(rho, mu, D, v)
    regime = classify_regime(re_unrounded)
    out_text = format_output(re_unrounded, regime)

    if args.out:
        try:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(out_text)
        except Exception as e:
            print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(out_text)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
