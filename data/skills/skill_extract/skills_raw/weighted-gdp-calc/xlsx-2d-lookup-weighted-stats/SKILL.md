---
name: xlsx-2d-lookup-weighted-stats
description: "Populate Excel blocks via two-key (row+column) lookups and compute ratios, summary stats, and GDP-weighted means without altering formatting."
---

# Excel 2D Lookup + Weighted Stats

Reusable workflow for spreadsheet tasks that require:
- Filling blocks in a Task sheet by looking up values in a Data sheet with two keys: a row key (e.g., series code) and a column key (e.g., year)
- Computing derived ratios (e.g., (exports − imports)/GDP × 100)
- Calculating per-year summary statistics (min, max, median, mean, 25th and 75th percentiles)
- Calculating a weighted mean using SUMPRODUCT (e.g., weighting by GDP)

This skill emphasizes formula-driven solutions (INDEX/MATCH or XLOOKUP/MATCH) and strict preservation of workbook formatting.

## When to Use
- You must fill colored cell blocks from a source sheet using two conditions (row key and column key)
- You need to compute cross-country/year metrics like net exports % of GDP
- You must generate per-year summary statistics and a weighted mean using built-in spreadsheet functions
- You must not add VBA/macros or modify the file’s formatting

## Core Workflow

1) Inspect the Workbook Structure
- Identify the Task (destination) and Data (source) sheets.
- Locate the two lookup keys:
  - Row key: typically a series code in a Task sheet column (e.g., column D)
  - Column key: years in a Task sheet header row (often near the top, e.g., a row labeled with years)
- In the Data sheet, identify:
  - Row key range (e.g., series codes column)
  - Column key range (e.g., year headers row)
  - Value matrix range (e.g., a rectangular block for all years and series)

2) Fill Blocks with Two-Key INDEX/MATCH
- Use absolute references for source ranges and mixed references for Task keys so formulas can fill across/down.
- Recommended pattern for high compatibility:
  =INDEX(SourceSheet!$VALS_TOP_LEFT:$VALS_BOTTOM_RIGHT,
         MATCH($RowKeyCell, SourceSheet!$ROWKEY_COL_TOP:$ROWKEY_COL_BOTTOM, 0),
         MATCH(ColKeyCell, SourceSheet!$COLKEY_ROW_LEFT:$COLKEY_ROW_RIGHT, 0))
- Quote sheet names with spaces: 'Source Sheet'!
- Use $ to lock source ranges and row/column positions where needed (e.g., $D for series code column; $HeaderRow for years).

3) Compute Derived Ratios
- Example pattern (net exports % of GDP):
  =((ExportsCell − ImportsCell) / GDPCell) × 100
- Confirm number formatting expectations:
  - If cells are formatted as percentage (e.g., 0.0%), you may not multiply by 100.
  - If cells show numeric percent with one decimal (e.g., 10.5), multiply by 100.

4) Add Summary Statistics per Year
- For each year column, across the country rows:
  - Min: =MIN(YearColStart:YearColEnd)
  - Max: =MAX(YearColStart:YearColEnd)
  - Median: =MEDIAN(YearColStart:YearColEnd)
  - Mean: =AVERAGE(YearColStart:YearColEnd)
  - 25th percentile: =PERCENTILE(YearColStart:YearColEnd, 0.25)
  - 75th percentile: =PERCENTILE(YearColStart:YearColEnd, 0.75)
- Prefer PERCENTILE over PERCENTILE.INC for better cross-engine compatibility.

5) Compute Weighted Mean (e.g., GDP-weighted)
- For each year column:
  =SUMPRODUCT(NetExportsPctRange, GDPRng) / SUM(GDPRng)
- Ensure both ranges align by row (same countries in the same order).

6) Recalculate and Validate
- Recalculate formulas using a compatible engine (Excel/Calc/headless recalc script) if available in your environment.
- Validate:
  - No #NAME? (function or sheet reference issue)
  - No #N/A in lookup blocks (key mismatches)
  - No #DIV/0! in ratios (check GDP or denominator zeros)
  - Weighted mean cells return numeric values
- Spot-check a few lookups by matching a known series/year from the Data sheet.

## Verification Checklist
- Two-key lookups return numbers across all requested years
- Derived ratio cells are populated and correctly scaled for the format
- Stats rows compute without errors for each year
- Weighted mean cells compute without errors for each year
- Original fills/colors/fonts remain unchanged

## Common Pitfalls and How to Avoid Them
- Wrong header row for years
  - Symptom: MATCH returns #N/A across a year column
  - Fix: Inspect Task sheet header rows visually and programmatically; reference the row that actually contains year values
- Incomplete source column range
  - Symptom: Last year column returns #N/A
  - Fix: Extend source value and header ranges to include the latest available year
- Sheet name case and quoting
  - Symptom: #NAME? or broken references
  - Fix: Use exact sheet name with correct case and include exclamation point; quote names with spaces: 'Data Sheet'!
- Unsupported functions in some engines
  - Symptom: #NAME? on percentile functions
  - Fix: Use PERCENTILE rather than PERCENTILE.INC for broader compatibility
- Percent scaling mismatch
  - Symptom: Values appear 100× too small or large
  - Fix: Check cell number format; multiply by 100 only if cells are not percentage-formatted
- Formatting changes
  - Symptom: Style deviations (colors, fonts) after editing
  - Fix: Only set cell .value to formulas; do not alter styles, widths, or formats

## Optional Script Usage
Use the provided helper to generate robust 2D INDEX/MATCH formulas and common aggregations without altering formatting. It accepts generic ranges and produces formulas with correct absolute/mixed references.

Example (pseudocode steps):
- Configure:
  - Destination block (top-left/bottom-right)
  - Task row key column letter (e.g., D)
  - Task column key row index (e.g., 9)
  - Data sheet name and ranges (row-key column range, column-key header range, values range)
- Run the tool to fill the block, then add ratio, stats, and weighted-mean formulas using its helpers.

See scripts/xlsx_2d_tools.py for reusable functions.
