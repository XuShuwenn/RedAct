---
name: lab-unit-harmonization
description: "Harmonize clinical lab data from multiple sources with different units, handling scientific notation and decimal format issues."
---

# Clinical Lab Unit Harmonization

## When to Use

- Harmonize lab data from different healthcare systems
- Handle mixed units for same measurements
- Clean and standardize clinical chemistry data

## Task-Specific Protocol

- If the task or system specifies an exact execution interface, tool/action format, command wrapper, response template, or completion string, follow it exactly throughout the run.
- Do not substitute unsupported tool-call styles, alternate formats, or free-form completion text when an exact protocol is required.
- Treat protocol compliance as mandatory alongside the data-cleaning requirements.


## Input Files

- `/root/environment/data/ckd_lab_data.csv`: 62 lab features, may have missing values
- `/root/environment/data/ckd_feature_descriptions.csv`: Feature descriptions and units

**Before coding, inspect both files beyond the header.** Read enough of `ckd_lab_data.csv` to see actual numeric encodings/issues, and read `ckd_feature_descriptions.csv` completely enough to cover every feature you will claim to harmonize. If any read is truncated, returns only headers, or errors, continue with smaller reads, targeted searches, chunked inspection, or column extraction until you confirm the relevant columns, feature presence, documented units, and ranges. Read representative rows from across the lab file for each feature you may convert. Do **not** invent dataset-wide conversion rules, unit mappings, or physiological ranges from partial reference information.

## Data Quality Issues

1. Missing values → remove patient rows
2. Scientific notation → convert 1.23e2 to 123.00
3. Decimal commas → 12,34 → 12.34
4. Mixed units → convert alternative units to standard (e.g., µmol/L → mg/dL)

## Harmonization Steps

1. Inspect the full schema, complete feature descriptions, and representative raw values before defining cleaning or conversion rules; if any metadata or data view is truncated, keep reading/searching until coverage is complete for every feature you will harmonize
2. Record the input header, feature count, and row count early so you can preserve schema and verify that final row-count changes come only from removed missing/unparsable rows
3. Build the harmonization as one reusable script/pipeline for the whole table, and load lab columns as raw strings first so decimal commas, scientific notation, whitespace, and empty-like tokens are normalized intentionally before numeric coercion
4. Extract or tabulate per-feature documented units and expected ranges from `ckd_feature_descriptions.csv` before finalizing conversion logic; maintain one authoritative per-feature conversion map (feature, source unit, target unit, factor, direction, evidence)
5. Normalize raw numeric text first: scientific notation, decimal commas, whitespace, and other non-canonical numeric strings
6. Convert normalized values to numeric and mark unparsable entries as missing
7. Remove rows with missing values only after parsing/normalization has converted malformed numeric text into missing values; base completeness checks on parsed numeric values, not the raw string dataframe
8. Detect mixed-unit candidates per feature using observed distributions plus fixed physiological/reference expectations after parsing: keep values already plausible in the target unit unchanged, and only consider supported alternate-unit conversions for values implausible in the target unit. Do not hard-code thresholds from feature names alone, use convert-only-extreme-outliers heuristics as the sole detector, or widen ranges just to silence warnings
9. Apply conversion factors only when supported by feature metadata, explicit units, or clear dataset-wide evidence; confirm the source→target direction and analyte-specific factor before bulk conversion, sanity-check multiply/divide direction with representative raw→converted examples, and do not reuse a guessed pattern across analytes
10. Re-check plausibility after conversion using the same fixed per-feature acceptance criteria and summarize remaining below-range/above-range counts by feature; if values remain implausible, investigate the logic and refine only the justified analyte-specific rule or treat unresolved values as missing and remove those rows per task requirements rather than leaving known bad values in place, clamping values, or forcing a pass
11. Round all values to 2 decimal places (X.XX) and write them with string-preserving formatting so trailing zeros are kept in the saved CSV
12. Validate the final saved CSV across the entire dataset before declaring success, and do not claim dataset-wide harmonization, conversion coverage, converted-row counts, supported units, or physiological compliance unless you explicitly computed or inspected evidence for each relevant feature from the final saved output

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
- Map final verification directly to each explicit requirement: row removal for missing/unparsable values, unit harmonization, physiological-range compliance, and exact output formatting.
- Make dataset-wide claims only after programmatic checks across all output rows and relevant columns; debugging samples, `head`, or truncated previews are not sufficient.
- Do not declare success while known unexplained out-of-range values or unit ambiguities remain.


