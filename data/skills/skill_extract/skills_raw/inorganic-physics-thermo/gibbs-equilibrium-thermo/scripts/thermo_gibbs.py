#!/usr/bin/env python3
"""Compute Gibbs free energy (ΔG) and equilibrium constant (K).

Supports:
- Direct CLI inputs for ΔH (kJ/mol), ΔS (J/mol·K), and T (K)
- Or reading from an input file with three lines (ΔH, ΔS, T), extracting the
  first numeric value per line (units may be present in text)

Outputs two lines (to stdout or a specified file):
  ΔG: XX.XX kJ/mol
  K: X.XXXXe+NN

Usage examples:
  python scripts/thermo_gibbs.py --dh-kj -100 --ds-j 50 --temp-k 298 --out-file output.txt
  python scripts/thermo_gibbs.py --in-file input.txt --R 8.314 --out-file output.txt
"""

import argparse
import math
import re
import sys
from typing import Optional, Tuple


def parse_first_number(s: str) -> Optional[float]:
    """Return the first float-like number found in a string, or None if absent."""
    m = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", s)
    return float(m.group(0)) if m else None


def read_values_from_file(path: str) -> Tuple[float, float, float]:
    """Read ΔH (kJ/mol), ΔS (J/mol·K), T (K) from a file (one per line).
    Ignores empty/comment lines; parses the first numeric per line.
    """
    values = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            val = parse_first_number(line)
            if val is not None:
                values.append(val)
            if len(values) == 3:
                break
    if len(values) != 3:
        raise ValueError("Expected three numeric values (ΔH, ΔS, T) in the input file.")
    return float(values[0]), float(values[1]), float(values[2])


def compute_gibbs_and_K(dh_kj: float, ds_j_per_k: float, t_k: float, R_j: float = 8.314) -> Tuple[float, float]:
    """Compute ΔG (kJ/mol) and K given ΔH (kJ/mol), ΔS (J/mol·K), T (K), and R (J/mol·K).

    Returns:
        (delta_g_kj, K)
    """
    if t_k <= 0:
        raise ValueError("Temperature must be in Kelvin and greater than 0.")
    if R_j <= 0:
        raise ValueError("Gas constant R must be positive.")

    ds_kj_per_k = ds_j_per_k / 1000.0
    delta_g_kj = dh_kj - t_k * ds_kj_per_k

    # Use R in J/mol·K; convert ΔG to J/mol for the exponent
    delta_g_j = delta_g_kj * 1000.0
    exponent = -delta_g_j / (R_j * t_k)
    K = math.exp(exponent)

    # Optional internal consistency check (not enforced)
    # lnK + ΔG/(R*T) should be ~ 0
    # _lnK = math.log(K)
    # _resid = _lnK + (delta_g_j / (R_j * t_k))
    # if abs(_resid) > 1e-8:
    #     print(f"Warning: numerical inconsistency resid={_resid}", file=sys.stderr)

    return delta_g_kj, K


def format_output(delta_g_kj: float, K: float) -> str:
    return f"ΔG: {delta_g_kj:.2f} kJ/mol\nK: {K:.4e}\n"


def main():
    p = argparse.ArgumentParser(description="Gibbs free energy and equilibrium constant calculator")
    p.add_argument("--dh-kj", type=float, help="ΔH in kJ/mol")
    p.add_argument("--ds-j", type=float, help="ΔS in J/mol·K")
    p.add_argument("--temp-k", type=float, help="Temperature in K")
    p.add_argument("--R", dest="R_j", type=float, default=8.314, help="Gas constant in J/mol·K (default: 8.314)")
    p.add_argument("--in-file", type=str, help="Path to input file with ΔH, ΔS, T on separate lines")
    p.add_argument("--out-file", type=str, help="Path to write formatted results")
    args = p.parse_args()

    # Determine input source
    if args.in_file:
        try:
            dh_kj, ds_j, t_k = read_values_from_file(args.in_file)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if args.dh_kj is None or args.ds_j is None or args.temp_k is None:
            print("ERROR: Provide --in-file or all of --dh-kj, --ds-j, --temp-k", file=sys.stderr)
            sys.exit(1)
        dh_kj, ds_j, t_k = args.dh_kj, args.ds_j, args.temp_k

    try:
        delta_g_kj, K = compute_gibbs_and_K(dh_kj, ds_j, t_k, R_j=args.R_j)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    out = format_output(delta_g_kj, K)

    if args.out_file:
        try:
            with open(args.out_file, 'w', encoding='utf-8') as f:
                f.write(out)
            # Verify write
            with open(args.out_file, 'r', encoding='utf-8') as f:
                _ = f.read()
        except Exception as e:
            print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
