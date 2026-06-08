#!/usr/bin/env python3
"""
Validate harmonized lab CSV for:
- numeric format X.XX in numeric lab columns
- absence of commas and scientific notation in numeric lab columns
- adherence to configured target ranges (if a JSON config is provided)

Usage:
  python scripts/validate_format.py \
    --input OUTPUT.csv \
    [--config conversions.json] \
    [--id-columns patient_id]
"""

import argparse
import json
import math
import re
import sys
from typing import Dict, Any, List, Set

import pandas as pd

TWO_DEC_RE = re.compile(r"^-?\d+\.\d{2}$")
HAS_SCI_RE = re.compile(r"[eE]")
HAS_COMMA_RE = re.compile(r",")


def parse_args():
    p = argparse.ArgumentParser(description="Validate numeric formatting and ranges of harmonized CSV")
    p.add_argument("--input", required=True, help="Path to harmonized CSV")
    p.add_argument("--config", help="JSON config with target ranges")
    p.add_argument("--id-columns", help="Comma-separated ID columns to skip")
    return p.parse_args()


def is_numeric_two_dec(s: str) -> bool:
    return bool(TWO_DEC_RE.match(s))


def detect_numeric_columns(df: pd.DataFrame, id_cols: Set[str]) -> List[str]:
    numeric_cols = []
    sample_n = min(len(df), 500)
    for col in df.columns:
        if col in id_cols:
            continue
        values = df[col].head(sample_n).tolist()
        # Consider numeric if most non-empty cells match X.XX
        non_empty = [v for v in values if isinstance(v, str) and v.strip() != '']
        if not non_empty:
            continue
        ok = sum(is_numeric_two_dec(v.strip()) for v in non_empty)
        if ok / max(1, len(non_empty)) >= 0.8:
            numeric_cols.append(col)
    return numeric_cols


def main():
    args = parse_args()

    cfg: Dict[str, Any] = {}
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as fh:
            cfg = json.load(fh)
    col_cfgs: Dict[str, Any] = cfg.get('columns', {}) if cfg else {}

    df = pd.read_csv(args.input, dtype=str, keep_default_na=False)

    id_cols: Set[str] = set()
    if args.id_columns:
        id_cols = {c.strip() for c in args.id_columns.split(',') if c.strip() in df.columns}
    else:
        id_cols = {c for c in df.columns if 'id' in c.lower()}

    numeric_cols = detect_numeric_columns(df, id_cols)

    issues = []

    # Check formatting
    for col in numeric_cols:
        for i, val in enumerate(df[col].tolist(), start=1):
            sval = (val or '').strip()
            if sval == '':
                issues.append(f"Row {i}, col {col}: empty numeric cell")
                continue
            if not is_numeric_two_dec(sval):
                issues.append(f"Row {i}, col {col}: not X.XX -> '{sval}'")
            if HAS_SCI_RE.search(sval):
                issues.append(f"Row {i}, col {col}: scientific notation present -> '{sval}'")
            if HAS_COMMA_RE.search(sval):
                issues.append(f"Row {i}, col {col}: comma present -> '{sval}'")

    # Check ranges if config provided
    for col, cfg_col in col_cfgs.items():
        if col not in df.columns:
            continue
        if 'target_range' not in cfg_col and 'range' not in cfg_col:
            continue
        t_range = cfg_col.get('target_range') or cfg_col.get('range')
        t_lo, t_hi = float(t_range[0]), float(t_range[1])
        for i, val in enumerate(df[col].tolist(), start=1):
            sval = (val or '').strip()
            if not is_numeric_two_dec(sval):
                continue
            try:
                v = float(sval)
            except Exception:
                continue
            if not (t_lo <= v <= t_hi):
                issues.append(f"Row {i}, col {col}: out of target range [{t_lo}, {t_hi}] -> {v}")

    if issues:
        sys.stderr.write("Validation failed with issues:\n")
        for msg in issues[:200]:
            sys.stderr.write(msg + "\n")
        if len(issues) > 200:
            sys.stderr.write(f"... and {len(issues) - 200} more issues\n")
        sys.exit(1)
    else:
        print("Validation passed: formatting and ranges OK.")


if __name__ == "__main__":
    main()
