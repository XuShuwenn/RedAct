#!/usr/bin/env python3
"""
HP-cycle and correlation utilities for macroeconomic time series.

Core functions:
- choose_lambda(freq=None, lam=None): returns appropriate HP lambda for the given frequency.
- hp_filter(y, lam): HP filter on a numeric 1D sequence; returns (trend, cycle).
- log_hp_cycle(values, lam): log-transform then HP-filter; returns cycle.
- align_year_series(years_a, vals_a, years_b, vals_b): align by intersection of years.
- corr(x, y): Pearson correlation for two same-length arrays.
- round_smart(x, decimals=5): numeric string with fixed decimals.

Notes:
- This implementation uses a direct linear solve for HP filtering; for typical macro annual samples
  (dozens of observations) this is efficient and dependency-free.
- Ensure all values are positive before using log_hp_cycle.
"""
from __future__ import annotations
import math
from typing import Iterable, List, Tuple

import numpy as np


def choose_lambda(freq: str | None = None, lam: float | None = None) -> float:
    """Return HP smoothing parameter. If lam is provided, it overrides freq.
    Common defaults: Annual=100, Quarterly=1600, Monthly=129600.
    """
    if lam is not None:
        return float(lam)
    if not freq:
        # Default to annual if not specified
        return 100.0
    f = freq.strip().upper()
    if f.startswith('A') or f == 'ANNUAL' or f == 'YEARLY':
        return 100.0
    if f.startswith('Q') or f == 'QUARTERLY':
        return 1600.0
    if f.startswith('M') or f == 'MONTHLY':
        return 129600.0
    # Fallback safe default
    return 100.0


def _second_diff_matrix(n: int) -> np.ndarray:
    """Construct the (n-2) x n second-difference operator K for HP filter."""
    if n < 3:
        return np.zeros((0, n))
    K = np.zeros((n - 2, n), dtype=float)
    for i in range(n - 2):
        K[i, i] = 1.0
        K[i, i + 1] = -2.0
        K[i, i + 2] = 1.0
    return K


def hp_filter(y: Iterable[float], lam: float) -> Tuple[np.ndarray, np.ndarray]:
    """Perform HP filtering on a numeric sequence y.
    Returns (trend, cycle) as numpy arrays.
    Minimizes sum((y - t)^2) + lam * sum((Δ^2 t)^2).
    """
    y = np.asarray(list(y), dtype=float)
    n = y.size
    if n == 0:
        return np.array([]), np.array([])
    if n < 3:
        # With fewer than 3 points, trend = y and cycle = 0
        return y.copy(), np.zeros_like(y)
    I = np.eye(n)
    K = _second_diff_matrix(n)
    A = I + lam * (K.T @ K)
    # Solve A * trend = y
    trend = np.linalg.solve(A, y)
    cycle = y - trend
    return trend, cycle


def log_hp_cycle(values: Iterable[float], lam: float) -> np.ndarray:
    """Log-transform and HP-filter a positive series; returns cycle component."""
    vals = np.asarray(list(values), dtype=float)
    if np.any(vals <= 0) or np.isnan(vals).any():
        raise ValueError("All values must be positive and non-NaN for log transform.")
    log_vals = np.log(vals)
    _, cycle = hp_filter(log_vals, lam)
    return cycle


def align_year_series(
    years_a: Iterable[int],
    vals_a: Iterable[float],
    years_b: Iterable[int],
    vals_b: Iterable[float],
) -> Tuple[List[int], np.ndarray, np.ndarray]:
    """Align two year-indexed series by intersection of years.
    Returns (years_sorted, a_aligned, b_aligned).
    """
    a_map = {int(y): float(v) for y, v in zip(years_a, vals_a)}
    b_map = {int(y): float(v) for y, v in zip(years_b, vals_b)}
    inter = sorted(set(a_map.keys()) & set(b_map.keys()))
    a_aligned = np.array([a_map[y] for y in inter], dtype=float)
    b_aligned = np.array([b_map[y] for y in inter], dtype=float)
    # Drop any NaN pairs safely
    mask = ~(np.isnan(a_aligned) | np.isnan(b_aligned))
    years = [y for y, m in zip(inter, mask) if m]
    return years, a_aligned[mask], b_aligned[mask]


def corr(x: Iterable[float], y: Iterable[float]) -> float:
    """Pearson correlation for two equal-length sequences."""
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    if x.size != y.size or x.size < 2:
        return float('nan')
    if np.allclose(x.std(ddof=0), 0) or np.allclose(y.std(ddof=0), 0):
        return float('nan')
    return float(np.corrcoef(x, y)[0, 1])


def round_smart(x: float, decimals: int = 5) -> str:
    """Format a float with fixed decimals, trimming nothing else."""
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "nan"
    fmt = f"{{:.{decimals}f}}"
    return fmt.format(float(x))


# Optional helpers for partial-year handling and CPI aggregation

def average_available(values: Iterable[float]) -> float:
    """Average available (non-NaN) values; returns NaN if none present."""
    arr = np.asarray(list(values), dtype=float)
    good = arr[~np.isnan(arr)]
    if good.size == 0:
        return float('nan')
    return float(good.mean())


def annualize_from_higher_freq(years: Iterable[int], periods: Iterable[int], values: Iterable[float]) -> Tuple[List[int], List[float]]:
    """Aggregate higher-frequency data (e.g., quarterly/monthly) to annual by simple mean.
    years, periods, and values should be parallel iterables of equal length.
    Returns (unique_years_sorted, annual_means).
    """
    agg = {}
    cnt = {}
    for y, p, v in zip(years, periods, values):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        y = int(y)
        agg[y] = agg.get(y, 0.0) + float(v)
        cnt[y] = cnt.get(y, 0) + 1
    yrs = sorted(agg.keys())
    means = [agg[y] / cnt[y] for y in yrs]
    return yrs, means

if __name__ == "__main__":
    # Minimal self-test on synthetic data
    y = np.linspace(1, 100, 52)  # positive values
    lam = choose_lambda('A')
    cyc = log_hp_cycle(y, lam)
    print("OK", len(cyc), round_smart(np.mean(cyc), 5))
