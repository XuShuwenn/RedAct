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
- Determine the exact requested deliverable before coding: which series, what time span, whether CPI deflation/log/HP filtering/Pearson correlation are required, whether latest-year quarterly annualization is needed, and whether the task even asks for a saved single-number answer. If the prompt differs from this skill's default workflow, follow the prompt rather than forcing the default pipeline.
- If the task asks for a different statistic, a different detrending method, or no deflation/log step, stop and follow the task-specific method instead of forcing this skill's default pipeline.
- In your first diagnostic print, state the exact requested output, whether deflation is required, whether log transformation is required, whether HP filtering is required, and the intended final sample years.


## Input Files

- `/root/ERP-2025-table10.xls`: Personal Consumption Expenditures (Nominal)
- `/root/ERP-2025-table12.xls`: Private Fixed Investment (Nominal)
- `/root/CPI.xlsx`: Consumer Price Index (for deflation)

- Treat these as Excel workbooks, not text files: identify each file type first and use a matching reader from the start. Prefer spreadsheet-aware tooling such as `pandas.read_excel` with `xlrd` for legacy `.xls` ERP files and `openpyxl` for `.xlsx` files like CPI; if the first reader fails on format support, switch to the correct engine before debugging extraction logic.

## Key Steps

1. Inspect each input workbook first with spreadsheet-aware tools: print sheet names, column labels, and representative top/middle/bottom rows before coding against assumed headers or row formats; identify the actual header row, where annual data begins, the correct Total/value column, and where quarterly/footer sections start
1b. During inspection, explicitly note for each file: sheet used, header row, year/label column, value column, where annual rows start, where annual rows stop and quarterly rows begin, and whether the bottom block contains continuation-style quarter labels that require carrying forward the active year/header context.
1c. Validate the intended value column with one known clearly annual row: print the year label plus candidate numeric columns and confirm the chosen Total/value column gives a sensible series value before writing the extractor.
1d. Base extraction rules on the labels you actually observe in each workbook (for example annual labels like `1973.` and quarterly labels like `2024: I.`, `II.`, `III p.`) instead of hard-coded row numbers or assumed repeated layouts.
1e. Build and validate the pipeline in stages: (a) workbook structure inspection, (b) nominal series extraction, (c) optional latest-year aggregation, (d) CPI alignment/deflation, (e) log + HP filter, (f) correlation + answer write-back. After each stage, print a compact diagnostic and do not proceed if the stage output is empty, misaligned, or inconsistent with the inspected workbook structure.

1a. Before building the pipeline, restate the requested methodology from the task prompt and confirm it matches this skill's default sequence; do not assume HP filtering, CPI deflation, log transformation, Pearson correlation, or special 2024 handling unless the task instructions or inspected source structure support them.
1aa. Make an explicit latest-year decision before writing extraction code: either (a) use reported annual observations only, or (b) derive the latest year from quarterly rows. Prefer annual-only when the direct annual sample already answers the task; use quarterly derivation only when the task explicitly requires the latest available year or the workbook lacks the needed annual endpoint.
1ab. If the prompt and workbook evidence indicate a simpler annual-only workflow, use that simpler workflow; do not add quarterly annualization, extra transformations, or sample extensions unless they are necessary for the requested result.
1ac. Before implementation, write a one-line plan stating the requested output artifact and exact transforms to apply. Keep the standard pipeline (nominal → real via CPI → log → HP filter → Pearson correlation) only when the prompt explicitly asks for detrended real-series comovement; if that plan does not explicitly call for correlation and `/root/answer.txt`, do not produce them by default.
1ad. Check library availability before writing the main pipeline (at minimum Excel-reading support and a preferred HP-filter implementation such as `statsmodels`); if a preferred package is unavailable, choose the simplest supported alternative before coding further.

