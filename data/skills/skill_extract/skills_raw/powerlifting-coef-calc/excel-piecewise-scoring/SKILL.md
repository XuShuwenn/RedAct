---
name: excel-piecewise-scoring
description: "Build spreadsheet score columns from piecewise polynomial formulas with clamping, by copying required source columns, inserting formulas, rounding to 3 decimals, and verifying results."
---

# Spreadsheet Piecewise Polynomial Scoring

A reusable workflow for spreadsheet tasks that require:
- selecting and copying specific columns from a source sheet to a target sheet while preserving header names and order
- adding a total/aggregate column via formula
- adding a score column defined by a piecewise (group-dependent) polynomial with input clamping
- rounding computed values to 3 decimal places
- recalculating and independently verifying results

This pattern applies to powerlifting Dots-like coefficients and other sports/benchmarks that use group-specific polynomial scoring functions based on attributes such as sex, class, or division.

## When to Use
Activate this skill when you need to:
- compute a score from existing columns using a polynomial in one variable (e.g., bodyweight), multiplied by a total, with different coefficients per group (e.g., male/female)
- add formulas to a new sheet while preserving the exact header names and order from a source sheet
- clamp an input variable (e.g., bodyweight) to a given interval before applying the polynomial
- ensure all outputs are rounded to 3 decimal places and verified

## Core Workflow

1) Understand the official formula
- Identify the required inputs and the exact mathematical form. Typical Dots-like scoring:
  score = Total × scale / P(clamped_input)
  where P(x) = a4·x^4 + b3·x^3 + c2·x^2 + d1·x + e0
- Identify groups (e.g., male/female) and their coefficient sets and clamping ranges.
- Record authoritative sources for coefficients and clamp bounds (do not guess).

2) Inspect the source sheet
- Load the workbook and list the headers of the source sheet’s first row.
- Determine the exact header names and their left-to-right order. Do not rename headers.
- Identify the minimal set of required columns, for example:
  - Identifier (e.g., Name)
  - Group selector (e.g., Sex)
  - Variable for polynomial input (e.g., BodyweightKg)
  - Components that sum to Total (e.g., Best3SquatKg, Best3BenchKg, Best3DeadliftKg)

3) Create and populate the target sheet
- Create or clear the target sheet.
- Copy only the required columns from the source sheet, preserving the original header names and the exact left-to-right order they appear in the source sheet.
- Append a new column TotalKg immediately after the copied columns.
  - Use an Excel formula to compute the total, e.g., =ROUND(D{row}+E{row}+F{row}, 3)
  - Put rounding inside the formula to enforce 3-decimal computation precision (formats affect display only).
- Append a new column Score (e.g., Dots) immediately after TotalKg.
  - Build a piecewise formula using IF/IFS on the group column to select coefficients and clamp bounds.
  - Construct clamped_input = MIN(MAX(bw_ref, lower), upper)
  - Build the polynomial P(clamped_input) using the proper coefficient order and powers.
  - Final cell formula example shape (placeholders shown):
    =IF(OR(Sex="G1", Sex="Alt1"), ROUND(Total*scale/(a4_m*(BWc)^4 + b3_m*(BWc)^3 + c2_m*(BWc)^2 + d1_m*(BWc) + e0_m), 3), ROUND(Total*scale/(a4_f*(BWc)^4 + b3_f*(BWc)^3 + c2_f*(BWc)^2 + d1_f*(BWc) + e0_f), 3))
    where BWc is the clamped bodyweight expression and constants are filled from the official spec.

4) Recalculate formulas
- Use a headless recalculation tool (e.g., LibreOffice-based script) to evaluate formulas so cached values are up to date.
- Note that openpyxl does not compute formulas; it only reads/writes them. Recalculate before reading values with data_only.

5) Verify results independently
- Compute 2–3 sample rows independently (Python or calculator) using the same polynomial, clamps, and coefficients.
- Compare the independently computed scores with spreadsheet results within a small tolerance (e.g., absolute difference < 0.001).
- Confirm that rounding and clamping behaved as intended for boundary cases (input below/above clamp range).

## Verification Checklist (Success Criteria)
- Target sheet contains only the required source columns, in the same names and order as the source.
- TotalKg exists directly after these and uses a formula with ROUND(..., 3).
- Score column exists directly after TotalKg and uses:
  - IF/IFS branch on the group column
  - correct polynomial power order (4→3→2→1→0)
  - clamping on the polynomial input per group
  - ROUND(..., 3) on the final score
- Headless recalc completes with zero formula errors.
- At least two spot-checked rows match an independent implementation within 0.001.

## Common Pitfalls and How to Avoid Them
- Using the wrong scoring formula family (e.g., a logarithmic formula instead of the polynomial form).
  - Mitigation: Confirm the exact formula family and coefficients from an authoritative source before coding.
- Forgetting to clamp the polynomial input before evaluation.
  - Mitigation: Always wrap the variable as MIN(MAX(var, lower), upper).
- Incorrect coefficient order or missing polynomial terms.
  - Mitigation: Explicitly write powers 4, 3, 2, 1, 0 in order. Keep coefficients with sufficient decimal precision.
- Relying only on number formatting for precision.
  - Mitigation: Put ROUND(..., 3) in the formula. Formatting does not change the value used in subsequent calculations.
- Mis-referencing columns due to hard-coded letters.
  - Mitigation: Resolve source headers to their 1-based column indices and derive letters programmatically.
- Group label variants (e.g., additional labels representing the same group) not handled.
  - Mitigation: Inspect unique group values and decide on equivalence classes (e.g., treat "Mx" like "M"). Encode all in IF/OR.
- Assuming openpyxl evaluates formulas.
  - Mitigation: Recalculate via a headless engine; only then read with data_only=True for verified values.

## Optional Script Usage
Use the helper to generate a robust Excel IF formula string for a row that:
- selects coefficient sets by group
- clamps the input variable per group
- builds the 4th-degree polynomial
- multiplies by scale and Total, and rounds to 3 decimals

Example workflow:
1) Decide cell references for one row, e.g.,
   - Total: G2
   - Input variable (e.g., bodyweight): C2
   - Group: B2
2) Prepare a JSON config with your group mappings, coefficients, and clamps (see script help below).
3) Generate the formula string with the script and write it into the corresponding cell for that row, then fill down.

See scripts/piecewise_poly_excel.py for details.
