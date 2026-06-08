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
- Before the first tool call or command, check the active environment protocol and mirror its required action syntax exactly for every step. If the environment mandates a specific completion token, emit that exact token only after all verification passes.
- Use a lightweight inspect-then-build pattern that has worked reliably: first print actual PDF/Excel headers, worksheet names where applicable, sample rows, row counts, observed dtypes/nulls for join and numeric fields, and candidate join-key values; then run one reproducible end-to-end build script for extract/clean/merge/enrich/workbook creation; then reopen the saved file and inspect sheet contents.
- In that build script, print concrete checkpoints such as extracted population row counts, cleaned population row counts, income row counts, merged row counts, unmatched-key counts, valid `MEDIAN_INCOME` count used for quartiles, and the final save path; use these as early sanity checks, not as a substitute for reopening the workbook.
- Do **not** summarize critical work with placeholders such as `ran a validation script`, `generated the workbook`, or `checked the PDF`. Show the literal executable shell command or inline script content that performed the step, including file paths and relevant arguments.
- Before changing any observed source column name, write down a one-line rename map from inspected header -> validated working name and the evidence for it. If you cannot validate the rename from the source text or inspected file, keep the observed header unchanged downstream.
- In that main script, follow this stable sequence: normalize extracted source tables -> validate join keys/types -> merge once into the preserved source dataset -> add `Quarter` and `Total` -> write `SourceData` -> create all summary sheets/pivots from that same source range -> save -> reopen and inspect.


## Input Files

- `/root/population.pdf`: Population data
- `/root/income.xlsx`: Income data

**Before writing transformation code, inspect both inputs and record the actual schema** (column names, sample rows, join keys, and row counts). Do not assume PDF-extracted columns match the requested output field names.
- For `/root/income.xlsx`, inspect the workbook's actual worksheet names first, then identify which sheet contains the income data used for analysis. If there are multiple relevant sheets, do **not** assume the first sheet or a guessed sheet name is correct; verify which sheet contains `SA2_CODE`, `SA2_NAME`, `STATE`, `EARNERS`, and `MEDIAN_INCOME` (or their observed source equivalents), then use that same sheet explicitly in the build script.
- Record a short inspection record before building anything: observed columns, 3-5 sample rows, row count, candidate keys, and join-key dtypes/formats for both sources; then state the chosen merge key explicitly and why it is valid.

- Follow this order strictly: inspect inputs -> extract/clean -> confirm actual headers/types/join keys -> validate merge quality -> build derived columns -> create workbook -> reopen workbook and verify contents.
- Treat the initial inspection as a hard gate, not a suggestion: do **not** write or run the full extraction/merge/workbook pipeline until you have explicitly inspected both inputs and recorded the real headers, representative rows, and candidate join keys.
- If the first script you are about to run would both inspect and build outputs in one step, stop and split it into an inspection step first and a build step second.
- Treat missing inspection evidence as a stop condition. If you have not yet displayed the real extracted samples, worksheet names where applicable, and field properties, do **not** write the full transformation/workbook-generation script.
- After the inspection gate is satisfied, use a two-phase workflow: (1) inspect and prepare one validated merged dataset, then write `SourceData`; (2) build all summary/pivot sheets from that same enriched source dataset. Do **not** mix inspection, merge repair, and final workbook generation in one opaque step.
- A good pattern is: quick inspection command(s) first to capture real schema and join keys, then one main script for the complete pipeline. Rerun that same script after fixes instead of patching the workbook manually or mixing ad hoc partial steps.
- For `/root/population.pdf`, inspect at least one representative page before bulk extraction to confirm the real table shape, true column count, repeated-header pattern, and whether headers are truncated; if extracted headers are unclear or shortened (for example `POPULATION_20`), confirm the intended name from raw PDF page text before renaming.
- Start PDF work with a brief structural audit: record page count, representative table count/layout, whether there are repeated page-header rows, whether row lengths are consistent, and whether the document repeats one stable narrow table pattern across pages before choosing the extraction approach.
- If that audit shows a stable repeated layout, prefer a targeted parser for the validated columns and lock the parser to that validated shape before bulk extraction so malformed overflow/wrapped columns do not leak into the merged dataset.
- When PDF-extracted headers are truncated, ambiguous, or shifted, confirm the intended field names from raw page text before renaming or merging; perform one explicit validated rename/mapping and keep the confirmed name consistent afterward.
- During PDF extraction, iterate across all pages and across all tables returned on each page rather than assuming one table per page. Remove repeated header rows by row content, skip empty/fragment rows, preserve continuation rows correctly, and normalize the cleaned result into one fixed schema before any merge or aggregation.
- Record which extracted PDF fields map to `STATE`, `SA2_CODE`, `SA2_NAME`, and `POPULATION_2023`; repair confirmed malformed, shifted, or truncated headers immediately after inspection.
- Preserve the observed source schema unless you have explicit evidence for a rename. If the PDF/extracted field is observed as `POPULATION_20` (or another variant), either keep that exact name through processing or document the validated mapping to `POPULATION_2023` from the source text before using the renamed field downstream.
- Do **not** silently switch column names between inspection, merge, and workbook creation. Wrong: inspect `POPULATION_20` then later build outputs with `POPULATION_2023` without evidence. Right: confirm from PDF text that `POPULATION_20` is the 2023 population field, rename once, and use that confirmed name consistently thereafter.
- Create exactly one schema map immediately after inspection for any confirmed renames (for example `POPULATION_20 -> POPULATION_2023` only if validated from source text). Normalize any confirmed headers immediately and only once near ingestion time, then keep that schema stable through merge, enrichment, workbook creation, and verification.
- Record a short schema checkpoint before writing the main build script: final column names to use, join key(s), row counts seen in each source, and representative merge-key values on both sides.

