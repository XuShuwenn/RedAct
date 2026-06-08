---
name: env-trend-and-driver-attribution
description: "Detect long-term trends in an environmental time series and attribute dominant drivers by grouping predictors into categories and decomposing explained variance."
---

# Environmental Trend and Driver Attribution

This skill provides a reproducible workflow to (1) test for a long-term trend in an environmental time series and (2) identify the dominant driver category among grouped predictors (e.g., Heat, Flow, Wind, Human) using factor scores and R² decomposition.

Use this when you need to:
- quantify a monotonic trend in a response (e.g., water temperature) over time
- output a trend slope and p-value in a simple CSV
- attribute the response to grouped drivers by categories and report the most important category and its percent contribution

## Core Workflow

Phase 1 — Trend Analysis (robust and reproducible)
1. Load the response time series (e.g., WaterTemperature) and time key (e.g., Year).
2. Sort by time; drop rows with missing response values.
3. Prefer a non-parametric Mann–Kendall test with Sen’s slope (robust to outliers and non-normality). If the package is unavailable, fall back to linear regression (report that it is parametric if asked).
4. Write `trend_result.csv` with exactly two columns: `slope` and `p-value`.

Phase 2 — Driver Attribution by Category
1. Load and merge predictor tables on the time key (e.g., Year). Keep only rows with complete values for selected predictors and the response.
2. Define a variable-to-category map (e.g., Heat, Flow, Wind, Human). Only use variables present in the merged data.
3. Standardize predictors (zero mean, unit variance).
4. Extract latent factors:
   - Preferred: Factor analysis with varimax rotation (number of factors ≤ number of categories and ≤ samples − 1).
   - Fallback: PCA with orthogonal varimax rotation.
5. Compute factor scores for each observation.
6. Fit a linear model: response ~ factor scores. Record full R².
7. For each factor i, compute R² without factor i. Factor contribution = max(0, full R² − R²_without_i).
8. Map each factor to a category by summing absolute loadings of variables within each category for that factor; assign the category with the highest sum.
9. Aggregate factor contributions per category and choose the dominant category (highest aggregated contribution).
10. Convert the dominant category’s contribution to a percentage (contribution × 100), round to two decimals, and write `dominant_factor.csv` with two columns: `variable` (the category name) and `contribution` (percentage).

## Verification

Before finalizing results, perform these checks:
- Data integrity:
  - Ensure the time series is sorted by the time key and contains no non-numeric values in the response column.
  - Confirm all variables in the category map exist in the merged dataset; log any that are missing.
- Trend output:
  - `trend_result.csv` exists with headers `slope` and `p-value`, both numeric.
  - The sign of the slope aligns with the trend direction from the test.
- Attribution output:
  - Check that the number of factors ≤ min(number of present categories, number of variables, samples − 1).
  - Confirm predictors were standardized.
  - Validate that `dominant_factor.csv` has exactly two columns: `variable` (one of the categories) and `contribution` (0–100).
  - If any factor contribution is negative due to suppression effects, use max(0, diff) for reporting and ranking.

## Common Pitfalls (and how to avoid them)

- Not sorting by time before trend computation → Always sort by the time key.
- Mixing methods/metrics → If Mann–Kendall is unavailable and you fall back to linear regression, do not label results as non-parametric.
- Misformatted output files → Use exact column names: `slope`, `p-value` for trend; `variable`, `contribution` for attribution.
- Dropping too many rows → Only drop rows with missing values in the response and selected predictors; report final sample size.
- Overfitting or unstable factor extraction → Ensure samples ≫ factors; reduce number of factors if data is short.
- Ignoring standardization → Always standardize predictors prior to factor/PCA.
- Ranking by individual-variable R² only → Use factor/PCA with R² decomposition to handle multicollinearity and shared variance.
- Ambiguous factor-to-category mapping → Use the sum of absolute loadings across variables in each category for robust assignment.

## Success Criteria

- `trend_result.csv` contains a numeric `slope` and `p-value` consistent with the chosen method.
- `dominant_factor.csv` names the most important category and a non-negative percent contribution, computed via R² decomposition of factor scores and category mapping.

## Optional Script Usage

This repository includes a helper script that implements the workflow with sensible fallbacks.

Example usage:
- Default column names and category mapping for lake warming studies:
  - Response = `WaterTemperature`
  - Time key = `Year`
  - Expected predictors (if present): `AirTempLake`, `Shortwave`, `Longwave`, `WindSpeedLake`, `Precip`, `Inflow`, `Outflow`, `DevelopedArea`, `AgricultureArea`

Run:
- python3 scripts/trend_and_attribution.py \
    --water /root/data/water_temperature.csv \
    --climate /root/data/climate.csv \
    --land /root/data/land_cover.csv \
    --hydro /root/data/hydrology.csv \
    --time-col Year \
    --response WaterTemperature \
    --output-dir /root/output

To provide a custom category map, pass a JSON file mapping variable names to categories:
- python3 scripts/trend_and_attribution.py ... --category-map /path/to/map.json

The script writes:
- /root/output/trend_result.csv
- /root/output/dominant_factor.csv
