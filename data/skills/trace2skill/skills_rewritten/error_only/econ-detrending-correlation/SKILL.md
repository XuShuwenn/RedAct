---
name: econ-detrending-correlation
description: "Apply Hodrick-Prescott filter to detrend economic time series and calculate Pearson correlation between consumption and investment."
---

# Economic Time Series Detrending and Correlation

## When to Use

- Detrend economic time series using HP filter
- Calculate correlation between detrended economic indicators
- Deflate nominal series using CPI to get real values

- First confirm the task actually asks for this workflow (deflation, log, HP filter, correlation) before executing it; if any step is not explicit in the prompt, verify it from the task instructions and workbook evidence rather than assuming the default pipeline applies.


## Input Files

- `/root/ERP-2025-table10.xls`: Personal Consumption Expenditures (Nominal)
- `/root/ERP-2025-table12.xls`: Private Fixed Investment (Nominal)
- `/root/CPI.xlsx`: Consumer Price Index (for deflation)

- Treat these as Excel workbooks, not text files: inspect and parse them with Python spreadsheet tooling such as `pandas.read_excel` using an appropriate engine (`xlrd` for legacy `.xls`, `openpyxl` for `.xlsx`).

## Key Steps

1. Inspect each input workbook first with spreadsheet-aware tools: print sheet names, column labels, and representative top/middle/bottom rows before coding against assumed headers or row formats; identify the actual header row, where annual data begins, the correct Total/value column, and where quarterly/footer sections start

1a. Before building the pipeline, restate the requested methodology from the task prompt and confirm it matches this skill's default sequence; do not assume HP filtering, CPI deflation, log transformation, Pearson correlation, or special 2024 handling unless the task instructions or inspected source structure support them.

2. Extract Personal Consumption Expenditures (Total, column 1) and PFI (Total, column 1) from their ERP tables separately
2a. For each ERP workbook, identify the year/label column and numeric value column from that workbook itself; do not reuse row offsets, header positions, or footer boundaries from the other ERP file.
2b. Print a small sample of extracted annual year→value pairs for each series before merging so wrong-row or wrong-column extraction is caught early.
3. Build independent year→value mappings for each series, then merge by year; do not assume matching row numbers across the two files
3a. Normalize extracted year labels before filtering or merging: trim whitespace/trailing punctuation so labels like `1973.` parse to the intended year instead of being silently dropped.
3b. After merging, print the overlapping year span and observation count, plus a few first/last merged rows, before proceeding.
4. Handle quarterly data at end of tables by inspecting the bottom rows first; for 2024, statefully track the active year, enumerate every matched 2024 quarter row from that active-year block (including inherited labels like `II.`/`III p.` after `2024: I.`), stop when notes/source/footer text begins, and compute the annual 2024 value as the mean of all available 2024 quarters shown in the source table
4a. Before constructing any 2024 annual value from quarters, verify whether the workbook already provides the latest usable annual observation range. DO NOT add a derived 2024 point if the task can be completed from the reported annual sample (for example, 1973–2023) and there is no explicit need to extend the sample.
4b. If you do use quarterly rows to form 2024, treat quarter coverage diagnostics as a gate, not a note: compare the visible quarter count in the workbook against the quarters actually captured by the parser, record why the conversion is necessary, and immediately reprint start year, end year, and observation count so any unexpected shift in sample boundaries is caught before merging or correlation.
4c. Decide explicitly whether the latest year is complete enough to include in an annual HP-filter analysis. If the workbook shows only a partial latest year (for example only 1 quarter), do not silently include it: either (a) exclude that year and use the last completed annual observation, or (b) include it only if the task clearly requires using the partial year and you state that choice in diagnostics.
5. Validate extraction results before proceeding: ensure annual observations are non-empty, years are in expected order, and 2024 handling did not accidentally pull quarters from earlier years, miss available quarters, or remove the series
6. Inspect `/root/CPI.xlsx` with targeted output (sheet names, exact column names, and sample rows), then confirm the actual year column, CPI/deflator column, and unit/scaling before deflating; if the workbook already provides a target-year deflator/ratio, use that column directly rather than rebuilding it from a guessed schema
7. Before HP filtering, verify the CPI-aligned real consumption and real investment series use the identical final year list, and print a short diagnostic showing overlapping years, sample real values, and the exact deflation formula used
8. Apply the required transformation order exactly: nominal → real via CPI → natural log → Hodrick-Prescott filter with λ=100
9. Compute Pearson correlation between the two cyclical components
10. Round result to 5 decimal places
11. Prefer one reproducible Python script for the full pipeline: inspect workbooks, extract both nominal series, annualize 2024 from quarters, merge by year with CPI, deflate, log, HP-filter, correlate, write `/root/answer.txt`, then read it back
12. Before concluding, rerun the final script end-to-end without error, explicitly print the extracted 2024 quarter labels/values and quarter counts for both series, the overlap year range/count, the final correlation, and read back `/root/answer.txt` to confirm the saved value was freshly written and matches the computed value
12a. If any prior run raised a parsing/alignment error or if the visible output was truncated before the final correlation/file confirmation, do at least one fresh rerun that visibly reaches the end; do not infer success from a partially shown earlier run.
12b. Treat the task as unfinished unless the observable final run shows all of: no exception, final correlation printed, `/root/answer.txt` written, and the read-back value matching the printed correlation.