- When joining the PDF-derived population data to the income data, prefer the most specific shared identifiers available (typically `SA2_CODE`, with `SA2_NAME` as a cross-check) rather than `STATE`; use `STATE` for reporting/grouping after the merge unless inspection proves no better join key exists.
- Normalize join keys and numeric analysis fields before merging: trim whitespace, standardize `SA2_CODE` to one canonical format on both sides, remove numeric formatting artifacts such as thousands separators, and coerce `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME` to numeric with error coercion.
- Immediately after extraction/ingest, standardize the fields used in joins and calculations before any quartile, arithmetic, or pivot logic: normalize `SA2_CODE`, remove numeric-formatting artifacts, and coerce `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME` to numeric/NaN in the working dataframes.
- During inspection and cleaning, explicitly look for non-numeric placeholder/suppression markers in numeric fields (for example `np`, `N/P`, blanks, or dash-like sentinels). Convert only those placeholders to blank/NaN, preserve the original row, and record a few concrete offending values so later coercion results are explainable.
- After this early normalization, inspect and report dtypes plus a few sample values for the chosen join fields and key numeric fields before continuing.
- Before any merge, explicitly compare the chosen join columns on both sides for **name, dtype, sample values, and formatting**. Convert both keys to the same canonical representation first (typically trimmed string form for `SA2_CODE`); do **not** rely on pandas to reconcile integer-vs-string or differently formatted identifiers during `merge()`.
- Before any quartile, total, or aggregation logic, explicitly verify that `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME` are numeric-compatible on the merged dataset; if coercion introduces unexpected nulls, mixed types, or implausible values, fix that before continuing.
- After normalization, compare matched vs unmatched counts, confirm the merged row count is plausible, and stop to fix extraction/cleaning/merge issues before building derived fields or summaries if critical records remain unmatched.
- Before choosing the merge strategy, quantify source coverage on the candidate key(s): report total rows and distinct `SA2_CODE` counts from the cleaned PDF data and from the selected income sheet, plus how many keys overlap. Do **not** assume both files cover the same universe.
- Run a concrete pre-merge audit on the chosen key: print each side's join-column name, dtype, 3-5 sample values, unique-key count, chosen join key, matched rows, unmatched-left rows, unmatched-right keys if checked, 3-5 sample matched keys, and post-merge rows missing imported `STATE` or `POPULATION_2023`. Treat unexpected nulls in those imported fields as evidence the join is not ready for workbook generation.
- If the PDF/reference source covers only a subset of income rows, preserve the full income-side dataset in `SourceData` and treat population/state enrichment as partial unless a validated fallback fills previously unmatched rows.
- Before creating any workbook sheet, confirm the merged dataset still contains `STATE`, `SA2_CODE`, `SA2_NAME`, `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME`.
- **Stop condition before coding/building:** Do not write the main transformation script or workbook-generation logic until you have inspected actual samples from both inputs (at least one representative PDF extraction result and one Excel sample), confirmed the real schema, and checked nulls/dtypes for every field used in joins, quartiles, and totals.
- Use a short pre-build audit and record the results explicitly: `(1)` cleaned PDF row count and normalized columns, `(2)` income row count and key columns, `(3)` chosen join key plus dtype/format normalization on both sides, `(4)` matched vs unmatched merge counts, `(5)` final merged column list. Do not proceed to workbook generation until all five checks pass.
- Before quartile assignment with `qcut` or equivalent, verify that `MEDIAN_INCOME` has been coerced to numeric successfully, has enough non-null rows, and has sufficient value variation for 4 bins. If not, fix preprocessing first instead of letting the workflow fail during binning.



