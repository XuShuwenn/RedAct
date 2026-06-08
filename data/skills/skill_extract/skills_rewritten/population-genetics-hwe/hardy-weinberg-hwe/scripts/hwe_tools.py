#!/usr/bin/env python3
"""Hardy–Weinberg Equilibrium utilities

Compute expected genotype counts and heterozygosity from genotype counts.

Usage:
  - From explicit counts (stdout):
      python hwe_tools.py --AA 120 --Aa 60 --aa 20
  - From input file (write to output file):
      python hwe_tools.py --input input.txt --output output.txt

Input parsing from file is robust to formats like:
  Number of homozygous reference (AA): 120
  Number of heterozygous (Aa): 60
  Number of homozygous alternate (aa): 20
or simply three numbers in order: AA, Aa, aa.
"""

import argparse
import math
import re
import sys
from typing import Dict, Tuple


def r4(x: float) -> str:
    """Format a float to 4 decimal places."""
    return f"{x:.4f}"


def parse_genotype_counts_from_text(text: str) -> Tuple[int, int, int]:
    """Parse AA, Aa, aa genotype counts from free-form text.

    Strategy:
    1) Try to find labeled values for 'AA', 'Aa', and 'aa' (case-sensitive as written).
    2) If any labels are missing, fall back to the first three integers in the text, in order: AA, Aa, aa.

    Returns:
        (AA, Aa, aa) as integers
    Raises:
        ValueError if counts are missing or invalid.
    """
    counts: Dict[str, int] = {}
    # Patterns: match 'AA', '(AA)', etc., followed by a number
    label_patterns = {
        'AA': [r"\bAA\b[^\d\-]*(-?\d+)", r"\(AA\)[^\d\-]*(-?\d+)"],
        'Aa': [r"\bAa\b[^\d\-]*(-?\d+)", r"\(Aa\)[^\d\-]*(-?\d+)"],
        'aa': [r"\baa\b[^\d\-]*(-?\d+)", r"\(aa\)[^\d\-]*(-?\d+)"]
    }

    for key, patterns in label_patterns.items():
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                try:
                    counts[key] = int(m.group(1))
                except Exception:
                    pass
                break

    if not all(k in counts for k in ('AA', 'Aa', 'aa')):
        # Fallback: first three integers in order AA, Aa, aa
        nums = re.findall(r"-?\d+", text)
        if len(nums) >= 3:
            try:
                aa_val = int(nums[0])
                Aa_val = int(nums[1])
                aa2_val = int(nums[2])
                counts = {'AA': aa_val, 'Aa': Aa_val, 'aa': aa2_val}
            except Exception:
                pass

    if not all(k in counts for k in ('AA', 'Aa', 'aa')):
        raise ValueError("Could not parse AA, Aa, aa counts from input text.")

    AA = counts['AA']
    Aa = counts['Aa']
    aa = counts['aa']

    if AA < 0 or Aa < 0 or aa < 0:
        raise ValueError("Genotype counts must be non-negative integers.")

    return AA, Aa, aa


def compute_hwe(AA: int, Aa: int, aa: int) -> Dict[str, float]:
    """Compute allele frequencies, expected counts, and heterozygosity.

    Returns a dict with keys:
      N, p, q, exp_AA, exp_Aa, exp_aa, He, Ho
    Raises ValueError for invalid inputs (e.g., N == 0).
    """
    N = AA + Aa + aa
    if N <= 0:
        raise ValueError("Total count N must be > 0.")

    p = (2.0 * AA + Aa) / (2.0 * N)
    q = 1.0 - p

    # Cross-check using the alternate formula for q
    q_alt = (2.0 * aa + Aa) / (2.0 * N)
    if abs(q - q_alt) > 1e-6:
        print(
            f"Warning: allele frequency inconsistency (q={q:.6f}, q_alt={q_alt:.6f}).",
            file=sys.stderr,
        )

    if not (0.0 - 1e-12 <= p <= 1.0 + 1e-12) or not (0.0 - 1e-12 <= q <= 1.0 + 1e-12):
        raise ValueError("Computed allele frequencies out of [0,1] range.")

    exp_AA = N * (p ** 2)
    exp_Aa = N * (2.0 * p * q)
    exp_aa = N * (q ** 2)

    He = 2.0 * p * q
    Ho = Aa / N if N > 0 else float('nan')

    # Verification checks
    if abs((exp_AA + exp_Aa + exp_aa) - N) > 1e-6:
        print("Warning: expected counts do not sum to N within tolerance.", file=sys.stderr)
    if abs((p ** 2 + q ** 2 + He) - 1.0) > 1e-6:
        print("Warning: He != 1 - (p^2 + q^2) within tolerance.", file=sys.stderr)

    return {
        'N': float(N),
        'p': p,
        'q': q,
        'exp_AA': exp_AA,
        'exp_Aa': exp_Aa,
        'exp_aa': exp_aa,
        'He': He,
        'Ho': Ho,
    }


def format_output(results: Dict[str, float]) -> str:
    """Create the required output string with values rounded to 4 decimals."""
    lines = [
        f"Expected AA: {r4(results['exp_AA'])}",
        f"Expected Aa: {r4(results['exp_Aa'])}",
        f"Expected aa: {r4(results['exp_aa'])}",
        f"Expected heterozygosity: {r4(results['He'])}",
        f"Observed heterozygosity: {r4(results['Ho'])}",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Hardy–Weinberg (HWE) calculator from genotype counts.")
    parser.add_argument("--AA", type=int, help="Count of AA genotypes")
    parser.add_argument("--Aa", type=int, help="Count of Aa genotypes")
    parser.add_argument("--aa", type=int, help="Count of aa genotypes")
    parser.add_argument("--input", type=str, help="Path to input text file with genotype counts")
    parser.add_argument("--output", type=str, help="Path to output text file for results")
    args = parser.parse_args()

    # Prefer explicit counts over file input if provided
    AA = args.AA
    Aa = args.Aa
    aa = args.aa

    if AA is None or Aa is None or aa is None:
        if not args.input:
            print("Error: Provide --AA, --Aa, --aa or --input file.", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
            AA, Aa, aa = parse_genotype_counts_from_text(text)
        except Exception as e:
            print(f"Error reading/parsing input: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        res = compute_hwe(AA, Aa, aa)
    except Exception as e:
        print(f"Error computing HWE: {e}", file=sys.stderr)
        sys.exit(1)

    out_text = format_output(res)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(out_text)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        sys.stdout.write(out_text)


if __name__ == "__main__":
    main()
