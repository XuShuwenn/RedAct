#!/usr/bin/env python3
"""
Harmonize clinical lab CSVs by:
- dropping incomplete rows (based on required numeric columns)
- normalizing numeric strings (scientific notation, decimal commas, thousands separators)
- converting alternate units into target units using physiological ranges
- formatting numeric lab values to exactly two decimals (X.XX)

Usage:
  python scripts/harmonize_labs.py \
    --input INPUT.csv \
    --output OUTPUT.csv \
    [--config conversions.json] \
    [--id-columns patient_id,record_id] \
    [--required-columns col1,col2] \
    [--tol-pct 0.02]

Notes:
- If --required-columns is omitted, required columns default to all detected numeric lab columns (excluding ID columns).
- If --config is omitted, the script performs cleaning/formatting only (no unit conversions).
"""

import argparse
import json
import math
import re
import sys
from typing import Dict, Any, Optional, Tuple, List, Set

import pandas as pd

NUM_PATTERN = re.compile(r"^[\s+-]*[0-9]+([.,][0-9]+)?([eE][+-]?[0-9]+)?[\s%]*$")


def parse_args():
    p = argparse.ArgumentParser(description="Clinical lab unit harmonizer")
    p.add_argument("--input", required=True, help="Path to input CSV")
    p.add_argument("--output", required=True, help="Path to output CSV")
    p.add_argument("--config", help="JSON file with conversion/range mapping")
    p.add_argument("--id-columns", help="Comma-separated ID columns to preserve as-is")
    p.add_argument("--required-columns", help="Comma-separated required numeric columns; defaults to detected numeric columns")
    p.add_argument("--tol-pct", type=float, default=0.02, help="Tolerance percent of range width for range checks (default 0.02 = 2%)")
    return p.parse_args()


def last_decimal_resolution(s: str) -> Tuple[str, Optional[str]]:
    """Given a string with possibly both '.' and ',', decide which is decimal.
    Rule: the last occurrence of either '.' or ',' is decimal; remove the other as a thousands sep.
    Returns a cleaned string with '.' as decimal and the chosen decimal char.
    """
    s = s.strip()
    # Remove percent symbol if present
    s = s.replace('%', '')
    if s.count('.') == 0 and s.count(',') == 0:
        return s, None
    # Find last separator position
    last_dot = s.rfind('.')
    last_comma = s.rfind(',')
    if last_dot == -1:
        # Only comma present -> treat as decimal
        return s.replace(',', '.'), ',',
    if last_comma == -1:
        # Only dot present -> already decimal
        return s, '.',
    # Both present
    if last_dot > last_comma:
        # '.' is decimal; remove commas as thousands separators
        return s.replace(',', ''), '.',
    else:
        # ',' is decimal; remove dots as thousands separators, then replace ',' with '.'
        s2 = s.replace('.', '').replace(',', '.')
        return s2, ',',