2. Extract Personal Consumption Expenditures (Total, column 1) and PFI (Total, column 1) from their ERP tables separately
2a. For each ERP workbook, identify the year/label column and numeric value column from that workbook itself; do not reuse row offsets, header positions, or footer boundaries from the other ERP file.
2a.i. Confirm the target value column by combining header labels with representative sample row values rather than trusting column position or an `Unnamed` label alone; verify it is the intended Total series before extraction.
2b. Print a small sample of extracted annual year→value pairs for each series before merging so wrong-row or wrong-column extraction is caught early.
3. Build independent year→value mappings for each series, then merge by year; do not assume matching row numbers across the two files
3a. Normalize extracted year labels before filtering or merging: trim whitespace/trailing punctuation so labels like `1973.` parse to the intended year instead of being silently dropped.
3aa. If an expected year is missing after extraction or merge, print the raw year labels alongside the normalized labels for the affected rows and fix normalization/parsing before continuing; do not debug coverage gaps only from aggregate counts.
3b. After merging, print the overlapping year span and observation count, plus a few first/last merged rows, before proceeding.
3c. Keep these diagnostics lightweight and repeatable: after nominal extraction, after any latest-year quarterly aggregation, and after CPI alignment, print `start year`, `end year`, and `count` so the final successful run still shows the full sample progression.
3d. Preserve each source as an explicit year→value mapping until the final aligned merge; do not join by row position or rely on workbook order alone.
3e. When the merged sample is ready, verify all three series (consumption, investment, CPI) share the same annual index before any deflation, logging, or filtering.
4. Handle quarterly data at the end of the tables only after confirming a quarterly-derived latest year is actually needed. Inspect the bottom rows first; if the task requires extending the sample beyond the completed annual rows, statefully track the active year, enumerate every matched latest-year quarter row from that active-year block (including inherited labels like `II.`/`III p.` after `2024: I.`), stop when notes/source/footer text begins, and compute the annual latest-year value as the mean of all available quarters shown in the source table.
4a. Before constructing any latest-year annual value from quarters, verify whether the workbook already provides the latest usable completed annual observation range. Default to the completed annual sample; only add a derived latest-year point when the task explicitly requires the latest available year or the source clearly lacks an annual value that the task still expects you to use.
4b. If you do use quarterly rows to form 2024, treat quarter coverage diagnostics as a gate, not a note: compare the visible quarter count in the workbook against the quarters actually captured by the parser, record why the conversion is necessary, and immediately reprint start year, end year, and observation count so any unexpected shift in sample boundaries is caught before merging or correlation.
4b1. Before writing the parser, inspect the exact displayed latest-year row-label text and continuation-row formatting in each workbook, then match only rows demonstrably belonging to the active latest-year block.
4b2. When later quarter rows inherit the year from the first labeled row (for example `2024: I.` followed by `II.` / `III.`), carry forward that active year while parsing and print the exact matched labels so inherited-quarter attachment is visibly verified before annualizing.
4c. Decide explicitly whether the latest year should enter the annual HP-filter sample. If the annual table is not yet complete but the task asks for the latest available data and the workbook shows multiple latest-year quarters, aggregate the available quarters consistently and state that choice in diagnostics. If the workbook shows only a genuinely sparse partial year (for example just 1 quarter) and the task does not clearly require including it, exclude that year and use the last completed annual observation.
5. Validate extraction results before proceeding: ensure annual observations are non-empty, years are in expected order, and 2024 handling did not accidentally pull quarters from earlier years, miss available quarters, or remove the series
5a. Before any CPI merge or statistical transformation, confirm the working extraction is annual-only except for an explicitly documented latest-year quarterly-to-annual conversion; do not let raw quarterly rows flow into the merged analysis dataset.
5b. Print a concise frequency sanity check for each extracted series (for example first/last annual labels kept, any quarter labels captured for latest-year handling, final annual observation count).
6. Inspect `/root/CPI.xlsx` with targeted output (sheet names, exact column names, and sample rows), then confirm the actual year column, CPI/deflator column, and unit/scaling before deflating; if the workbook already provides a target-year deflator/ratio, use that column directly rather than rebuilding it from a guessed schema
6a. Before running the full pipeline, verify prerequisites up front: confirm the CPI workbook covers the full intended analysis span after any latest-year decision and that the HP-filter library you plan to use (for example `statsmodels`) imports successfully; if either prerequisite fails, adjust the plan before doing the full extraction/merge workflow.
6b. When the CPI workbook exposes a clearly named target-year column (for example `CPI_2024` or an equivalent deflator-to-target-year field), prefer that inspected column directly for real-value conversion and print the exact column name chosen; do not substitute a different CPI formula unless the workbook structure requires it.
7. Before HP filtering, verify the CPI-aligned real consumption and real investment series use the identical final year list, and print a short diagnostic showing overlapping years, sample real values, and the exact deflation formula used
7a. Keep the workflow staged and auditable: finish nominal extraction and year alignment first, then merge CPI, then compute real series, then log/HP/correlation. At each handoff, print a few sample year→value rows so extraction mistakes are caught before statistical transformation hides them.
7b. Before division, `np.log`, or HP filtering, explicitly coerce the extracted nominal values, CPI values, and merged real-series arrays to numeric dtypes and confirm there are no object/string leftovers or unexpected non-numeric entries.
8. Apply the required transformation order exactly: nominal → real via CPI → natural log → Hodrick-Prescott filter with λ=100
8a. Keep this order unchanged even if workbook cleanup is messy: first align annual nominal series with CPI by year, then deflate both with the same CPI basis, then take natural logs of the real series, then apply the HP filter to those logged real series, and finally correlate the resulting cyclical components.
8b. Before running the HP-filter step, confirm the intended library is importable (prefer `statsmodels.tsa.filters.hp_filter.hpfilter`); if import fails, stop and resolve the dependency or choose another trusted implementation before continuing so the final run does not fail mid-pipeline.
9. Compute Pearson correlation between the two cyclical components
10. Round result to 5 decimal places
11. Prefer one reproducible Python script for the full pipeline: inspect workbooks, extract both nominal series, annualize 2024 from quarters, merge by year with CPI, deflate, log, HP-filter, correlate, write `/root/answer.txt`, then read it back
11a. Keep all transformations in that same script so extraction, deflation, detrending, correlation, and file output can be rerun together after any parsing fix; avoid patching results manually in separate steps.
11b. Keep the script modular even if it is a single file: separate workbook inspection, per-workbook extraction, optional latest-year aggregation, CPI alignment, and final analysis so diagnostics can show exactly where a year-range or quarter-capture mistake occurs.
11c. Keep the script parameterized around the latest-year decision: completed-annual-only and quarterly-derived-latest-year are both acceptable when supported by the prompt/workbook, but the run must execute one choice consistently from extraction through final reported sample span.
12. Before concluding, rerun the final script end-to-end without error, explicitly print the extracted 2024 quarter labels/values and quarter counts for both series, the overlap year range/count, the final correlation, and read back `/root/answer.txt` to confirm the saved value was freshly written and matches the computed value
12a. If any prior run raised a parsing/alignment error or if the visible output was truncated before the final correlation/file confirmation, do at least one fresh rerun that visibly reaches the end; do not infer success from a partially shown earlier run.
12b. Treat the task as unfinished unless the observable final run shows all of: no exception, final correlation printed, `/root/answer.txt` written, and the read-back value matching the printed correlation.
12c. If diagnostics show a suspicious latest-year result (for example `averaged 1 quarter`, missing expected quarter labels, or a final span that contradicts the intended sample), STOP and debug extraction before accepting any printed correlation or answer file; a numerically plausible result does not override anomalous coverage diagnostics.
12d. In that final visible run, also print a one-line method summary matching the task request, e.g. `Method used: annual sample years ..., nominal->real via CPI, log, HP(100), Pearson correlation`; if the printed method does not match the prompt, fix the workflow before saving the answer.

