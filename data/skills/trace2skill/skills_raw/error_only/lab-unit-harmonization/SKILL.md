---
name: lab-unit-harmonization
description: "Harmonize clinical lab data from multiple sources with different units, handling scientific notation and decimal format issues."
---

# Clinical Lab Unit Harmonization

## When to Use

- Harmonize lab data from different healthcare systems
- Handle mixed units for same measurements
- Clean and standardize clinical chemistry data

## Input Files

- `/root/environment/data/ckd_lab_data.csv`: 62 lab features, may have missing values
- `/root/environment/data/ckd_feature_descriptions.csv`: Feature descriptions and units

**Before coding, inspect both files beyond the header.** Read enough of `ckd_lab_data.csv` to see actual numeric encodings/issues, and read `ckd_feature_descriptions.csv` completely enough to cover every feature you will claim to harmonize. If a view is truncated, keep reading/searching until you confirm the relevant columns, documented units, and ranges. Do **not** invent dataset-wide conversion rules from partial reference information.

## Data Quality Issues

1. Missing values → remove patient rows
2. Scientific notation → convert 1.23e2 to 123.00
3. Decimal commas → 12,34 → 12.34
4. Mixed units → convert alternative units to standard (e.g., µmol/L → mg/dL)

## Harmonization Steps

1. Inspect the full schema, feature descriptions, and representative raw values before defining cleaning or conversion rules
2. Normalize raw numeric text first: scientific notation, decimal commas, whitespace, and other non-canonical numeric strings
3. Convert normalized values to numeric and mark unparsable entries as missing
4. Remove rows with missing values after parsing/normalization
5. Detect values that may indicate alternate units using observed distributions plus physiological expectations; do not hard-code thresholds from feature names alone or widen ranges just to silence warnings
6. Apply conversion factors only when supported by feature metadata, explicit units, or clear dataset-wide evidence; confirm the source→target direction and analyte-specific factor before bulk conversion
7. Re-check plausibility after conversion using fixed acceptance criteria; if values remain implausible, investigate the logic and drop/flag unresolved cases per task requirements rather than forcing a pass
8. Round all values to 2 decimal places (X.XX)
9. Validate the final saved CSV across the entire dataset before declaring success

## Output

`/root/ckd_lab_data_harmonized.csv`:
- Same column count as input
- All values in US conventional units
- Within expected physiological ranges
- No scientific notation or commas


Verification requirements before finishing:
- Inspect the actual `/root/ckd_lab_data_harmonized.csv` file text, not just a pandas round-trip or a header preview.
- Confirm across the full file that row/column structure matches expectations and row count decreased only because rows with missing or unparseable values were removed.
- Confirm numeric fields use `.` as decimal separator, contain no scientific notation text or decimal commas, and are written in exact `X.XX` format where applicable.
- Audit every lab feature with full-column checks or summaries to catch mixed-unit leftovers and implausible ranges.
- Do not declare success while known unexplained out-of-range values or unit ambiguities remain.


## Output

## Validation and Completion

- Validate the saved CSV itself, not only intermediate DataFrames or console summaries.
- Treat any schema, missing-data, range, or formatting failure as a blocker: update the harmonization logic, regenerate the file, and verify again.
- Keep physiological acceptance ranges fixed during final verification; if values still fail, revisit conversion logic instead of relaxing thresholds.
- Do not claim a conversion rule, converted-value count, pass rate, or dataset-wide guarantee unless you explicitly computed or inspected evidence for it from the final output.
- If a feature shows suspiciously high or near-universal conversion counts, inspect raw and converted examples to confirm the detection rule is correct.
- Keep scripts and intermediate/debug artifacts until validation is complete.
- If any requirement was not checked directly, say so and validate it before finishing.
- Follow any task-specific execution protocol or exact completion string verbatim, but only after all checks pass.
## Tips

- Know conversion factors: mg/dL ↔ µmol/L for creatinine, g/dL ↔ g/L for hemoglobin
- Define valid physiological ranges per feature
- Use pandas for data processing


- Derive per-feature conversions from the actual feature-description file, documented units, and observed distributions; do not infer broad rules from partial previews or generic lab knowledge alone.
- Sanity-check conversion direction before coding. Use analyte-specific factors; do not reuse a guessed multiply/divide rule across different labs.
- Treat physiological ranges as validation criteria and supporting evidence, not proof of which alternate unit was used.
- Do not convert every out-of-range value blindly, and do not clamp values to physiological min/max as a fallback.
- Do not validate exact `X.XX` formatting by loading the CSV back into pandas alone; parsing may hide trailing zeros. Use raw-text or string-preserving checks as well.
- Compare conversion counts by feature; nearly all rows converting for one feature can be a red flag that the feature was already in the target unit.
- Use full-file/programmatic inspection for validation; a truncated preview or a few spot checks is not enough.
