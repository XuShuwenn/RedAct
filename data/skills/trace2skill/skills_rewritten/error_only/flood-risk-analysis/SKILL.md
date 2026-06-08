---
name: flood-risk-analysis
description: "Analyze USGS streamflow data to find stations with flooding during specific date ranges and output flood statistics."
---

# Flood Risk Analysis from Streamflow Data

## When to Use

- Identify stations that experienced flooding in a time period
- Analyze USGS streamflow records
- Calculate flood days per station

## Input File

- `/root/data/michigan_stations.txt`: authoritative local input for station scope; inspect it first to determine whether it contains station IDs, metadata, streamflow records, or another structure

- Treat `/root/data/michigan_stations.txt` as authoritative for which stations are in scope and for any data it actually contains; if it does not contain the required thresholds or observations, obtain only those missing inputs from task-appropriate sources.
- Inspect enough of the file to confirm its actual structure before choosing an approach.
- If an initial peek looks inconsistent with the prompt, inspect additional lines/fields and reconcile the discrepancy before redesigning the workflow.
- Do not reclassify the file as a mere station list from a shallow sample; confirm whether records, delimiters, headers, or repeated per-date/per-station fields are present.
- Confirm the raw on-disk format before writing the parser; if a viewer adds line numbers, arrows, or other decoration, inspect sample lines with a low-level read (`repr`, direct Python read, or equivalent) and parse the actual file contents, not the display formatting.
- Treat `station_id` and any other identifiers as strings end-to-end; do not coerce to numeric because leading zeros are significant.
- As soon as you read the station file, run a quick format sanity check on the IDs you extracted (for example: unexpected length, truncated-looking values, blanks, or mixed schemas). If any entry looks malformed or the file display seems incomplete, inspect additional raw lines before starting expensive retrieval/processing.
- Do not silently treat a malformed or truncated station ID as valid scope. Either repair it only with direct evidence from the file structure, exclude it with justification, or report the limitation explicitly.

## Output

CSV at `/root/output/flood_results.csv`.


## Output

## Execution Protocol Checks

- **Mandatory protocol gate before first action:** if the runtime specifies a tool/action schema, identify the exact allowed tool names and action structure first, then use only that schema for every action.
- **Do not improvise tool syntax.** Wrong: alternate tool names, casing variants, XML-style wrappers, markdown-wrapped tool calls, or freeform substitutes. Right: the exact runtime-required schema.
- **Mandatory final gate before responding:** if the runtime requires an exact completion marker, output that exact string alone with no summary, bullets, or extra text.
- Follow the task/runtime's exact tool-call and action protocol if one is specified; do not invent alternate wrappers, tags, or markdown around tool calls.
- Do a quick preflight before any analysis: confirm the required tool/action format, allowed read/write paths, and exact required final response string if one exists.
- If the runtime specifies an exact tool-call schema, use that format verbatim for every step; do not switch to other wrappers or freeform command styles mid-task.
- Treat protocol compliance as blocking, not advisory: malformed, truncated, content-free, or unsupported action/tool calls must be corrected immediately in the exact required format before proceeding.
- Before the final response, check whether the task/runtime requires an exact completion string or token. If it does, output that exact string and nothing else.
- Write generated files only inside explicitly allowed directories. If only `/root/output` is writable, do not create helper scripts under `/root/` or elsewhere.
- Keep all helper code, temp files, and outputs inside explicitly allowed directories only; otherwise prefer inline commands so nothing is written outside allowed paths.
- Verify every command or script actually succeeded before building on it: inspect stdout/stderr and exit status, and fix syntax/quoting errors before proceeding.
- If command output is truncated, cut off, or stops mid-process, do not assume success. Confirm completion by checking exit status and inspecting the expected artifact directly.
- Do not assume a generated script ran just because the file was written; explicitly run it, inspect the result, and verify the expected output artifact was created or updated.
- If you write a script file, write actual executable code only — never a prose placeholder, pseudocode, or a natural-language summary. After writing it, inspect the file contents or run a syntax/import check before relying on it.
- Before creating any script or temp file, confirm its path is inside an explicitly allowed directory. Do not write helper code under `/root` or any parent directory unless that exact path is authorized.
- If a script, join, or retrieval step produces station counts, station membership, or `station_id` formatting that contradict the input file or earlier inspection, stop and reconcile the discrepancy before continuing.
- Before attempting package installation or environment changes, quickly check whether the needed interpreter and Python packages are already available/importable and prefer existing dependencies when present.
- Before running any non-trivial Python block or external-retrieval workflow, do a quick viability check: confirm needed libraries import successfully, keep quoting simple, and fix syntax/quoting errors before proceeding.
- Prefer inline Python or shell commands, or a single small validated Python script inside an allowed writable directory, over scattered temporary files when directory permissions are constrained.
- If the analysis spans many stations or combines threshold lookup, time-series processing, and CSV generation, prefer one validated end-to-end Python workflow over many ad hoc commands.
- If Python package installation is blocked by an externally managed system environment, create and use a virtual environment in an allowed writable location rather than forcing a system-wide install.
- If a planned package or tool is unavailable, switch to another valid in-environment method or explicitly report the limitation instead of continuing with an unvalidated workflow.
- Do not treat a requested date as invalid, unavailable, or "in the future" unless you have direct evidence from the data source, task context, or runtime.
- Immediately before finishing, confirm the required output file exists and then emit the exact required completion marker with no extra text if the runtime specifies one.
- Final verification must be requirements-level, not existence-only: confirm the output path is authorized, the CSV is complete and readable, all output station IDs are within the original input scope, and the final response uses the exact required completion string.
- If the runtime specifies an exact completion marker, output that exact string and nothing else after verifying the artifact.

