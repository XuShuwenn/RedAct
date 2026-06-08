#!/usr/bin/env python3
"""
Group contribution analysis: attribute dominant driver category.

CLI usage:
  python3 scripts/group_contrib.py \
    --input merged.csv \
    --target water_temp \
    --groups "Heat:air_temp,rad;Flow:precip,discharge;Wind:wind;Human:urban_frac" \
    --out dominant_factor.csv

Method:
- Standardize each predictor column (z-score).
- Create a category index by averaging z-scores within each category.
- Fit ridge regression (closed-form) of target on category indices.
- Compute contribution of each category as var(X_j * beta_j) / sum_k var(X_k * beta_k).
- Write the single top category and its contribution (integer percent) to CSV with headers: variable,contribution.
"""

import argparse
import csv
import math
import sys
from typing import Dict, List, Tuple

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    np = None


def parse_groups(s: str) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    if not s:
        return groups
    parts = [p for p in s.split(';') if p.strip()]
    for part in parts:
        if ':' not in part:
            continue
        name, cols = part.split(':', 1)
        col_list = [c.strip() for c in cols.split(',') if c.strip()]
        if col_list:
            groups[name.strip()] = col_list
    return groups


def zscore(col: 'np.ndarray') -> 'np.ndarray':  # type: ignore
    mu = np.nanmean(col)
    sd = np.nanstd(col)
    if not np.isfinite(sd) or sd == 0:
        return np.full_like(col, np.nan, dtype=float)
    return (col - mu) / sd


def ridge_closed_form(X: 'np.ndarray', y: 'np.ndarray', alpha: float = 1.0) -> 'np.ndarray':  # type: ignore
    # Center y and X (no intercept)
    Xc = X - np.nanmean(X, axis=0)
    yc = y - np.nanmean(y)
    # Drop rows with NaNs
    mask = np.isfinite(yc)
    for j in range(Xc.shape[1]):
        mask &= np.isfinite(Xc[:, j])
    Xf = Xc[mask]
    yf = yc[mask]
    if Xf.shape[0] < Xf.shape[1] + 1:
        # Not enough rows; fall back to zeros
        return np.zeros(Xf.shape[1])
    XtX = Xf.T @ Xf
    nfeat = XtX.shape[0]
    A = XtX + alpha * np.eye(nfeat)
    try:
        beta = np.linalg.solve(A, Xf.T @ yf)
    except Exception:
        beta = np.linalg.pinv(A) @ (Xf.T @ yf)
    return beta


def contributions_from_betas(X: 'np.ndarray', beta: 'np.ndarray', y: 'np.ndarray') -> Tuple[List[float], float]:  # type: ignore
    Xc = X - np.nanmean(X, axis=0)
    yc = y - np.nanmean(y)
    mask = np.isfinite(yc)
    for j in range(Xc.shape[1]):
        mask &= np.isfinite(Xc[:, j])
    Xf = Xc[mask]
    yf = yc[mask]
    yhat_parts = []
    for j in range(Xf.shape[1]):
        yhat_j = Xf[:, [j]] @ beta[[j]]
        yhat_parts.append(yhat_j[:, 0])
    var_parts = [np.var(p) for p in yhat_parts]
    denom = sum(var_parts)
    if denom <= 0 or not np.isfinite(denom):
        return [0.0 for _ in var_parts], 0.0
    contribs = [v / denom for v in var_parts]
    # Overall R^2 for sanity (not used in output)
    yhat = sum(yhat_parts)
    ss_res = np.sum((yf - yhat) ** 2)
    ss_tot = np.sum((yf - np.mean(yf)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return contribs, r2


def write_dominant_csv(path: str, variable: str, contribution_pct: int) -> None:
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['variable', 'contribution'])
        writer.writerow([variable, str(contribution_pct)])


def main():
    ap = argparse.ArgumentParser(description='Compute dominant driver category via grouped contributions.')
    ap.add_argument('--input', required=True, help='Path to merged CSV containing target and predictors')
    ap.add_argument('--target', required=True, help='Target column name')
    ap.add_argument('--groups', required=True, help='Category mapping string, e.g., "Heat:air_temp,rad;Flow:precip,discharge"')
    ap.add_argument('--alpha', type=float, default=1.0, help='Ridge regularization strength (default 1.0)')
    ap.add_argument('--out', required=True, help='Path to output CSV (variable,contribution)')
    args = ap.parse_args()

    if pd is None or np is None:
        print('ERROR: pandas and numpy are required for this script.', file=sys.stderr)
        sys.exit(1)

    groups = parse_groups(args.groups)
    if not groups:
        print('ERROR: No valid groups provided.', file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(args.input)
    if args.target not in df.columns:
        print('ERROR: Target column not found.', file=sys.stderr)
        sys.exit(1)

    # Build category indices
    cat_names: List[str] = []
    cat_arrays: List['np.ndarray'] = []  # type: ignore

    for cat, cols in groups.items():
        valid_cols = [c for c in cols if c in df.columns]
        if not valid_cols:
            continue
        Zs = []
        for c in valid_cols:
            col = df[c].astype(float).to_numpy()
            Zs.append(zscore(col))
        if not Zs:
            continue
        Z = np.vstack(Zs)
        idx = np.nanmean(Z, axis=0)
        if np.all(~np.isfinite(idx)) or np.nanstd(idx) == 0:
            continue
        cat_names.append(cat)
        cat_arrays.append(idx)

    if not cat_arrays:
        print('ERROR: No valid category indices could be computed.', file=sys.stderr)
        sys.exit(1)

    X = np.vstack(cat_arrays).T  # shape (n_samples, n_categories)
    y = df[args.target].astype(float).to_numpy()

    beta = ridge_closed_form(X, y, alpha=args.alpha)
    # If beta length mismatch (rare), adjust
    if beta.shape[0] != X.shape[1]:
        beta = np.zeros(X.shape[1])

    contribs, r2 = contributions_from_betas(X, beta, y)
    # Normalize to percentages
    pct = [max(0.0, min(1.0, c)) * 100.0 for c in contribs]

    # Select dominant with deterministic tie-break
    best_idx = 0
    for i in range(1, len(pct)):
        if abs(pct[i] - pct[best_idx]) < 1e-9:
            # tie: choose lexicographically smaller name
            if cat_names[i] < cat_names[best_idx]:
                best_idx = i
        elif pct[i] > pct[best_idx]:
            best_idx = i

    dominant_name = cat_names[best_idx]
    dominant_pct_int = int(round(pct[best_idx]))

    write_dominant_csv(args.out, dominant_name, dominant_pct_int)


if __name__ == '__main__':
    main()