## HP Filter

- Use natural log of real series before filtering
- λ = 100 for annual data
- Prefer a trusted library implementation such as `statsmodels.tsa.filters.hp_filter.hpfilter` when available
- Cyclical component = series - trend component


## Validation Checks

- If ERP parsing depends on inferred headers and the rows look irregular, reread with `header=None` and inspect the raw grid before continuing.
- Verify separately for each ERP workbook which sheet/header/column contains the target Total series; do not reuse one workbook's layout assumptions for the other.
- Confirm the chosen ERP value column using both the visible header context and a few representative year→value samples; do not rely on column index alone even when the usable column is labeled `Unnamed:*`.
- Preserve workbook-specific extraction logic even when both files are ERP tables: similarity of source type is not evidence of identical row starts, footer positions, or quarter-label formatting.
- For each ERP workbook, print a compact extraction summary before merging: chosen sheet, header row, year column, value column, and 3 to 5 sample year→value pairs. Keep this summary concise so final diagnostics remain visible.
- Verify parsed years are clean integers after normalization (for example, labels like `1973.` should become `1973`) and that cleaned year keys are unique before merging.
- Confirm annual and quarterly observations were classified from displayed row labels and active-year context, not from row numbers or brittle heuristics.
- Treat the derived latest-year annual value as unverified until the run shows both the visible quarter coverage in the workbook and the exact captured quarter labels/values used in the average.
- If only one 2024 quarter is captured, manually inspect the following rows to verify whether later quarter rows omit the year label rather than assuming only one quarter exists.
- Treat output such as `2024 average from 1 quarter` as a hard failure checkpoint, not an informational note: do not trust downstream deflation, HP filtering, correlation, or `/root/answer.txt` until you either confirm only one quarter is visible in the workbook or rerun with corrected quarter capture.
- Treat suspicious latest-year diagnostics as a hard stop, not a soft warning: if output shows only 1 captured 2024 quarter when more quarter rows are visibly present, missing expected quarter labels, an unexpected sample span (for example 1973–2023 when 2024 was meant to be included), or any mismatch between claimed and printed coverage, debug extraction and rerun before trusting the correlation.
- If the latest year is represented by quarterly rows, make an explicit include/exclude decision before HP filtering. Include it when the task calls for the latest available data and the workbook provides enough visible quarters to form a defensible annual proxy; otherwise prefer the last completed annual year. Do not let this choice happen implicitly.
- After joining consumption, investment, and CPI by year, print the overlapping year range and count; if the overlap is empty, unexpectedly short, or not 1973–2024 with 52 observations, fix extraction/alignment before continuing.
- Do not hard-code 1973–2024 as the only valid span; compare the overlap against the explicitly chosen sample policy. If you intentionally stayed with completed annual data, expect the overlap to end at the last completed annual year and keep that choice consistent in all downstream diagnostics.
- Before CPI merge, print separate nominal year spans/counts for consumption and investment and a few extracted year/value pairs from each workbook; do not proceed to deflation if either nominal series still looks misparsed or unexpectedly short.
- Before deflation, confirm the CPI/deflator workbook spans the full final year range you plan to analyze; do not discover missing CPI coverage only after merging.
- Before `np.log` or HP filtering, confirm the working arrays are numeric and the CPI-aligned real PCE and real PFI series use the exact same final years.
- After reading from Excel and again after merging with CPI, coerce the value columns with a numeric conversion step (for example `pd.to_numeric(..., errors='raise')` or equivalent) so spreadsheet strings/objects do not silently propagate into deflation, logs, or HP filtering.
- Before computing correlation, inspect the transformed real/log/HP-cycle series for NaNs, infinities, or all-missing output; if any appear, trace back to extraction/merge/deflation issues before finalizing.
- If the HP-filtered cyclical component for either series is entirely missing or obviously degenerate, treat that as an upstream data problem rather than a valid statistical result and debug the pipeline first.
- Keep the preprocessing order exact: nominal extraction → CPI deflation → natural log → HP filter with `lambda=100` → Pearson correlation of cyclical components.
- Treat `/root/answer.txt` as valid only if the immediately preceding end-to-end run completed successfully and produced the same printed correlation.
- Do not treat a truncated console log, a completed script alone, or an existing `/root/answer.txt` as proof of success. The accepted run must visibly reach the correlation print, write the file, read the same value back after the script exits normally, and show no unresolved extraction anomalies.

