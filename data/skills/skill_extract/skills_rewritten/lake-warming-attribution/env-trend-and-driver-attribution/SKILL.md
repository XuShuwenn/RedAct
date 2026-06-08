---
name: env-trend-and-driver-attribution
description: "Analyze long-term trends in an environmental time series and attribute the dominant driver category using grouped contributions."
---

# Environmental Trend and Driver Attribution

This skill guides you to (1) quantify a long-term trend in a target environmental time series and (2) attribute the dominant driver category (e.g., Heat, Flow, Wind, Human) using grouped contributions from explanatory variables.

## When to Use

Activate this skill when the user asks you to:
- test for a long-term trend (slope and significance) in a target time series (e.g., lake temperature)
- determine which category of drivers is most important and report its contribution percentage
- produce two concise CSV outputs with exact column names for trend and dominant factor

## Core Workflow

1. Inspect and Align Data
   - List available files and read the first few lines to collect column names and time keys.
   - Identify a common time key (e.g., year, date) and ensure consistent frequency.
   - Parse dates and convert to a numeric time axis when needed.
   - Select the target series (e.g., water temperature) and the explanatory variables from other files. Merge by the common time key.
   - Handle missing values: drop rows with missing target; impute or drop predictors conservatively. Document the approach.

2. Trend Analysis (Target Only)
   - Preferred robust approach: non-parametric trend test with Sen's slope (e.g., Mann–Kendall) if available.
   - Fallback approach: ordinary least squares regression of target on numeric time.
     - Compute slope (units per time unit) and p-value for the time coefficient.
     - Confirm assumptions are reasonable; if seasonality is present, aggregate to a consistent period (e.g., annual means) or use seasonal methods.
   - Output CSV format: two columns with lowercase headers exactly: "slope,p-value" and a single row of numeric values.

3. Group Drivers into Categories
   - Map explanatory variables to categories. Typical patterns:
     - Heat: air temperature, radiation/heat flux proxies
     - Flow: precipitation, inflow/outflow/discharge
     - Wind: wind speed or wind-related metrics
     - Human: land-cover/land-use/anthropogenic pressure indicators
   - Exclude categories with no available variables.
   - Standardize predictor columns (z-scores). Within each category, build a single category index by averaging z-scores or using the first principal component; average is acceptable and deterministic.

4. Fit Category-Level Model and Compute Contributions
   - Regress the (optionally standardized) target on category indices using a stable linear model.
   - If multicollinearity is present, use ridge regression (L2) with a small regularization (e.g., alpha ~ 1.0) to stabilize coefficients.
   - Compute each category's contribution as its share of the model's explained signal. A deterministic approach:
     - Compute fitted signal y_hat.
     - For each category j, compute y_hat_j = X_j * beta_j (its partial fitted signal).
     - Contribution_j = var(y_hat_j) / sum_k var(y_hat_k).
     - Convert to percentages and round sensibly (e.g., nearest integer).
   - Select the dominant category as the one with the largest contribution. Tie-break deterministically (e.g., alphabetical order).

5. Produce Required Outputs
   - trend_result.csv
     - Columns: "slope,p-value"
     - One row with numeric slope and p-value. Avoid units or extra text.
   - dominant_factor.csv
     - Columns: "variable,contribution"
     - One row where "variable" is the category name (e.g., Heat) and "contribution" is an integer percent (0–100).

## Verification

Perform these checks before finalizing:
- Data alignment:
  - Confirm target and drivers share the same time index and the merged dataset has > 2 data points after cleaning.
- Trend result sanity:
  - p-value is within [0, 1].
  - Slope units match the time unit used (e.g., per year). If you aggregated to annual means, slope is per year.
- Driver model integrity:
  - Each included category index has non-zero variance.
  - Contributions are non-negative and sum to ~100% (numerical rounding may cause slight deviation).
  - Dominant category equals argmax(contribution).
- Output formatting:
  - trend_result.csv has exactly two headers: slope,p-value; one data row.
  - dominant_factor.csv has exactly two headers: variable,contribution; one data row; contribution is an integer.

## Common Pitfalls and How to Avoid Them

- Placeholder processing that never runs:
  - Avoid pseudo-commands or unspecified tools. Implement analysis concretely or use the provided helper scripts.
- Misaligned or mixed time scales:
  - Do not mix monthly and annual records without aggregation. Aggregate to a consistent frequency before modeling.
- Missing or zero-variance predictors:
  - Drop or impute predictors with excessive missingness; exclude categories with no valid columns.
- Unstandardized inputs:
  - Always standardize predictors before combining into category indices to avoid scale-induced dominance.
- Multicollinearity instability:
  - Use ridge regression to stabilize coefficient estimates when category indices are correlated.
- Wrong output schema:
  - Ensure column names exactly match the specification and avoid adding extra columns, comments, or units in the CSV.

## Optional Script Usage

Two reusable helpers are provided.

1) Trend estimation tool (linear fallback with robust p-value approximation when advanced packages are unavailable):
- Inputs: a CSV with time and value columns.
- Example:
  - python3 scripts/trend_tools.py --input data.csv --time-col year --value-col water_temp --out trend_result.csv

2) Group contribution tool (ridge-based category attribution):
- Inputs: a merged CSV containing the target and all predictor columns, plus a category mapping string.
- Mapping format: "CategoryA:col1,col2;CategoryB:col3;CategoryC:col4,col5".
- Example:
  - python3 scripts/group_contrib.py --input merged.csv --target water_temp --groups "Heat:air_temp,rad;Flow:precip,discharge;Wind:wind;Human:urban_frac" --out dominant_factor.csv

Both scripts are deterministic, handle basic data cleaning, and write the required CSVs in the exact formats.
