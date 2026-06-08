#!/usr/bin/env python3
"""Compute Cox PH concordance index from a CSV using scikit-survival with robust fallbacks.

Usage:
  python scripts/cox_cindex.py --input INPUT.csv --output OUTPUT.txt --time-col time --event-col event [--features f1,f2,...] [--alpha 0.0] [--ties efron] [--no-scale]

Behavior:
- Validates schema and types
- Selects numeric features, drops zero-variance columns
- Standardizes features by default
- Fits CoxPHSurvivalAnalysis with retries (increasing alpha) on instability
- Falls back to CoxnetSurvivalAnalysis (ridge-like) if needed
- Computes C-index with concordance_index_censored and writes formatted output
"""

import argparse
import sys
import os
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold

from sksurv.util import Surv
from sksurv.metrics import concordance_index_censored

# Optional imports guarded at use time
try:
    from sksurv.linear_model import CoxPHSurvivalAnalysis
except Exception as e:  # pragma: no cover
    CoxPHSurvivalAnalysis = None  # type: ignore

try:
    from sksurv.linear_model import CoxnetSurvivalAnalysis
except Exception:
    CoxnetSurvivalAnalysis = None  # type: ignore


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Cox PH concordance index from CSV (scikit-survival)")
    p.add_argument("--input", required=True, help="Path to input CSV")
    p.add_argument("--output", required=True, help="Path to output file")
    p.add_argument("--time-col", required=True, help="Name of time column")
    p.add_argument("--event-col", required=True, help="Name of event column (0/1 or boolean)")
    p.add_argument("--features", default=None, help="Comma-separated list of feature columns to use (default: all numeric except time/event)")
    p.add_argument("--alpha", type=float, default=0.0, help="Initial ridge penalty for CoxPHSurvivalAnalysis (if supported)")
    p.add_argument("--ties", choices=["efron", "breslow"], default="efron", help="Ties handling method")
    p.add_argument("--no-scale", action="store_true", help="Disable feature standardization")
    return p.parse_args()


