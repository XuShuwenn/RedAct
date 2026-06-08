#!/usr/bin/env python3
"""Structural isomer counter helper for small acyclic alkanes and DBE checks.

Features:
- Parse chemical formulas like C4H10, C6H14
- Compute DBE (index of hydrogen deficiency)
- Fast-path count for acyclic alkanes (CnH2n+2) using a built-in mapping for small n
- Strict single-line output: "Number of isomers: <count>"

Usage:
  python scripts/isomer_counter.py --formula "C4H10"
  python scripts/isomer_counter.py --formula "C6H14"

Exit codes:
  0: success and count printed
  2: unsupported formula (e.g., DBE > 0, heteroatoms, or n outside mapping)
  3: invalid input (parse failure, nonpositive counts)
"""

import argparse
import re
import sys
from typing import Dict

# Number of constitutional isomers of acyclic alkanes CnH2n+2
# Reference sequence is well-established; include small n for quick answers.
ALKANE_ISOMERS = {
    1: 1,   # methane
    2: 1,   # ethane
    3: 1,   # propane
    4: 2,
    5: 3,
    6: 5,
    7: 9,
    8: 18,
    9: 35,
    10: 75,
    11: 159,
    12: 355,
}

HALOGENS = {"F", "Cl", "Br", "I"}

_FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?)(\d*)")


def parse_formula(s: str) -> Dict[str, int]:
    s = s.strip()
    if not s:
        raise ValueError("Empty formula")
    counts: Dict[str, int] = {}
    pos = 0
    for m in _FORMULA_TOKEN.finditer(s):
        el, num = m.group(1), m.group(2)
        if m.start() != pos:
            # Found a gap -> invalid segment
            raise ValueError(f"Invalid segment near '{s[pos:m.start()]}'")
        n = int(num) if num else 1
        if n <= 0:
            raise ValueError("Element count must be positive")
        counts[el] = counts.get(el, 0) + n
        pos = m.end()
    if pos != len(s):
        raise ValueError(f"Unparsed tail: '{s[pos:]}'")
    return counts


def dbe(counts: Dict[str, int]) -> float:
    C = counts.get("C", 0)
    H = counts.get("H", 0)
    N = counts.get("N", 0)
    X = sum(counts.get(h, 0) for h in HALOGENS)
    # Oxygen/sulfur, etc., do not affect DBE directly
    return (2 * C + 2 + N - H - X) / 2


def is_acyclic_alkane(counts: Dict[str, int]) -> bool:
    # Only C and H present, and DBE == 0
    allowed = {"C", "H"}
    if set(counts.keys()) - allowed:
        return False
    return dbe(counts) == 0


def count_isomers(counts: Dict[str, int]) -> int:
    """Return isomer count for supported cases, or raise NotImplementedError."""
    if is_acyclic_alkane(counts):
        nC = counts.get("C", 0)
        if nC in ALKANE_ISOMERS:
            return ALKANE_ISOMERS[nC]
        raise NotImplementedError("Alkane carbon count outside built-in mapping")
    raise NotImplementedError("Only acyclic alkanes (C,H; DBE=0) supported by fast path")


def main():
    ap = argparse.ArgumentParser(description="Structural isomer counter (fast path for acyclic alkanes)")
    ap.add_argument("--formula", required=True, help="Molecular formula, e.g., C4H10")
    args = ap.parse_args()

    try:
        counts = parse_formula(args.formula)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(3)

    # Validate DBE for basic sanity
    db = dbe(counts)
    if db < 0:
        print("ERROR: Negative DBE suggests malformed formula", file=sys.stderr)
        sys.exit(3)

    try:
        n = count_isomers(counts)
        print(f"Number of isomers: {n}")
        sys.exit(0)
    except NotImplementedError as e:
        # Unsupported by fast path; caller should use enumeration or references
        print(f"UNSUPPORTED: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
