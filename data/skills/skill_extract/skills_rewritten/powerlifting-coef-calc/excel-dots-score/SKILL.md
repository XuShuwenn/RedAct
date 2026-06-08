---
name: excel-dots-score
description: "Build a Dots scoring sheet from a source data sheet by copying required columns, adding TotalKg and Dots formulas, and validating 3-decimal precision."
---

# Excel Dots Score Sheet Construction

This skill guides you to construct a spreadsheet sheet that computes Dots scores from a source data sheet. It covers identifying required inputs, copying columns while preserving header names and order, adding TotalKg and Dots columns with robust formulas, and verifying correctness and precision.

## When to Use

Use this skill when you need to:
- Create a new sheet that computes Dots scores from an existing dataset
- Preserve original column names and order in the destination
- Add Excel formulas that sum lifts and compute Dots with sex-conditional logic
- Ensure results are rounded to exactly 3 decimals and formulas are recalculated

## Core Workflow

1. Inspect inputs and structure
   - Read the dataset README or data dictionary for column definitions.
   - Open the workbook and inspect the source sheet (e.g., "Data") headers and sample rows.
   - Confirm that lift amounts are in kilograms and that there is a sex field and a bodyweight field.

2. Identify and copy required columns
   - Required to compute Dots:
     - Name (or equivalent identifier for the lifter)
     - Sex (text; typically "M"/"F" or full words; case may vary)
     - BodyweightKg
     - Best3SquatKg
     - Best3BenchKg
     - Best3DeadliftKg
   - Create/clear the destination sheet (e.g., "Dots").
   - Copy only the needed columns from the source, preserving the exact header names and the relative order they appear in the source sheet (do not rename headers).

3. Append TotalKg column after the copied columns
   - Add a header "TotalKg" immediately after the copied fields.
   - Insert a rounded Excel formula for each data row using the three lift columns by header reference:
     - Example pattern: =ROUND({Best3SquatKg}+{Best3BenchKg}+{Best3DeadliftKg}, 3)
   - Implement formulas by resolving header names to cell references per row; do not hardcode column letters.

4. Append Dots column after TotalKg
   - Add a header "Dots".
   - Compute Dots with sex-conditional formulas using the correct polynomial for bodyweight:
     - General shape: Dots = ROUND(TotalKg * 500 / denom, 3)
     - denom is sex-specific and depends on ln(bodyweight) terms. Implement as:
       - =ROUND({TotalKg}*500/IF(LEFT(UPPER({Sex}),1)="M", male_denom_expr, IF(LEFT(UPPER({Sex}),1)="F", female_denom_expr, 0)), 3)
     - Where male_denom_expr and female_denom_expr are the official Dots denominators expressed in Excel syntax using:
       - BWc = MIN(MAX({BodyweightKg}, lower_bound), upper_bound)
       - Natural log: LN(BWc)
       - Polynomial terms in LN(BWc) with the correct coefficient ordering for each sex.
   - Rounding must be applied via ROUND(..., 3) in the formula itself (not just number formatting).

5. Recalculate and save
   - Recalculate formulas using a compatible calculation engine (e.g., open the file in Excel/LibreOffice with automatic recalculation, or use a provided recalc tool in your environment).
   - Save the workbook.

## Verification

Perform these checks before finalizing:
- Headers and order
  - The destination sheet contains exactly the required copied headers in the same order and with the same names as the source.
  - "TotalKg" is immediately after the copied fields; "Dots" is immediately after "TotalKg".
- Formula semantics
  - TotalKg cells contain ROUND(SUM of the three lift cells, 3).
  - Dots cells contain a single ROUND(..., 3) wrapping the full computation.
  - Dots formula selects male/female polynomials by inspecting the first letter of uppercased Sex ("M"/"F").
  - Bodyweight in the denominator is clamped to the official lower and upper limits using MIN/MAX.
- Recalculation and values
  - After recalculation, non-empty lift rows produce non-zero Dots values within expected ranges for the given bodyweight and totals.
  - Spot-check two rows: manually compute TotalKg and confirm that TotalKg equals the sum of the three lift cells; confirm Dots shows 3-decimal rounding.
- Error scan
  - Ensure there are no #NAME!, #VALUE!, or #DIV/0! errors in the Dots column.

Success criteria:
- Destination sheet contains required inputs, TotalKg, and Dots columns in the specified order.
- All formula cells compute without errors and are rounded to 3 decimals.
- Dots values vary plausibly with bodyweight and total (not constant or all zeros) and update if inputs change.

## Common Pitfalls

- Wrong polynomial ordering or constants
  - Mixing coefficient order or applying the wrong sex’s coefficients yields incorrect or zero scores. Always verify the exact coefficient ordering and source.
- Missing bodyweight clamping
  - Omitting MIN/MAX clamping can cause unrealistic or invalid denominators. Clamp to the official bounds before applying LN.
- Display formatting vs rounding
  - Setting number format to 3 decimals without using ROUND(...,3) changes display, not computation. The formula must include ROUND.
- Case sensitivity and category variants
  - Sex values can be "M", "F", or full words in various cases. Use UPPER() and LEFT() to normalize before comparison.
- Hardcoding column letters
  - Formulas that reference fixed column letters will break if column positions differ. Always resolve by header name per row.
- Stale formulas
  - Failing to recalculate leaves zeros or outdated values. Recalculate before validating and delivering the file.
- Missing or non-numeric inputs
  - If any lift cells are blank or non-numeric, SUM may error. Decide on policy (treat blank as 0 or ensure data is cleaned) and verify for errors.

## Optional Script Usage

Use the helper script to automate copying columns by header and adding row-wise formulas that reference headers, not column letters.

Example usage:
- Prepare a Dots denominator expression for each sex using the official constants and the clamped bodyweight. In Excel syntax, define male_denom_expr and female_denom_expr using LN(MIN(MAX({BodyweightKg}, LBOUND), UBOUND)) and the correct polynomial terms.
- Build the Dots formula as a single string with placeholders for headers, e.g.:
  - Dots formula:
    - ROUND({TotalKg}*500/IF(LEFT(UPPER({Sex}),1)="M", <male_denom_expr>, IF(LEFT(UPPER({Sex}),1)="F", <female_denom_expr>, 0)), 3)
- Run the script:
  - python3 scripts/sheet_builder.py \
    --workbook /path/to/workbook.xlsx \
    --source-sheet Data \
    --target-sheet Dots \
    --columns Name Sex BodyweightKg Best3SquatKg Best3BenchKg Best3DeadliftKg \
    --total-name TotalKg \
    --total-formula "ROUND({Best3SquatKg}+{Best3BenchKg}+{Best3DeadliftKg}, 3)" \
    --dots-name Dots \
    --dots-formula "ROUND({TotalKg}*500/IF(LEFT(UPPER({Sex}),1)=\"M\", <male_denom_expr>, IF(LEFT(UPPER({Sex}),1)=\"F\", <female_denom_expr>, 0)), 3)"

Notes:
- Replace <male_denom_expr> and <female_denom_expr> with the official expressions using {BodyweightKg} placeholder.
- After writing formulas, open the workbook in Excel/LibreOffice or run a compatible recalculation tool to compute results.
