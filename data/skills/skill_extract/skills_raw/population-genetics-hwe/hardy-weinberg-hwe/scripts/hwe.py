#!/usr/bin/env python3
"""Hardy–Weinberg Equilibrium calculator for a biallelic locus.

Features:
- Accept counts via CLI flags (--AA, --Aa, --aa) or from an input text file.
- Validates counts (non-negative integers, N > 0).
- Computes p, q, expected genotype counts under HWE, He and Ho.
- Verifies invariants and prints results with 4-decimal formatting.

Usage:
  python scripts/hwe.py --AA 12 --Aa 7 --aa 5
  python scripts/hwe.py --input /path/to/input.txt
  python scripts/hwe.py --AA 12 --Aa 7 --aa 5 --out /path/to/output.txt

Input file parsing rules:
- Case-insensitive keys: AA, Aa, aa (leading/trailing spaces allowed).
- The script searches for lines like "AA: <num>" or "AA <num>"; other text is ignored.
"""

import argparse
import math
import os
import re
import sys
from typing import Dict, Optional, Tuple

KEYS = ("AA", "Aa", "aa")
LINE_PATTERNS = [
    re.compile(r"^\s*(AA|Aa|aa)\s*[:=]?\s*(-?\d+)\s*$", re.IGNORECASE),
    re.compile(r"\b(AA|Aa|aa)\b\s*[:=]?\s*(-?\d+)\b", re.IGNORECASE),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Hardy–Weinberg calculator (biallelic)")
    p.add_argument("--AA", type=int, help="Count of homozygous reference (AA)")
    p.add_argument("--Aa", type=int, help="Count of heterozygous (Aa)")
    p.add_argument("--aa", type=int, help="Count of homozygous alternate (aa)")
    p.add_argument("--input", type=str, help="Path to text file containing AA, Aa, aa")
    p.add_argument("--out", type=str, help="Output file path (default: stdout)")
    return p.parse_args()


def parse_file(path: str) -> Dict[str, int]:
    counts: Dict[str, Optional[int]] = {k: None for k in KEYS}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            for pat in LINE_PATTERNS:
                m = pat.search(line)
                if m:
                    key = m.group(1)
                    val = int(m.group(2))
                    # Normalize key capitalization to match KEYS
                    if key.lower() == "aa":
                        # Ambiguity: could be AA or aa; disambiguate by exact case if possible
                        # Use original case to decide; if original was lowercase 'aa', map to 'aa'; if uppercase 'AA', handle separately.
                        # But regex captured the literal; we check if it equals 'AA' exactly.
                        pass
                    if key == "AA":
                        counts["AA"] = val
                    elif key == "Aa":
                        counts["Aa"] = val
                    elif key == "aa":
                        counts["aa"] = val
                    else:
                        # Fallback by case-insensitive mapping
                        low = key.lower()
                        if low == "aa":
                            counts["aa"] = val
                        elif low == "aa".upper().lower():
                            counts["AA"] = val
                        elif low == "aa".capitalize().lower():
                            counts["Aa"] = val
            # Continue scanning lines to allow duplicates; last occurrence wins.
    missing = [k for k, v in counts.items() if v is None]
    if missing:
        raise ValueError(f"Missing keys in input file: {', '.join(missing)}")
    return {k: int(v) for k, v in counts.items()}  # type: ignore


def parse_inputs(ns: argparse.Namespace) -> Tuple[int, int, int]:
    if ns.input:
        counts = parse_file(ns.input)
        AA, Aa, aa = counts["AA"], counts["Aa"], counts["aa"]
        return AA, Aa, aa
    # Use CLI args
    if ns.AA is None or ns.Aa is None or ns.aa is None:
        raise ValueError("Provide --AA, --Aa, and --aa or an --input file.")
    return ns.AA, ns.Aa, ns.aa


def validate_counts(AA: int, Aa: int, aa: int) -> None:
    for name, val in (("AA", AA), ("Aa", Aa), ("aa", aa)):
        if val is None:
            raise ValueError(f"Missing count: {name}")
        if not isinstance(val, int):
            raise ValueError(f"Count for {name} must be an integer, got {type(val)}")
        if val < 0:
            raise ValueError(f"Count for {name} must be non-negative, got {val}")
    N = AA + Aa + aa
    if N <= 0:
        raise ValueError("Total N must be > 0.")


def compute_hwe(AA: int, Aa: int, aa: int) -> Dict[str, float]:
    N = AA + Aa + aa
    # Allele frequencies
    p = (2 * AA + Aa) / (2 * N)
    q = 1.0 - p
    # Expectations
    exp_AA = N * (p ** 2)
    exp_Aa = N * (2.0 * p * q)
    exp_aa = N * (q ** 2)
    He = 2.0 * p * q
    Ho = Aa / N
    return {
        "N": float(N),
        "p": p,
        "q": q,
        "exp_AA": exp_AA,
        "exp_Aa": exp_Aa,
        "exp_aa": exp_aa,
        "He": He,
        "Ho": Ho,
    }


def verify(results: Dict[str, float], tol_sum: float = 1e-6, tol_eq: float = 1e-12) -> None:
    p = results["p"]
    q = results["q"]
    if not (0.0 - 1e-15 <= p <= 1.0 + 1e-15 and 0.0 - 1e-15 <= q <= 1.0 + 1e-15):
        raise ValueError(f"Allele frequencies out of bounds: p={p}, q={q}")
    if abs((p + q) - 1.0) > tol_eq:
        raise ValueError(f"p + q != 1 within tolerance (p+q={p+q})")
    N = results["N"]
    total_exp = results["exp_AA"] + results["exp_Aa"] + results["exp_aa"]
    if abs(total_exp - N) > tol_sum:
        raise ValueError(f"Expected counts do not sum to N within tolerance (sum={total_exp}, N={N})")
    He = results["He"]
    exp_Aa = results["exp_Aa"]
    if N > 0 and abs(He - (exp_Aa / N)) > tol_eq:
        raise ValueError("He != ExpectedAa/N within tolerance")


def format_output(results: Dict[str, float]) -> str:
    lines = [
        f"Expected AA: {results['exp_AA']:.4f}",
        f"Expected Aa: {results['exp_Aa']:.4f}",
        f"Expected aa: {results['exp_aa']:.4f}",
        f"Expected heterozygosity: {results['He']:.4f}",
        f"Observed heterozygosity: {results['Ho']:.4f}",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    try:
        ns = parse_args()
        AA, Aa, aa = parse_inputs(ns)
        validate_counts(AA, Aa, aa)
        results = compute_hwe(AA, Aa, aa)
        verify(results)
        out_text = format_output(results)
        if ns.out:
            with open(ns.out, "w", encoding="utf-8") as f:
                f.write(out_text)
        else:
            sys.stdout.write(out_text)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
