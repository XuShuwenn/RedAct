---
name: business-cycle-hp-correlation
description: "Compute correlation between business-cycle (HP-filtered) components of macroeconomic series from spreadsheets, handling deflation, log transform, annualization of partial-year data, and robust alignment."
---

When to Use

- You need the correlation between cyclical components of macroeconomic time series (e.g., consumption vs. investment) using the Hodrick–Prescott (HP) filter.
- Your inputs are nominal values in spreadsheets with annual rows and a trailing quarterly section for the latest year(s).
- You must convert to real terms using a price index and handle partial-year data by averaging available quarters.

Core Workflow

1) Inspect and Locate Series
- Open each spreadsheet and identify the Total series column for each target variable.
- Confirm how years are stored (numeric year column, row labels, or a mix) and where the quarterly section begins.
- Note any header rows, merged cells, or multi-line headers; normalize column names and drop non-data header rows before extraction.

2) Extract Annual Data
- Build an annual series for each variable from the structured annual rows.
- For the latest year with only partial quarters available, compute the annual value as the simple average of available quarters (use the count of available quarters, not 4).
- Ensure the year index is clean (coerce to integer year keys) and there are no duplicate years.

3) Deflate to Real Terms
- Align the price index (e.g., CPI) to the same annual frequency and year keys as the nominal series.
- If the price index is at higher frequency, convert to annual (commonly the arithmetic mean or a designated month, applied consistently across the sample).
- Compute real values as nominal divided by the price index. Any constant base or scaling in the price index is acceptable; it will be absorbed by the log and does not affect correlation.

4) Prepare and Filter
- Apply the natural logarithm to each real series. Verify all inputs are positive before logging; handle or drop non-positive values.
- Choose HP filter smoothing parameter by frequency:
  - Annual: lambda = 100
  - Quarterly: lambda = 1600
  - Monthly: lambda = 129600
- Apply the HP filter to the logged series; the cyclical component is the logged series minus its trend.

5) Align and Compute Correlation
- Align the two cyclical series by the intersection of their year keys.
- Drop any years with missing values after alignment.
- Compute the Pearson correlation on the aligned cyclical components.
- Round the final result to the required precision; if writing to a file, output only the number.

Verification

- Column/Series Check
  - Confirm that you extracted the intended Total series by inspecting headers and checking a couple of known-year entries.
  - If the table contains subtotals or components, verify you are not mixing components instead of the total.

- Year Handling
  - Print the first and last few aligned years to confirm expected coverage.
  - For the latest year, output the number of quarters used in the average and their values to confirm partial-year handling.

- Real Conversion
  - Check that the index covers all target years; report any missing deflator years before proceeding.
  - Ensure all real series values are positive prior to log transformation.

- Filtering and Result Sanity
  - Confirm lambda matches the data frequency (e.g., 100 for annual).
  - After filtering, the cyclical series should have a mean near zero. If not, confirm that you filtered the logged real series.
  - Verify that the correlation is computed on the cyclical components, not on levels.

- Robustness Checks (optional but useful)
  - Recompute correlation excluding the latest year to ensure the result is not driven by a single data point.
  - Confirm that changing CPI base does not change the correlation (only an additive constant in logs).

Common Pitfalls

- Misidentifying the Total column due to multi-row headers or merged cells; always validate with header inspection and sample values.
- Averaging partial-year data incorrectly (e.g., dividing by four quarters regardless of how many are available). Use the count of available quarters.
- Misaligned series (string vs. integer years, or different year coverage) leading to unintended NaNs and incorrect correlations. Coerce years to integers and use intersection of keys.
- Skipping the log transform before HP filtering; HP on levels can leave residual trend and distort cycles.
- Using the wrong HP lambda for the data frequency (e.g., 1600 for annual data) and producing inconsistent cycles.
- Deflating with mismatched frequency (e.g., using monthly CPI directly against annual nominal without aggregation) or leaving gaps in the deflator series.
- Computing correlation on unaligned arrays (implicit broadcasting or index union) instead of the intersection of valid years.

Optional Script Usage

- Use scripts/hp_cycle_tools.py to:
  - Compute HP-filtered cycles on log(real) with a frequency-appropriate lambda.
  - Align two series by intersecting year keys and compute correlation.
  - Safely round and format the final number.

Example (pseudocode outline)
- Extract two annual nominal series A_nominal, B_nominal and an annual price index CPI with matching year keys.
- Convert to real: A_real = A_nominal / CPI, B_real = B_nominal / CPI.
- Use hp_cycle_tools.log_hp_cycle to get cycles.
- Align years with hp_cycle_tools.align_year_series and compute correlation with hp_cycle_tools.corr.
- Round with hp_cycle_tools.round_smart and write to the answer file.
