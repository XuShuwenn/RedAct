# Quarterly Boundary Checks

Use this when handling the latest year's quarterly rows (especially 2024).

## Goal
Extract annual history plus a 2024 value formed by averaging all available 2024 quarters shown in the table.

## Required checks
- Inspect the source rows near the bottom of each ERP table before coding the parser.
- Normalize any year/header labels before integer parsing; spreadsheet exports may show values like `1973.` or padded strings that need cleanup.
- Track the active year/header while parsing quarter rows so 2024 quarter labels are not accidentally matched from earlier years.
- Record the exact row labels matched for 2024 quarters; do not assume a specific punctuation pattern.
- Confirm the number of 2024 quarters included for each series.
- Print or save a short summary such as: matched labels, extracted quarterly values, computed 2024 average.

- If the first 2024 quarter row is labeled with the year (for example `2024: I.`), attach subsequent quarter-only labels such as `II.` or `III p.` to 2024 until a non-data boundary (notes/source/footer text) is reached.
- Compare the matched 2024 quarter count against what is visibly present near the bottom of the workbook; do not accept a single matched quarter unless manual inspection confirms only one quarter exists.
- If your script prints a summary like `2024 average from 1 quarter`, treat that as a failed validation checkpoint until you have inspected the nearby source rows and confirmed the workbook truly provides only one quarter.

- First decide whether quarterly-to-annual conversion is needed at all. If the workbook already yields a coherent annual sample for the intended analysis window, do not manufacture an extra 2024 observation just because quarter rows are present.
- If you convert 2024 quarters into an annual value, immediately compare the new sample start/end years and observation count against the pre-conversion annual extraction and explain any change.

## Do / Do Not
- Do: verify boundary rows from the workbook structure itself.
- Do: treat oddly formatted labels as a sign to inspect manually.
- Do not: conclude correctness from a parser that reports `avg of 1 quarters` without confirming only one quarter actually exists.
- Do not: trust clipped console output; rerun with concise diagnostics or redirect output to a file.
- Do not: use global quarter-label matching that can pull `I./II./III./IV.` rows from the wrong year.

- Do: confirm the parser captures several known annual rows before checking the latest-year quarter handling.
- Do not: rely on heuristics like requiring the year text to appear inside every quarter label.
- Do not: combine quarter filtering with unverified annual-row heuristics that can eliminate the entire annual history.

- Do: treat odd quarter summaries as evidence to re-check parsing before trusting downstream detrending/correlation output.
- Do: treat output like `Added 2024: averaged 1 quarters` or a final span ending at 2023 as a mandatory reinspection trigger unless the workbook visibly contains only one 2024 quarter.
- Do not: accept the final answer merely because `/root/answer.txt` contains a number when the latest run log is truncated or shows suspicious quarter extraction output.
- Do not: finalize just because the script completed and produced a correlation; anomalous quarter-count or year-range diagnostics mean the extraction is still unverified.

## Minimal verification example
After extraction, emit a summary like:
- `Consumption 2024 quarter labels: [...]`
- `Consumption 2024 quarter values: [...]`
- `PFI 2024 quarter labels: [...]`
- `PFI 2024 quarter values: [...]`
- `Correlation: ...`

If any of those lines are missing or truncated, rerun before finalizing.

- `Merged overlap years/count: ...`
- `Real consumption head/tail: ...`
- `Real investment head/tail: ...`
- `HP input length: ...`

Do not treat a hidden script as sufficient verification; the run should expose enough intermediate values to confirm the parser and transformations behaved as intended.