- Use these exact absolute paths when reading inputs; do not substitute relative paths.

- Reuse the provided absolute paths verbatim for every read/write step (`/root/population.pdf`, `/root/income.xlsx`, `/root/demographic_analysis.xlsx`). Do **not** switch to relative paths or save ad hoc intermediates in other directories such as `/tmp` unless the task explicitly permits it.

- Keep outputs in the specified destination path; avoid ad hoc intermediates in other directories unless the task explicitly allows them.


## Output

`/root/demographic_analysis.xlsx` with 5 sheets:

**Required source fields before building summaries:** `STATE`, `SA2_CODE`, `SA2_NAME`, `POPULATION_2023`, `EARNERS`, `MEDIAN_INCOME` (plus any other original fields carried into `SourceData`). If a required field is missing, fix the extraction/merge first.

**Pre-build data gate:** Before creating the workbook, confirm the extracted/merged dataset has expected row counts, complete state names, sensible join results, and the intended population field name from PDF source text. If PDF headers are truncated, repeated header rows leaked into data, `STATE` values are split/truncated, or join checks show unmatched critical records, stop and fix extraction/cleaning/merge before building any summary sheet.
**Required pre-build schema checkpoint:** Immediately before workbook generation, print and verify the final merged dataframe columns, dtypes, row count, and a few sample rows for `STATE`, `SA2_CODE`, `SA2_NAME`, `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME`. Do **not** proceed if any required field is missing, mislabeled, or still in the wrong dtype/format for the requested summaries.


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
- Before workbook generation, confirm the merged dataset is analysis-ready by checking the exact final schema after enrichment: required source fields are present and derived columns `Quarter` and `Total` can be computed on sample rows without type errors.
- Distinguish **row preservation** from **calculation eligibility**: keep the full merged dataset in `SourceData`, but for quartiles, totals, and pivot value aggregation, operate only on rows whose required numeric inputs are valid after coercion.
- Before workbook creation, explicitly count how many rows are preserved in `SourceData` versus how many rows are eligible for `Quarter`, `Total`, and each value aggregation; use that distinction consistently in verification.
- Treat that enriched merged dataframe as the only reporting source: do not rebuild separate summary-specific datasets with different filters, joins, or field names once `SourceData` is finalized.
- Keep this separation visible in the audit trail: show the command/script that writes `SourceData`, then the command/script that adds summary sheets or pivot tables. If you regenerate after a fix, rebuild both phases against the corrected merged dataset.

- Before quartile assignment, explicitly coerce `MEDIAN_INCOME` to numeric and inspect how many values are valid vs blank/NaN; compute quartiles only from the valid numeric subset.
- Use this exact gate before quartiles: inspect dtype and sample values for `MEDIAN_INCOME` -> run `pd.to_numeric(..., errors='coerce')` on the column -> count valid vs invalid rows -> confirm enough distinct numeric values exist for 4 bins -> only then run `qcut` or equivalent.
- Normalize numeric-looking analysis fields early in the prepared dataframe, before quartiles, totals, or pivots: remove formatting artifacts, run `pd.to_numeric(..., errors='coerce')` on `POPULATION_2023`, `EARNERS`, and `MEDIAN_INCOME`, then print dtypes plus valid/null counts for those exact columns before deriving `Quarter` or `Total`.
- Do **not** repair quartile or total-calculation errors by dropping source rows from `SourceData`. Keep all merged rows, leave `Quarter` and/or `Total` blank where inputs are invalid, and exclude only those invalid values from the specific calculation that requires numeric input.
- If a numeric-conversion step changes usable-row counts materially, record both counts and verify the workbook still preserves the full merged dataset in `SourceData`.


