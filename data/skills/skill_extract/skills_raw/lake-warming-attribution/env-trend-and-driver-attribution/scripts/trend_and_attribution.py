#!/usr/bin/env python3
"""
Environmental trend and driver attribution utility.

- Computes Mann–Kendall Sen's slope trend (if available) with p-value
  and writes trend_result.csv with columns: slope, p-value.
- Attributes dominant driver category using factor/PCA with varimax rotation
  and R^2 decomposition; writes dominant_factor.csv with columns: variable, contribution.

Usage examples:
  python3 scripts/trend_and_attribution.py \
    --water /root/data/water_temperature.csv \
    --climate /root/data/climate.csv \
    --land /root/data/land_cover.csv \
    --hydro /root/data/hydrology.csv \
    --time-col Year --response WaterTemperature \
    --output-dir /root/output

  python3 scripts/trend_and_attribution.py ... --category-map /path/to/map.json

Notes:
- If pymannkendall is unavailable, falls back to scipy's linregress for slope/p-value.
- If factor_analyzer is unavailable, falls back to PCA + varimax; if factors are not feasible,
  falls back to category-wise R^2 regression.
"""

import argparse
import json
import math
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# ---------- Optional imports with graceful fallbacks ----------
try:
    import pymannkendall as mk  # type: ignore
except Exception:
    mk = None

try:
    from factor_analyzer import FactorAnalyzer  # type: ignore
except Exception:
    FactorAnalyzer = None  # type: ignore

try:
    from scipy import stats
except Exception:
    stats = None  # type: ignore

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression


# ---------- Utilities ----------

def varimax(Phi: np.ndarray, gamma: float = 1.0, q: int = 20, tol: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]:
    """Varimax rotation for loadings.
    Returns (rotated_loadings, rotation_matrix).
    """
    if Phi.ndim != 2:
        raise ValueError("Phi must be 2D (variables x factors)")
    p, k = Phi.shape
    R = np.eye(k)
    d = 0
    for _ in range(q):
        d_old = d
        Lambda = Phi @ R
        u, s, vh = np.linalg.svd(
            Phi.T @ (Lambda ** 3 - (gamma / p) * Lambda @ np.diag(np.diag(Lambda.T @ Lambda)))
        )
        R = u @ vh
        d = np.sum(s)
        if d_old != 0 and d / d_old < 1 + tol:
            break
    return Phi @ R, R


def calc_r2(X: np.ndarray, y: np.ndarray) -> float:
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    if X.shape[1] == 0:
        return 0.0
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0


def mann_kendall_sen(values: np.ndarray) -> Tuple[float, float]:
    """Compute Sen's slope and p-value via pymannkendall if available.
    Falls back to linear regression (parametric) if not available.
    """
    vals = np.asarray(values, dtype=float)
    if mk is not None:
        res = mk.original_test(vals)
        # pymannkendall reports Sen's slope as 'slope'
        return float(res.slope), float(res.p)
    # Fallbacks
    if stats is not None:
        slope, intercept, r_value, p_value, std_err = stats.linregress(np.arange(len(vals)), vals)
        return float(slope), float(p_value)
    # Last-resort: numpy polyfit (no p-value)
    slope = float(np.polyfit(np.arange(len(vals)), vals, 1)[0])
    return slope, float('nan')


def load_and_merge(water_path: Path, tables: List[Path], time_col: str) -> pd.DataFrame:
    df = pd.read_csv(water_path)
    for t in tables:
        if t is None or (isinstance(t, float) and math.isnan(t)):
            continue
        if not Path(t).exists():
            continue
        other = pd.read_csv(t)
        if time_col not in other.columns:
            raise ValueError(f"Time column '{time_col}' not found in {t}")
        df = df.merge(other, on=time_col, how='inner')
    return df


def factor_scores_with_rotation(X_scaled: np.ndarray, n_factors: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return (scores, loadings) using FactorAnalyzer if available, else PCA + varimax."""
    if n_factors <= 0:
        raise ValueError("n_factors must be >= 1")
    if FactorAnalyzer is not None:
        fa = FactorAnalyzer(n_factors=n_factors, rotation='varimax')
        fa.fit(X_scaled)
        scores = fa.transform(X_scaled)  # (n_samples x n_factors)
        loadings = fa.loadings_          # (n_variables x n_factors)
        return scores, loadings
    # Fallback: PCA + varimax
    pca = PCA(n_components=n_factors)
    scores = pca.fit_transform(X_scaled)                      # (n_samples x n_factors)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)  # (n_variables x n_factors)
    loadings_rot, R = varimax(loadings)
    scores_rot = scores @ R  # rotate scores consistently
    return scores_rot, loadings_rot


def map_factors_to_categories(loadings: np.ndarray, predictors: List[str], cat_map: Dict[str, str]) -> List[str]:
    cats = sorted(set(cat_map.values()))
    factor_to_cat: List[str] = []
    for f in range(loadings.shape[1]):
        sums = {c: 0.0 for c in cats}
        for vi, var in enumerate(predictors):
            if var in cat_map:
                sums[cat_map[var]] += abs(loadings[vi, f])
        # choose category with max sum; if all zero, assign 'Unknown'
        best_cat = max(sums, key=sums.get) if len(sums) else 'Unknown'
        factor_to_cat.append(best_cat)
    return factor_to_cat


def category_r2_fallback(df: pd.DataFrame, y: np.ndarray, categories: Dict[str, List[str]]) -> Tuple[str, float]:
    """If factor/PCA isn't feasible, compute R^2 per category regression as a fallback."""
    best_cat = None
    best_r2 = -np.inf
    for cat, vars_list in categories.items():
        vars_present = [v for v in vars_list if v in df.columns]
        if not vars_present:
            continue
        X = df[vars_present].values
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)
        r2 = calc_r2(Xs, y)
        if r2 > best_r2:
            best_r2 = r2
            best_cat = cat
    return best_cat or 'Unknown', max(0.0, best_r2) * 100.0


