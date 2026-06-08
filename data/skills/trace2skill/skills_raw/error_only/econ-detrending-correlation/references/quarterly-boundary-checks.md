# Quarterly Boundary Checks

Use this when handling the latest year's quarterly rows (especially 2024).

## Goal
Extract annual history plus a 2024 value formed by averaging all available 2024 quarters shown in the table.

## Required checks
- Inspect the source rows near the bottom of each ERP table before coding the parser.
- Track the active year/header while parsing quarter rows so 2024 quarter labels are not accidentally matched from earlier years.
- Record the exact row labels matched for 2024 quarters; do not assume a specific punctuation pattern.
- Confirm the number of 2024 quarters included for each series.
- Print or save a short summary such as: matched labels, extracted quarterly values, computed 2024 average.

## Do / Do Not
- Do: verify boundary rows from the workbook structure itself.
- Do: treat oddly formatted labels as a sign to inspect manually.
- Do not: conclude correctness from a parser that reports `avg of 1 quarters` without confirming only one quarter actually exists.
- Do not: trust clipped console output; rerun with concise diagnostics or redirect output to a file.
- Do not: use global quarter-label matching that can pull `I./II./III./IV.` rows from the wrong year.

## Minimal verification example
After extraction, emit a summary like:
- `Consumption 2024 quarter labels: [...]`
- `Consumption 2024 quarter values: [...]`
- `PFI 2024 quarter labels: [...]`
- `PFI 2024 quarter values: [...]`
- `Correlation: ...`

If any of those lines are missing or truncated, rerun before finalizing.