### Compliance requirements
- If the task says **pivot tables**, create actual Excel pivot tables in the workbook; do **not** substitute pandas `groupby` outputs or `pd.pivot_table` exports unless the task explicitly allows static summaries.
- Decide the pivot path explicitly before workbook generation: either use a method that can create **real Excel pivot-table objects** and plan to prove them after save/reopen, or, if no such verifiable method is available in the environment, stop and request or report the need for a task-permitted static-summary alternative. Do **not** build static sheets first and then describe them as pivots.
- Use `pd.pivot_table` or `groupby` only as validation helpers to cross-check expected totals/layout, not as the deliverable when the task explicitly requires Excel pivot tables.
- Prefer an Excel-native or otherwise end-to-end verifiable method that creates real pivot-table objects in the saved workbook. Use low-level workbook-library pivot internals only if no better option is available and you can prove after save/reopen that the pivot tables exist and are usable.
- Choose the pivot-generation method before coding the full build. If you cannot name a concrete method that is likely to persist real Excel pivot tables after save/reopen, stop and either switch methods or request a task-permitted static-summary fallback; do **not** spend the run building pandas summaries and later present them as pivots.
- Keep the workflow reproducible: after the required inspection/validation gate, prefer one end-to-end script that performs extraction, cleaning, merge validation, enrichment, workbook generation, save, reopen, and content checks in the same run.
- If you use openpyxl for real pivot tables, treat it as a high-risk path: read [references/openpyxl-pivot-cache-pattern.md](references/openpyxl-pivot-cache-pattern.md) first, reuse one shared cache for all pivots from `SourceData`, and reject the result unless the reopened workbook shows populated summary output on every required report sheet.
- Do **not** claim pivot-table success from sheet names, cached cell values, file existence, workbook reload, `_pivots`, or other in-memory metadata alone.

- To claim **actual Excel pivot tables** exist, capture explicit persisted evidence after reopen from the saved file itself, such as workbook package parts/relationships showing pivot-table definitions and caches, together with populated pivot report sheets. Populated static-looking sheets alone do not prove persisted pivot objects.
- Keep two claims separate in verification: (1) the reopened workbook shows the requested populated report layout, and (2) real Excel pivot-table objects persist in the saved file. Do not collapse these into one claim unless you verified both.
- Match the requested workbook structure exactly: sheet names, row fields, column fields, value fields, and labels must use the task wording verbatim.

- Preserve requested labels exactly. For example, if the task says `Count of SA2 regions`, do not rename it to alternatives such as `SA2 Region Count`.

- For "Population by State", the value must be **Sum of `POPULATION_2023`**. Do **not** replace it with a count of regions/rows/SA2s because population was lost during preprocessing.

- If `POPULATION_2023` is missing from the merged data, stop and fix the extraction/rename/merge upstream before building pivots. Do **not** ship a fallback workbook with a different metric.
- Do not claim completion from partial or truncated execution logs. If save/reload confirmation is missing from tool output, explicitly reopen `/root/demographic_analysis.xlsx` and inspect the workbook before continuing.

- Treat post-save sheet content as a hard gate: if any required summary sheet reopens as empty/placeholder content (for example dimension `1x1`, only cell `A1`, headers without data, or a pivot shell with no populated results), the workbook is **not** complete.
- Do **not** finalize with instructions such as "Refresh All" or other manual follow-up to make required summaries appear. The saved `/root/demographic_analysis.xlsx` must already contain the requested populated report outputs when reopened.
- If your chosen pivot-writing method does not persist usable populated summaries after save/reopen, switch methods before finishing: either create working real pivot tables that survive reopen **or** ask for a task-permitted static-summary alternative. Do not claim success while reopened report sheets remain blank.
- If reopen shows any required summary sheet as `1x1`, only `A1`, placeholder headers, blank tables, or otherwise unpopulated, treat that as a hard failure of the generation method. Rebuild the workbook with a method that produces populated saved output; do **not** hand off a file that depends on Excel `Refresh All` or any user action.
- When the task requires pivots but your chosen library path cannot persist visible populated pivot results, do **not** claim pivot success from object creation alone. Switch to a verifiable pivot-capable method or explicitly request permission for static summaries only if the task allows it.


### SourceData preservation rule
- `SourceData` must preserve the original merged data and original source columns used for analysis; then append derived columns such as `Quarter` and `Total`.
- Keep all original income rows in `SourceData`; enrich them with new columns rather than deleting records.
- If `MEDIAN_INCOME` or `EARNERS` is invalid, coerce to blank/NaN for calculations, but preserve the original row in `SourceData`.
- Only exclude invalid rows from specific derived computations when necessary; do not shrink the underlying source dataset.