- After each major stage—nominal extraction, optional 2024 annualization, CPI merge/deflation, and final HP-filter inputs—print and compare the start year, end year, and observation count for both series. If any stage changes the sample unexpectedly, stop and fix the pipeline before computing correlation.
- Do not mix a derived quarterly-based 2024 observation into one stage of the pipeline while describing another stage as annual-only; the reported year range and count must stay internally consistent.
- If annual data are already complete through the intended end year, prefer the direct annual sample over constructing a partial-year proxy from quarterly rows.
- Do not accept `/root/answer.txt` or a printed correlation as evidence of success if intermediate logs show anomalies; first reconcile the quarter labels/values, merged overlap years/count, and final sample span with the source tables.
- Before full implementation, verify that the planned steps are grounded in the task prompt: confirm the requested output, required transformations, and whether latest-year quarterly annualization is actually needed for these sources.

- Before writing the full script, print a one-line plan stating: requested output, whether CPI deflation is needed, whether logs/HP/correlation are needed, and whether latest-year quarterly annualization will be used. If that plan is not supported by both the prompt and workbook inspection, revise it before proceeding.
- Treat year alignment as a hard checkpoint before statistics: confirm consumption years, investment years, and CPI years match exactly on the final analysis sample, then apply deflation, log, HP filter, and correlation on that same common set.
- Before HP filtering, confirm the merged analysis table is one row per year with no duplicate years, and that consumption, investment, and CPI all cover the same final year set.
- Before final computation, explicitly check that the merged working dataset has no missing values in the two real logged series used for HP filtering and that both arrays have identical length/year coverage.
- If you do extend the sample with a derived latest year, print both the pre-extension and post-extension year span/count so it is obvious that only the intended end year changed and the earlier annual history stayed intact.
- When a latest-year annual value is constructed from quarterly rows, compare it to the preceding completed annual value(s) and treat a wildly implausible jump/drop as a cue to re-check quarter capture, value column selection, or averaging logic before continuing.
- If any script run raises a parsing/conversion/alignment error or the visible output is truncated before the final confirmations, debug the issue and require one visibly clean end-to-end rerun before treating the task as complete.
- Treat truncated tool output as non-evidence. When the final correlation or file confirmation is not visible in the log, rerun with shorter diagnostics or redirected output so the successful end state is fully observable.
- Do not carry forward a numeric result from an earlier failed, inferred, hidden, or partially shown run; the accepted result must come from the observable repaired run that prints extracted-year/count diagnostics, final overlap years/count, the correlation, and the fresh `/root/answer.txt` read-back.
- Make the latest-year decision observable and consistent: print whether the final analysis uses completed annual observations only or includes an annualized latest year, then verify the same end year/count appears in the merged nominal data, real series, HP-filter inputs, and final correlation diagnostics.
- Before coding the full pipeline, write a one-line plan in diagnostics: `Method confirmed: ... ; latest-year policy: annual-only / derive from quarters`. If the observed sample boundary later disagrees with that plan, stop and fix the extraction rather than proceeding to correlation.
- If you choose to derive the latest year from quarters, require all of these before keeping it: visible quarter count checked, captured labels/values printed, annualized value computed from exactly those captured rows, and post-conversion span/count reprinted. Otherwise fall back to the completed annual sample.
- Before writing the final answer, compare the printed method summary against the task prompt and source evidence; if they differ on required transformations, statistic, or sample endpoint, rerun with the correct method.

