---
name: robust-coxph-cindex
description: "Fit a Cox proportional hazards model with scikit-survival robustly on small or collinear datasets and report the concordance index."
---

# Robust Cox PH Concordance Index

This skill provides a reliable workflow for fitting a Cox proportional hazards (Cox PH) model using scikit-survival and reporting the concordance index (C-index), especially on small datasets and those with highly correlated features.

## When to Use

Use this skill when you need to:
- Fit a Cox PH model on tabular survival data (time-to-event).
- Compute and report the C-index for model discrimination.
- Handle numerical issues from small sample sizes and multicollinearity.

## Core Workflow

1. Validate input schema
   - Required columns: a duration column (time), an event indicator (event), and one or more feature columns.
   - Ensure event is boolean (True for event occurred, False for censored). If encoded as 0/1, cast to bool.
   - Drop rows with missing values in time or event. Decide on an imputation strategy for feature NA values if present (simple drop or impute).

2. Select and prepare features
   - Use numeric features; either explicitly list them or infer them by selecting numeric columns that exclude time and event.
   - Remove zero-variance features.
   - Standardize features with StandardScaler. This stabilizes optimization and prevents a single feature’s scale from dominating.

3. Fit a penalized Cox PH model
   - Use scikit-survival’s CoxPHSurvivalAnalysis with a small L2 penalty (alpha) to address singularities and multicollinearity.
   - Start with a small alpha (e.g., 1e-4 to 0.1). If fitting fails or warns about singular matrices, increase alpha by a factor (e.g., ×10) until stable.
   - For extreme collinearity or persistent convergence issues, consider an elastic net Cox model (CoxnetSurvivalAnalysis) as a fallback.

4. Compute risk scores and C-index
   - Predict linear risk scores for the training data (higher score = higher hazard = shorter survival).
   - Compute C-index using sksurv.metrics.concordance_index_censored.
   - If C-index < 0.5, flip the sign of risk scores and recompute (some pipelines may invert risk orientation).

5. Format and write output
   - Round the C-index to 4 decimal places.
   - Write exactly one line in the required format for your task, for example:
     "Concordance index: X.XXXX"

## Verification

Perform these checks before finalizing:
- Schema check: time column is numeric and non-negative; event is boolean; at least one feature remains after preprocessing.
- Stability check: model fit completes without convergence or singularity errors; if encountered, increase alpha and refit.
- Score orientation check: ensure C-index ≥ 0.5 on training; if not, try negating risk scores and recomputing.
- Determinism check: fix random seeds where applicable; avoid randomized CV for the final reported C-index unless the task explicitly requests it.
- Output check: exactly one line, correct label text, and 4-decimal rounding.

## Common Pitfalls

- Event dtype not boolean: Passing integer or string-encoded events without conversion can cause errors or incorrect metrics.
- No scaling: Unscaled features can lead to numerical instability and slow or failed convergence.
- Over-regularization: Using a very large alpha can overshrink coefficients and degrade discrimination (lower C-index). Start small and increase only as needed for stability.
- Risk orientation mismatch: Interpreting lower scores as higher risk or vice versa yields a low C-index; flip the sign if needed.
- Including non-numeric features without encoding: Ensure X is numeric, or encode categoricals before fitting.
- Zero-variance or perfectly collinear features: These can cause singular matrices; remove zero-variance columns and use L2 regularization to handle collinearity.
- Wrong output format or precision: Ensure rounding to exactly 4 decimals and the specified text format.

## Optional Script Usage

Use the helper script to run the complete workflow end-to-end on a CSV file.

Example:
- Compute and print the C-index using inferred numeric features (excluding time and event):
  python scripts/coxph_cindex.py --input data.csv --time time --event event

- Specify features and write to an output file with a chosen penalty:
  python scripts/coxph_cindex.py --input data.csv --time time --event event --features feature1,feature2,feature3 --alpha 0.01 --output output.txt

Script behavior:
- Reads CSV, validates columns, converts event to bool, drops rows with missing time/event.
- Selects numeric features (or the provided list), drops zero-variance columns, standardizes via a pipeline.
- Fits a Cox PH model with L2 penalty alpha and computes the training C-index.
- Ensures correct risk orientation and prints or writes the rounded C-index.
