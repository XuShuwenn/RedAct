#!/usr/bin/env python3
"""
Lab Unit Harmonizer

Standardizes multi-source clinical lab datasets by:
- Parsing numeric formats (commas, scientific notation)
- Dropping incomplete rows (lab columns)
- Converting mixed units to a configured target system using physiological ranges
- Enforcing two-decimal numeric output formatting (X.XX)
- Verifying outputs

Inputs (JSON configs):
- ranges.json: { "Column": [min, max], ... }
- conversions.json: { "Column": [factor1, factor2, ...], ... }  # value_target = value_raw * factor
- special_rules.json (optional): { "Column": [rule_name1, rule_name2, ...], ... }
  Supported rule names:
    - "hba1c_ifcc_to_ngsp": NGSP% = 0.09148 * IFCC + 2.152
    - "fraction_to_percent": if value <= 1, multiply by 100
    - "sg_thousandths": if value >= 10, multiply by 0.001  (e.g., 1020 -> 1.020)

Usage:
  python lab_unit_harmonizer.py \
    --input raw.csv \
    --output harmonized.csv \
    --ranges ranges.json \
    --conversions conversions.json \
    [--special-rules special_rules.json] \
    [--id-column patient_id --id-column record_id] \
    [--tolerance 0.05 --final-tolerance 0.10] \
    [--drop-unharmonizable] \
    [--verify]

Notes:
- Provide appropriate ranges and conversion factors for your lab panel.
- Identifiers are preserved as strings and never formatted as decimals.
"""

import argparse
import json
import math
import re
import sys
from typing import Dict, List, Tuple, Any

import pandas as pd
import numpy as np

MISSING_MARKERS = {"", "nan", "none", "null", "na", "n/a", "nan ", " none", "null ", "-999", "-999.0"}

DECIMAL_RE = re.compile(r"^-?\d+\.\d{2}$")


def load_json(path: str) -> Dict[str, Any]:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_id_columns(df: pd.DataFrame, user_ids: List[str]) -> List[str]:
    ids = []
    for c in user_ids:
        if c in df.columns:
            ids.append(c)
    if not ids and "patient_id" in df.columns:
        ids.append("patient_id")
    return ids


def normalize_decimal_string(s: str) -> str:
    # Remove spaces
    s = s.replace(" ", "")
    if "," in s and "." in s:
        # Use the rightmost separator as decimal; remove the other
        last_comma = s.rfind(",")
        last_dot = s.rfind(".")
        if last_comma > last_dot:
            # comma decimal: remove dots
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            # dot decimal: remove commas
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    return s


def parse_number(value: Any) -> float:
    if value is None:
        return np.nan
    s = str(value).strip()
    if s.lower() in MISSING_MARKERS:
        return np.nan
    try:
        # try direct float (covers scientific notation)
        return float(s)
    except Exception:
        # try normalization then float
        try:
            s2 = normalize_decimal_string(s)
            return float(s2)
        except Exception:
            return np.nan


def in_range(val: float, rng: Tuple[float, float], tol: float = 0.0) -> bool:
    lo, hi = rng
    lower = lo - abs(lo) * tol
    upper = hi + abs(hi) * tol
    return (val >= lower) and (val <= upper)


def clamp(val: float, rng: Tuple[float, float]) -> float:
    lo, hi = rng
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val

# Special rule implementations

def rule_hba1c_ifcc_to_ngsp(v: float) -> float:
    # NGSP% = 0.09148 * IFCC + 2.152
    return 0.09148 * v + 2.152


def rule_fraction_to_percent(v: float) -> float:
    # If given as fraction (<=1), convert to percent
    if v <= 1.0:
        return v * 100.0
    return v


def rule_sg_thousandths(v: float) -> float:
    # Convert 1005 -> 1.005, 1020 -> 1.020
    if v >= 10:
        return v * 0.001
    return v

SPECIAL_RULES_REGISTRY = {
    "hba1c_ifcc_to_ngsp": rule_hba1c_ifcc_to_ngsp,
    "fraction_to_percent": rule_fraction_to_percent,
    "sg_thousandths": rule_sg_thousandths,
}


def convert_value(
    value: float,
    col: str,
    rngs: Dict[str, Tuple[float, float]],
    conv_factors: Dict[str, List[float]],
    special_rules: Dict[str, List[str]],
    tol: float,
    final_tol: float,
) -> float:
    if pd.isna(value) or col not in rngs:
        return value
    rng = rngs[col]

    # Already in range
    if in_range(value, rng, tol=0.0):
        return value

    # Tight tolerance clamp
    if in_range(value, rng, tol=tol):
        return clamp(value, rng)

    # Try special rules first (when indicated)
    for name in special_rules.get(col, []):
        fn = SPECIAL_RULES_REGISTRY.get(name)
        if not fn:
            continue
        try:
            cand = fn(value)
        except Exception:
            cand = value
        if in_range(cand, rng, tol=0.0):
            return cand
        if in_range(cand, rng, tol=tol):
            return clamp(cand, rng)

    # Try multiplicative conversion factors
    candidates: List[float] = []
    for factor in conv_factors.get(col, []):
        try:
            cand = value * factor
        except Exception:
            continue
        if in_range(cand, rng, tol=0.0):
            return cand
        if in_range(cand, rng, tol=tol):
            return clamp(cand, rng)
        candidates.append(cand)

    # Gentle clamp for near-range converted candidates (final tolerance)
    for cand in candidates:
        if in_range(cand, rng, tol=final_tol):
            return clamp(cand, rng)

    # Final gentle clamp for original value, if permitted
    if in_range(value, rng, tol=final_tol):
        return clamp(value, rng)

    return value


