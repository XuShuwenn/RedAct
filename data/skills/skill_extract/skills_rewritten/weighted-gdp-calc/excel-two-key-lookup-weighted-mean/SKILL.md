---
name: excel-two-key-lookup-weighted-mean
description: "Populate spreadsheets with two-key lookups (row key + year), compute percentage metrics, summary stats, and a SUMPRODUCT-weighted mean without altering workbook formatting."
---

# Two-Key Lookup and Weighted Mean in Spreadsheets

Use this skill when you need to fill target ranges from a source table using two conditions (e.g., a series identifier and a year), then compute derived percentages, summary statistics, and a SUMPRODUCT-weighted mean — all within existing sheets and without changing formatting.

## When to Use

Activate this skill for tasks that require:
- Filling a rectangular output block from a source sheet by matching a row identifier (e.g., code/name) and a column header (e.g., year)
- Calculating ratios such as net exports as a percentage of GDP
- Producing per-year summary statistics (min, max, median, mean, percentiles)
- Computing a group weighted mean using SUMPRODUCT with appropriate weights (e.g., GDP)
- Preserving workbook structure and formatting (no new sheets, macros, or style changes)

## Core Workflow

1) Map Inputs and Ranges
- Identify in the target sheet:
  - Row key cells (e.g., series code or country) and their range
  - Year header cells (typically one row spanning multiple year columns)
  - Yellow or highlighted blocks to populate
- Identify in the source sheet:
  - A single column that uniquely identifies each row (row key column)
  - A single row that contains year headers (the header row)
  - The contiguous data block containing the values to retrieve
- Confirm orientation and types:
  - Ensure the row keys are identical between sheets (same spelling, no extra spaces)
  - Ensure the year labels match in type (text vs number). Normalize if needed using VALUE(year_cell) or TEXT(year_cell, "0").

2) Build a Two-Key Lookup Formula
- Preferred (broad compatibility): INDEX + MATCH + MATCH
  - Template:
    =INDEX(SourceSheet!$DataBlock,
           MATCH(RowKeyCell, SourceSheet!$RowKeyColumn, 0),
           MATCH(YearHeaderCell, SourceSheet!$HeaderRow, 0))
  - Use exact matches (0), and anchor ranges with $ so they remain stable when filled.
  - Lock references thoughtfully:
    - RowKeyCell: lock row if copying down, lock column if copying across
    - YearHeaderCell: lock column if copying across, lock row if copying down
    - DataBlock, RowKeyColumn, HeaderRow: fully anchored with $.
- Alternatives (only if supported in the environment):
  - XLOOKUP + MATCH: =XLOOKUP(RowKeyCell, Source!$RowKeyColumn, INDEX(Source!$DataBlock,0, MATCH(YearHeaderCell, Source!$HeaderRow,0)))
  - VLOOKUP/HLOOKUP with MATCH for the column/row index (requires exact match)
- Test the formula in a single cell first, recalculate, and verify it returns the expected value from the source sheet. Then fill across/down the target range.
- Optionally wrap with IFERROR to keep templates clean of #N/A during build-out:
  =IFERROR(<lookup_formula>, "")

3) Compute Derived Percentage (e.g., Net Exports as % of GDP)
- Typical structure:
  =IFERROR((ExportsCell - ImportsCell) / GDPCell, "")
- Apply percent formatting if needed. Ensure the numerator and denominator are in the same currency/units.
- When filling across, lock row/column references appropriately so each row uses its own exports/imports/GDP but slides across years correctly.

4) Summary Statistics Per Year
- Per year (i.e., per column) across the group of rows:
  - Min: =MIN(YearColumnRange)
  - Max: =MAX(YearColumnRange)
  - Median: =MEDIAN(YearColumnRange)
  - Simple mean: =AVERAGE(YearColumnRange)
  - 25th percentile and 75th percentile (pick what your engine supports):
    - Excel modern: =PERCENTILE.INC(YearColumnRange, 0.25) and =PERCENTILE.INC(YearColumnRange, 0.75)
    - Excel alt: =PERCENTILE.EXC(..., 0.25/0.75) if required by spec
    - LibreOffice/older Excel: =PERCENTILE(YearColumnRange, 0.25/0.75)
- Keep the percentile method consistent and documented.