## Validation Checks

- Before computing correlation, inspect the extracted year/value pairs for both series, especially the first/last years and 2024.
- Verify that the selected rows/columns correspond to the intended ERP series: Personal Consumption Expenditures (Total, column 1) and Private Fixed Investment (Total, column 1).
- Confirm that 2024 annual values are computed from all available quarterly observations shown in the source tables, not from a guessed or truncated subset.
- Do not finalize after only checking `/root/answer.txt`; validate the upstream extraction and annualization logic first.
## Output Format

Single number to `/root/answer.txt`

Only use this output format when the task explicitly asks for a single numeric result saved there; otherwise, match the prompt's requested deliverable.

Only trust that file after an observable successful run shows the final correlation and a matching read-back from `/root/answer.txt`.


Before trusting `/root/answer.txt`, verify the computation ran end-to-end: confirm deflation, HP filtering, and correlation steps executed successfully and the script exited normally. If output is truncated or diagnostics stop early, rerun or inspect the error instead of treating an existing answer file as success.

Do not present the number as final unless the immediately preceding observable run printed the correlation and showed a matching read-back from a freshly written `/root/answer.txt`; if the environment also requires a fixed completion string or termination format, emit that exact required final signal after verification.

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
- Keep the inspection concise: sheet names, a few top rows, a known annual sample row, and a few bottom rows are usually enough to map headers/columns and latest-year boundaries without flooding the console.
- When the first quarter row carries the year label and later quarter rows only show `II.`/`III.`/`IV.`, keep collecting only while the active year remains 2024; stop or reset when the table advances to another year/header or to notes/footer text.
- Treat the CPI workbook as data to interpret, not a fixed schema: confirm whether the numeric column is an index level, a deflator, or already normalized to a target year before dividing nominal values.
- If CPI inspection reveals an explicit target-year conversion column, use that inspected field directly and log the chosen column name in the final run output so the deflation basis is unambiguous.
- Prefer a short summary log or redirected output file over long console dumps so the quarter diagnostics, overlap checks, and final correlation remain visible.