def verify_output(
    df_out: pd.DataFrame,
    id_cols: List[str],
    ranges: Dict[str, Tuple[float, float]],
) -> Tuple[bool, List[str]]:
    issues = []

    # Check formatting and characters for numeric columns
    num_cols = [c for c in df_out.columns if c not in id_cols]

    for c in num_cols:
        ser = df_out[c].astype(str)
        if ser.str.contains(",", regex=False).any():
            issues.append(f"Comma found in column {c}")
        if ser.str.contains(r"[eE]", regex=True).any():
            issues.append(f"Scientific notation found in column {c}")
        bad_fmt = ~ser.str.match(DECIMAL_RE)
        if bad_fmt.any():
            issues.append(f"Bad numeric format in column {c}")
            break

    # Check missing
    if df_out[num_cols].isna().any(axis=1).any() or (df_out[num_cols] == "").any(axis=1).any():
        issues.append("Missing values detected in numeric columns")

    # Check ranges
    # Cast to float for range validation
    for c in num_cols:
        if c not in ranges:
            continue
        try:
            vals = df_out[c].astype(float)
        except Exception:
            issues.append(f"Cannot cast column {c} to float for range check")
            continue
        lo, hi = ranges[c]
        bad = (vals < lo) | (vals > hi)
        if bad.any():
            issues.append(f"Out-of-range values remain in column {c}")

    ok = len(issues) == 0
    return ok, issues


def main():
    p = argparse.ArgumentParser(description="Clinical lab unit harmonizer")
    p.add_argument("--input", required=True, help="Input CSV path")
    p.add_argument("--output", required=True, help="Output CSV path")
    p.add_argument("--ranges", required=True, help="JSON file with {col: [min, max]} in target units")
    p.add_argument("--conversions", required=False, default=None, help="JSON file with {col: [factors...]} raw->target")
    p.add_argument("--special-rules", required=False, default=None, help="JSON file with {col: [rule names...]} ")
    p.add_argument("--id-column", action="append", default=[], help="Identifier column to preserve unchanged; can be repeated")
    p.add_argument("--tolerance", type=float, default=0.05, help="Primary tolerance fraction for clamping (default 0.05)")
    p.add_argument("--final-tolerance", type=float, default=0.10, help="Gentle tolerance for near-range candidates (default 0.10)")
    p.add_argument("--drop-unharmonizable", action="store_true", help="Drop rows still outside ranges after harmonization")
    p.add_argument("--verify", action="store_true", help="Run verification after saving")
    args = p.parse_args()

    # Load configs
    ranges_raw = load_json(args.ranges)
    if not ranges_raw:
        print("ERROR: ranges configuration is required and appears empty.", file=sys.stderr)
        sys.exit(1)
    # Normalize ranges to tuple
    ranges = {}
    for k, v in ranges_raw.items():
        try:
            lo, hi = float(v[0]), float(v[1])
            ranges[k] = (lo, hi)
        except Exception:
            print(f"WARNING: Skipping invalid ranges for {k}")

    conversions = load_json(args.conversions) if args.conversions else {}
    for k, lst in list(conversions.items()):
        try:
            conversions[k] = [float(x) for x in lst]
        except Exception:
            print(f"WARNING: Skipping invalid conversion factors for {k}")
            conversions.pop(k, None)

    special_rules = load_json(args.special_rules) if args.special_rules else {}

    # Load data as strings
    df_raw = pd.read_csv(args.input, dtype=str)

    # Identify id columns
    id_cols = detect_id_columns(df_raw, args.id_column)

    # Determine numeric columns (all except id columns)
    num_cols = [c for c in df_raw.columns if c not in id_cols]

    # Parse numeric values
    df_parsed = df_raw.copy()
    for c in num_cols:
        df_parsed[c] = df_parsed[c].apply(parse_number)

    # Drop rows with missing numeric values
    complete_mask = ~df_parsed[num_cols].isna().any(axis=1)
    df_parsed = df_parsed.loc[complete_mask].reset_index(drop=True)

    # Convert units/ranges
    for c in num_cols:
        df_parsed[c] = df_parsed[c].apply(
            lambda v: convert_value(
                v,
                c,
                ranges,
                conversions,
                special_rules,
                tol=args.tolerance,
                final_tol=args.final_tolerance,
            )
        )

    # Optionally drop rows still out-of-range
    if args.drop_unharmonizable:
        keep_mask = pd.Series(True, index=df_parsed.index)
        for c in num_cols:
            if c not in ranges:
                continue
            lo, hi = ranges[c]
            keep_mask &= df_parsed[c].between(lo, hi, inclusive="both")
        df_parsed = df_parsed.loc[keep_mask].reset_index(drop=True)

    # Format numeric columns to two decimals as strings
    df_out = df_parsed.copy()
    for c in num_cols:
        df_out[c] = df_out[c].apply(lambda x: f"{x:.2f}" if pd.notna(x) and isinstance(x, (int, float, np.floating)) else ("" if pd.isna(x) else str(x)))

    # Preserve id columns as original strings (no decimal formatting)
    # Already preserved by not touching id_cols

    # Save
    # Ensure original column order
    df_out = df_out[df_raw.columns.intersection(df_out.columns).tolist()]
    df_out.to_csv(args.output, index=False)

    if args.verify:
        # Read back as strings and verify formatting & ranges
        df_verify = pd.read_csv(args.output, dtype=str)
        ok, issues = verify_output(df_verify, id_cols, ranges)
        print("=== Verification ===")
        print(f"Columns: {len(df_verify.columns)}  Rows: {len(df_verify)}")
        if ok:
            print("PASS: Output meets formatting and range requirements.")
        else:
            print("FAIL:")
            for msg in issues:
                print(" -", msg)
            sys.exit(2)


if __name__ == "__main__":
    main()
