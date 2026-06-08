#!/usr/bin/env python3
"""
Generate an Excel formula for a piecewise (group-dependent) polynomial score with clamping and rounding.

This is useful for building Dots-like spreadsheet formulas without hard-coding brittle strings.

The resulting Excel formula has the general shape:
  =IF(OR(sex_ref="G1",sex_ref="Alt1"), ROUND(total_ref*scale/Poly(clamp(bw_ref)), round_digits), IF(..., ..., NA()))

Where Poly(x) = a4*x^4 + b3*x^3 + c2*x^2 + d1*x + e0
and clamp(x) = MIN(MAX(x, low), high)

Usage examples:
  python3 piecewise_poly_excel.py \
      --total G2 --bw C2 --sex B2 --scale 500 --round 3 \
      --config-json '{
        "groups": [
          {"name": "male", "sex_values": ["M","Mx"],
           "coeffs": {"a4": -1.093e-6, "b3": 0.0007391293, "c2": -0.1918759221, "d1": 24.0900756, "e0": -307.75076},
           "clamp": {"low": 40, "high": 210}}
          ,
          {"name": "female", "sex_values": ["F"],
           "coeffs": {"a4": -1.0706e-6, "b3": 0.0005158568, "c2": -0.1126655495, "d1": 13.6175032, "e0": -57.96288},
           "clamp": {"low": 40, "high": 150}}
        ]
      }'

Notes:
- Provide your own coefficients/clamps from an authoritative source for your use case.
- The script prints the Excel formula to stdout. You can then assign it to a cell and fill down.
- The default else branch returns NA(); adjust with --else-expression if needed.
"""

import argparse
import json
import sys
from typing import Dict, List


def or_equals_expr(ref: str, values: List[str]) -> str:
    vals = ",".join([f'{ref}="{v}"' for v in values])
    # Excel OR takes comma-separated logical expressions
    return f"OR({vals})"


def clamp_expr(ref: str, low: float, high: float) -> str:
    return f"MIN(MAX({ref},{low}),{high})"


def poly_expr(x_expr: str, coeffs: Dict[str, float]) -> str:
    # Expect keys: a4, b3, c2, d1, e0
    a4 = coeffs.get("a4", 0)
    b3 = coeffs.get("b3", 0)
    c2 = coeffs.get("c2", 0)
    d1 = coeffs.get("d1", 0)
    e0 = coeffs.get("e0", 0)
    # Ensure all constants are represented with full precision strings
    return (
        f"{a4}*({x_expr})^4+{b3}*({x_expr})^3+{c2}*({x_expr})^2+{d1}*({x_expr})+{e0}"
    )


def build_group_branch(sex_ref: str, total_ref: str, scale: float, round_digits: int,
                        sex_values: List[str], clamp_low: float, clamp_high: float,
                        bw_ref: str, coeffs: Dict[str, float]) -> str:
    cond = or_equals_expr(sex_ref, sex_values)
    clamped = clamp_expr(bw_ref, clamp_low, clamp_high)
    denom = poly_expr(clamped, coeffs)
    inner = f"ROUND({total_ref}*{scale}/({denom}),{round_digits})"
    return cond, inner


def build_formula(total_ref: str, bw_ref: str, sex_ref: str, scale: float, round_digits: int,
                  groups: List[Dict], else_expr: str = "NA()") -> str:
    # Build nested IF chain: IF(cond1, val1, IF(cond2, val2, ... else ...))
    formula = else_expr
    # Build in reverse order so we can nest from the end
    for g in reversed(groups):
        cond, val = build_group_branch(
            sex_ref=sex_ref,
            total_ref=total_ref,
            scale=scale,
            round_digits=round_digits,
            sex_values=g["sex_values"],
            clamp_low=g["clamp"]["low"],
            clamp_high=g["clamp"]["high"],
            bw_ref=bw_ref,
            coeffs=g["coeffs"],
        )
        formula = f"IF({cond},{val},{formula})"
    return f"={formula}"


def main():
    p = argparse.ArgumentParser(description="Generate Excel piecewise polynomial score formula")
    p.add_argument("--total", required=True, help="Cell ref for total, e.g., G2")
    p.add_argument("--bw", required=True, help="Cell ref for polynomial input, e.g., C2")
    p.add_argument("--sex", required=True, help="Cell ref for group/sex, e.g., B2")
    p.add_argument("--scale", type=float, default=500.0, help="Scale multiplier (default 500)")
    p.add_argument("--round", dest="round_digits", type=int, default=3, help="ROUND digits (default 3)")
    p.add_argument("--config-json", required=True, help="JSON with groups, coeffs, clamps")
    p.add_argument("--else-expression", default="NA()", help="Excel expression for else branch (default NA())")
    args = p.parse_args()

    try:
        cfg = json.loads(args.config_json)
    except Exception as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "groups" not in cfg or not isinstance(cfg["groups"], list) or not cfg["groups"]:
        print("ERROR: config must include non-empty 'groups' list", file=sys.stderr)
        sys.exit(1)

    formula = build_formula(
        total_ref=args.total,
        bw_ref=args.bw,
        sex_ref=args.sex,
        scale=args.scale,
        round_digits=args.round_digits,
        groups=cfg["groups"],
        else_expr=args.else_expression,
    )

    print(formula)


if __name__ == "__main__":
    main()