- Do not declare success from partial logs or mere file existence; require a clean run signal (successful exit status and no unresolved truncation/interrupt evidence), then inspect the written CSV enough to verify key constraints before finalizing.
- Immediately before each tool call, do a one-line self-check: "Am I using the exact required wrapper/schema?" If not, rewrite it before sending.
- Immediately before the final response, do a one-line self-check: "Is an exact completion token required, and if so am I sending only that token?"
## Final Compliance Check

Before ending the task, verify all of the following:
- Every tool interaction used the exact runtime-specified schema
- `/root/output/flood_results.csv` exists and passed validation
- The final CSV reflects the exact requested dates and station scope, not a diagnostic substitute run
- The final response matches the runtime's exact required completion string, with no extra prose if the runtime requires that

## Key Steps

1. Inspect `/root/data/michigan_stations.txt` first to determine whether it contains station IDs only, metadata, or actual measurements, and preserve every `station_id` exactly as text
   - Immediately sanity-check the extracted station IDs for malformed or truncated values and record a quick baseline from the source inspection, such as the station count and 3-5 sample IDs.
   - Treat that loaded station set as the only allowed processing scope; do not rely on a script's broader default station source.
1a. Record the directly observed station-count/cardinality from `/root/data/michigan_stations.txt` after inspection. If later parsing, joins, or downloads produce more in-scope stations than were observed in that authoritative file, stop and debug the parser/scope logic before continuing.
1b. If the file appears to be one station ID per line, verify the parsed station list length matches the visible line count (excluding blanks/comments if present) before any downstream retrieval or analysis.
1c. After parsing `/root/data/michigan_stations.txt`, reconcile the parsed station count and a spot-check/all-check of IDs against the raw file inspection before doing any downstream retrieval or joins; if the parser yields extra IDs, missing IDs, or a materially different count than the source you inspected, stop and fix the parse/input selection first.
2. If the file contains measurements, parse them directly; inspect the dataframe/schema before choosing the measurement column, identify the requested series by name rather than position, and prefer stage/gage-height observations when that matches the task
3. If the file is only a station list or scope file, use it to define station scope and obtain the required thresholds and observations separately only when the task allows or requires that
4. Determine each station's flood threshold from authoritative station metadata or task-provided data before classifying any day; record threshold provenance, normalize join keys on every input to the same string format, spot-check that leading zeros survived parsing, and verify measurement type/units match before comparison

   - Before processing all stations, explicitly verify the threshold source worked by printing or inspecting a few sample `station_id -> threshold` values and confirming the units/series used in the comparison.
   - If threshold retrieval fails, is incomplete, or returns values you cannot inspect and validate, stop and report that limitation rather than switching to an unverified method.
5. Normalize observation timestamps to a consistent datetime representation before resampling or slicing by calendar date
6. Filter the exact requested date range (April 1-7, 2025); if data appears missing or unusable, debug parsing, measurement selection, and data-source assumptions first, but do not substitute another year or window unless the user explicitly authorizes it
   - Do not replace April 1-7, 2025 with April 1-7, 2024, a nearby window, or any other fallback period based on your own judgment.
   - You may use alternate dates or known-good stations only for diagnosis, never for the final deliverable.
   - Keep diagnostic experiments separate from production outputs: after any debugging run on substitute data, switch back to the exact requested window before writing `/root/output/flood_results.csv`.
   - If one endpoint or product lacks the needed records, try other methods that still answer the April 1-7, 2025 question; treat source failure as an implementation problem, not permission to redefine the task.
   - If the requested window cannot be completed with authoritative data, report that limitation explicitly rather than shipping results for another period.