def parse_numeric_cell(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        if math.isnan(val):
            return None
        return float(val)
    s = str(val).strip()
    if s == '' or s.lower() in {'na', 'n/a', 'null', 'none', 'nan'}:
        return None
    if not NUM_PATTERN.match(s):
        # Try minimal cleanup
        s2, _ = last_decimal_resolution(s)
        try:
            return float(s2)
        except Exception:
            return None
    s2, _ = last_decimal_resolution(s)
    try:
        return float(s2)
    except Exception:
        return None


def detect_numeric_columns(df: pd.DataFrame, id_cols: Set[str]) -> List[str]:
    numeric_cols = []
    sample_n = min(len(df), 500)
    for col in df.columns:
        if col in id_cols:
            continue
        values = df[col].head(sample_n).tolist()
        parsed = [parse_numeric_cell(v) for v in values]
        ok = sum(v is not None for v in parsed)
        if sample_n == 0:
            continue
        if ok / sample_n >= 0.8:
            numeric_cols.append(col)
    return numeric_cols


def within(v: float, lo: float, hi: float, tol: float) -> bool:
    return (v >= lo - tol) and (v <= hi + tol)


def compute_tolerance(lo: float, hi: float, tol_pct: float) -> float:
    width = max(hi - lo, 0.0)
    return width * tol_pct


def apply_conversions(series: pd.Series, col_cfg: Dict[str, Any], tol_pct: float) -> Tuple[pd.Series, int]:
    """Apply range-guided conversions. Returns (converted_series, conversions_count)."""
    target_range = col_cfg.get('target_range') or col_cfg.get('range')
    if not target_range or len(target_range) != 2:
        return series, 0
    t_lo, t_hi = float(target_range[0]), float(target_range[1])
    t_tol = compute_tolerance(t_lo, t_hi, tol_pct)
    alts = col_cfg.get('alternates', [])

    conv_count = 0
    out_vals: List[Optional[float]] = []
    for raw in series.tolist():
        v = parse_numeric_cell(raw)
        if v is None:
            out_vals.append(None)
            continue
        # If already within target range, keep
        if within(v, t_lo, t_hi, t_tol):
            out_vals.append(v)
            continue
        converted = False
        for alt in alts:
            factor = float(alt.get('factor', 1.0))
            src_range = alt.get('src_range')
            if src_range and len(src_range) == 2:
                s_lo, s_hi = float(src_range[0]), float(src_range[1])
                s_tol = compute_tolerance(s_lo, s_hi, tol_pct)
                if not within(v, s_lo, s_hi, s_tol):
                    continue
            v2 = v * factor
            if within(v2, t_lo, t_hi, t_tol):
                out_vals.append(v2)
                conv_count += 1
                converted = True
                break
        if not converted:
            out_vals.append(v)  # leave as-is if no plausible conversion
    return pd.Series(out_vals, index=series.index), conv_count


def format_two_decimals(x: Any) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ''
    try:
        v = float(x)
    except Exception:
        return ''
    return f"{v:.2f}"


def main():
    args = parse_args()

    # Load config if provided
    cfg: Dict[str, Any] = {}
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as fh:
            cfg = json.load(fh)
    col_cfgs: Dict[str, Any] = (cfg.get('columns') or {}) if cfg else {}

    # Read CSV as strings to preserve formatting
    df = pd.read_csv(args.input, dtype=str, keep_default_na=False)

    # Identify ID columns
    id_cols: Set[str] = set()
    if args.id_columns:
        id_cols = {c.strip() for c in args.id_columns.split(',') if c.strip() in df.columns}
    else:
        # Heuristic: columns containing 'id' (case-insensitive)
        id_cols = {c for c in df.columns if 'id' in c.lower()}

    # Detect numeric lab columns
    numeric_cols = detect_numeric_columns(df, id_cols)

    # Determine required columns
    if args.required_columns:
        req_cols = [c.strip() for c in args.required_columns.split(',') if c.strip() in df.columns]
    else:
        req_cols = numeric_cols.copy()

    # Normalize and convert configured columns first (operating on a working numeric copy)
    conversions_applied = {}
    tol_pct = max(0.0, float(args.tol_pct))

    # Create a working numeric DataFrame for numeric columns
    work = df.copy()

    for col in numeric_cols:
        # Apply conversions only if column is configured
        if col in col_cfgs:
            work[col], cnt = apply_conversions(work[col], col_cfgs[col], tol_pct)
            if cnt:
                conversions_applied[col] = cnt

    # After conversions, parse all numeric columns and format to two decimals
    # Also determine rows with missing/unparsable required numeric values
    invalid_mask = pd.Series(False, index=df.index)
    for col in numeric_cols:
        parsed_vals: List[Optional[float]] = []
        for val in work[col].tolist():
            parsed_vals.append(parse_numeric_cell(val))
        # Track invalids for required columns
        if col in req_cols:
            invalid_col_mask = pd.Series([v is None for v in parsed_vals], index=df.index)
            invalid_mask = invalid_mask | invalid_col_mask
        # Replace with formatted strings
        formatted_vals = [format_two_decimals(v) if v is not None else '' for v in parsed_vals]
        work[col] = formatted_vals

    # Drop rows with missing required numeric values
    before_rows = len(work)
    work = work.loc[~invalid_mask].copy()
    dropped = before_rows - len(work)

    # Ensure non-numeric, ID, and other columns are preserved as original strings
    for col in work.columns:
        if col not in numeric_cols:
            # Already string from original df
            continue
        if col in id_cols:
            # Preserve as-is
            work[col] = df.loc[work.index, col]

    # Save CSV
    work.to_csv(args.output, index=False)

    # Print a brief summary to stderr
    sys.stderr.write(f"Rows in: {before_rows}, dropped incomplete: {dropped}, rows out: {len(work)}\n")
    if conversions_applied:
        for k, v in conversions_applied.items():
            sys.stderr.write(f"Converted {v} values in column {k}\n")


if __name__ == "__main__":
    main()