5) Weighted Mean via SUMPRODUCT
- Use the physical weights (e.g., GDP levels), not percentage shares unless explicitly required:
  =IFERROR(SUMPRODUCT(PercentRange, WeightRange) / SUM(WeightRange), "")
- Notes:
  - If PercentRange contains percent-formatted values, they are already fractions internally (e.g., 12% = 0.12). Do not divide by 100 again.
  - Ensure the PercentRange and WeightRange align row-for-row and year-for-year.
  - Exclude blanks or errors via IFERROR in the numerator terms if needed.

6) Non-Destructive Editing
- Do not add sheets, styles, or macros/VBA.
- Keep all formulas within the existing sheets and ranges.
- Quote sheet names that contain spaces or special characters (e.g., 'Data Sheet'!).
- After filling, recalculate and spot-check before finalizing.

## Verification

Perform these checks before delivering:
- Lookup accuracy:
  - Pick one row key and one year; manually confirm the result equals the source table value.
  - Ensure there are no #N/A for years that exist in the source; if present, investigate type or whitespace mismatches.
- Anchor correctness:
  - Spot-check a few cells in the first and last columns of the filled block to ensure references are still pointing to the intended row/column.
- Percentage sanity:
  - Confirm denominators are nonzero; no #DIV/0! should remain.
  - Spot-check one country-year using a hand calculation.
- Summary stats:
  - Confirm Min ≤ Median ≤ Max for each year.
  - Ensure 25th percentile ≤ Median ≤ 75th percentile.
- Weighted mean sanity:
  - Weighted mean should lie between Min and Max for that year (if weights are nonnegative).
  - Confirm SUM(WeightRange) > 0 for each year.
- Compatibility:
  - If the environment doesn’t support certain functions (e.g., XLOOKUP, PERCENTILE.INC), use the compatible alternative.
- Structure/formatting:
  - Confirm no changes to colors, fonts, merged cells, or added sheets.

## Common Pitfalls and Fixes

- Mismatched year types (text vs number)
  - Symptom: MATCH returns #N/A despite visible match
  - Fix: Use VALUE(YearHeaderCell) or TEXT(...) consistently on both sides, or align types in the source/target once.

- Trailing/leading spaces in keys
  - Symptom: Row key match fails
  - Fix: Use TRIM around key cells in MATCH, or clean source/target keys once.

- Wrong header row or key column
  - Symptom: Returned values are blank/incorrect
  - Fix: Re-verify the actual year header row and row key column; adjust MATCH references.

- Missing exact match flag
  - Symptom: VLOOKUP/HLOOKUP returns wrong row/column
  - Fix: Always use exact match (0 or FALSE) for lookups.

- Incorrect anchoring ($)
  - Symptom: Formulas work in the first cell but shift to wrong ranges when filled
  - Fix: Lock DataBlock, RowKeyColumn, and HeaderRow fully; lock key/label cells in the appropriate dimension only.

- Unsupported functions/formula separators
  - Symptom: #NAME? or parsing errors
  - Fix: Switch to INDEX+MATCH for compatibility; match the locale-specific argument separator if necessary.

- Weighted mean scaling errors
  - Symptom: Weighted mean too small/large by factor 100
  - Fix: If PercentRange is percent-formatted, do not divide by 100 again. If they’re text like "12%", convert with VALUE() first.

- Division by zero in percentages
  - Symptom: #DIV/0!
  - Fix: Wrap with IFERROR or IF(denominator=0, "", numerator/denominator).

## Optional Script Usage

Use the helper script to generate robust formula templates tailored to your sheet and range names. This helps avoid anchoring and reference mistakes when assembling INDEX+MATCH and SUMPRODUCT formulas.

Examples:
- Two-key lookup (INDEX+MATCH+MATCH):
  scripts/formula_templates.py --type two_key \
    --data-sheet Data --data-range A1:Z100 \
    --rowkey-col A:A --header-row 1:1 \
    --rowkey-ref $A$12 --year-ref $H$10

- Net exports % of GDP:
  scripts/formula_templates.py --type net_exports \
    --exports-ref H12 --imports-ref H19 --gdp-ref H26

- Weighted mean via SUMPRODUCT:
  scripts/formula_templates.py --type weighted_mean \
    --values-range H35:H40 --weights-range H26:H31

These templates are generic; paste and adapt them to your workbook’s exact ranges, then fill across and down with correct anchoring.
