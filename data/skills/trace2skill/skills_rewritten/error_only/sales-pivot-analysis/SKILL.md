---
name: sales-pivot-analysis
description: "Create Excel pivot tables from population and income data for demographic analysis across states and regions."
---

# Sales/Population Pivot Analysis

## When to Use

- Create pivot tables from demographic data
- Analyze population by state and region
- Calculate income quartiles and earnings summaries

## Execution discipline

- Show the actual executable command or script for every critical step: input inspection, PDF extraction/cleaning, merge/build logic, workbook generation, and final verification. Do **not** replace these with placeholders such as "ran a validation script" or "generated the workbook".
- Make each major transformation auditable by exposing the code, file path, and key parameters used.


## Input Files

- `/root/population.pdf`: Population data
- `/root/income.xlsx`: Income data

**Before writing transformation code, inspect both inputs and record the actual schema** (column names, sample rows, join keys, and row counts). Do not assume PDF-extracted columns match the requested output field names.

- Follow this order strictly: inspect inputs -> extract/clean -> confirm actual headers/types/join keys -> validate merge quality -> build derived columns -> create workbook -> reopen workbook and verify contents.
- Treat the initial inspection as a hard gate, not a suggestion: do **not** write or run the full extraction/merge/workbook pipeline until you have explicitly inspected both inputs and recorded the real headers, representative rows, and candidate join keys.
- If the first script you are about to run would both inspect and build outputs in one step, stop and split it into an inspection step first and a build step second.
- For `/root/population.pdf`, inspect at least one representative page before bulk extraction to confirm the real table shape, true column count, repeated-header pattern, and whether headers are truncated; if extracted headers are unclear or shortened (for example `POPULATION_20`), confirm the intended name from raw PDF page text before renaming.
- During PDF extraction, iterate across all pages/tables, remove repeated header rows by row content, skip empty/fragment rows, preserve continuation rows correctly, and normalize the cleaned result into one fixed schema before any merge or aggregation.
- Record which extracted PDF fields map to `STATE`, `SA2_CODE`, `SA2_NAME`, and `POPULATION_2023`; repair confirmed malformed, shifted, or truncated headers immediately after inspection.
- Preserve the observed source schema unless you have explicit evidence for a rename. If the PDF/extracted field is observed as `POPULATION_20` (or another variant), either keep that exact name through processing or document the validated mapping to `POPULATION_2023` from the source text before using the renamed field downstream.
- Do **not** silently switch column names between inspection, merge, and workbook creation. Wrong: inspect `POPULATION_20` then later build outputs with `POPULATION_2023` without evidence. Right: confirm from PDF text that `POPULATION_20` is the 2023 population field, rename once, and use that confirmed name consistently thereafter.

- When joining the PDF-derived population data to the income data, prefer the most specific shared identifiers available (typically `SA2_CODE`, with `SA2_NAME` as a cross-check) rather than `STATE`; use `STATE` for reporting/grouping after the merge unless inspection proves no better join key exists.
- Normalize join keys and numeric analysis fields before merging: trim whitespace, standardize `SA2_CODE` to one canonical format on both sides, remove numeric formatting artifacts such as thousands separators, and coerce `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME` to numeric with error coercion.
- Before any merge, explicitly compare the chosen join columns on both sides for **name, dtype, sample values, and formatting**. Convert both keys to the same canonical representation first (typically trimmed string form for `SA2_CODE`); do **not** rely on pandas to reconcile integer-vs-string or differently formatted identifiers during `merge()`.
- Before any quartile, total, or aggregation logic, explicitly verify that `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME` are numeric-compatible on the merged dataset; if coercion introduces unexpected nulls, mixed types, or implausible values, fix that before continuing.
- After normalization, compare matched vs unmatched counts, confirm the merged row count is plausible, and stop to fix extraction/cleaning/merge issues before building derived fields or summaries if critical records remain unmatched.
- Before creating any workbook sheet, confirm the merged dataset still contains `STATE`, `SA2_CODE`, `SA2_NAME`, `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME`.
- **Stop condition before coding/building:** Do not write the main transformation script or workbook-generation logic until you have inspected actual samples from both inputs (at least one representative PDF extraction result and one Excel sample), confirmed the real schema, and checked nulls/dtypes for every field used in joins, quartiles, and totals.
- Before quartile assignment with `qcut` or equivalent, verify that `MEDIAN_INCOME` has been coerced to numeric successfully, has enough non-null rows, and has sufficient value variation for 4 bins. If not, fix preprocessing first instead of letting the workflow fail during binning.