- Record the original source row count before cleaning/merge steps and verify `SourceData` preserves those source records unless the task explicitly authorizes deletions.
- Build the full enriched dataset first: merge source inputs, preserve original columns/rows, append `Quarter` and `Total`, and only after that create workbook summaries/pivot tables from that same `SourceData` range.
- If numeric coercion is needed, use blank/NaN for invalid `POPULATION_2023`, `EARNERS`, or `MEDIAN_INCOME` values in calculations but preserve the original row in `SourceData`.
- If the primary join key leaves unmatched rows, use a controlled fallback match only for those previously unmatched rows and only when the fallback mapping is validated and unambiguous; do not overwrite successful primary-key matches.
- If you apply any fallback join or identifier-pattern recovery, validate it on known rows first, then apply it only to previously unresolved records. Verify it preserves pre-fallback matched rows exactly, does not introduce duplicate `SA2_CODE` assignments, and does not overwrite existing validated `STATE` or `SA2_NAME` values.

- Treat any material row-count drop between income source rows, merged rows, and final `SourceData` rows as a blocking issue. Before finishing, quantify each drop, inspect unmatched keys and any filters/deduplication that caused it, and either fix the pipeline or explicitly verify that the reduction is task-authorized and does not remove required records.




## Verification Before Completion

- Compare `SourceData` row count against the preserved source dataset row count; investigate any unexpected drop before finishing.

- If you changed numeric cleaning, quartile logic, or error handling after a runtime failure, explicitly verify that `SourceData` still preserves the pre-build merged row count and that invalid numeric inputs were handled as blanks/NaN rather than removed unless the task explicitly authorizes deletions.
- Inspect actual values after reopen, not just workbook existence: check a few `SourceData` rows with invalid or blank numeric fields, confirm `Quarter` is blank for invalid `MEDIAN_INCOME` rows, and confirm `Total` is blank when either factor is invalid.
- Also inspect a few rows that were excluded from quartile/total/pivot-value calculations due to invalid numeric inputs and confirm they still remain present in `SourceData` with original source fields intact.
- If you report a reduced eligible-row count for calculations, explicitly confirm that this reflects calculation eligibility only and not unintended row loss from the preserved merged dataset.
- Validate output semantics after any repair that affected data eligibility: compare at least one key aggregate from the reopened workbook against the in-memory prepared data (for example total `SourceData` rows and one state-level population/earners summary).
- Treat printed row counts, merge counts, and save-success messages as necessary but insufficient evidence: completion still requires reopening `/root/demographic_analysis.xlsx` and checking sheet contents/values from the saved file.
- Use a concrete verification script after save/reopen that reports at minimum: sheet names, each sheet's dimensions, `SourceData` columns, presence of `Quarter` and `Total`, and at least one sample aggregate/value check. Do **not** stop at a visual impression or workbook-load success.
- Preserve lightweight evidence from the successful run: report the final `SourceData` row count, one small sample preview including `Quarter` and `Total`, and the exact saved path `/root/demographic_analysis.xlsx` after the last successful regeneration.
- Even when workbook structure looks correct, compare at least one reopened summary result from `Population by State` or `Earners by State` against the prepared dataframe or pivot input, and confirm `State Income Quartile` shows `Q1`-`Q4` columns rather than merely existing as a sheet.
- Confirm the merge key used to combine sources was standardized consistently on both inputs and that the merged result did not lose rows due to type/format mismatches.
- Recheck the actual merged dataframe used for workbook creation, not an earlier intermediate, and confirm it is the same dataset from which `Quarter`, `Total`, and all summary sheets were generated.
- Verify the chosen join strategy matches the source coverage you measured before merge, and explain any expected partial enrichment rather than treating it as silent data loss.
- If population data came from PDF extraction, inspect a few final `SourceData` rows to confirm repeated PDF headers/artifacts were removed and state/region fields were parsed into the intended columns.
- Compare any row counts, matched-record counts, or sheet dimensions you report against the reopened workbook and the latest successful run; if counts disagree, resolve the mismatch before finishing.

