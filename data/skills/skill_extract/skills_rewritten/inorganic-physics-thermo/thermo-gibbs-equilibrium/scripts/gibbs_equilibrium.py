#!/usr/bin/env python3
"""Compute Gibbs free energy (ΔG) and equilibrium constant (K) from
ΔH (kJ/mol), ΔS (J/mol·K), and T (K).

Features:
- Enforces unit consistency (ΔS conversion, R units)
- Uses full-precision ΔG for K; rounds only for display
- Strict two-line output formatting

Usage:
  # Provide values directly
  python gibbs_equilibrium.py --dh 10.5 --ds 25.0 --t 298

  # Or read three lines from an input file and write to an output file
  python gibbs_equilibrium.py --input input.txt --output output.txt

Options:
  --k-decimals N   Set decimals after the decimal point for K (default: 4)
  --use-kj-R       Use R in kJ/mol·K (0.008314) instead of J/mol·K; both are equivalent if units match
"""

import argparse
import math
import sys
from typing import Tuple, Optional

R_J = 8.314  # J/mol·K
R_KJ = 0.008314  # kJ/mol·K


def parse_file(path: str) -> Tuple[float, float, float]:
    """Read ΔH (kJ/mol), ΔS (J/mol·K), T (K) from a file with values one per line.
    Ignores blank lines and lines starting with '#'.
    """
    vals = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith('#'):
                    continue
                try:
                    vals.append(float(s))
                except ValueError:
                    raise ValueError(f"Non-numeric value encountered: {s}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {path}")

    if len(vals) != 3:
        raise ValueError(f"Expected 3 numeric values (ΔH, ΔS, T); got {len(vals)}")
    dh_kj, ds_j_per_k, t_k = vals
    return dh_kj, ds_j_per_k, t_k


def compute_delta_g_kj(dh_kj: float, ds_j_per_k: float, t_k: float) -> float:
    """Compute ΔG in kJ/mol given ΔH (kJ/mol), ΔS (J/mol·K), and T (K)."""
    ds_kj_per_k = ds_j_per_k / 1000.0
    return dh_kj - t_k * ds_kj_per_k


def compute_equilibrium_constant(dg_kj: float, t_k: float, use_kj_R: bool = False) -> float:
    """Compute equilibrium constant K from ΔG (kJ/mol) and T (K).
    If use_kj_R is False, convert ΔG to J and use R in J/mol·K.
    If use_kj_R is True, use R in kJ/mol·K directly.
    """
    if use_kj_R:
        exponent = -dg_kj / (R_KJ * t_k)
    else:
        dg_j = dg_kj * 1000.0
        exponent = -dg_j / (R_J * t_k)
    # Guard against overflow in extreme cases; math.exp handles typical ranges
    return math.exp(exponent)


def format_output(dg_kj: float, K: float, k_decimals: int) -> str:
    dg_str = f"{dg_kj:.2f}"
    k_str = f"{K:.{k_decimals}e}"
    return f"ΔG: {dg_str} kJ/mol\nK: {k_str}\n"


def validate_inputs(dh_kj: float, ds_j_per_k: float, t_k: float) -> Optional[str]:
    if not math.isfinite(dh_kj) or not math.isfinite(ds_j_per_k) or not math.isfinite(t_k):
        return "Inputs must be finite real numbers."
    if t_k <= 0:
        return "Temperature must be in Kelvin and greater than 0."
    return None


def main():
    p = argparse.ArgumentParser(description="Gibbs free energy and equilibrium constant calculator")
    p.add_argument('--dh', type=float, help='ΔH in kJ/mol')
    p.add_argument('--ds', type=float, help='ΔS in J/mol·K')
    p.add_argument('--t', type=float, help='T in K')
    p.add_argument('--input', type=str, help='Path to input file with ΔH, ΔS, T (one per line)')
    p.add_argument('--output', type=str, help='Path to write output (two lines)')
    p.add_argument('--k-decimals', type=int, default=4, help='Decimals for K in scientific notation (default: 4)')
    p.add_argument('--use-kj-R', action='store_true', help='Use R in kJ/mol·K (0.008314) instead of J/mol·K')
    args = p.parse_args()

    # Acquire inputs
    if args.input:
        try:
            dh_kj, ds_j_per_k, t_k = parse_file(args.input)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if args.dh is None or args.ds is None or args.t is None:
            p.print_help()
            sys.exit(1)
        dh_kj, ds_j_per_k, t_k = args.dh, args.ds, args.t

    # Validate
    err = validate_inputs(dh_kj, ds_j_per_k, t_k)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    # Compute
    dg_kj = compute_delta_g_kj(dh_kj, ds_j_per_k, t_k)
    K = compute_equilibrium_constant(dg_kj, t_k, use_kj_R=args.use_kj_R)

    # Optional cross-check for unit consistency (silent check)
    try:
        K_check = compute_equilibrium_constant(dg_kj, t_k, use_kj_R=not args.use_kj_R)
        # If large relative discrepancy, warn on stderr
        if K > 0 and K_check > 0:
            rel = abs(K - K_check) / max(K, K_check)
            if rel > 1e-10:
                print("WARNING: K differs between unit methods beyond tolerance; check units.", file=sys.stderr)
    except Exception:
        pass

    out = format_output(dg_kj, K, args.k_decimals)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(out)
        except Exception as e:
            print(f"ERROR: could not write output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        sys.stdout.write(out)


if __name__ == '__main__':
    main()