- Use these exact absolute paths when reading inputs; do not substitute relative paths.

- Reuse the provided absolute paths verbatim for every read/write step (`/root/population.pdf`, `/root/income.xlsx`, `/root/demographic_analysis.xlsx`). Do **not** switch to relative paths or save ad hoc intermediates in other directories such as `/tmp` unless the task explicitly permits it.

- Keep outputs in the specified destination path; avoid ad hoc intermediates in other directories unless the task explicitly allows them.


## Output

`/root/demographic_analysis.xlsx` with 5 sheets:

**Required source fields before building summaries:** `STATE`, `SA2_CODE`, `SA2_NAME`, `POPULATION_2023`, `EARNERS`, `MEDIAN_INCOME` (plus any other original fields carried into `SourceData`). If a required field is missing, fix the extraction/merge first.

**Pre-build data gate:** Before creating the workbook, confirm the extracted/merged dataset has expected row counts, complete state names, sensible join results, and the intended population field name from PDF source text. If PDF headers are truncated, repeated header rows leaked into data, `STATE` values are split/truncated, or join checks show unmatched critical records, stop and fix extraction/cleaning/merge before building any summary sheet.


### 1. "Population by State"
- Rows: STATE
- Values: Sum of POPULATION_2023

### 2. "Earners by State"
- Rows: STATE
- Values: Sum of EARNERS

### 3. "Regions by State"
- Rows: STATE
- Values: Count of SA2 regions

### 4. "State Income Quartile"
- Rows: STATE
- Columns: Q1, Q2, Q3, Q4 (based on MEDIAN_INCOME)
- Values: Sum of EARNERS

### 5. "SourceData"
- Original data enriched with:
  - Quarter (Q1-Q4 based on MEDIAN_INCOME)
  - Total = EARNERS × MEDIAN_INCOME

- Do not reinterpret `Total` as a custom business metric or use any other formula. Use the task-defined `EARNERS × MEDIAN_INCOME` definition verbatim; if the requirement seems ambiguous, stop and resolve that before adding the column.


Build and write the validated merged `SourceData` sheet first as the single enriched source range, then create all requested pivot tables from that shared worksheet data so every summary uses the same cleaned fields and derived columns. Compute `Quarter` once from the global distribution of valid `MEDIAN_INCOME` values across the full merged dataset, then reuse that same `Quarter` field in both `SourceData` and `State Income Quartile`.

- Before quartile assignment, explicitly coerce `MEDIAN_INCOME` to numeric and inspect how many values are valid vs blank/NaN; compute quartiles only from the valid numeric subset.
- Do **not** repair quartile or total-calculation errors by dropping source rows from `SourceData`. Keep all merged rows, leave `Quarter` and/or `Total` blank where inputs are invalid, and exclude only those invalid values from the specific calculation that requires numeric input.
- If a numeric-conversion step changes usable-row counts materially, record both counts and verify the workbook still preserves the full merged dataset in `SourceData`.


### Compliance requirements
- If the task says **pivot tables**, create actual Excel pivot tables in the workbook; do **not** substitute pandas `groupby` outputs or `pd.pivot_table` exports unless the task explicitly allows static summaries.
- Prefer an Excel-native or otherwise end-to-end verifiable method that creates real pivot-table objects in the saved workbook. Use low-level workbook-library pivot internals only if no better option is available and you can prove after save/reopen that the pivot tables exist and are usable.
- Do **not** claim pivot-table success from sheet names, cached cell values, file existence, workbook reload, `_pivots`, or other in-memory metadata alone.

- Match the requested workbook structure exactly: sheet names, row fields, column fields, value fields, and labels must use the task wording verbatim.

- Preserve requested labels exactly. For example, if the task says `Count of SA2 regions`, do not rename it to alternatives such as `SA2 Region Count`.

- For "Population by State", the value must be **Sum of `POPULATION_2023`**. Do **not** replace it with a count of regions/rows/SA2s because population was lost during preprocessing.