7. When source observations are sub-daily or instantaneous, reduce them to one daily value or daily exceedance indicator per station first; for flood-day counting, typically use each station's daily maximum and count distinct calendar dates with at least one exceedance rather than raw exceedance rows
8. Count flood days as days in that window where the daily event metric meets or exceeds the station's fixed threshold
9. If a small number of stations fail due to timeout or transient retrieval/processing issues, retry just those stations once before finalizing exclusions or zero-flood conclusions
10. Keep only stations with >= 1 flood day and output only the requested columns (`station_id`, `flood_days`) unless the prompt explicitly asks for more
11. Restrict analysis to station IDs present in `/root/data/michigan_stations.txt` and verify every output `station_id` is a member of that input list

   - Treat the original input station list/count as an invariant. If a retrieval, join, or threshold step suddenly produces more stations than were in scope, fewer matched stations than expected, or reformatted IDs, debug that mismatch before proceeding.
12. Validate the final CSV before declaring success: required columns, requested sort/order, exact `station_id` formatting including leading zeros, membership of every output `station_id` in the input station list, plausible station counts relative to the inspected input, `flood_days` bounds of 0-7 for the April 1-7 window, and exactly the required output columns with no extra diagnostic fields; if results look suspicious (for example, nearly every station floods), re-check threshold provenance and logic
- Make the membership check explicit: compute `unexpected_ids = output_ids - input_ids` and treat any non-empty `unexpected_ids` as a failure that must be fixed before delivery.
- Treat any `flood_days` value outside 0-7 for the April 1-7 window as a hard failure requiring debugging before completion.
- Treat count mismatches as blockers, not warnings: reconcile input station count, parsed in-scope station count, analyzed station count, and output row count before finishing.
- If a script's stdout/log summary conflicts with the generated CSV or intermediate tables, treat that as a blocker: inspect the underlying data/join logic, rerun after fixing, and do not declare success until the results are reconciled.
- If results look plausible only because a CSV was produced, but the threshold inputs were not visibly validated, do not finalize.
13. For workflows that combine multiple sources, prefer one reproducible end-to-end pipeline that loads the station IDs first, performs joins/calculations in one place, writes `/root/output/flood_results.csv`, and then inspects the written CSV directly
- If you abandon one approach and switch to a rewritten script or retrieval method, re-run the final artifact audit from scratch on the written CSV: required columns, exact date-window logic, and especially `output station_id ⊆ input station_id`.
14. If authoritative thresholds or required data for the requested window are unavailable, report the limitation explicitly rather than inventing criteria, using alternate heuristics, or changing the scope

15. Do not ask the user for permission to perform substeps already implied by the task, such as fetching required observations or thresholds; execute them when needed and allowed
16. If you generate helper scripts, confirm the on-disk contents are actual executable code, not a prose description; do not continue until a quick readback or syntax check passes
17. Add a scope guard before finalizing: compare the station IDs actually processed and the station IDs written to `/root/output/flood_results.csv` against the IDs loaded from `/root/data/michigan_stations.txt`; if any processed or output ID is outside the input set, the run is invalid

## Tips

