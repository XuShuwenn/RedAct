#!/usr/bin/env python3
"""
Trend estimation utilities: compute slope and p-value for a target time series.

CLI usage:
  python3 scripts/trend_tools.py --input data.csv --time-col year --value-col temp --out trend_result.csv

Notes:
- Uses scipy.stats.linregress if available; otherwise uses a closed-form OLS
  with Fisher z for p-value approximation.
- Time column can be numeric or parseable dates; dates are converted to an
  ordinal numeric scale.
"""

import argparse
import csv
import math
import sys
from typing import List, Tuple

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # fallback to csv module

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    np = None


def _to_numeric_time(col: List[str]) -> List[float]:
    # Try pandas to_datetime first for robust parsing
    if pd is not None:
        try:
            dt = pd.to_datetime(pd.Series(col), errors='coerce', infer_datetime_format=True)
            if dt.notna().sum() >= max(3, len(col) // 2):
                # Convert to ordinal (days) for stability, then scale to years
                base = pd.Timestamp('1970-01-01')
                secs = (dt - base).dt.total_seconds()
                # Scale to years to keep slope interpretable
                years = secs / (365.25 * 24 * 3600.0)
                return years.fillna(method='ffill').fillna(method='bfill').tolist()
        except Exception:
            pass
    # Fallback: try float conversion
    out = []
    for v in col:
        try:
            out.append(float(v))
        except Exception:
            out.append(float('nan'))
    # Simple forward/backward fill to handle occasional NaNs
    for i in range(len(out)):
        if math.isnan(out[i]):
            j = i - 1
            while j >= 0 and math.isnan(out[j]):
                j -= 1
            k = i + 1
            while k < len(out) and math.isnan(out[k]):
                k += 1
            if j >= 0 and k < len(out):
                out[i] = (out[j] + out[k]) / 2.0
            elif j >= 0:
                out[i] = out[j]
            elif k < len(out):
                out[i] = out[k]
            else:
                out[i] = 0.0
    return out


def _linregress_fallback(x: List[float], y: List[float]) -> Tuple[float, float]:
    """Return slope and two-sided p-value approximation.

    p-value approximation via Fisher z-transform of Pearson r.
    For moderate n, this is reasonable when scipy is unavailable.
    """
    n = len(x)
    if n < 3:
        return float('nan'), float('nan')
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    num = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    den = sum((xi - x_mean) ** 2 for xi in x)
    if den == 0:
        return float('nan'), float('nan')
    slope = num / den

    # Pearson r
    ssx = sum((xi - x_mean) ** 2 for xi in x)
    ssy = sum((yi - y_mean) ** 2 for yi in y)
    if ssx == 0 or ssy == 0:
        return slope, float('nan')
    r = num / math.sqrt(ssx * ssy)
    r = max(-1.0, min(1.0, r))

    # Fisher z transform -> approximate two-sided p-value
    if n > 3 and abs(r) < 0.999999:
        z = 0.5 * math.log((1 + r) / (1 - r)) * math.sqrt(n - 3)
        # two-sided p from normal approx
        # p = 2 * (1 - Phi(|z|)) ; Phi via erfc
        p = 2.0 * 0.5 * math.erfc(abs(z) / math.sqrt(2.0))
    else:
        p = float('nan')
    return slope, p


def compute_trend(time_vals: List[float], y_vals: List[float]) -> Tuple[float, float]:
    # Drop rows with NaNs
    xy = [(t, y) for t, y in zip(time_vals, y_vals) if (t is not None and y is not None and not (isinstance(t, float) and math.isnan(t)) and not (isinstance(y, float) and math.isnan(y)))]
    if len(xy) < 3:
        return float('nan'), float('nan')
    x = [t for t, _ in xy]
    y = [v for _, v in xy]

    # Try scipy if available
    try:
        from scipy.stats import linregress  # type: ignore
        res = linregress(x, y)
        return float(res.slope), float(res.pvalue)
    except Exception:
        return _linregress_fallback(x, y)


def write_trend_csv(path: str, slope: float, pval: float) -> None:
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['slope', 'p-value'])
        writer.writerow([f"{slope}", f"{pval}"])


def main():
    ap = argparse.ArgumentParser(description='Compute linear trend slope and p-value for a target series.')
    ap.add_argument('--input', required=True, help='Path to input CSV')
    ap.add_argument('--time-col', required=True, help='Name of time column (numeric or date)')
    ap.add_argument('--value-col', required=True, help='Name of target value column')
    ap.add_argument('--out', required=True, help='Path to output CSV (slope,p-value)')
    args = ap.parse_args()

    if pd is not None:
        df = pd.read_csv(args.input)
        if args.time_col not in df.columns or args.value_col not in df.columns:
            print('ERROR: Missing required columns.', file=sys.stderr)
            sys.exit(1)
        t = _to_numeric_time(df[args.time_col].astype(str).tolist())
        y = df[args.value_col].astype(float).tolist()
    else:
        # Fallback: use csv module
        with open(args.input, 'r', newline='') as f:
            reader = csv.DictReader(f)
            if args.time_col not in reader.fieldnames or args.value_col not in reader.fieldnames:
                print('ERROR: Missing required columns.', file=sys.stderr)
                sys.exit(1)
            rows = list(reader)
        t = _to_numeric_time([r.get(args.time_col, '') for r in rows])
        y = []
        for r in rows:
            try:
                y.append(float(r.get(args.value_col, '')))
            except Exception:
                y.append(float('nan'))

    slope, pval = compute_trend(t, y)
    write_trend_csv(args.out, slope, pval)


if __name__ == '__main__':
    main()
