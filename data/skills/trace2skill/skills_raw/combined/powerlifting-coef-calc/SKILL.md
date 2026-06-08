---
name: powerlifting-coef-calc
description: "Calculate Dots coefficients for powerlifting competitions from lifter performance data in Excel files."
---

# Powerlifting Dots Coefficient Calculation

## When to Use

- Calculate Dots score coefficients for powerlifting
- Process International Powerlifting Federation competition data
- Work with multi-sheet Excel files

## Input Files

- `/root/data/openipf.xlsx`: Competition data
- `/root/data/data-readme.md`: Data format documentation

## Steps

0. Before editing, inspect the workbook directly: confirm sheet names, read the actual `Data` header row, use `/root/data/data-readme.md` to interpret field meanings, and map the real source columns for `Sex`, `BodyweightKg`, and the lift fields used to compute `TotalKg` rather than assuming fixed positions, letters, or names

1. Read the header row of "Data" and copy **all existing columns** to "Dots" in the **exact same order and with the same names**

   - Derive destination headers and source column positions programmatically from the workbook schema.
   - Use the observed `Data` headers to build formula references, but do **not** reduce the sheet to only calculation-related columns; preserve the full `Data` header row in the same order, then append new columns.
   - Before writing formulas, map formula inputs back to the copied headers: `Sex`, `BodyweightKg`, and the lift columns that make up `TotalKg`.
2. Preserve row order when copying data from "Data" to "Dots"
3. Add "TotalKg" column after the copied source columns using an Excel formula
4. Add "Dots" column using an Excel formula with **explicit 3-decimal precision**
5. Before finalizing the `Dots` formula, inspect representative `Sex` values in the source data and confirm the branch values actually used by the workbook.
6. When filling formulas down, make them blank-safe so rows with missing required inputs stay blank instead of showing errors or misleading numbers.
7. Use `openpyxl` to modify the existing workbook in place, then save, recalculate, reopen/read back the workbook, and inspect the `Dots` header row plus representative top/middle/bottom rows to confirm headers still match `Data` through the copied columns, formulas were stored and filled down consistently, and both `TotalKg` and `Dots` show 3-decimal results.

## Dots Formula

Dots uses both `TotalKg` and `BodyweightKg`.
- DO NOT use a log-based formula or any formula that depends only on `TotalKg`.
- Use sex-specific polynomial coefficients on `BodyweightKg`, then multiply by `TotalKg`:
  - Male denominator: `-307.75076 + 24.0900756*w - 0.1918759221*w^2 + 0.0007391293*w^3 - 0.000001093*w^4`
  - Female denominator: `-57.96288 + 13.6175032*w - 0.1126655495*w^2 + 0.0005158568*w^3 - 0.0000010706*w^4`
  - Score: `DOTS = 500 / denominator * TotalKg`
- Excel pattern: `=ROUND(IF(SexCell="M",500*TotalKgCell/(-307.75076+24.0900756*BodyweightCell-0.1918759221*BodyweightCell^2+0.0007391293*BodyweightCell^3-0.000001093*BodyweightCell^4),500*TotalKgCell/(-57.96288+13.6175032*BodyweightCell-0.1126655495*BodyweightCell^2+0.0005158568*BodyweightCell^3-0.0000010706*BodyweightCell^4)),3)`

- Build the Excel formula from the required inputs `Sex`, `BodyweightKg`, and `TotalKg`, and confirm the final written formula references those exact columns.
- Reject any candidate DOTS formula that is log-based, depends only on `TotalKg`, omits `BodyweightKg`, or changes the polynomial term order/signs even if Excel recalculates it successfully.
- Keep the bodyweight polynomial terms exactly as specified (`w`, `w^2`, `w^3`, `w^4` with the listed coefficients); if any coefficient or term order is uncertain, verify it against an authoritative specification or implementation before writing formulas.
- Before filling down, test one sample row manually to confirm the denominator and resulting score are plausible.
- If bodyweight clamping is explicitly required by the task or data rules, encode the clamp directly in the Excel formula with `MIN`/`MAX` rather than preprocessing values outside the sheet.

## Output

Modify "Dots" sheet in openipf.xlsx with:
- Original columns from Data
- New "TotalKg" column (formula)
- New "Dots" column (formula)
- 3 digit precision throughout

- Keep every source column from `Data` before the new columns; do not drop intervening columns or reorder headers
- `TotalKg` and `Dots` must be Excel formulas stored in the sheet, not hard-coded values
- Enforce 3-decimal results for `TotalKg` and `Dots` with `ROUND(...,3)` and/or cell number format `0.000`
- Determine formula inputs from the actual `Data` sheet schema before inserting formulas, but still copy all existing source columns to `Dots` in the original order.
- Do not report success until you have read back representative stored formula strings from the saved sheet and confirmed they are formulas, use the intended cells, preserve the required DOTS structure, and produce/evaluate to 3-decimal results.

## Tips

- openpyxl for Excel manipulation
- Prefer `openpyxl` for workbook inspection, in-place sheet editing, row copying, and formula insertion; use it as the default fallback if dataframe libraries are unavailable
- Before coding, check which spreadsheet libraries are installed; if needed packages are missing and system install is blocked, create a temporary/local virtual environment and install only the required spreadsheet tools there
- Read `/root/data/data-readme.md` first, then inspect the actual `Data` sheet headers and sample values so formulas reference the real source columns and the `Sex` branch matches the dataset's actual category values
- Use Excel formulas, not hard-coded values
- Match lifter names exactly
- Verify formula syntax for Excel
- When reference pages are incomplete or hide the math, prefer authoritative raw source/spec files over calculator frontends

- Derive destination headers programmatically from the `Data` sheet header row; do not hand-pick a subset of columns unless the task explicitly says to
- Use explicit formulas such as `=ROUND(<sum formula>,3)` and `=ROUND(<dots formula>,3)` instead of raw unrounded coefficients/results
- If you identified a column as required for the calculation, confirm the final Excel formula actually references that column
- Treat successful recalculation as a syntax check only; also verify the formula structure matches the intended DOTS method
- DO NOT stop after verifying one truncated formula string; inspect the complete formula text and sample multiple rows
- Check that formulas reference the intended bodyweight/sex/total cells and that the same pattern is filled down the sheet
- Validate after writing: confirm `Dots` headers match `Data` headers exactly up to the appended columns, and inspect representative rows to verify formulas are populated and results show 3-decimal precision
- If the task requires an exact final completion token or output format, output exactly that string and nothing else

- Use schema/dependency inspection to find required input columns, but still copy **all** `Data` columns to `Dots` unless the task explicitly says otherwise
- Treat successful recalculation as a syntax check only; also verify the workbook artifact directly by reopening once normally and once with computed values when possible
- Read back complete stored formulas, not truncated previews, for representative `TotalKg` and `Dots` cells in multiple rows
- Confirm the filled-down formulas keep the same relative-reference pattern across sampled rows and still reference the intended `Sex`, `BodyweightKg`, lift, and `TotalKg` cells
- After writing the workbook, read back the `Dots` header row itself and confirm it matches `Data` exactly through the last copied source column, with only `TotalKg` and `Dots` appended afterward
- Compare at least one sampled `TotalKg` and `Dots` result against an independent/manual calculation to catch coefficient or reference mistakes that still recalculate cleanly
- Use scripts only to edit the workbook; treat the saved Excel workbook formulas as the required deliverable, not just the script logic
- If the task requires a specific tool invocation format, use that exact schema throughout; if it requires an exact final completion token or output format, output exactly that string and nothing else