def main():
    ap = argparse.ArgumentParser(description="Trend analysis and driver attribution")
    ap.add_argument('--water', required=True, help='Path to response (e.g., water_temperature.csv)')
    ap.add_argument('--climate', help='Path to climate.csv')
    ap.add_argument('--land', help='Path to land_cover.csv')
    ap.add_argument('--hydro', help='Path to hydrology.csv')
    ap.add_argument('--time-col', default='Year', help='Time key column (default: Year)')
    ap.add_argument('--response', default='WaterTemperature', help='Response column (default: WaterTemperature)')
    ap.add_argument('--output-dir', default='/root/output', help='Directory to write outputs')
    ap.add_argument('--category-map', help='Path to JSON file mapping variable -> category')
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ----- Phase 1: Trend -----
    water_df = pd.read_csv(args.water)
    if args.time_col not in water_df.columns:
        raise ValueError(f"Time column '{args.time_col}' not found in {args.water}")
    if args.response not in water_df.columns:
        raise ValueError(f"Response column '{args.response}' not found in {args.water}")
    w = water_df[[args.time_col, args.response]].dropna().sort_values(args.time_col)
    slope, pval = mann_kendall_sen(w[args.response].values)
    pd.DataFrame({'slope': [slope], 'p-value': [pval]}).to_csv(out_dir / 'trend_result.csv', index=False)

    # ----- Phase 2: Attribution -----
    # Load/merge tables
    tables = [p for p in [args.climate, args.land, args.hydro] if p]
    merged = load_and_merge(Path(args.water), [Path(p) for p in tables], args.time_col)

    # Default category mapping for typical lake-warming inputs (override via --category-map)
    if args.category_map:
        with open(args.category_map, 'r') as f:
            var_to_cat = json.load(f)
    else:
        var_to_cat = {
            'AirTempLake': 'Heat',
            'Shortwave': 'Heat',
            'Longwave': 'Heat',
            'Precip': 'Flow',
            'Inflow': 'Flow',
            'Outflow': 'Flow',
            'WindSpeedLake': 'Wind',
            'DevelopedArea': 'Human',
            'AgricultureArea': 'Human',
        }

    # Select predictors present
    predictors = [v for v in var_to_cat.keys() if v in merged.columns]
    if not predictors:
        # No predictors available; write a placeholder result
        pd.DataFrame({'variable': ['Unknown'], 'contribution': [0.0]}).to_csv(out_dir / 'dominant_factor.csv', index=False)
        return

    # Prepare data
    df_model = merged.dropna(subset=predictors + [args.response])
    if df_model.empty:
        pd.DataFrame({'variable': ['Unknown'], 'contribution': [0.0]}).to_csv(out_dir / 'dominant_factor.csv', index=False)
        return
    y = df_model[args.response].values
    X = df_model[predictors].values

    # If too few samples for factors, fall back to category-wise R^2
    present_cats = sorted({var_to_cat[v] for v in predictors})
    max_factors = min(len(present_cats), len(predictors), max(1, len(df_model) - 1))
    if max_factors < 1 or len(df_model) < 3:
        # Fallback
        categories = {}
        for v in predictors:
            categories.setdefault(var_to_cat[v], []).append(v)
        best_cat, best_pct = category_r2_fallback(df_model, y, categories)
        pd.DataFrame({'variable': [best_cat], 'contribution': [round(best_pct, 2)]}).to_csv(out_dir / 'dominant_factor.csv', index=False)
        return

    # Standardize predictors
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    # Obtain factor/PCA scores and loadings
    n_factors = max_factors
    scores, loadings = factor_scores_with_rotation(Xs, n_factors)

    # Full R^2
    full_r2 = calc_r2(scores, y)

    # Factor contributions via leave-one-factor-out R^2
    contribs = []
    for i in range(scores.shape[1]):
        cols = [j for j in range(scores.shape[1]) if j != i]
        r2_without = calc_r2(scores[:, cols], y)
        contribs.append(max(0.0, full_r2 - r2_without))
    contribs = np.array(contribs)

    # Map factors to categories
    factor_to_cat = map_factors_to_categories(loadings, predictors, var_to_cat)

    # Aggregate contributions by category
    cat_contrib = {c: 0.0 for c in present_cats}
    for i, c in enumerate(factor_to_cat):
        if c in cat_contrib:
            cat_contrib[c] += float(contribs[i])

    if not cat_contrib:
        pd.DataFrame({'variable': ['Unknown'], 'contribution': [0.0]}).to_csv(out_dir / 'dominant_factor.csv', index=False)
        return

    # Determine dominant category
    dominant_cat = max(cat_contrib, key=cat_contrib.get)
    dominant_pct = round(cat_contrib[dominant_cat] * 100.0, 2)

    pd.DataFrame({'variable': [dominant_cat], 'contribution': [dominant_pct]}).to_csv(out_dir / 'dominant_factor.csv', index=False)


if __name__ == '__main__':
    main()
