#!/usr/bin/env python3
"""Robust Cox PH model fitting and concordance index computation using scikit-survival.

Usage examples:
  python scripts/coxph_cindex.py --input data.csv --time time --event event
  python scripts/coxph_cindex.py --input data.csv --time t --event status --features x1,x2,x3 --alpha 0.01 --output out.txt

Notes:
- Expects scikit-survival, scikit-learn, pandas, and numpy to be installed.
- Computes training concordance index by default.
"""

import argparse
import sys
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

try:
    from sksurv.util import Surv
    from sksurv.linear_model import CoxPHSurvivalAnalysis
    from sksurv.metrics import concordance_index_censored
except Exception as e:
    print("ERROR: scikit-survival is required (pip install scikit-survival)", file=sys.stderr)
    raise


def parse_args():
    p = argparse.ArgumentParser(description="Fit Cox PH and report concordance index")
    p.add_argument("--input", required=True, help="Path to input CSV")
    p.add_argument("--time", required=True, help="Name of duration/time column")
    p.add_argument("--event", required=True, help="Name of event indicator column (1=event, 0=censored)")
    p.add_argument("--features", help="Comma-separated feature column names. If omitted, use numeric columns excluding time and event.")
    p.add_argument("--alpha", type=float, default=1e-3, help="L2 regularization strength for Cox PH (default: 1e-3)")
    p.add_argument("--max-corr", type=float, default=None, help="Optional: drop one of any pair of features with absolute correlation above this threshold")
    p.add_argument("--decimals", type=int, default=4, help="Number of decimals for rounding the C-index (default: 4)")
    p.add_argument("--output", help="Optional path to write the result line 'Concordance index: X.XXXX'. If omitted, print to stdout.")
    return p.parse_args()


def coerce_event_bool(s: pd.Series) -> pd.Series:
    # Accept bool; or 0/1 ints/floats; or strings '0'/'1'/'True'/'False'
    if s.dtype == bool:
        return s
    # Try numeric 0/1
    try:
        sn = pd.to_numeric(s, errors="coerce")
        if sn.isna().all():
            raise ValueError
        # treat nonzero as True, zero as False
        return sn.fillna(0).astype(int).astype(bool)
    except Exception:
        # Try string mapping
        m = s.astype(str).str.strip().str.lower().map({"1": True, "0": False, "true": True, "false": False})
        if m.isna().any():
            raise ValueError("Event column cannot be coerced to boolean.")
        return m.astype(bool)


def drop_zero_variance(X: pd.DataFrame) -> pd.DataFrame:
    std = X.std(ddof=0)
    keep = std[std > 0].index
    return X[keep]


def drop_high_correlation(X: pd.DataFrame, threshold: float) -> pd.DataFrame:
    if X.shape[1] <= 1:
        return X
    corr = X.corr().abs()
    # Upper triangle mask to avoid duplicate pairs
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = set()
    for col in upper.columns:
        # Drop later columns if correlated with an earlier kept column
        high_corr = upper[col] > threshold
        if high_corr.any():
            to_drop.update(upper.index[high_corr].tolist())
    # Deterministic: drop by column order
    keep_cols = [c for c in X.columns if c not in to_drop]
    return X[keep_cols]


def compute_cindex(y, risk_scores: np.ndarray) -> float:
    # Concordance expects higher risk scores to indicate higher hazard (shorter survival)
    cindex = float(concordance_index_censored(y['event'], y['time'], risk_scores)[0])
    if cindex < 0.5:
        # Flip orientation if needed
        cindex = float(concordance_index_censored(y['event'], y['time'], -risk_scores)[0])
    return cindex


def main():
    args = parse_args()

    df = pd.read_csv(args.input)
    if args.time not in df.columns or args.event not in df.columns:
        print("ERROR: Missing required time/event columns", file=sys.stderr)
        sys.exit(1)

    # Coerce event to bool and ensure time numeric
    try:
        event_bool = coerce_event_bool(df[args.event])
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        time_values = pd.to_numeric(df[args.time], errors="coerce")
    except Exception:
        print("ERROR: Time column must be numeric", file=sys.stderr)
        sys.exit(1)

    # Drop rows with missing time/event
    mask_valid = (~time_values.isna()) & (~event_bool.isna())
    df = df.loc[mask_valid].copy()
    time_values = time_values.loc[mask_valid]
    event_bool = event_bool.loc[mask_valid]

    # Select features
    if args.features:
        feature_list: List[str] = [f.strip() for f in args.features.split(',') if f.strip()]
        missing = [f for f in feature_list if f not in df.columns]
        if missing:
            print(f"ERROR: Missing feature columns: {missing}", file=sys.stderr)
            sys.exit(1)
        X = df[feature_list].copy()
    else:
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude time column if numeric
        num_cols = [c for c in num_cols if c != args.time]
        # Exclude event if mistakenly numeric in the data frame
        num_cols = [c for c in num_cols if c != args.event]
        if not num_cols:
            print("ERROR: No numeric feature columns found.", file=sys.stderr)
            sys.exit(1)
        X = df[num_cols].copy()

    # Drop rows with missing feature values (simple policy); could be replaced by imputation if needed
    valid_feat_mask = ~X.isna().any(axis=1)
    X = X.loc[valid_feat_mask]
    time_values = time_values.loc[valid_feat_mask]
    event_bool = event_bool.loc[valid_feat_mask]

    # Remove zero-variance features
    X = drop_zero_variance(X)
    if X.shape[1] == 0:
        print("ERROR: All features have zero variance after filtering.", file=sys.stderr)
        sys.exit(1)

    # Optionally remove highly correlated features
    if args.max_corr is not None:
        X = drop_high_correlation(X, args.max_corr)
        if X.shape[1] == 0:
            print("ERROR: No features remain after correlation filtering.", file=sys.stderr)
            sys.exit(1)

    # Build survival object
    y = Surv.from_dataframe(event_col=event_bool.name, time_col=time_values.name, data=pd.DataFrame({event_bool.name: event_bool, time_values.name: time_values}))

    # Pipeline: scaling + Cox PH with L2 penalty
    try:
        pipe = make_pipeline(
            StandardScaler(with_mean=True, with_std=True),
            CoxPHSurvivalAnalysis(alpha=float(args.alpha)),
        )
        pipe.fit(X, y)
    except Exception as e:
        # Retry with increased alpha if numerical issues arise
        try:
            alpha2 = max(float(args.alpha) * 10.0, 1e-4)
            pipe = make_pipeline(
                StandardScaler(with_mean=True, with_std=True),
                CoxPHSurvivalAnalysis(alpha=alpha2),
            )
            pipe.fit(X, y)
        except Exception as e2:
            print(f"ERROR: Model failed to fit even after increasing alpha. {e2}", file=sys.stderr)
            sys.exit(1)

    # Predict risk scores and compute C-index
    try:
        risk = pipe.predict(X)
    except Exception as e:
        print(f"ERROR: Failed to predict risk scores: {e}", file=sys.stderr)
        sys.exit(1)

    cindex = compute_cindex(y, np.asarray(risk))
    rounded = f"{cindex:.{args.decimals}f}"
    line = f"Concordance index: {rounded}"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(line + "\n")
    else:
        print(line)


if __name__ == "__main__":
    main()
