---
name: lake-warming-attribution
description: "Analyze lake temperature trends and attribute warming to climate drivers (Heat, Flow, Wind, Human factors)."
---

# Lake Warming Attribution Analysis

## When to Use

- Analyze long-term water temperature trends
- Attribute warming to driving factors
- Process climate and hydrology data

## Input Files

- `/root/data/water_temperature.csv`: Lake surface temperature (0-5m)
- `/root/data/climate.csv`: Climate variables
- `/root/data/land_cover.csv`: Land cover data
- `/root/data/hydrology.csv`: Hydrology data

## Pre-Analysis Checks

- Inspect the full contents of each input file before modeling; do not rely on truncated previews.
- Verify key columns, year coverage, duplicate years, delimiter/parsing assumptions, and missing/malformed numeric values.
- Confirm tables can be joined on a shared year field and handle incomplete rows before regression or attribution.


## Output Files

### trend_result.csv
```csv
slope,p-value
```

### dominant_factor.csv
```csv
variable,contribution
```

**Use these filenames and headers exactly.**
- `trend_result.csv` must have columns exactly: `slope,p-value`
- `dominant_factor.csv` must have columns exactly: `variable,contribution`
- Write both required files to `/root/output/` and verify they exist before finishing.
- Do **not** change punctuation or casing (for example, `p.value` is wrong; use `p-value`).

## Key Steps

1. **Trend Analysis**: Linear regression on water temperature vs time
   - Output slope and p-value to `trend_result.csv`

2. **Attribution Analysis**: Use climate, hydrology, and land-cover predictors to explain temperature variation with one defensible importance method
   - Verify the full header/schema of every input file before choosing predictors or assigning variables to Heat/Flow/Wind/Human
   - First validate merged data: confirm years align across files, handle missing/malformed rows, and use only complete comparable rows for attribution
   - Prefer a single multivariable model with standardized predictors, then compare validated importance values from that model; if the merged dataset is small relative to predictor count, use the simplest interpretable approach that remains defensible
   - Do **not** normalize R² values from separate models into contribution percentages, and do **not** use latent-factor/factor-analysis pipelines unless they are clearly appropriate, stable for sample size, and map factors unambiguously
   - Use Heat / Flow / Wind / Human for grouping or interpretation if helpful, but for `dominant_factor.csv`, output the single most important verified **variable** and its computed contribution/importance value
   - If reporting percentages from model-importance scores, normalize nonnegative contributions so reported shares are interpretable
   - If the method supports association rather than causal attribution, report it conservatively as the dominant or most associated factor


3. **Method Validation and Output Verification**: Ensure the calculations and files match the requested deliverables before reporting
   - For trend, regress temperature against the actual time/year variable; do not substitute a different trend statistic unless explicitly requested
   - If any script or run failed, looked truncated, or did not clearly complete, rerun fully and confirm completion before using its results
   - Open and inspect both output CSVs after writing them; do not claim success based on partial console output
   - Verify the final CSVs contain the required columns only: `slope,p-value` and `variable,contribution`

## Tips

- Use scipy.stats for linear regression
- pandas for data merging and analysis
- Consider multiple regression for attribution
- Check significance levels (p < 0.05)


- Before merging, check row counts, year ranges, join keys, and NA counts for every file
- Prefer simple, auditable attribution over opaque dimensionality reduction when the task only asks for the dominant driver
- Before trusting outputs, verify the analysis actually executed and keep claims bounded to numbers that appear in the saved CSVs
- When reporting the dominant factor, write a concrete predictor name rather than a category label