- If `POPULATION_2023` is missing from the merged data, stop and fix the extraction/rename/merge upstream before building pivots. Do **not** ship a fallback workbook with a different metric.
- Do not claim completion from partial or truncated execution logs. If save/reload confirmation is missing from tool output, explicitly reopen `/root/demographic_analysis.xlsx` and inspect the workbook before continuing.

- Treat post-save sheet content as a hard gate: if any required summary sheet reopens as empty/placeholder content (for example dimension `1x1`, only cell `A1`, headers without data, or a pivot shell with no populated results), the workbook is **not** complete.
- Do **not** finalize with instructions such as "Refresh All" or other manual follow-up to make required summaries appear. The saved `/root/demographic_analysis.xlsx` must already contain the requested populated report outputs when reopened.
- If your chosen pivot-writing method does not persist usable populated summaries after save/reopen, switch methods before finishing: either create working real pivot tables that survive reopen **or** ask for a task-permitted static-summary alternative. Do not claim success while reopened report sheets remain blank.


### SourceData preservation rule
- `SourceData` must preserve the original merged data and original source columns used for analysis; then append derived columns such as `Quarter` and `Total`.
- Keep all original income rows in `SourceData`; enrich them with new columns rather than deleting records.
- If `MEDIAN_INCOME` or `EARNERS` is invalid, coerce to blank/NaN for calculations, but preserve the original row in `SourceData`.
- Only exclude invalid rows from specific derived computations when necessary; do not shrink the underlying source dataset.

- Record the original source row count before cleaning/merge steps and verify `SourceData` preserves those source records unless the task explicitly authorizes deletions.
- Build the full enriched dataset first: merge source inputs, preserve original columns/rows, append `Quarter` and `Total`, and only after that create workbook summaries/pivot tables from that same `SourceData` range.
- If numeric coercion is needed, use blank/NaN for invalid `POPULATION_2023`, `EARNERS`, or `MEDIAN_INCOME` values in calculations but preserve the original row in `SourceData`.
- If the primary join key leaves unmatched rows, use a controlled fallback match only for those previously unmatched rows and only when the fallback mapping is validated and unambiguous; do not overwrite successful primary-key matches.




## Verification Before Completion

- Compare `SourceData` row count against the preserved source dataset row count; investigate any unexpected drop before finishing.

- If you changed numeric cleaning, quartile logic, or error handling after a runtime failure, explicitly verify that `SourceData` still preserves the pre-build merged row count and that invalid numeric inputs were handled as blanks/NaN rather than removed unless the task explicitly authorizes deletions.
- Inspect actual values after reopen, not just workbook existence: check a few `SourceData` rows with invalid or blank numeric fields, confirm `Quarter` is blank for invalid `MEDIAN_INCOME` rows, and confirm `Total` is blank when either factor is invalid.
- Validate output semantics after any repair that affected data eligibility: compare at least one key aggregate from the reopened workbook against the in-memory prepared data (for example total `SourceData` rows and one state-level population/earners summary).
- Confirm the merge key used to combine sources was standardized consistently on both inputs and that the merged result did not lose rows due to type/format mismatches.
- If population data came from PDF extraction, inspect a few final `SourceData` rows to confirm repeated PDF headers/artifacts were removed and state/region fields were parsed into the intended columns.
- Compare any row counts, matched-record counts, or sheet dimensions you report against the reopened workbook and the latest successful run; if counts disagree, resolve the mismatch before finishing.

### Evidence-only execution rule
- Treat truncated, cut-off, or partial tool output as **no proof of success**. If a command result ends mid-script, mid-print, or without a clear completion signal, rerun or perform a direct verification step before proceeding.
- Before claiming the workbook was created or updated, directly verify `/root/demographic_analysis.xlsx` exists and then reopen that exact file and inspect its sheets.
- Do **not** infer specific failure causes without explicit evidence. Base any diagnosis on the actual observed error/output; if no concrete error is shown, say verification is incomplete and gather more evidence first.
- Do **not** describe workbook contents, pivot presence, or sheet results unless those details were confirmed from the saved file after execution.

