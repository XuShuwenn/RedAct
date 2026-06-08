---
name: pdf-xlsx-pivot-report
description: "Build an Excel report with a SourceData sheet and pivot tables by extracting tabular data from PDFs, merging with spreadsheets, and computing quartiles and totals."
---

# PDF → Excel Pivot Report

Create data-driven Excel reports by extracting rows from tabular PDFs, merging with spreadsheet data, enriching with derived columns (income quartiles and totals), and defining pivot tables that populate on refresh in Excel.

## When to Use

Use this skill when:
- You must combine a tabular PDF (e.g., regions and population by state) with an Excel/CSV dataset (e.g., incomes per region).
- You need a unified SourceData sheet plus multiple pivot tables (e.g., totals by state, counts by region, cross-tabs by quartile).
- The PDF has repeated headers or truncated column names that require normalization.

## Core Workflow

1. Inspect inputs and plan joins
   - Identify the join key (e.g., SA2_CODE). Decide a canonical type for the key across sources. Prefer strings for codes to preserve leading zeros.
   - List required output columns for SourceData (example set you can adapt):
     - SA2_CODE, SA2_NAME, STATE, POPULATION_2023
     - EARNERS, MEDIAN_INCOME, MEAN_INCOME
     - Quarter (Q1–Q4), Total (EARNERS × MEDIAN_INCOME)

2. Extract population-like tables from PDF
   - Iterate all pages with a table extractor (e.g., pdfplumber.extract_tables()).
   - Detect header vs continuation rows:
     - If the first row contains known header tokens (e.g., SA2_CODE, STATE, POPULATION), treat it as a header and skip it for data.
     - Otherwise, treat all rows as data for that table.
   - Normalize header names:
     - Trim whitespace.
     - Unify column names; if the population column is truncated (e.g., "POPULATION_20"), rename to the intended name (e.g., "POPULATION_2023").
   - Clean cell values:
     - Strip whitespace.
     - For numeric fields with thousands separators, remove commas before conversion.
     - Convert to the chosen numeric types using to_numeric(..., errors="coerce").

3. Read spreadsheet data and standardize types
   - Load the Excel file with pandas.
   - Ensure join keys align with the PDF extraction (e.g., cast both to string or both to numeric consistently).
   - Clean numeric columns that may be stored as text or contain commas.
   - Retain only the needed columns for the merge (e.g., EARNERS, MEDIAN_INCOME, MEAN_INCOME, SA2_CODE, SA2_NAME if applicable).

4. Merge datasets
   - Perform a merge on the agreed key (typically SA2_CODE). Use inner joins for matched analysis or left joins when you must preserve one side.
   - If duplicate columns arise (e.g., STATE_x/STATE_y), pick the source-of-truth column and drop the duplicate.
   - Drop rows missing critical numeric fields only if necessary for downstream computations.

5. Enrich data
   - Compute income quartiles across all regions using the MEDIAN_INCOME distribution:
     - Compute cut points with Series.quantile([0.25, 0.5, 0.75]).
     - Assign labels: Q1 ≤ Q1_cutoff, Q2 ≤ median, Q3 ≤ Q3_cutoff, Q4 > Q3_cutoff.
     - If a quantile-based method raises duplicate-edge errors, fall back to pd.cut with de-duplicated edges.
     - Ensure the Quarter column is string-typed with values only in {"Q1","Q2","Q3","Q4"} or empty for missing income.
   - Compute Total = EARNERS × MEDIAN_INCOME. Leave blank or NaN if either operand is missing.

6. Build the Excel report
   - Create a new workbook and add the "SourceData" sheet first.
   - Write a header row and all source data rows with the intended column order.
   - Define four pivot tables that reference SourceData (Excel will populate values on refresh/open):
     - Population by State: Rows = STATE; Values = Sum of POPULATION_2023
     - Earners by State: Rows = STATE; Values = Sum of EARNERS
     - Regions by State: Rows = STATE; Values = Count of SA2_CODE
     - State Income Quartile: Rows = STATE; Columns = Quarter (Q1–Q4); Values = Sum of EARNERS
   - Use a pivot cache definition referencing the full SourceData range (from A1 to the bottom-right cell).
   - Save the workbook.

7. Communicate refresh behavior
   - Note: openpyxl writes pivot definitions but does not calculate them. Users must open the file in Excel/compatible software and use Refresh All to populate values.

## Verification

Before delivering:
- Structure checks:
  - Confirm the workbook exists and contains exactly the expected sheet names, including SourceData.
  - Verify SourceData header order and presence of required columns.
  - Confirm each pivot sheet has one pivot definition.
- Data checks:
  - Validate that numeric columns (e.g., EARNERS, MEDIAN_INCOME, POPULATION_2023) are numeric and not strings.
  - Ensure the join key’s type matches across inputs and has reasonable non-null coverage post-merge.
  - Confirm Quarter values are within {Q1, Q2, Q3, Q4} (and optionally empty for missing incomes) and dtype is string.
  - Sanity-check sample totals: Total should equal EARNERS × MEDIAN_INCOME where both exist.
- Pivot wiring checks:
  - The pivot cache range must cover the entire SourceData including header.
  - Row fields and data fields point to the correct column indices based on the written SourceData order.
  - Regions-by-state pivot counts a stable field (e.g., SA2_CODE) rather than a numeric that could be missing.

## Common Pitfalls

- Merging on the wrong key or with mismatched types:
  - Symptom: Few or no matches. Fix by casting both join keys to the same type (prefer strings for codes to preserve leading zeros).
- Truncated or inconsistent column names from PDF extraction:
  - Symptom: Missing population values post-merge. Normalize and rename headers (e.g., map "POPULATION_20" → "POPULATION_2023").
- Unclean numeric fields (commas or object dtype):
  - Symptom: NaNs after conversion or arithmetic errors. Strip commas and coerce with errors="coerce" before calculations.
- Quartile assignment errors (duplicate bin edges):
  - Symptom: pd.qcut ValueError. Fall back to quantile cut points with pd.cut and duplicates="drop", or use a robust helper.
- Pivot definitions misaligned with SourceData columns:
  - Symptom: Pivot shows wrong fields after refresh. Build pivotFields in the same order as SourceData columns and map indices by name.
- Expecting pivots to calculate in openpyxl:
  - Symptom: Blank pivot values in the saved file. Inform users to open and refresh in Excel/Calc.
- Writing pivot sheets before SourceData or pointing cache to the wrong range:
  - Symptom: Broken pivot references. Always create SourceData first and reference the full A1:... range.

## Optional Script Usage

The helper script `scripts/pivot_tools.py` provides two reusable utilities:
- assign_quartiles(series): Robustly assigns Q1–Q4 labels to a numeric series.
- write_source_and_default_pivots(df, output_path): Writes SourceData and the four standard pivot tables, given a DataFrame containing the required columns.

Example (Python):

- Prepare a pandas DataFrame `df` with columns:
  ["SA2_CODE","SA2_NAME","STATE","POPULATION_2023","EARNERS","MEDIAN_INCOME","MEAN_INCOME","Quarter","Total"].
- Then:

```
from scripts.pivot_tools import assign_quartiles, write_source_and_default_pivots

# df["Quarter"] = assign_quartiles(df["MEDIAN_INCOME"])  # if not already assigned
write_source_and_default_pivots(df, "demographic_analysis.xlsx")
```

Success criteria:
- The file contains 5 sheets: 1 SourceData + 4 pivot sheets.
- Pivot definitions reference the full SourceData range and correct fields.
- Data types are appropriate and derived columns are present.
- On Excel refresh, pivots show aggregated values per design.
