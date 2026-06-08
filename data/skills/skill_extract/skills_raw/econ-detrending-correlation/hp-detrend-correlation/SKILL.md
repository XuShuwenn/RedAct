---
name: hp-detrend-correlation
description: "Detrend macroeconomic time series with the HP filter (on log real values) and compute Pearson correlation, robust to mixed annual/quarterly Excel tables and CPI deflation."
---

# HP Detrending and Business-Cycle Correlation

A reusable workflow to compute the correlation between cyclical components of two macroeconomic series. It covers extracting annual totals from ERP-style Excel tables that mix annual and quarterly rows, deflating with CPI, log-transforming, HP filtering (λ=100 for annual), and computing the Pearson correlation.

## When to Use

Use this skill when you need to:
- Extract annual totals from Excel tables that mix annual and quarterly entries (e.g., ERP tables with 1973–recent annual rows and quarterly rows for the latest year).
- Deflate nominal macro series to real values using CPI (any base year).
- Apply Hodrick–Prescott filtering to the log of real series and correlate cyclical components.
- Produce a single-number correlation result with strict output formatting.

## Core Workflow

1) Inspect and Load Data
- Identify available files and formats (.xls legacy vs .xlsx). For legacy .xls, use a compatible engine (e.g., xlrd) if pandas/openpyxl fail.
- Confirm which column contains the desired "Total" series (often Column 1 after the year label). Verify by printing header rows and a few data rows.

2) Parse Annual vs Quarterly Rows
- Annual rows typically show a 4-digit year, sometimes followed by a period, e.g., "1980.".
- Quarterly rows often include patterns like "YYYY:Q1/Q2/Q3/Q4" or roman numerals (I, II, III, IV) with optional notes (e.g., preliminary markers).
- Extract a clean annual series:
  - Keep rows matching a year-only pattern (e.g., ^\d{4}\.?$) as annual.
  - For the latest year with only quarterly data, compute the annual value as the average of available quarters (e.g., average of Q1–Q3 if Q4 is missing). Do not use a single quarter as the annual value unless explicitly required.

3) Align the Two Series by Year
- Build two dicts or pandas Series indexed by integer Year.
- Inner-join by Year to avoid row-offset issues across files.
- Sort by Year and ensure no duplicates.

4) Merge CPI and Deflate to Real Values
- Merge CPI by Year.
- Use a consistent base-year normalization:
  - If CPI is already normalized (base=1.0 for a chosen year), Real_t = Nominal_t / CPI_t.
  - Otherwise, normalize CPI to a chosen base year B: Real_t = Nominal_t × (CPI_B / CPI_t).
- Verify CPI coverage across the full sample (no missing years).

5) Log Transform and HP Filter
- Apply the natural logarithm to the real series.
- Apply the HP filter with λ appropriate to the frequency:
  - Annual data: λ = 100
  - Quarterly data: λ = 1600 (only if you decide to use quarterly series; otherwise stay with annual and λ=100)
- Use the cyclical components for correlation.

6) Compute Pearson Correlation and Output
- Compute the Pearson correlation between the two cyclical series.
- Round to 5 decimals for final output when required (e.g., writing a single number to a file).

## Verification

Before finalizing the result, run these checks:
- Structure/Extraction
  - Print the last ~15 rows of each ERP table to confirm where quarterly rows begin.
  - Verify that annual detection excludes quarterly rows and footnotes.
  - Confirm the latest year’s annual value is the average of available quarters (and report how many quarters were used).
- Alignment
  - Print the intersecting Year range after joining both series (e.g., start and end Year, count of observations).
  - Ensure no NaNs after merging with CPI and before HP filtering.
- Deflation
  - Verify the deflation rule used (normalized CPI or explicit base-year scaling). Confirm that switching the base year does not change the correlation (only the level of real values).
- HP Filtering
  - Confirm input to HP filter is log(real) and λ matches data frequency.
  - Check that filtered series lengths match and contain no NaNs.
- Correlation
  - Cross-check using two methods (e.g., numpy.corrcoef and scipy.stats.pearsonr) to ensure consistency (sign and magnitude).
- Output
  - Ensure the final file contains exactly one number rounded to 5 decimals if specified by the task.

## Common Pitfalls

- Mixing annual and quarterly observations:
  - Including quarterly rows in the annual sample leads to misalignment and spurious NaNs. Strictly filter annual rows; compute the latest year’s annual value by averaging available quarters.
- Misaligned start rows across tables:
  - Different tables may introduce an extra blank/header row. Always align by Year keys after extraction rather than relying on row positions.
- Wrong column selection:
  - Confirm the "Total" column by inspecting header/label rows. Don’t assume Column 1 without checking.
- CPI mismatches:
  - Missing CPI years or using inconsistent base-year normalization. Normalize CPI correctly and verify complete coverage.
- Skipping the log transform:
  - HP filtering levels of aggregates can distort business-cycle signals. Apply logs to real values before filtering.
- Wrong HP λ:
  - Use λ = 100 for annual data (λ = 1600 for quarterly). Using the wrong λ biases cycle extraction.
- NaNs in filter input or output:
  - Any NaN in inputs yields NaNs in cycles and invalid correlation. Assert no NaNs before filtering, and re-check joins and parsing.
- Final-year handling:
  - Using a single quarter as the annual value or ignoring available quarters contradicts instructions. Average all available quarters.

## Success Criteria

- Annual series extracted for both variables, with the last year computed as the average of available quarters if annual total is missing.
- CPI-merged, real series computed with a documented base.
- Log transform and HP filter applied with λ aligned to data frequency.
- Pearson correlation computed on aligned cyclical series.
- Output formatted exactly as required (typically one number rounded to 5 decimals).

## Optional Script Usage

The included helper scripts provide reusable parsing and analysis utilities.

- Extract annual and quarterly values from mixed Excel tables:
  - Use scripts/mixed_excel_timeseries.py to parse annual rows and detect quarterly entries (Arabic Q1–Q4 or Roman numerals I–IV). Average available quarters to build the latest-year annual value.

Example (Python):
- from scripts.mixed_excel_timeseries import extract_annual_and_quarterly, build_annual_series
- df = pandas.read_excel(path_to_excel, header=None)
- annual, quarterly = extract_annual_and_quarterly(df, year_col=0, value_col=1)
- series = build_annual_series(annual, quarterly, fill_last_year_from_quarters=True)

- Compute HP-cycle correlation from a single CSV containing Year, X_nom, Y_nom, CPI:
  - Use scripts/hp_cycle_corr.py as a CLI to deflate, log, HP-filter, and correlate. Choose base year and λ.

CLI example:
- python scripts/hp_cycle_corr.py --input data.csv --year Year --x X_nom --y Y_nom --cpi CPI --base-year 2024 --lambda 100 --out answer.txt

These utilities are generic and can be adapted to other macro series requiring business-cycle correlation analysis.