### Evidence-only execution rule
- Treat truncated, cut-off, or partial tool output as **no proof of success**. If a command result ends mid-script, mid-print, or without a clear completion signal, rerun or perform a direct verification step before proceeding.
- First verify the artifact exists at the exact required path (`/root/demographic_analysis.xlsx`) with a direct filesystem check, then reopen that same file and inspect contents. Treat path existence as necessary but not sufficient evidence.
- Before claiming the workbook was created or updated, directly verify `/root/demographic_analysis.xlsx` exists and then reopen that exact file and inspect its sheets.
- Do **not** infer specific failure causes without explicit evidence. Base any diagnosis on the actual observed error/output; if no concrete error is shown, say verification is incomplete and gather more evidence first.
- If the chosen pivot-writing approach produced only static summaries, blank pivot shells, or unverifiable results after reopen, report that the pivot requirement is still unmet; do **not** relabel those outputs as successful pivot tables.
- Do **not** describe workbook contents, pivot presence, or sheet results unless those details were confirmed from the saved file after execution.

- Treat any traceback, exception, or partially failed diagnostic during extraction, cleaning, merge validation, numeric coercion, or quartile checks as a stop condition. Do **not** continue to workbook creation or final verification until you fix the issue and rerun the failed check successfully.
- If a diagnostic prints some values and then raises an exception, treat the entire check as failed. Do **not** use the partial printed output as evidence that the data is acceptable; isolate the offending column/operation, fix it, and rerun the same validation cleanly before proceeding.
- If a first-run script fails during quartile assignment, aggregation, or arithmetic, treat that as evidence that preprocessing checks were insufficient. Go back to inspect the exact offending columns (`MEDIAN_INCOME`, `EARNERS`, `POPULATION_2023`, join keys), show sample problematic values/dtypes, fix preprocessing, and rerun validation before rebuilding the workbook.
- Inspect workbook contents semantically, not just structurally: open `SourceData` and at least one representative row/value area in each summary sheet to confirm the requested metrics, labels, and populated results are actually present.
- Use a short semantic verification pass after reopen: confirm exact sheet names, inspect a few `SourceData` rows, check that `Quarter` has only `Q1`-`Q4` or blanks, verify `Total = EARNERS × MEDIAN_INCOME` on at least one sample row, and compare at least one summary value against the prepared dataframe.
- For each required summary sheet, read back the visible headers plus at least one populated data row or value block after reopen; do not stop at dimensions, sheet names, or top-left-cell checks.
- In the final verification, also confirm the cleaned population input actually resolved to the intended narrow source schema rather than a leftover malformed extraction, with no spillover columns from wrapped PDF text leaking into downstream summaries.
- Do **not** stop at file existence, workbook load success, or sheet-name checks; verify row counts, derived-column values, and summary values/headers inside the saved workbook.
- Use a small post-save validation step that prints sheet order/names, `SourceData` row count and headers, presence of `Quarter` and `Total`, one representative populated area from each summary sheet, and whether each summary sheet contains substantive data beyond a `1x1` placeholder.
- If any verification output is truncated, cut off, or only partially shows sheet names/contents, treat verification as incomplete; rerun a narrower inspection until every required sheet and key content check is fully visible.
- Do **not** finalize after a partial listing such as a cut-off sheet-name list or incomplete cell preview. Rerun a narrower reopen/inspection command until the missing sheet names and contents are fully visible.
- Reconcile counts across the workflow: extracted PDF rows, cleaned population rows, income rows, merged rows, and final `SourceData` rows must be explainable. Investigate any off-by-one, unexpected increase, or row-count decrease before finishing.
- Make row-count reconciliation explicit in the final verification: compare the latest extracted PDF row count, cleaned population row count, merged dataframe row count, and reopened `SourceData` row count. If reopened `SourceData` differs even by 1, assume duplication, header leakage, filtering, or another data-loss/data-gain issue until you identify the cause.
- Specifically rule out repeated PDF headers, duplicated joins, dropped unmatched rows, accidental filtering, or deduplication side effects as causes of unexpected row counts or leaked header rows in `SourceData`.
- If any earlier workbook build, import, or save attempt failed, treat all prior verification as invalid. Regenerate `/root/demographic_analysis.xlsx`, reopen the final file from disk, and rerun the full checklist against that final successful artifact before declaring completion.
- Verify requirement-by-requirement against the task spec before finishing; do not stop at sheet names, sample previews, or file existence.
- Explicitly confirm and, if needed, inspect for: exact sheet names, exact requested Rows/Columns/Values layout, presence of `Quarter` and `Total` in `SourceData`, `Population by State` using **Sum of `POPULATION_2023`**, and whether the workbook contains actual Excel pivot tables when the task requires pivots.