- Treat any traceback, exception, or partially failed diagnostic during extraction, cleaning, merge validation, numeric coercion, or quartile checks as a stop condition. Do **not** continue to workbook creation or final verification until you fix the issue and rerun the failed check successfully.
- Inspect workbook contents semantically, not just structurally: open `SourceData` and at least one representative row/value area in each summary sheet to confirm the requested metrics, labels, and populated results are actually present.
- Do **not** stop at file existence, workbook load success, or sheet-name checks; verify row counts, derived-column values, and summary values/headers inside the saved workbook.
- If any verification output is truncated, cut off, or only partially shows sheet names/contents, treat verification as incomplete; rerun a narrower inspection until every required sheet and key content check is fully visible.
- Reconcile counts across the workflow: extracted PDF rows, cleaned population rows, income rows, merged rows, and final `SourceData` rows must be explainable. Investigate any off-by-one, unexpected increase, or row-count decrease before finishing.
- Specifically rule out repeated PDF headers, duplicated joins, dropped unmatched rows, accidental filtering, or deduplication side effects as causes of unexpected row counts or leaked header rows in `SourceData`.
- If any earlier workbook build, import, or save attempt failed, treat all prior verification as invalid. Regenerate `/root/demographic_analysis.xlsx`, reopen the final file from disk, and rerun the full checklist against that final successful artifact before declaring completion.
- Verify requirement-by-requirement against the task spec before finishing; do not stop at sheet names, sample previews, or file existence.
- Explicitly confirm and, if needed, inspect for: exact sheet names, exact requested Rows/Columns/Values layout, presence of `Quarter` and `Total` in `SourceData`, `Population by State` using **Sum of `POPULATION_2023`**, and whether the workbook contains actual Excel pivot tables when the task requires pivots.
- Explicitly inspect each summary sheet after reopen for substantive populated output; sheet existence alone is insufficient. A reopened summary sheet with only one cell or only placeholder headers means the deliverable failed and must be rebuilt.
- Never rely on in-Excel manual refresh, deferred rendering, or user cleanup to complete required sheets.
- Before finalizing, re-check the active task/system instructions for any required completion or handoff format and follow that exact syntax literally; do not substitute a narrative success message for a mandated completion signal.
- If any key requirement remains uncertain after reopen/inspection, treat the task as unfinished: fix, regenerate, reopen, and re-check.


## Verification Before Completion

Before declaring the task done, reopen `/root/demographic_analysis.xlsx` and verify all of the following:
- Workbook contains exactly these sheets: `Population by State`, `Earners by State`, `Regions by State`, `State Income Quartile`, `SourceData`
- `SourceData` retains the original source rows/columns needed for analysis and includes the derived columns `Quarter` and `Total`
- `Quarter` values are labeled `Q1`-`Q4` based on `MEDIAN_INCOME`
- `Total` is calculated as `EARNERS × MEDIAN_INCOME` where both inputs are valid
- Each summary sheet matches the requested Rows / Columns / Values layout from the `## Output` section and contains readable headers plus non-empty results
- `Population by State` uses sum of `POPULATION_2023`, not a fallback count metric
- Do not treat a successful script run, file creation, workbook reload alone, or pivot metadata as proof the workbook is correct; inspect the produced sheet contents themselves

## Tips

- openpyxl for Excel creation
- Use pandas for data processing
- Create pivot tables with proper structure
- Handle quartile calculations correctly


- Inspect the PDF extraction result and Excel sheet headers first; confirm the real column names before building merges or summaries.

- For semi-structured PDF tables, prefer a targeted parser based on the observed layout over naive full-table extraction.
- If the PDF sample shows a stable narrow layout, extract only the validated columns you need and discard overflow columns created by wrapped text.

- Validate extraction and merge quality before building summaries: confirm expected headers, row counts, join keys, and unmatched records after joining PDF and Excel data.

- Explicitly compare join-key dtypes/formats before merging; do not rely on pandas to reconcile numeric vs string identifiers automatically.
- Quantify join quality explicitly: compare unique `SA2_CODE` coverage between sources and inspect unmatched records before deciding the merge is usable.
- Immediately after merging on the chosen key, count unmatched or null values in critical fields such as `STATE` and `POPULATION_2023`; fix the join before building pivots if those checks fail.

- When extracting population data from `/root/population.pdf`, validate key grouping fields before aggregation. If `STATE` values look truncated or inconsistent (for example `New South W`), fix the extraction/cleaning before creating any state-based output.

- Treat visibly truncated grouping keys as a stop condition, not a warning: do not build pivots or summaries keyed by `STATE` until those values are repaired and standardized.

