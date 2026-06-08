---
name: lab-unit-harmonization
description: "Harmonize multi-source clinical lab datasets by parsing numeric formats, detecting mixed units with physiological ranges, converting to a single unit system, and enforcing two-decimal output."
---

# Clinical Lab Unit Harmonization

This skill standardizes laboratory data from heterogeneous sources into a single unit system while cleaning numeric formatting issues and validating physiological plausibility.

Use it when you need to: combine lab feeds using different units, normalize decimal formats (commas, scientific notation), enforce two-decimal outputs, and verify values fall within configured physiological ranges.

## When to Use

Activate this skill for tasks involving:
- Mixed-unit lab feeds (e.g., mmol/L vs. mg/dL, pmol/L vs. pg/mL)
- European decimal commas and scientific notation in CSVs
- Dropping incomplete lab rows prior to harmonization
- Range-based unit inference (out-of-range → likely alternate unit)
- Producing clean two-decimal numeric strings without scientific notation

## Core Workflow

1) Ingest as strings and preserve identifiers
- Read the CSV as strings (dtype=str). This preserves original formatting and trailing characters.
- Identify identifier columns (e.g., patient_id) and keep them untouched as strings. Do not format IDs to two decimals.

2) Normalize numeric strings
- For each lab column:
  - Treat empty strings, common NA tokens ("", nan, none, null, na, n/a) as missing.
  - Handle decimal separators:
    - If both comma and dot are present, treat the rightmost as the decimal separator: remove the other.
    - If only comma is present, replace with dot.
  - Allow scientific notation via float() parsing.
- Convert to float; if parsing fails, mark as missing.

3) Drop incomplete lab rows
- Drop rows with any missing numeric lab value after parsing. Keep identifiers aligned by applying the same mask to the entire row.

4) Harmonize units using physiological ranges
- Prepare configuration:
  - Reference ranges: dict of {column: [min, max]} in the target (US) unit system.
  - Conversion factors: dict of {column: [factor1, factor2, ...]} where value_in_target = value_raw * factor.
  - Optional special rules per column (e.g., HbA1c IFCC→NGSP, hematocrit fraction→percent, urine specific gravity 1xxx→1.xxx).
- For each numeric value:
  - If in-range: keep as is.
  - Else if within a small tolerance (default 5%) beyond the bounds: clamp to the bound.
  - Else try each conversion factor:
    - Apply factor and check range; if in-range, accept.
    - If within tolerance, clamp to the bound and accept.
  - Apply applicable special rules (e.g., HbA1c formula) similarly before/after factors.
  - Optional gentle clamp pass (e.g., 10%) for borderline converted results.

5) Enforce output requirements
- If any value remains out-of-range after all conversions, either:
  - Drop those rows (default for strict outputs), or
  - Keep rows but only if a governance policy allows flagged exceptions (not typical when the spec requires in-range outputs).
- Format every lab numeric value as a string with exactly two decimals: X.XX
- Ensure no scientific notation or commas remain in output.
- Keep identifier columns unmodified and in original type/format.

6) Save and verify
- Write the CSV with the same column order/count as input.
- Verify:
  - Same number of columns as input.
  - No commas or scientific notation in numeric fields.
  - All numeric fields match regex ^-?\d+\.\d{2}$
  - No missing values in lab columns.
  - All numeric values are within configured physiological ranges.

## Verification

Perform these checks after saving (ideally read back as dtype=str):
- Column count equals input column count.
- Numeric formatting:
  - No commas present.
  - No 'e' or 'E' (scientific notation) present.
  - Matches two-decimal regex ^-?\d+\.\d{2}$ for all lab fields.
- Ranges: After casting numeric strings to float, every value lies within its configured [min, max].
- Missingness: No NA/blank in lab fields.
- Identifiers: Present and unchanged; not forcibly converted to decimals.

## Common Pitfalls and How to Avoid Them

- Formatting identifiers to decimals: Keep ID columns as strings; only format lab numerics.
- Index misalignment after filtering: When dropping rows, apply the mask to the entire DataFrame, not just lab columns, to maintain row alignment and correct IDs.
- Premature clamping: Try conversions first; clamp only for small tolerance deviations. Over-clamping can hide true unit issues.
- Wrong conversion direction: Ensure factors map from raw to target units (value_target = value_raw × factor). Document factor provenance.
- Decimal comma handling: If both comma and dot appear, detect the true decimal by the rightmost separator rule; otherwise you may misinterpret thousands vs. decimals.
- Scientific notation reappearing: If you read output without dtype=str, pandas may reformat values. Always validate formatting on string-loaded data.
- Reordering or dropping columns: Preserve input column order and count to meet downstream schema expectations.
- Overbroad tolerance: Keep a strict main tolerance (e.g., 5%) and, if allowed, a small secondary tolerance (e.g., 10%) for post-conversion clamping of near-boundary cases.
- Special-case analytes: Some require formulas (e.g., HbA1c IFCC→NGSP), heuristic scaling (hematocrit fraction→percent), or normalization (specific gravity 1xxx→1.xxx). Include explicit rules rather than ad-hoc guesses.

## Success Criteria

- Output CSV has same column count as input.
- All lab numeric values are in target units and within configured physiological ranges.
- Every lab numeric value is formatted as X.XX (two decimals), with no scientific notation or commas.
- No missing values in lab columns; dropped rows accounted for.
- Identifier columns preserved and not altered into decimal format.

## Optional Script Usage

A reusable helper script is provided to perform the workflow with configurable ranges, factors, and special rules.

Example invocation:
- Prepare JSON files (examples shown as structure only):
  - ranges.json: {"Glucose": [min, max], "Serum_Creatinine": [min, max], ...}
  - conversions.json: {"Glucose": [18.02], "Serum_Creatinine": [0.0113], ...}
  - special_rules.json: {"HbA1c": ["hba1c_ifcc_to_ngsp"], "Hematocrit": ["fraction_to_percent"], "Urine_Specific_Gravity": ["sg_thousandths"]}

Run:
- python scripts/lab_unit_harmonizer.py --input raw.csv --output harmonized.csv --ranges ranges.json --conversions conversions.json --special-rules special_rules.json --id-column patient_id --drop-unharmonizable

Notes:
- Provide your own ranges and factors appropriate to your domain/panel.
- Use --verify to print a post-save validation report.