- Check for flood stage/threshold values
- A reliable pattern is: build a `station_id -> flood threshold` map first, normalize the observation series to one value per day when needed (typically daily max for sub-daily stage/height data), then count April 1-7 exceedance days.
- Use pandas for data analysis
- Create output directory if needed
- Sort results by station_id
- When using pandas, load station identifiers with string dtype (for example, `dtype={'station_id': 'string'}` or equivalent) and re-open the output CSV to confirm leading zeros were preserved.
- Before joining station metadata or thresholds with streamflow data, spot-check a few keys to confirm leading zeros are preserved on both sides.
- When a join unexpectedly drops many stations or reports missing thresholds, inspect the raw `station_id` values and dtypes on both sides before changing the analysis logic; formatting drift is a common cause.
- Treat the provided local file as authoritative for station scope and any data it actually contains, but do not assume it already includes thresholds or observations; inspect first, then retrieve only the missing required data.
- Do not assume the local file already contains streamflow observations; first confirm whether it is a station list, metadata, or measurements, then build the workflow around that finding.
- Read from and write to only task-authorized paths; keep any helper artifacts inside allowed directories.
- Before running the main analysis, do a quick dependency check for the libraries your approach needs.
- If a planned package is unavailable, switch to another valid in-environment method or explicitly report the limitation; do not continue with an unvalidated workflow.
- When a task depends on a non-stdlib library, test a direct import first; if it is already available, use it rather than spending time on blocked installation attempts.
- Before executing generated Python, confirm the available interpreter/environment and use the validated one consistently.
- If using a library such as `dataretrieval.nwis`, inspect the returned object type and shape before processing; some calls return tuples or metadata alongside the dataframe.
- Locate the measurement column by searching names for the requested parameter/series and exclude qualifier/code columns (for example, names ending in `_cd`) before computing exceedances.
- Do not select the measurement series by position; identify the requested variable by name and confirm the dataframe uses the expected datetime index before resampling or counting days.
- Do not invent flood criteria from relative statistics, percentiles, or heuristics unless the task explicitly authorizes that approximation.
- Use a fixed, externally defined flood threshold per station. Do not replace it with percentiles, rolling baselines, or thresholds derived from the April 1-7 evaluation window itself.
- Do not compute the flood threshold from the same April 1-7, 2025 evaluation window being labeled; use an external definition, metadata, or separately established baseline.
- If no authoritative flood threshold is available, stop and state the missing requirement or limitation instead of substituting an arbitrary heuristic.
- When threshold metadata comes from a separate source, normalize `station_id` formatting on both datasets before the join, verify matched and unmatched counts or spot-check a few keys, and compare only like-for-like measurement units/types.
- When external retrieval is explicitly required, prefer the source whose temporal granularity matches the metric: for day-level flood counts, use sub-daily observations when needed and aggregate to daily maxima rather than relying on daily summaries that can miss peaks.
- For high-frequency records, derive `flood_days` from unique exceedance dates or a daily exceedance indicator, not the raw number of exceedance rows or timestamps.
- If the task explicitly requires retrieving thresholds for many stations from external sources, prefer a bulk metadata export/report over station-by-station requests, then filter it to the station IDs in `/root/data/michigan_stations.txt`.
- Do not change core task parameters (date range, dataset, station scope) unless the user explicitly authorizes it.
- After loading data, inspect dataframe columns and index explicitly, and verify intermediate counts are consistent with the input you observed.
- Normalize datetimes before resampling or date filtering so timezone-aware timestamps do not cause off-by-one day errors or slicing failures.
- If command output is truncated or partial, verify generated files directly (exists, row count, sample rows) before proceeding.
- For workflows that combine multiple sources, prefer one validated pipeline that loads inputs, performs joins, computes daily metrics, and writes the final CSV.
- After writing `/root/output/flood_results.csv`, explicitly compare output `station_id` values to the IDs loaded from `/root/data/michigan_stations.txt`; fail the run if any output ID is outside that source list.
- After writing `/root/output/flood_results.csv`, read it back and verify the required columns, row filtering, and station IDs before declaring success.
- Sanity-check output against hard bounds and semantics: for April 1-7, `flood_days` must be between 0 and 7 for every station; if nearly every station floods, re-check the threshold method.
- Treat empty or missing results as a debugging signal about path, parser, column choice, or threshold method, not as justification to change dates or produce a substitute-period CSV.
- If you write Python for the analysis, perform a quick syntax/quoting sanity check and confirm the output file was actually created before concluding.
- Do not treat successful CSV creation as sufficient; validate schema, confirm all output station IDs come from the input file, and always write `/root/output/flood_results.csv` even if the correctly processed result is empty.
- Validation is not complete until both are true: the CSV is correctly formatted, and the flood/non-flood logic is justified by an external or task-provided threshold definition.

- Keep a simple invariant checklist during the run: original station count, exact set membership, and `station_id` string formatting. Re-check these after each major load, join, retrieval, or pipeline rewrite.
- Do not rely on a script's default station source. Pass the IDs loaded from `/root/data/michigan_stations.txt` explicitly into the processing pipeline, or verify the script is reading that file directly.
- Preserve `station_id` as a zero-padded string in every dataframe, file, join key, log, and CSV. Spot-check 3-5 IDs end-to-end from input file to final CSV; if you ever see a form like `4031000` for input ID `04031000`, treat that as a bug and debug before proceeding.
- Prefer an explicit set-based audit over visual inspection, e.g. compare `set(output.station_id)` to `set(input_ids)` and investigate any non-empty difference before concluding.
- If intermediate outputs, logs, and the written CSV disagree with each other, do not trust any one of them by default; reconcile the contradiction first, then regenerate the CSV.
- If requested data seems unavailable, keep the requested period and scope fixed while testing alternate retrieval methods, endpoints, or aggregation approaches that still produce the requested result.
- If threshold retrieval had earlier failed or returned missing data, add a visible checkpoint showing several retrieved threshold values before trusting downstream flood-day counts.
- Separate debugging validation from final analysis: a historical or known-good flood period can help verify parsing/threshold logic, but must not be used for the final CSV unless the user explicitly changes the task.
- Impossible outputs are hard failures: for an April 1-7 analysis, `flood_days > 7` means the date window or aggregation is wrong and must be corrected before completion.
- If a quick file preview is truncated, re-open the written CSV with a full structured check (row count, columns, sample IDs, out-of-scope IDs) before declaring success.
- Before finalizing, perform a last checklist: output file exists, schema is correct, all `flood_days` are within the task's date-window bounds, threshold provenance was validated, and the exact required completion marker will be emitted.