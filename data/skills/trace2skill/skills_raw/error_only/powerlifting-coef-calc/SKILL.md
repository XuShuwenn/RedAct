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

1. Read the header row of "Data" and copy **all existing columns** to "Dots" in the **exact same order and with the same names**
2. Preserve row order when copying data from "Data" to "Dots"
3. Add "TotalKg" column after the copied source columns using an Excel formula
4. Add "Dots" column using an Excel formula with **explicit 3-decimal precision**

## Dots Formula

Dots uses both `TotalKg` and `BodyweightKg`.
- DO NOT use a log-based formula or any formula that depends only on `TotalKg`.
- Use sex-specific polynomial coefficients on `BodyweightKg`, then multiply by `TotalKg`:
  - Male denominator: `-307.75076 + 24.0900756*w - 0.1918759221*w^2 + 0.0007391293*w^3 - 0.000001093*w^4`
  - Female denominator: `-57.96288 + 13.6175032*w - 0.1126655495*w^2 + 0.0005158568*w^3 - 0.0000010706*w^4`
  - Score: `DOTS = 500 / denominator * TotalKg`
- Excel pattern: `=ROUND(IF(SexCell="M",500*TotalKgCell/(-307.75076+24.0900756*BodyweightCell-0.1918759221*BodyweightCell^2+0.0007391293*BodyweightCell^3-0.000001093*BodyweightCell^4),500*TotalKgCell/(-57.96288+13.6175032*BodyweightCell-0.1126655495*BodyweightCell^2+0.0005158568*BodyweightCell^3-0.0000010706*BodyweightCell^4)),3)`

## Output

Modify "Dots" sheet in openipf.xlsx with:
- Original columns from Data
- New "TotalKg" column (formula)
- New "Dots" column (formula)
- 3 digit precision throughout

- Keep every source column from `Data` before the new columns; do not drop intervening columns or reorder headers
- `TotalKg` and `Dots` must be Excel formulas stored in the sheet, not hard-coded values
- Enforce 3-decimal results for `TotalKg` and `Dots` with `ROUND(...,3)` and/or cell number format `0.000`

## Tips

- openpyxl for Excel manipulation
- Use Excel formulas, not hard-coded values
- Match lifter names exactly
- Verify formula syntax for Excel

- Derive destination headers programmatically from the `Data` sheet header row; do not hand-pick a subset of columns unless the task explicitly says to
- Use explicit formulas such as `=ROUND(<sum formula>,3)` and `=ROUND(<dots formula>,3)` instead of raw unrounded coefficients/results
- If you identified a column as required for the calculation, confirm the final Excel formula actually references that column
- Treat successful recalculation as a syntax check only; also verify the formula structure matches the intended DOTS method
- DO NOT stop after verifying one truncated formula string; inspect the complete formula text and sample multiple rows
- Check that formulas reference the intended bodyweight/sex/total cells and that the same pattern is filled down the sheet
- Validate after writing: confirm `Dots` headers match `Data` headers exactly up to the appended columns, and inspect representative rows to verify formulas are populated and results show 3-decimal precision
- If the task requires an exact final completion token or output format, output exactly that string and nothing else