## HP Filter

- Use natural log of real series before filtering
- λ = 100 for annual data
- Prefer a trusted library implementation such as `statsmodels.tsa.filters.hp_filter.hpfilter` when available
- Cyclical component = series - trend component


## Validation Checks

- If ERP parsing depends on inferred headers and the rows look irregular, reread with `header=None` and inspect the raw grid before continuing.
- Verify separately for each ERP workbook which sheet/header/column contains the target Total series; do not reuse one workbook's layout assumptions for the other.
- Verify parsed years are clean integers after normalization (for example, labels like `1973.` should become `1973`) and that cleaned year keys are unique before merging.
- Confirm annual and quarterly observations were classified from displayed row labels and active-year context, not from row numbers or brittle heuristics.
- If only one 2024 quarter is captured, manually inspect the following rows to verify whether later quarter rows omit the year label rather than assuming only one quarter exists.
- Treat suspicious latest-year diagnostics as a hard stop, not a soft warning: if output shows only 1 captured 2024 quarter when more quarter rows are visibly present, missing expected quarter labels, an unexpected sample span (for example 1973–2023 when 2024 was meant to be included), or any mismatch between claimed and printed coverage, debug extraction and rerun before trusting the correlation.
- If the latest year remains partial after inspection (for example only one visible quarter exists), make an explicit include/exclude decision before HP filtering; do not let a partial year enter the final correlation by default.
- After joining consumption, investment, and CPI by year, print the overlapping year range and count; if the overlap is empty, unexpectedly short, or not 1973–2024 with 52 observations, fix extraction/alignment before continuing.
- Before `np.log` or HP filtering, confirm the working arrays are numeric and the CPI-aligned real PCE and real PFI series use the exact same final years.
- Keep the preprocessing order exact: nominal extraction → CPI deflation → natural log → HP filter with `lambda=100` → Pearson correlation of cyclical components.
- Treat `/root/answer.txt` as valid only if the immediately preceding end-to-end run completed successfully and produced the same printed correlation.
- Do not treat a truncated console log, a completed script alone, or an existing `/root/answer.txt` as proof of success. The accepted run must visibly reach the correlation print, write the file, read the same value back after the script exits normally, and show no unresolved extraction anomalies.

