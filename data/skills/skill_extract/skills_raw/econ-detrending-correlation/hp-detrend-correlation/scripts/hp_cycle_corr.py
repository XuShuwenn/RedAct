#!/usr/bin/env python3
"""
HP-cycle correlation utility for two nominal series with CPI deflation.

Reads a CSV with columns for Year, series X (nominal), series Y (nominal), and CPI.
Computes real series (base-year normalization), applies log transform, HP filter,
then computes Pearson correlation of the cyclical components.

Example:
  python scripts/hp_cycle_corr.py \
      --input data.csv --year Year --x X_nom --y Y_nom --cpi CPI \
      --base-year 2024 --lambda 100 --out answer.txt
"""

from __future__ import annotations
import argparse
import sys

import numpy as np
import pandas as pd
from statsmodels.tsa.filters.hp_filter import hpfilter


def hp_cycle_correlation(
    df: pd.DataFrame,
    year_col: str,
    x_col: str,
    y_col: str,
    cpi_col: str,
    base_year: int | None = None,
    lamb: float = 100.0,
    use_log: bool = True,
) -> float:
    # Clean and align
    for col in [year_col, x_col, y_col, cpi_col]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in input DataFrame")

    df2 = df[[year_col, x_col, y_col, cpi_col]].copy()
    df2 = df2.dropna()
    # Ensure integer years
    df2[year_col] = df2[year_col].astype(int)
    df2 = df2.sort_values(year_col)

    # Normalize CPI to base_year if specified
    if base_year is None:
        base_year = int(df2[year_col].iloc[-1])
    if base_year not in set(df2[year_col]):
        raise ValueError(f"Base year {base_year} not found in data")

    cpi_base = float(df2.loc[df2[year_col] == base_year, cpi_col].iloc[0])
    if cpi_base == 0 or np.isnan(cpi_base):
        raise ValueError("Invalid CPI base value (0 or NaN)")
    # Real = Nominal * (CPI_base / CPI_t)  → equivalent to dividing by CPI normalized to base year
    scale = df2[cpi_col].astype(float)
    real_x = df2[x_col].astype(float) * (cpi_base / scale)
    real_y = df2[y_col].astype(float) * (cpi_base / scale)

    # Optional log transform
    if use_log:
        if (real_x <= 0).any() or (real_y <= 0).any():
            raise ValueError("Log transform requested but real series contains non-positive values")
        series_x = np.log(real_x.to_numpy())
        series_y = np.log(real_y.to_numpy())
    else:
        series_x = real_x.to_numpy()
        series_y = real_y.to_numpy()

    # HP filter
    cycle_x, _trend_x = hpfilter(series_x, lamb=lamb)
    cycle_y, _trend_y = hpfilter(series_y, lamb=lamb)

    if np.isnan(cycle_x).any() or np.isnan(cycle_y).any():
        raise ValueError("NaN detected in HP-filtered cycles; check alignment and missing values")

    # Pearson correlation
    corr = float(np.corrcoef(cycle_x, cycle_y)[0, 1])
    return corr


def main():
    p = argparse.ArgumentParser(description="HP-cycle correlation from a CSV with Year, X, Y, and CPI")
    p.add_argument("--input", required=True, help="CSV file path")
    p.add_argument("--year", required=True, help="Year column name")
    p.add_argument("--x", required=True, help="Nominal series X column name")
    p.add_argument("--y", required=True, help="Nominal series Y column name")
    p.add_argument("--cpi", required=True, help="CPI column name")
    p.add_argument("--base-year", type=int, default=None, help="Base year for CPI normalization (default: last year in data)")
    p.add_argument("--lambda", dest="lamb", type=float, default=100.0, help="HP filter lambda (100 annual, 1600 quarterly)")
    p.add_argument("--no-log", action="store_true", help="Disable log transform before HP filter")
    p.add_argument("--out", default=None, help="Optional path to write rounded correlation (5 decimals)")
    args = p.parse_args()

    try:
        df = pd.read_csv(args.input)
    except Exception as e:
        print(f"ERROR: failed to read CSV: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        corr = hp_cycle_correlation(
            df,
            year_col=args.year,
            x_col=args.x,
            y_col=args.y,
            cpi_col=args.cpi,
            base_year=args.base_year,
            lamb=args.lamb,
            use_log=not args.no_log,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.out:
        try:
            with open(args.out, 'w') as f:
                f.write(f"{corr:.5f}\n")
        except Exception as e:
            print(f"ERROR writing output: {e}", file=sys.stderr)
            sys.exit(3)
    else:
        # Print full precision and rounded for diagnostics
        print(f"Correlation: {corr}")
        print(f"Rounded (5 decimals): {corr:.5f}")


if __name__ == "__main__":
    main()
