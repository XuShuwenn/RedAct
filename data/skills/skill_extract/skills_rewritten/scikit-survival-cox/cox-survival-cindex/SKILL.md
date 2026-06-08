---
name: cox-survival-cindex
description: "Fit a Cox proportional hazards model with scikit-survival on tabular survival data and report a robust, verified concordance index."
---

# Cox PH Concordance Index from CSV (scikit-survival)

Reliable workflow to fit a Cox proportional hazards (CPH) model using scikit-survival on a CSV dataset and compute the concordance index (C-index). Emphasizes schema validation, numerically stable fitting, and output verification.

## When to Use

Use this skill when the user asks to:
- fit a Cox proportional hazards model on a CSV with time-to-event data
- compute and report the concordance index (C-index)
- handle small datasets, ties, collinearity, or convergence issues robustly

## Core Workflow

1. Load and validate input data
- Read the CSV with a data frame library.
- Confirm required columns: time and event, plus feature columns.
- Ensure event is boolean-like (0/1 or True/False). Convert to bool explicitly (event = value > 0).
- Ensure time is numeric and non-negative. Coerce to float.
- Select numeric feature columns only. Exclude time and event from features.
- Drop rows with missing values in required columns or impute consistently. Log how many rows were affected.

2. Prepare survival target and features
- Build a structured survival array using scikit-survival utilities (e.g., Surv.from_dataframe with event and time).
- Filter out constant or near-constant features (zero variance). This reduces singularities and improves stability.
- Standardize features (e.g., StandardScaler) to unit scale to improve conditioning of the optimization.

3. Fit a stable Cox PH model
- Start with CoxPHSurvivalAnalysis using ties='efron' (robust for tied event times).
- If supported by the installed version, add a small L2 penalty (alpha) for numerical stability. If not supported, proceed without alpha.
- Increase max iterations and set a reasonable tolerance if the default fails to converge.
- On convergence or numerical errors, retry with a slightly larger alpha (ridge penalty) while keeping standardization. Use a short escalation schedule (e.g., alpha in [1e-8, 1e-6, 1e-4, 1e-3]).
- If CoxPHSurvivalAnalysis lacks penalty support or still fails, fall back to a regularized Cox model (e.g., CoxnetSurvivalAnalysis with ridge-like configuration) and select a stable set of coefficients along its path.

4. Compute the concordance index
- Obtain linear risk scores for the training data (e.g., model.decision_function(X) or model.predict(X) if defined). In scikit-survival, larger scores indicate higher hazard (higher risk).
- Use sksurv.metrics.concordance_index_censored(event, time, scores) to compute the C-index (first return value).
- Round the C-index to 4 decimal places.

5. Write the required output
- Write a single line exactly in the expected format to the requested output file, for example:
  "Concordance index: X.XXXX"

## Verification

Perform these checks to ensure correctness and task compliance:
- Schema and types:
  - event is boolean (dtype bool) and time is numeric; no missing values in these columns.
  - Features are numeric; no object or categorical dtypes remain.
  - No constant features remain (variance > 0 for all features).
- Model fit:
  - The optimizer completes without errors; coefficients are finite (no NaN or inf).
  - If the first attempt fails, confirm stabilization changes (scaling, alpha, iterations) before retrying.
- Scoring correctness:
  - C-index is in [0, 1]. If it is unexpectedly < 0.5, sanity-check the sign of scores by recomputing with negated scores and selecting the higher C-index (this guards against inverted scoring semantics across models).
- Output format:
  - The output file contains exactly one line: "Concordance index: X.XXXX" with 4 decimal places.
  - No extra spaces, headers, or additional lines.

## Common Pitfalls

- Event indicator not boolean: Many scikit-survival utilities require a boolean event array. Convert integer-coded events (e.g., 0/1) to bool.
- Including non-numeric or constant features: Object dtypes or zero-variance columns cause failures or unstable fits. Filter features explicitly.
- Missing data: NaN values in time, event, or features cause errors. Drop or impute deterministically before fitting.
- No scaling: Unscaled features can cause numerical instability. Standardize before fitting.
- Ignoring ties handling: Use ties='efron' for small datasets or tied event times.
- Assuming penalty support: Some versions of CoxPHSurvivalAnalysis may not support alpha. Detect and adapt; fall back to a regularized Cox model if needed.
- Wrong score direction: If C-index is unexpectedly low, check whether risk scores need sign inversion for the chosen estimator.
- Formatting errors: Incorrect rounding or extra content in the output file often leads to task failure.

## Success Criteria

- The model fits successfully (or via stabilized retry) without numerical errors.
- The C-index computed on the intended dataset is within [0, 1].
- The output file exists and contains exactly: "Concordance index: X.XXXX".

## Optional Script Usage

The included helper script automates the full workflow with robust fallbacks.

Example:
- python scripts/cox_cindex.py --input /path/to/input.csv --output /path/to/output.txt --time-col time --event-col event

Optional flags:
- --features f1,f2,f3 to select a subset explicitly (default: all numeric columns except time/event)
- --alpha 1e-6 to start with a small ridge penalty
- --ties efron or breslow for tie handling
- --no-scale to skip feature standardization (not recommended)
