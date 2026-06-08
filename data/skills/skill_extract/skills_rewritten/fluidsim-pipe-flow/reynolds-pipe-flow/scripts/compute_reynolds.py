#!/usr/bin/env python3
"""Compute pipe-flow Reynolds number from density, dynamic viscosity, diameter, and velocity.

Features:
- Accepts values via command-line options or by parsing a labeled text file.
- Robust parsing for common label variants (rho/\u03c1, mu/\u00b5/\u03bc, D/diameter, v/velocity) and scientific notation.
- Validates inputs and classifies flow regime using standard thresholds.
- Outputs exactly two lines matching the common benchmark format or writes them to a file.

Usage examples:
  python scripts/compute_reynolds.py --rho 1000 --mu 0.001 --D 0.05 --v 1.2
  python scripts/compute_reynolds.py --from-file input.txt --write output.txt
"""

import argparse
import re
import sys
from typing import Optional, Tuple

FLOAT_RE = re.compile(r"[+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+\-]?\d+)?")

LABEL_SETS = {
    'rho': (r"rho", r"\u03c1", r"density", r"dens"),
    'mu': (r"mu", r"\u00b5", r"\u03bc", r"viscosity", r"dynamic\s+viscosity"),
    'D': (r"\bD\b", r"diameter", r"pipe\s*diameter"),
    'v': (r"\bv\b", r"velocity", r"flow\s*velocity", r"speed"),
}

THRESHOLDS = (2300.0, 4000.0)  # laminar < 2300, 2300 <= transitional < 4000, turbulent >= 4000


def reynolds_number(rho: float, v: float, D: float, mu: float) -> float:
    return (rho * v * D) / mu


def classify_re(Re: float) -> str:
    lo, hi = THRESHOLDS
    if Re < lo:
        return "laminar"
    elif Re < hi:
        return "transitional"
    else:
        return "turbulent"


def find_first_float(s: str) -> Optional[float]:
    m = FLOAT_RE.search(s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def compile_label_pattern(keys) -> re.Pattern:
    # Build a case-insensitive pattern to detect any of the provided keys
    joined = "|".join(keys)
    return re.compile(fr"(?i)(?:{joined})")


LABEL_PATTERNS = {
    k: compile_label_pattern(v) for k, v in LABEL_SETS.items()
}


def extract_values_from_text(text: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    rho = mu = D = v = None
    # Scan line by line; on a match, extract the first float on that line
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        if rho is None and LABEL_PATTERNS['rho'].search(l):
            val = find_first_float(l)
            if val is not None:
                rho = val
                continue
        if mu is None and LABEL_PATTERNS['mu'].search(l):
            val = find_first_float(l)
            if val is not None:
                mu = val
                continue
        if D is None and LABEL_PATTERNS['D'].search(l):
            val = find_first_float(l)
            if val is not None:
                D = val
                continue
        if v is None and LABEL_PATTERNS['v'].search(l):
            val = find_first_float(l)
            if val is not None:
                v = val
                continue

    # If any remain missing, try a broader search across the whole text as a fallback
    if rho is None:
        m = LABEL_PATTERNS['rho'].search(text)
        if m:
            tail = text[m.end():]
            rho = find_first_float(tail)
    if mu is None:
        m = LABEL_PATTERNS['mu'].search(text)
        if m:
            tail = text[m.end():]
            mu = find_first_float(tail)
    if D is None:
        m = LABEL_PATTERNS['D'].search(text)
        if m:
            tail = text[m.end():]
            D = find_first_float(tail)
    if v is None:
        m = LABEL_PATTERNS['v'].search(text)
        if m:
            tail = text[m.end():]
            v = find_first_float(tail)

    return rho, mu, D, v


def parse_args():
    p = argparse.ArgumentParser(description="Compute pipe-flow Reynolds number and classify regime")
    p.add_argument('--rho', type=float, help='Fluid density (kg/m^3)')
    p.add_argument('--mu', type=float, help='Dynamic viscosity (Pa·s)')
    p.add_argument('--D', type=float, help='Pipe diameter (m)')
    p.add_argument('--v', type=float, help='Average flow velocity (m/s)')
    p.add_argument('--from-file', dest='from_file', help='Path to input text file to parse')
    p.add_argument('--write', help='Path to write standardized two-line output')
    return p.parse_args()


def main():
    args = parse_args()

    rho = args.rho
    mu = args.mu
    D = args.D
    v = args.v

    if args.from_file:
        try:
            with open(args.from_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"ERROR: unable to read input file: {e}", file=sys.stderr)
            sys.exit(1)
        prho, pmu, pD, pv = extract_values_from_text(text)
        if rho is None:
            rho = prho
        if mu is None:
            mu = pmu
        if D is None:
            D = pD
        if v is None:
            v = pv

    missing = []
    if rho is None:
        missing.append('rho (density)')
    if mu is None:
        missing.append('mu (dynamic viscosity)')
    if D is None:
        missing.append('D (diameter)')
    if v is None:
        missing.append('v (velocity)')

    if missing:
        print("ERROR: missing values: " + ", ".join(missing), file=sys.stderr)
        sys.exit(1)

    # Basic physical validation
    if mu <= 0:
        print("ERROR: dynamic viscosity mu must be > 0", file=sys.stderr)
        sys.exit(1)
    if rho <= 0:
        print("ERROR: density rho must be > 0", file=sys.stderr)
        sys.exit(1)
    if D <= 0:
        print("ERROR: diameter D must be > 0", file=sys.stderr)
        sys.exit(1)
    if v < 0:
        print("ERROR: velocity v must be >= 0", file=sys.stderr)
        sys.exit(1)

    Re = reynolds_number(rho, v, D, mu)
    regime = classify_re(Re)

    # Format with exactly one decimal for display
    Re_str = f"{Re:.1f}"
    out_lines = [
        f"Reynolds number: {Re_str}",
        f"Flow regime: {regime}",
    ]

    if args.write:
        try:
            with open(args.write, 'w', encoding='utf-8') as f:
                f.write("\n".join(out_lines))
        except Exception as e:
            print(f"ERROR: unable to write output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n".join(out_lines))


if __name__ == '__main__':
    main()