- After each major stage—nominal extraction, optional 2024 annualization, CPI merge/deflation, and final HP-filter inputs—print and compare the start year, end year, and observation count for both series. If any stage changes the sample unexpectedly, stop and fix the pipeline before computing correlation.
- Do not mix a derived quarterly-based 2024 observation into one stage of the pipeline while describing another stage as annual-only; the reported year range and count must stay internally consistent.
- If annual data are already complete through the intended end year, prefer the direct annual sample over constructing a partial-year proxy from quarterly rows.
- Do not accept `/root/answer.txt` or a printed correlation as evidence of success if intermediate logs show anomalies; first reconcile the quarter labels/values, merged overlap years/count, and final sample span with the source tables.
- Before full implementation, verify that the planned steps are grounded in the task prompt: confirm the requested output, required transformations, and whether latest-year quarterly annualization is actually needed for these sources.

## Validation Checks

- Before computing correlation, inspect the extracted year/value pairs for both series, especially the first/last years and 2024.
- Verify that the selected rows/columns correspond to the intended ERP series: Personal Consumption Expenditures (Total, column 1) and Private Fixed Investment (Total, column 1).
- Confirm that 2024 annual values are computed from all available quarterly observations shown in the source tables, not from a guessed or truncated subset.
- Do not finalize after only checking `/root/answer.txt`; validate the upstream extraction and annualization logic first.
## Output Format

Single number to `/root/answer.txt`

Only trust that file after an observable successful run shows the final correlation and a matching read-back from `/root/answer.txt`.


Before trusting `/root/answer.txt`, verify the computation ran end-to-end: confirm deflation, HP filtering, and correlation steps executed successfully and the script exited normally. If output is truncated or diagnostics stop early, rerun or inspect the error instead of treating an existing answer file as success.

## Tips

- pandas for Excel reading

- For `.xls`/`.xlsx` sources, `pandas.read_excel(..., header=None)` is often the safest inspection mode for ERP-style sheets with title rows, merged cells, and mixed annual/quarterly blocks.
- scipy.signal for HP filter or implement manually
- Handle missing/partial 2024 data carefully


- ERP table layouts may differ between PCE and PFI; extract each sheet independently and align only on the year field
- DO NOT assume CPI headers such as `Year` or a specific CPI value column; inspect the actual schema in `/root/CPI.xlsx`
- Parse quarter rows statefully using the active year context; do not match `I./II./III./IV.` labels globally across the table
- DO NOT use brittle year tests, hard-coded quarter values, or ad hoc string heuristics to detect quarter rows; inspect raw row labels, normalize year labels, and distinguish annual vs quarterly entries from the workbook's actual formatting while carrying forward the active year context.
- For the 2024 special case, verify every captured quarter row and confirm the annual 2024 value equals the average of the available quarters actually used in computation
- After extraction, sanity-check that both annual series contain many years before deflation/filtering; if a series is empty, very short, or the overlapping sample span changes unexpectedly, fix parsing before continuing
- Sanity-check that consumption years, investment years, and CPI years align exactly before applying logs and the HP filter
- If tool output is truncated, rerun with concise targeted prints or redirect to a log file; do not report an unverified number
- Keep final reasoning consistent with the observed successful run output
- See [Quarterly Boundary Checks](references/quarterly-boundary-checks.md) for a concise latest-year extraction checklist

- Before coding extraction logic, inspect both the top and bottom of each ERP sheet so you can confirm headers, target value column, latest-year quarter formatting, and where notes/source/footer text begins.
- When the first quarter row carries the year label and later quarter rows only show `II.`/`III.`/`IV.`, keep collecting only while the active year remains 2024; stop or reset when the table advances to another year/header or to notes/footer text.
- Treat the CPI workbook as data to interpret, not a fixed schema: confirm whether the numeric column is an index level, a deflator, or already normalized to a target year before dividing nominal values.
- Prefer a short summary log or redirected output file over long console dumps so the quarter diagnostics, overlap checks, and final correlation remain visible.

- Read [references/partial-latest-year-policy.md](references/partial-latest-year-policy.md) when the newest year is represented by quarterly rows rather than a completed annual observation.