- Verify sheet order as well as presence when the task specifies a fixed workbook structure: `Population by State`, `Earners by State`, `Regions by State`, `State Income Quartile`, `SourceData`.
- For pivot-required tasks, verification must answer two separate questions from the saved file: do the sheets show populated results with the requested layout, and are they backed by actual Excel pivot-table objects rather than static exports? If either answer is unproven after reopen, treat the task as unfinished.- Explicitly inspect each summary sheet after reopen for substantive populated output; sheet existence alone is insufficient. A reopened summary sheet with only one cell or only placeholder headers means the deliverable failed and must be rebuilt.
- Use the reopened workbook as binding evidence. If inspection contradicts what you expected to create, trust the saved file rather than script intent, save-time success, or in-memory pivot metadata, and fix the workbook before continuing.
- For each reopened summary sheet, verify both layout and substance: the requested row/column/value labels are present and at least one actual summarized data row or value appears. Treat empty pivot shells, blank tables, or header-only output as failure even if pivot objects exist.
- Cross-check at least one reopened summary value against the prepared data or a direct recomputation before declaring success.
- Never rely on in-Excel manual refresh, deferred rendering, or user cleanup to complete required sheets.
- Before finalizing, re-check the active task/system instructions for any required completion or handoff format and follow that exact syntax literally; do not substitute a narrative success message for a mandated completion signal.
- Final protocol check: verify that your last response uses the exact required completion string/token from the environment and nothing else if the environment requires a token-only completion.
- If any key requirement remains uncertain after reopen/inspection, treat the task as unfinished: fix, regenerate, reopen, and re-check.

- If a tool observation is truncated, cut off mid-command, or missing an explicit success/failure ending, treat that step as unverified. Rerun the command or run a narrow follow-up check before using that step as evidence.
- Do **not** claim the workbook exists, was saved, or contains specific sheets/pivots unless a completed observation from the current run explicitly shows that fact.
- Do **not** infer a likely runtime error from context alone. When remediating, cite the actual traceback/error text or describe the concrete observed symptom instead of guessing the cause.
- If any workbook-generation attempt failed earlier in the run, invalidate any prior success assumptions. Only finish after a later full build succeeds **and** you reopen that final saved file and verify the required sheet contents/layouts from disk.

- If verification shows truncated sheet names, incomplete output, ambiguous dimensions (for example `1x1`), or cut-off inspection results, treat that as verification failure. Run narrower follow-up checks until the saved workbook contents are fully visible and each required sheet is confirmed from disk.
- Keep the final verification concrete and read-from-disk: reopen `/root/demographic_analysis.xlsx`, list sheet names, inspect `SourceData` columns/sample rows, and inspect at least one populated area from each summary sheet before declaring success.
- Run the final check as an explicit requirement-by-requirement checklist against the task wording: output path, exact sheet names, exact Rows/Columns/Values layout, required derived columns, required metric definitions, and whether actual Excel pivot tables were required and are present.
- Do **not** finish with uncertainty or conditional language such as `if you want true pivot tables` or `should be correct`. If any key requirement has not been directly verified from the saved workbook, treat the task as incomplete.
- In the final response, claim only what the saved workbook inspection proved. If a requirement was not met or not verifiable, say so and continue fixing rather than declaring completion.


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
- A reliable starting pattern is: use `pdfplumber` to inspect one PDF page and then iterate page-by-page across all returned tables to collect all population rows into one dataframe; use `pandas` to inspect Excel worksheet names, column names, and sample rows before deciding join and cleaning logic.
- A good minimal workflow is: inspect both inputs separately -> confirm PDF header meaning from page text -> clean/normalize join and numeric fields -> validate merge counts/unmatched rows -> build workbook -> verify file exists on disk -> reopen and inspect sheet contents.

- For semi-structured PDF tables, prefer a targeted parser based on the observed layout over naive full-table extraction.
- If the PDF spans multiple pages or contains more than one table on a page, start with comprehensive extraction of all returned tables, then filter and normalize; do not assume a single extracted table covers the dataset.
- If the PDF sample shows a stable narrow layout, extract only the validated columns you need and discard overflow columns created by wrapped text.

- Validate extraction and merge quality before building summaries: confirm expected headers, row counts, join keys, unmatched records, and the final merged schema required for workbook generation after joining PDF and Excel data.

