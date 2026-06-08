---
name: sales-pivot-analysis
description: "Create Excel pivot tables from population and income data for demographic analysis across states and regions."
---

# Sales/Population Pivot Analysis

## When to Use

- Create pivot tables from demographic data
- Analyze population by state and region
- Calculate income quartiles and earnings summaries

## Input Files

- `/root/population.pdf`: Population data
- `/root/income.xlsx`: Income data

**Before writing transformation code, inspect both inputs and record the actual schema** (column names, sample rows, join keys, and row counts). Do not assume PDF-extracted columns match the requested output field names.

- Follow this order strictly: inspect inputs -> extract/clean -> confirm actual headers/types/join keys -> validate merge quality -> build derived columns -> create workbook -> reopen workbook and verify contents.
- For `/root/population.pdf`, inspect at least one representative page before bulk extraction to confirm the real table shape, true column count, repeated-header pattern, and whether headers are truncated; if extracted headers are unclear or shortened (for example `POPULATION_20`), confirm the intended name from raw PDF page text before renaming.
- During PDF extraction, iterate across all pages/tables, remove repeated header rows by row content, skip empty/fragment rows, preserve continuation rows correctly, and normalize the cleaned result into one fixed schema before any merge or aggregation.
- Record which extracted PDF fields map to `STATE`, `SA2_CODE`, `SA2_NAME`, and `POPULATION_2023`; repair confirmed malformed, shifted, or truncated headers immediately after inspection.
- When joining the PDF-derived population data to the income data, prefer the most specific shared identifiers available (typically `SA2_CODE`, with `SA2_NAME` as a cross-check) rather than `STATE`; use `STATE` for reporting/grouping after the merge unless inspection proves no better join key exists.
- Normalize join keys and numeric analysis fields before merging: trim whitespace, standardize `SA2_CODE` to one canonical format on both sides, remove numeric formatting artifacts such as thousands separators, and coerce `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME` to numeric with error coercion.
- After normalization, compare matched vs unmatched counts, confirm the merged row count is plausible, and stop to fix extraction/cleaning/merge issues before building derived fields or summaries if critical records remain unmatched.
- Before creating any workbook sheet, confirm the merged dataset still contains `STATE`, `SA2_CODE`, `SA2_NAME`, `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME`.



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


Build and write the validated merged `SourceData` sheet first as the single enriched source range, then create all requested pivot tables from that shared worksheet data so every summary uses the same cleaned fields and derived columns. Compute `Quarter` once from the global distribution of valid `MEDIAN_INCOME` values across the full merged dataset, then reuse that same `Quarter` field in both `SourceData` and `State Income Quartile`.


### Compliance requirements
- If the task says **pivot tables**, create actual Excel pivot tables in the workbook; do **not** substitute pandas `groupby` outputs or `pd.pivot_table` exports unless the task explicitly allows static summaries.
- Prefer an Excel-native or otherwise end-to-end verifiable method that creates real pivot-table objects in the saved workbook. Use low-level workbook-library pivot internals only if no better option is available and you can prove after save/reopen that the pivot tables exist and are usable.
- Do **not** claim pivot-table success from sheet names, cached cell values, file existence, workbook reload, `_pivots`, or other in-memory metadata alone.

- Match the requested workbook structure exactly: sheet names, row fields, column fields, value fields, and labels must use the task wording verbatim.

- Preserve requested labels exactly. For example, if the task says `Count of SA2 regions`, do not rename it to alternatives such as `SA2 Region Count`.

- For "Population by State", the value must be **Sum of `POPULATION_2023`**. Do **not** replace it with a count of regions/rows/SA2s because population was lost during preprocessing.

- If `POPULATION_2023` is missing from the merged data, stop and fix the extraction/rename/merge upstream before building pivots. Do **not** ship a fallback workbook with a different metric.
- Do not claim completion from partial or truncated execution logs. If save/reload confirmation is missing from tool output, explicitly reopen `/root/demographic_analysis.xlsx` and inspect the workbook before continuing.


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
- Confirm the merge key used to combine sources was standardized consistently on both inputs and that the merged result did not lose rows due to type/format mismatches.
- If population data came from PDF extraction, inspect a few final `SourceData` rows to confirm repeated PDF headers/artifacts were removed and state/region fields were parsed into the intended columns.
- Compare any row counts, matched-record counts, or sheet dimensions you report against the reopened workbook and the latest successful run; if counts disagree, resolve the mismatch before finishing.


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

