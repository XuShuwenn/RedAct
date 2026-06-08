#!/usr/bin/env python3
"""Chemical formula utilities for structural (constitutional) isomer counting.

Features:
- Robust molecular formula parsing to element counts.
- Degree of Unsaturation (DBE) calculation with halogen and nitrogen support.
- Curated lookup for number of constitutional isomers of acyclic alkanes (C_n H_(2n+2)) for small n.

Usage examples:
    python chem_formula_utils.py --formula "C4H10"

Outputs a small report including element counts, DBE, class, and isomer count if supported.

Notes:
- DBE formula used: DBE = 1 + 0.5 * (2*C + 2 + N - H - X), where X is total halogens (F, Cl, Br, I). O and S do not affect DBE.
- Isomer counts here refer to constitutional isomers only (no stereoisomers).
"""

import re
import sys
import argparse
from typing import Dict, Optional

# Regular expression for tokenizing a chemical formula
TOKEN_RE = re.compile(r"([A-Z][a-z]?)(\d*)")

HALOGENS = {"F", "Cl", "Br", "I"}


def parse_formula(formula: str) -> Dict[str, int]:
    """Parse a chemical formula into a dict of element -> count.

    Supports simple sum formulas without parentheses (e.g., C4H10, C6H6, C2H5Cl).
    Returns a dict like {"C": 4, "H": 10}.

    Raises ValueError on malformed input.
    """
    if not isinstance(formula, str) or not formula.strip():
        raise ValueError("Empty formula")
    s = formula.strip()

    # Validate: only allowable characters for this simple parser
    if not re.fullmatch(r"[A-Za-z0-9]+", s):
        raise ValueError("Unsupported characters in formula")

    pos = 0
    counts: Dict[str, int] = {}
    for m in TOKEN_RE.finditer(s):
        if m.start() != pos:
            # Detected a gap; means unsupported structure (e.g., parentheses) or malformed input
            raise ValueError("Malformed formula (unexpected structure)")
        elem = m.group(1)
        num = m.group(2)
        pos = m.end()
        if not elem:
            raise ValueError("Missing element symbol")
        # Basic sanity: element starts with uppercase, optional lowercase
        if not re.fullmatch(r"[A-Z][a-z]?", elem):
            raise ValueError(f"Invalid element symbol: {elem}")
        count = int(num) if num else 1
        if count <= 0:
            raise ValueError("Element count must be positive")
        counts[elem] = counts.get(elem, 0) + count

    if pos != len(s):
        # Trailing unsupported content
        raise ValueError("Trailing content after parsing formula")

    return counts


def dbe(counts: Dict[str, int]) -> float:
    """Compute degree of unsaturation (DBE) using:
    DBE = 1 + 0.5 * (2*C + 2 + N - H - X),
    where X is total halogens (F, Cl, Br, I). O and S do not enter the formula.
    Returns a float that should be an integer or half-integer for valid formulas.
    """
    C = counts.get("C", 0)
    H = counts.get("H", 0)
    N = counts.get("N", 0)
    X = sum(counts.get(h, 0) for h in HALOGENS)
    return 1 + 0.5 * (2 * C + 2 + N - H - X)


# Curated constitutional isomer counts for acyclic alkanes (OEIS A000602)
# These values are widely known for small n and exclude stereoisomers
ALKANE_ISOMERS = {
    1: 1,
    2: 1,
    3: 1,
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


def count_alkane_isomers(n_c: int) -> Optional[int]:
    """Return the number of constitutional isomers for an acyclic alkane with n_c carbons.
    Returns None if n_c is outside the curated range.
    """
    return ALKANE_ISOMERS.get(n_c)


def classify_formula(counts: Dict[str, int]) -> str:
    """Classify a formula into a simple bucket for this skill's scope.
    Returns one of: 'acyclic_alkane', 'unsupported'.
    """
    # CH-only check
    elements = set(counts)
    ch_only = elements.issubset({"C", "H"}) and counts.get("C", 0) > 0
    if ch_only:
        C = counts.get("C", 0)
        H = counts.get("H", 0)
        if dbe(counts) == 0 and H == 2 * C + 2:
            return "acyclic_alkane"
    return "unsupported"


def main():
    ap = argparse.ArgumentParser(description="Chemical formula parsing and simple isomer counting")
    ap.add_argument("--formula", required=True, help="Molecular formula string (e.g., C4H10)")
    args = ap.parse_args()

    try:
        counts = parse_formula(args.formula)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    formula_class = classify_formula(counts)
    db = dbe(counts)

    print("Parsed counts:")
    for k in sorted(counts.keys()):
        print(f"  {k}: {counts[k]}")
    print(f"DBE: {db}")
    print(f"Class: {formula_class}")

    if formula_class == "acyclic_alkane":
        n_c = counts.get("C", 0)
        iso = count_alkane_isomers(n_c)
        if iso is not None:
            print(f"Constitutional isomers (acyclic alkane): {iso}")
        else:
            print("Constitutional isomers (acyclic alkane): unsupported carbon count range")
    else:
        print("Constitutional isomers: unsupported formula class for this utility")


if __name__ == "__main__":
    main()