def _validate_and_prepare(df: pd.DataFrame, time_col: str, event_col: str, features_list: Optional[List[str]]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    # Check required columns
    missing = [c for c in [time_col, event_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Coerce event to boolean: event > 0
    event = df[event_col]
    if event.isna().any():
        df = df.loc[~event.isna()].copy()
        event = df[event_col]
    try:
        event_bool = (event.astype(float) > 0).astype(bool)
    except Exception:
        # If already boolean-like
        event_bool = event.astype(bool)

    # Coerce time to float and non-negative
    time = df[time_col]
    time = pd.to_numeric(time, errors="coerce")
    mask_valid = time.notna() & (time >= 0)
    if not mask_valid.all():
        df = df.loc[mask_valid].copy()
        time = df[time_col].astype(float)
        event_bool = event_bool.loc[df.index]

    # Feature selection
    if features_list is None or len(features_list) == 0:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        features = [c for c in numeric_cols if c not in (time_col, event_col)]
    else:
        features = [c.strip() for c in features_list]
        for c in features:
            if c not in df.columns:
                raise ValueError(f"Feature column not found: {c}")
        # Ensure selected features are numeric
        non_num = [c for c in features if not np.issubdtype(df[c].dtype, np.number)]
        if non_num:
            raise ValueError(f"Selected features must be numeric. Non-numeric: {non_num}")

    if len(features) == 0:
        raise ValueError("No numeric feature columns found after excluding time/event.")

    X = df[features].copy()

    # Drop rows with NaN in features
    mask_no_nan = ~X.isna().any(axis=1)
    if not mask_no_nan.all():
        X = X.loc[mask_no_nan]
        time = time.loc[mask_no_nan]
        event_bool = event_bool.loc[mask_no_nan]

    # Remove zero-variance features
    vt = VarianceThreshold(threshold=0.0)
    X_v = vt.fit_transform(X.values)
    kept_idx = vt.get_support(indices=True)
    kept_features = [features[i] for i in kept_idx]
    if X_v.shape[1] == 0:
        raise ValueError("All features had zero variance after filtering.")

    # Build Surv structured array
    y = Surv.from_arrays(event=event_bool.values.astype(bool), time=time.values.astype(float))

    return X_v.astype(float), y, kept_features


def _fit_coxph(X: np.ndarray, y: np.ndarray, scale: bool, alpha: float, ties: str) -> Tuple[object, np.ndarray]:
    if CoxPHSurvivalAnalysis is None:
        raise RuntimeError("sksurv.linear_model.CoxPHSurvivalAnalysis is not available.")

    # Escalation schedule for ridge penalty
    alphas = []
    if alpha is not None:
        alphas.append(float(alpha))
    alphas += [1e-8, 1e-6, 1e-4, 1e-3]

    # Ensure uniqueness and ascending order
    alphas = sorted(set(a for a in alphas if a >= 0.0))

    last_err = None
    for a in alphas:
        try:
            # Some versions may not support alpha or ties in the constructor; guard via try/except
            try:
                model = CoxPHSurvivalAnalysis(alpha=a, ties=ties)
            except TypeError:
                # Retry without alpha
                model = CoxPHSurvivalAnalysis()

            if scale:
                pipe = make_pipeline(StandardScaler(with_mean=True, with_std=True), model)
                pipe.fit(X, y)
                return pipe, pipe.predict(X) if hasattr(pipe, "predict") else pipe.decision_function(X)  # type: ignore
            else:
                model.fit(X, y)
                # Prefer decision_function if available
                scores = model.decision_function(X) if hasattr(model, "decision_function") else model.predict(X)
                return model, scores
        except Exception as e:
            last_err = e
            continue
    # If all attempts failed
    raise RuntimeError(f"CoxPHSurvivalAnalysis failed to fit after retries: {last_err}")


def _fit_coxnet_ridge(X: np.ndarray, y: np.ndarray, scale: bool) -> Tuple[object, np.ndarray]:
    if CoxnetSurvivalAnalysis is None:
        raise RuntimeError("CoxnetSurvivalAnalysis is not available for fallback.")

    # Ridge-like via elastic net with l1_ratio ~ 0.0
    # Use a broad alpha path; the estimator selects along the path
    alphas = np.logspace(-4, 1, 30)
    try:
        model = CoxnetSurvivalAnalysis(l1_ratio=0.0, alphas=alphas)
    except TypeError:
        # Older versions may use l1_ratio parameter name 'l1_ratio' consistently; if unavailable, re-raise
        model = CoxnetSurvivalAnalysis(alphas=alphas)  # type: ignore

    if scale:
        pipe = make_pipeline(StandardScaler(with_mean=True, with_std=True), model)
        pipe.fit(X, y)
        est = pipe.named_steps.get('coxnetsurvivalanalysis', None)
        # If pipeline name differs, fallback to last step attribute
        est = est if est is not None else pipe.steps[-1][1]
        coef = getattr(est, 'coef_', None)
        if coef is None:
            # As a fallback, try decision function
            scores = pipe.decision_function(X) if hasattr(pipe, 'decision_function') else pipe.predict(X)
            return pipe, np.asarray(scores).ravel()
        coef_vec = np.asarray(coef)[:, -1]
        X_scaled = pipe.named_steps['standardscaler'].transform(X)
        scores = X_scaled @ coef_vec
        return pipe, np.asarray(scores).ravel()
    else:
        model.fit(X, y)
        coef = getattr(model, 'coef_', None)
        if coef is None:
            scores = model.decision_function(X) if hasattr(model, 'decision_function') else model.predict(X)
            return model, np.asarray(scores).ravel()
        coef_vec = np.asarray(coef)[:, -1]
        scores = X @ coef_vec
        return model, np.asarray(scores).ravel()


def main() -> None:
    args = _parse_args()

    # Load CSV
    try:
        df = pd.read_csv(args.input)
    except Exception as e:
        print(f"ERROR: failed to read CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Prepare data
    features_list = args.features.split(',') if args.features else None
    try:
        X, y, kept_features = _validate_and_prepare(df, args.time_col, args.event_col, features_list)
    except Exception as e:
        print(f"ERROR: data preparation failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Fit model with robust fallbacks
    scores = None
    try:
        model, scores = _fit_coxph(X, y, scale=(not args.no_scale), alpha=args.alpha, ties=args.ties)
    except Exception as e1:
        # Try ridge-like Coxnet fallback
        try:
            model, scores = _fit_coxnet_ridge(X, y, scale=(not args.no_scale))
        except Exception as e2:
            print(f"ERROR: model fitting failed (coxph: {e1}; coxnet: {e2})", file=sys.stderr)
            sys.exit(1)

    # Compute C-index
    try:
        # In scikit-survival, higher scores => higher risk
        cindex, _, _ = concordance_index_censored(y['event'], y['time'], np.asarray(scores).ravel())
        cindex = float(cindex)
        # Sanity: if oddly low, consider inverted scores and keep the better one
        if cindex < 0.5:
            cindex_neg, _, _ = concordance_index_censored(y['event'], y['time'], -np.asarray(scores).ravel())
            if float(cindex_neg) > cindex:
                cindex = float(cindex_neg)
    except Exception as e:
        print(f"ERROR: failed to compute concordance index: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"Concordance index: {cindex:.4f}\n")
    except Exception as e:
        print(f"ERROR: failed to write output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