- Before computing summaries keyed by `STATE`, check that state names are complete and standardized so identical states are not split into separate groups.
- Before creating summaries, verify the merged dataset still contains every field needed by the workbook spec, especially `POPULATION_2023` for the population sheet.

- Build one cleaned, merged, enriched source table first; then create every workbook sheet and pivot from that same source table rather than mixing separate intermediate datasets.
- Consolidate only the needed population fields into a single clean dataframe before joining; do not merge directly from raw PDF table fragments.

- Convert `EARNERS`, `MEDIAN_INCOME`, and `POPULATION_2023` to numeric before quartile assignment, totals, or pivot aggregation; then build `Quarter` from global `MEDIAN_INCOME` quartiles on the merged dataset and `Total = EARNERS × MEDIAN_INCOME`.
- If quartile, comparison, or arithmetic logic raises a mixed-type error (for example `int` vs `str`), diagnose the exact input columns before applying a broad patch: inspect dtypes, sample non-numeric values, then rerun `pd.to_numeric(..., errors='coerce')` on the specific fields used by that computation.
- Before regenerating the workbook after a numeric-type fix, explicitly confirm that `MEDIAN_INCOME`, `EARNERS`, and `POPULATION_2023` are numeric/NaN in the cleaned dataframe and that `Quarter`/`Total` can be computed on sample rows without type errors.
- Treat `pandas.pivot_table` as a data-prep helper only; it does not create an Excel pivot-table object.

- If you use any method to create Excel pivot tables, prove it worked by reopening the saved workbook and checking the resulting sheet contents. Do not rely on object creation, cache metadata, or save-time success alone.

- Avoid fragile low-level openpyxl pivot internals such as `TableDefinition`, `CacheDefinition`, `openpyxl.pivot.*`, or `ws._pivots` unless no better option is available and you can verify after save/reload that the resulting workbook still contains functional pivot tables.
- When verification output is inconclusive, treat the task as unfinished; do not infer that pivots will appear later without direct evidence.
- Prefer workbook outputs you can verify after save/reload; do not treat file existence, sheet names alone, or in-memory pivot metadata as proof of success.
- Do **not** drop rows just to make quartile or total calculations succeed; preserve rows and leave derived fields blank where inputs are invalid.
- After any runtime fix or data-cleaning change, regenerate the workbook and repeat the full verification checklist before finishing.

- When extracting tables from `/root/population.pdf`, detect and remove repeated page header rows before merging or aggregating, then assemble one cleaned population table from all PDF pages first.
- Before computing quartiles, totals, or pivot values, coerce `MEDIAN_INCOME`, `EARNERS`, and any extracted population measure to true numeric types; treat non-numeric values as blank/NaN for derived calculations while preserving the original rows.
- Create all summary pivot tables from the single enriched `SourceData` range rather than rebuilding separate intermediate summary tables for each sheet.
- If you apply a fallback join or fill step after the main merge, verify that it affects only previously unmatched rows and does not create duplicate or conflicting state assignments.
- Prefer one reproducible script for the full workflow so fixes can be applied and the workbook regenerated consistently.
- Use row counts, unmatched-join counts, and output-file existence as early sanity checks only; they do **not** replace reopening the workbook and inspecting actual sheet contents against the requested layout.
- After any exception-driven code patch, treat the next workbook as a fresh deliverable: save it, reopen it from disk, and inspect the produced sheets again end to end before finishing.
- If you choose to generate actual Excel pivot-table objects with openpyxl, read [references/openpyxl-pivot-cache-pattern.md](references/openpyxl-pivot-cache-pattern.md) first for the workbook-compatibility pattern to use.



## New Section

## Environment Protocol Override

- Follow the active environment/system interaction protocol exactly. If the session requires a specific `Thought:` / `Action:` format, JSON action schema, or one exact completion token, use that format for **every** tool call and for task completion.
- Treat protocol instructions as hard requirements that override this skill's workflow guidance. Do **not** invent alternate tool-call syntax, XML-style tags, or free-form action text.
- For shell/tool usage, provide literal executable commands only. Do **not** write intent descriptions such as `check the generated workbook file` or `remove temporary helper scripts`; write the exact command to run.
- If the environment specifies an exact completion string, finish with that exact string only after all workbook verification is complete.