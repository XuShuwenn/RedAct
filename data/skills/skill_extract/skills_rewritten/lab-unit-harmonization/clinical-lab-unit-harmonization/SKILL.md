---
name: clinical-lab-unit-harmonization
description: "Standardize multi-source clinical lab CSVs by normalizing numeric formats, dropping incomplete rows, converting alternate units into target US conventional units using physiological ranges, and writing values as X.XX."
---

# Clinical Lab Unit Harmonization

This skill provides a robust workflow to harmonize clinical laboratory datasets sourced from multiple systems that may use mixed numeric formats and measurement units. It cleans numeric strings (including scientific notation and decimal commas), removes incomplete records, converts alternate units into target US conventional units based on physiological ranges, and writes all numeric values in exactly two-decimal `X.XX` format while preserving IDs and column structure.

## When to Use

Activate this skill when you have a tabular clinical lab dataset that:
- mixes numeric formats (e.g., scientific notation like `1.23e2`, or comma decimal `12,34`)
- contains incomplete patient rows that must be dropped
- uses different units across sources for the same analyte and needs standardization into target (US conventional) units
- requires exactly two-decimal output formatting with consistent `.` as the decimal separator

## Core Workflow

1. Inspect Inputs
   - Open the dataset and any feature description documentation to confirm column names and intended units.
   - Identify ID columns (e.g., patient identifiers) that must be preserved without numeric reformatting.

2. Define Target Units and Physiological Ranges
   - Prepare a conversion configuration (JSON) that specifies, per lab feature:
     - target_unit and its physiological range `[min, max]` in that unit
     - alternate source units with a multiplication `factor` to convert to the target unit and their plausible ranges
   - Only convert values that are likely in alternate units by using range checks.

3. Drop Incomplete Rows
   - Determine the set of required numeric columns (all numeric labs by default, excluding ID columns) and drop any row with missing/unparsable values in these columns.

4. Normalize Numeric Text
   - Trim whitespace.
   - Convert scientific notation (`1.5e3`) to numeric.
   - Handle decimal commas: if a value uses `,` as the sole decimal separator (no `.` present), treat `,` as `.`.
   - Resolve mixed `,` and `.` by treating the last occurring separator as the decimal point and removing the other as a thousands separator.

5. Range-Guided Unit Conversion
   - For each configured lab column:
     - If a value falls within the target physiological range (with tolerance), keep it.
     - Otherwise, try each alternate unit definition:
       - If the raw value fits the alternate unit's source range (with tolerance), convert via `value * factor`.
       - Accept the conversion only if the converted value falls within the target range (with tolerance).
     - Do not convert values that already fit the target range.
     - Apply at most one successful conversion per value.

6. Formatting and Output
   - Round all numeric lab values to exactly two decimals and store them as strings to preserve trailing zeros.
   - Keep ID columns as-is (do not append `.00`).
   - Save the harmonized CSV with the same columns as input.

## Configuration Schema (JSON)

Provide a JSON file to guide conversions. Example structure (illustrative only; replace with actual features and units you expect):

{
  "columns": {
    "CREAT": {
      "target_unit": "mg/dL",
      "target_range": [0.4, 12.0],
      "alternates": [
        {"src_unit": "umol/L", "factor": 0.0113, "src_range": [20, 2000]}
      ]
    },
    "HGB": {
      "target_unit": "g/dL",
      "target_range": [5.0, 20.0],
      "alternates": [
        {"src_unit": "g/L", "factor": 0.1, "src_range": [50, 250]}
      ]
    }
  }
}

Notes:
- `target_range` and `src_range` should reflect plausible physiological values for adults unless your cohort differs.
- Add only units and factors you expect in your dataset.

## Verification

Perform these checks on the output:
- Structural
  - Column count equals input; column order preserved.
  - All required numeric fields are present and non-missing.
- Formatting
  - No scientific notation, no commas in numeric fields.
  - Every numeric lab cell matches the regex: `^-?\d+\.\d{2}$`.
  - ID columns remain unaltered (e.g., no `.00`).
- Ranges
  - For configured columns, values are within the specified target ranges (with tolerance) after conversion.
- Spot Checks
  - Manually review a few columns with known alternate units to confirm conversions.

You can use the provided validator script to check formatting and ranges.

## Common Pitfalls and How to Avoid Them

- Converting already-correct values
  - Only convert values that are out of target range and plausibly within an alternate unit range; never convert if already within target range.
- Formatting IDs as decimals
  - Explicitly declare ID columns and exclude them from numeric formatting and rounding.
- Ambiguous decimal separators
  - When both `,` and `.` appear, treat the last separator as the decimal and strip the other as thousands separator. Validate by sampling values before bulk processing.
- Losing trailing zeros in output
  - Cast numeric lab columns to strings using fixed two-decimal formatting before writing CSV.
- Over-dropping rows
  - Restrict completeness checks to required numeric lab columns; do not drop based on optional or textual columns.
- Range edge rejections after rounding
  - Use a small tolerance (e.g., ±2% of range width) when checking ranges to avoid false negatives due to rounding.

## Optional Script Usage

1) Harmonize a dataset
- Inputs:
  - A CSV file with lab data
  - Optional JSON config with ranges and unit conversions
  - ID column names (comma-separated)

Example:
- python scripts/harmonize_labs.py \
  --input /path/to/input.csv \
  --output /path/to/output.csv \
  --config /path/to/conversions.json \
  --id-columns patient_id \
  --tol-pct 0.02

Behavior:
- Drops rows with missing/unparsable values in detected numeric lab columns (excluding IDs)
- Normalizes numeric text, applies range-guided unit conversions, formats numeric labs to X.XX
- Preserves non-numeric and ID columns unchanged

2) Validate output formatting and ranges
- Provide the same JSON config and ID columns to validate numeric format and ranges

Example:
- python scripts/validate_format.py \
  --input /path/to/output.csv \
  --config /path/to/conversions.json \
  --id-columns patient_id

The validator prints any issues and exits non-zero if problems are found.