## Output

## Validation and Completion

- Validate the saved CSV itself, not only intermediate DataFrames or console summaries.

- Use validation as a repair loop, not a one-time check: if any check reports bad values, formatting failures, schema problems, contradictory evidence, or suspicious conversion patterns, inspect those exact cases, update the harmonization logic, regenerate the CSV, and rerun validation until all blockers are cleared.
- Separate validation into two passes: (1) raw-text/file-serialization checks on the saved CSV, and (2) parsed semantic checks for schema, missingness, intended units, and physiological ranges.
- Inspect actual data rows from the saved CSV during final verification; a header-only or truncated preview does not count.
- Use checks that distinguish CSV delimiters from decimal commas; field-separating commas are not evidence of bad numeric formatting.
- For exact output-format checks, inspect the saved CSV as raw text or with string-preserving reads; do not rely on `pandas.read_csv` alone because parsing can hide trailing zeros and scientific-notation text.
- Do not treat `head`, a header-only preview, truncated output, file existence, or a failed/incomplete verification command as validation. Fix the check and rerun it on the saved file.

- Treat any schema, missing-data, range, or formatting failure as a blocker: update the harmonization logic, regenerate the file, and verify again.
- Keep physiological acceptance ranges fixed during final verification; if values still fail, revisit conversion logic instead of relaxing thresholds.
- Do not claim a conversion rule, converted-value count, pass rate, or dataset-wide guarantee unless you explicitly computed or inspected evidence for it from the final output.

- Compare final schema and row count against the input counts captured at the start; investigate any mismatch beyond the rows intentionally removed for missing/unparsable data.

- If a feature shows suspiciously high or near-universal conversion counts, inspect raw and converted examples to confirm the detection rule is correct.

- Re-check that conversions were applied only to rows identified as plausible alternate-unit cases; if many already-plausible values changed, treat that as a likely detection error and revisit the rule.
- Confirm the workflow order in code and checks: raw text normalization/parsing first, then missing-value handling, then unit detection/conversion, then final formatting and file-level validation.

- Keep scripts and intermediate/debug artifacts until validation is complete.

- Do not delete the harmonization script, verification helpers, or debug outputs before all validations pass and the task is formally complete; keep them available for reruns if any check fails.

- If any requirement was not checked directly, say so and validate it before finishing.
- Follow any task-specific execution protocol or exact completion string verbatim, but only after all checks pass.


- Treat any failed check, unresolved warning, unresolved out-of-range value, unverified feature-level unit target, unit ambiguity, failed exact-format check, or contradictory example as a hard blocker for claiming the dataset is fully harmonized.
- Keep physiological acceptance ranges fixed during debugging and final QA unless the task or inspected source metadata explicitly justifies a corrected standard; never loosen bounds ad hoc to clear residual failures.
- Validate semantic success from the final saved CSV, not from script intent: use full-column summaries and targeted raw/converted examples for features with suspicious values, high conversion counts, near-universal conversion, or remaining out-of-range values.
- Ensure the final conclusion matches the last validation results exactly; never report completion while any format, range, or unit check still shows FAIL or unresolved warnings.
- Report only results you directly observed or explicitly computed from the final saved file or complete, untruncated reference/validation output. If you mention counts, percentages, pass rates, factors, ranges, or exceptions, show how they were obtained.
- Before the final response, re-read the task instructions and output any required exact completion string, token, or final line verbatim only after all validations pass.

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


- A reliable pattern is: inspect full schema and metadata → normalize numeric text → parse to numeric → profile each feature's distributions and out-of-range clusters → apply analyte-specific conversions only where supported → save CSV → verify the written file with both raw-text and full-feature semantic checks.
- Prefer a string-first parse pipeline: read raw lab fields as text, normalize numeric text explicitly, then convert to numeric for cleaning/conversion logic.
- Start by extracting a compact table for each feature you may harmonize: feature name, documented unit, target unit, expected range, and any candidate alternate units.
- Prefer a small analyte-by-analyte conversion table in code over broad if/else rules from feature-name patterns.
- When mixed units may occur within a column, convert only values justified by metadata plus value evidence; leave already-plausible target-unit values unchanged.
- After the first harmonization pass, summarize remaining out-of-range counts and conversion counts by feature and investigate only the features still failing or showing suspiciously high conversion rates.
- For mmol/L-style analytes or other direction-sensitive conversions, sanity-check whether conversion into US conventional units should make values numerically larger or smaller before trusting the factor.