- Explicitly compare join-key dtypes/formats before merging; do not rely on pandas to reconcile numeric vs string identifiers automatically.
- Quantify join quality explicitly: compare unique `SA2_CODE` coverage between sources and inspect unmatched records before deciding the merge is usable.
- Immediately after merging on the chosen key, count unmatched or null values in critical fields such as `STATE` and `POPULATION_2023`; fix the join before building pivots if those checks fail.

- When extracting population data from `/root/population.pdf`, validate key grouping fields before aggregation. If `STATE` values look truncated or inconsistent (for example `New South W`), fix the extraction/cleaning before creating any state-based output.

- Treat visibly truncated grouping keys as a stop condition, not a warning: do not build pivots or summaries keyed by `STATE` until those values are repaired and standardized.

- Before computing summaries keyed by `STATE`, check that state names are complete and standardized so identical states are not split into separate groups.
- Before creating summaries, verify the merged dataset still contains every field needed by the workbook spec, especially `POPULATION_2023` for the population sheet.

- Build one cleaned, merged, enriched source table first; then create every workbook sheet and pivot from that same source table rather than mixing separate intermediate datasets.
- Keep the workflow in two distinct phases: (1) stabilize and validate each source schema, especially the PDF extraction, then merge into one canonical `SourceData`; (2) generate every report sheet from that canonical table and verify the saved workbook against it.
- Consolidate only the needed population fields into a single clean dataframe before joining; do not merge directly from raw PDF table fragments.

- Convert `EARNERS`, `MEDIAN_INCOME`, and `POPULATION_2023` to numeric before quartile assignment, totals, or pivot aggregation; then build `Quarter` from global `MEDIAN_INCOME` quartiles on the merged dataset and `Total = EARNERS × MEDIAN_INCOME`.
- If quartile, comparison, or arithmetic logic raises a mixed-type error (for example `int` vs `str`), diagnose the exact input columns before applying a broad patch: inspect dtypes, sample non-numeric values, then rerun `pd.to_numeric(..., errors='coerce')` on the specific fields used by that computation.
- When fixing a numeric-type failure, show targeted evidence before and after the fix: print the dtypes of `MEDIAN_INCOME`, `EARNERS`, and `POPULATION_2023`, sample the non-numeric/problem rows, then rerun a small check proving quartile and total calculations work on the cleaned columns before rebuilding the workbook.
- Do **not** describe the repair vaguely. State which function or columns changed and verify that the exact failing computation now succeeds.
- Before regenerating the workbook after a numeric-type fix, explicitly confirm that `MEDIAN_INCOME`, `EARNERS`, and `POPULATION_2023` are numeric/NaN in the cleaned dataframe and that `Quarter`/`Total` can be computed on sample rows without type errors.
- Treat `pandas.pivot_table` as a data-prep helper only; it does not create an Excel pivot-table object.

- If you use any method to create Excel pivot tables, prove it worked by reopening the saved workbook and checking the resulting sheet contents. Do not rely on object creation, cache metadata, or save-time success alone.

- For pivot-required tasks, check both semantics and structure after reopen: verify the summary sheets contain the requested visible results and that the saved workbook package still contains actual pivot-table objects on those sheets.
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

- Follow the active environment/system interaction protocol exactly from the first tool call through the final completion message. If the session requires a specific `Thought:` / `Action:` format, JSON action schema, or one exact completion token, use that exact syntax on every step.
- Before the first tool call, identify the exact required tool-invocation syntax and any exact completion token from the active system/environment instructions, then use only that authorized interface for the rest of the run.
- Treat protocol instructions as hard requirements that override this skill's workflow guidance. Do **not** invent alternate tool-call syntax, XML-style tags, placeholder action descriptions, undeclared tools, or free-form substitutes.
- For shell/tool usage, provide literal executable commands or inline scripts only. Do **not** write intent descriptions such as `check the generated workbook file`, `ran a validation script`, or `generated the workbook`; write the exact command or script to run.
- Track protocol compliance separately from workbook logic: allowed tools, required action schema, and the exact completion token are independent hard gates.
- A script traceback or failed command invalidates any implied success claim. Fix the error, rerun the affected step, and only continue once the repaired run and the saved workbook both verify successfully.
- Before finishing, run a final procedural checklist: (1) all tool calls used the authorized interface only, (2) required verification is complete, and (3) emit the exact required completion string/token with no substitution or extra narrative.
- If the environment specifies an exact completion string, do not paraphrase it and do not add extra narrative after it. Finish with that exact string only after all workbook verification is complete.