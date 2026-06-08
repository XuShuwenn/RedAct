#!/usr/bin/env python3
"""
Utilities to parse mixed annual/quarterly time series from Excel-like tables.

Key features:
- Detects annual rows with year-only labels (e.g., "1980" or "1980.")
- Detects quarterly rows with Arabic quarters (Q1..Q4) or Roman numerals (I..IV),
  handling optional suffixes like preliminary markers.
- Builds an annual series and can compute the latest year's value as the
  average of available quarters when the annual total is absent.

This module is generic and works with pandas DataFrames read from Excel files
(e.g., ERP-style tables). It focuses on a single (year/label, value) column pair.

Example:
    import pandas as pd
    from mixed_excel_timeseries import (
        extract_annual_and_quarterly,
        build_annual_series,
        align_on_years,
    )

    df = pd.read_excel('table.xls', header=None)
    annual, quarterly = extract_annual_and_quarterly(df, year_col=0, value_col=1)
    annual_series = build_annual_series(annual, quarterly, fill_last_year_from_quarters=True)
"""

from __future__ import annotations
import re
from typing import Dict, Tuple, Optional, Iterable

import numpy as np
import pandas as pd

_ANNUAL_RX = re.compile(r"^\s*(\d{4})\s*\.?\s*$")
_Q_ARABIC_RX = re.compile(r"^\s*(\d{4}).*?Q\s*([1-4])\b", re.IGNORECASE)
_Q_ROMAN_RX = re.compile(r"^\s*(\d{4}).*?\b(I{1,3}|IV)\b", re.IGNORECASE)

_ROMAN_TO_INT = {
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4,
}


def _to_float(x) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        xs = x.strip().replace(',', '')
        try:
            return float(xs)
        except Exception:
            return None
    return None


def extract_annual_and_quarterly(
    df: pd.DataFrame,
    year_col: int = 0,
    value_col: int = 1,
    exclude_if_contains: Iterable[str] = ("Includes", "Source")
) -> Tuple[Dict[int, float], Dict[Tuple[int, int], float]]:
    """Extract annual and quarterly observations from a DataFrame.

    Args:
        df: DataFrame with a label/year column and a numeric value column.
        year_col: Column index holding the year/quarter labels.
        value_col: Column index holding the numeric values.
        exclude_if_contains: Row is skipped if any of these substrings appear
            in the label (to avoid footnotes and sources).

    Returns:
        (annual, quarterly) where:
          - annual is {year: value}
          - quarterly is {(year, quarter): value} with quarter in {1,2,3,4}
    """
    annual: Dict[int, float] = {}
    quarterly: Dict[Tuple[int, int], float] = {}

    nrows = len(df)
    for i in range(nrows):
        label_raw = df.iat[i, year_col]
        val_raw = df.iat[i, value_col] if value_col is not None else None

        if pd.isna(label_raw) or pd.isna(val_raw):
            continue

        label = str(label_raw).strip()
        if not label:
            continue
        if any(key in label for key in exclude_if_contains):
            continue

        val = _to_float(val_raw)
        if val is None:
            continue

        # 1) Annual match (year only)
        m_ann = _ANNUAL_RX.match(label)
        if m_ann:
            try:
                year = int(m_ann.group(1))
                annual[year] = val
                continue
            except Exception:
                pass

        # 2) Quarterly Arabic (YYYY:Qk)
        m_q = _Q_ARABIC_RX.match(label)
        if m_q:
            try:
                year = int(m_q.group(1))
                q = int(m_q.group(2))
                if 1 <= q <= 4:
                    quarterly[(year, q)] = val
                    continue
            except Exception:
                pass

        # 3) Quarterly Roman numerals (YYYY: I/II/III/IV)
        m_qr = _Q_ROMAN_RX.match(label)
        if m_qr:
            try:
                year = int(m_qr.group(1))
                roman = m_qr.group(2).upper()
                q = _ROMAN_TO_INT.get(roman)
                if q is not None:
                    quarterly[(year, q)] = val
                    continue
            except Exception:
                pass

    return annual, quarterly


def average_partial_year(quarterly: Dict[Tuple[int, int], float], year: int) -> Optional[float]:
    """Average available quarters for the given year. Returns None if none present."""
    vals = [v for (y, q), v in quarterly.items() if y == year]
    if not vals:
        return None
    return float(np.mean(vals))


def build_annual_series(
    annual: Dict[int, float],
    quarterly: Dict[Tuple[int, int], float],
    years_range: Optional[Tuple[int, int]] = None,
    fill_last_year_from_quarters: bool = True,
) -> pd.Series:
    """Build an annual series; optionally fill the latest year from available quarters.

    If years_range is None, the range spans min(annual.keys()∪quarterly_years)
    to max(annual.keys()∪quarterly_years).
    """
    years_from_quarters = set(y for (y, _q) in quarterly.keys())
    known_years = set(annual.keys()) | years_from_quarters
    if not known_years:
        return pd.Series(dtype=float)

    start = min(known_years) if years_range is None else years_range[0]
    end = max(known_years) if years_range is None else years_range[1]

    data = {}
    for y in range(start, end + 1):
        if y in annual:
            data[y] = float(annual[y])
        else:
            data[y] = None

    # Optionally fill the last year from quarters if annual is missing
    if fill_last_year_from_quarters and data.get(end) is None:
        avg = average_partial_year(quarterly, end)
        if avg is not None:
            data[end] = avg

    s = pd.Series(data, dtype=float)
    return s.dropna()


def align_on_years(x: pd.Series, y: pd.Series, cpi: pd.Series) -> pd.DataFrame:
    """Inner-join three series by integer Year index and return a clean DataFrame."""
    def _clean_index(s: pd.Series) -> pd.Series:
        s2 = s.copy()
        s2.index = pd.Index([int(i) for i in s.index], name='Year')
        return s2.sort_index()

    x2 = _clean_index(x)
    y2 = _clean_index(y)
    c2 = _clean_index(cpi)
    df = pd.concat({'x_nom': x2, 'y_nom': y2, 'cpi': c2}, axis=1, join='inner')
    return df.dropna()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse mixed annual/quarterly Excel time series.")
    parser.add_argument("excel", help="Path to Excel file")
    parser.add_argument("--year-col", type=int, default=0, help="Label/Year column index (default: 0)")
    parser.add_argument("--value-col", type=int, default=1, help="Value column index (default: 1)")
    args = parser.parse_args()

    df = pd.read_excel(args.excel, header=None)
    annual, quarterly = extract_annual_and_quarterly(df, year_col=args.year_col, value_col=args.value_col)

    if not annual:
        print("No annual rows detected.")
    else:
        yrs = sorted(annual.keys())
        print(f"Annual: {len(yrs)} rows from {yrs[0]} to {yrs[-1]}")

    # Identify the last year across both maps and preview filling
    known_years = set(annual.keys()) | set(y for (y, _q) in quarterly)
    if known_years:
        end = max(known_years)
        s = build_annual_series(annual, quarterly, years_range=(min(known_years), end), fill_last_year_from_quarters=True)
        print(f"Built annual series with {len(s)} observations. Last year {end} value: {s.iloc[-1]:.4f}")
        if (end not in annual) and any(y == end for (y, _q) in quarterly):
            print("Note: Last year filled from available quarters (average).")