- Read [references/partial-latest-year-policy.md](references/partial-latest-year-policy.md) when the newest year is represented by quarterly rows rather than a completed annual observation.

- Spreadsheet extracts often arrive as object dtype even when they look numeric; coerce nominal series, CPI, and merged real arrays to numeric before division, `np.log`, or `hpfilter`.
- Early in the run, confirm the needed libraries/imports work (for example `pandas`, the correct Excel engine, and preferably `statsmodels`) so you can commit to one supported implementation path before building the full script.
- A reliable parsing pattern for these ERP-style tables is: inspect labels first, classify annual vs quarterly rows from the observed text pattern, carry forward the active year across continuation quarter rows, then build a clean year→value mapping before any merge.
- Preserve the robust default workflow when it is actually requested and supported by the files: inspect workbook structure first, extract each ERP series independently, align by year, then apply nominal → CPI-deflated real → log → HP filter → Pearson correlation.
- Preserve the successful workflow: inspect first, extract with concise diagnostics, then run one end-to-end script that can be rerun unchanged after parser fixes.
- A successful run is not just a finished script; it must also keep the declared sample policy consistent with the printed overlap years/count and latest-year diagnostics.


# Economic Time Series Detrending and Correlation

## Execution Protocol

- Before using tools, check the current environment's required action format and completion signal; follow that protocol exactly.
- Treat this skill as analysis guidance only; it does not override the runtime's action protocol, allowed tools, or completion requirements.
- Use concrete executable commands rather than placeholder or narrative pseudo-commands, and avoid unnecessary cleanup commands unless the environment explicitly requires them.
- If the environment requires a specific final completion string, output that exact string after writing and verifying `/root/answer.txt`; do not replace it with a narrative summary.