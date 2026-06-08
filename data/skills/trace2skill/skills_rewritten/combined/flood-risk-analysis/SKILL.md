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
- Do a tiny raw-file spot check before designing the parser or retrieval plan: read a few undecorated lines directly from disk and confirm whether the file is a station list, metadata table, or measurement data.
- If the file turns out to be station IDs only, lock that in as station scope and build the rest of the workflow around external threshold/observation retrieval rather than trying to parse nonexistent local measurements.
- Treat `station_id` and any other identifiers as strings end-to-end; do not coerce to numeric because leading zeros are significant.
- As soon as you read the station file, run a quick format sanity check on the IDs you extracted (for example: unexpected length, truncated-looking values, blanks, or mixed schemas). If any entry looks malformed or the file display seems incomplete, inspect additional raw lines before starting expensive retrieval/processing.
- Do not silently treat a malformed or truncated station ID as valid scope. Either repair it only with direct evidence from the file structure, exclude it with justification, or report the limitation explicitly.

## Output

CSV at `/root/output/flood_results.csv`.


## Output

## Execution Protocol Checks

- **Mandatory protocol gate before first action:** if the runtime specifies a tool/action schema, identify the exact allowed tool names and action structure first, then use only that schema for every action.
- If the environment is bash-only, every action must use the exact bash tool name and the runtime's required wrapper/schema; do not substitute lookalike names such as `Bash`, `Read`, `Write`, `Edit`, `TodoWrite`, or question-asking tools unless the runtime explicitly allows them.
- If the runtime prescribes a `Thought`/`Action` pattern or requires `Action:` followed by a JSON object, use that structure verbatim on every tool step; do not substitute tags such as `<tool_call ...>` or any other wrapper.
- Before the first real tool call, mirror the runtime's required action shape exactly and keep that same format for the entire task.
- **Do not improvise tool syntax.** Wrong: alternate tool names, casing variants, XML-style wrappers, markdown-wrapped tool calls, or freeform substitutes. Right: the exact runtime-required schema.
- **Mandatory final gate before responding:** if the runtime requires an exact completion marker, output that exact string alone with no summary, bullets, or extra text.
- **Protocol failure is task failure even if the CSV is correct.** Do not treat artifact creation, CSV inspection, or analytical plausibility as sufficient until both conditions are true: (1) every tool call used the exact runtime-required schema and (2) the final response is the exact required completion marker with no extra text.
- Treat the exact completion marker as a hard requirement, not a stylistic preference. Never prepend or append a conversational recap to the completion marker. For example, if the runtime requires `ACTION: TASK_COMPLETE`, emit exactly `ACTION: TASK_COMPLETE` and nothing else.
- Follow the task/runtime's exact tool-call and action protocol if one is specified; do not invent alternate wrappers, tags, or markdown around tool calls.
- Do a quick preflight before any analysis: confirm the required tool/action format, allowed read/write paths, and exact required final response string if one exists.
- If the runtime specifies an exact tool-call schema, use that format verbatim for every step; do not switch to other wrappers or freeform command styles mid-task.
- Treat protocol compliance as blocking, not advisory: malformed, truncated, content-free, or unsupported action/tool calls must be corrected immediately in the exact required format before proceeding.
- If a task-management or tool action is malformed, partially emitted, or content-free, do not assume the environment's acceptance means it was valid; resend a corrected action in the exact required schema before relying on it.
- If you realize you used the wrong tool/action wrapper even once, stop and switch immediately to the exact required schema; do not continue analysis in the wrong format or try to compensate with a prose summary later.
- Before the final response, check whether the task/runtime requires an exact completion string or token. If it does, output that exact string and nothing else.
- Write generated files only inside explicitly allowed directories. If only `/root/output` is writable, do not create helper scripts under `/root/` or elsewhere.
- If writable locations are ambiguous, resolve that ambiguity before creating any helper file. Do not assume `/root` is allowed just because `/root/output` is allowed.
- Keep all helper code, temp files, and outputs inside explicitly allowed directories only; otherwise prefer inline commands so nothing is written outside allowed paths.
- Verify every command or script actually succeeded before building on it: inspect stdout/stderr and exit status, and fix syntax/quoting errors before proceeding.
- If command output is truncated, cut off, or stops mid-process, do not assume success. Confirm completion by checking exit status and inspecting the expected artifact directly.
- Do not assume a generated script ran just because the file was written; explicitly run it, inspect the result, and verify the expected output artifact was created or updated.
- If you write a script file, write actual executable code only — never a prose placeholder, pseudocode, or a natural-language summary. After writing it, inspect the file contents or run a syntax/import check before relying on it.
- Before creating any script or temp file, confirm its path is inside an explicitly allowed directory. Do not write helper code under `/root` or any parent directory unless that exact path is authorized.
- If a script, join, or retrieval step produces station counts, station membership, or `station_id` formatting that contradict the input file or earlier inspection, stop and reconcile the discrepancy before continuing.
- Before attempting package installation or environment changes, quickly check whether the needed interpreter and Python packages are already available/importable and prefer existing dependencies when present.
- Confirm which interpreter actually runs in the environment before testing imports or writing scripts; do not assume `python` exists when `python3` is the valid command.
- If imports fail and the task needs Python tooling, fix the runtime cleanly first (for example, validate interpreter availability, then use an isolated environment in an allowed writable path when needed) instead of repeatedly forcing installs into a broken base environment.
- If required packages are missing and the task permits writing in an allowed directory, prefer creating a small virtual environment there and running the analysis inside it rather than modifying the system Python environment.
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
- The parsed/analyzed station scope never exceeded the station IDs directly confirmed from `/root/data/michigan_stations.txt` without an explicit source-based reconciliation
- No final `flood_days` value exceeds the mathematical maximum for the requested window
- Every tool interaction used the exact runtime-specified schema
- `/root/output/flood_results.csv` exists and passed validation
- Validation was done from the written artifact itself: read back the full CSV with a structured check (row count, columns, sample/full ID audit as needed), not just a partial preview, log snippet, or script summary
- The final CSV reflects the exact requested dates and station scope, not a diagnostic substitute run
- The final response matches the runtime's exact required completion string, with no extra prose if the runtime requires that
- The written `/root/output/flood_results.csv` was produced from the requested analysis window, not from any diagnostic or historical substitute run
- Immediately before the final response, verify that no debug date override remains in the active script/command parameters; then emit the exact required completion token alone

- The final flood-threshold method was visibly validated with sample retrieved threshold values from the exact source/method used in the run
- Any helper script that was executed was read back after writing and confirmed to contain real executable code, not prose or placeholders
- No `flood_days` value exceeds 7 for the April 1-7 window; if any do, stop and debug date filtering or aggregation before finalizing
- If an exact completion marker is required (for example `ACTION: TASK_COMPLETE`), output that exact string alone and nothing else


## Key Steps

1. Inspect `/root/data/michigan_stations.txt` first to determine whether it contains station IDs only, metadata, or actual measurements, and preserve every `station_id` exactly as text
   - Start with a minimal reality check: list the available input files and sample enough of `/root/data/michigan_stations.txt` to confirm whether it is only a station list or contains richer structure before designing the pipeline.
   - Also inspect the surrounding input/output layout up front: confirm the source file is where you expect and that `/root/output` exists or can be created before building the workflow.
   - Identify the actual working interpreter command in this runtime (for example, `python3` instead of assuming `python`) before writing or running the main analysis.
   - Before any bulk retrieval or script run, explicitly bind the workflow to this loaded station list: pass these IDs into the pipeline or verify the code reads this exact file directly. Do not rely on a script's built-in/default station source.
   - Treat the observed input cardinality as a hard scope lock. If the file inspection shows 31 stations, any later message such as "Processing 79 stations" is a blocker that must be debugged before continuing.
   - Prefer a single reproducible pipeline (inline Python or one small validated script in an allowed writable directory) that loads this authoritative input first, carries the exact `station_id` strings through threshold/observation joins, computes flood days, writes `/root/output/flood_results.csv`, and then reads that CSV back for verification.
   - Immediately sanity-check the extracted station IDs for malformed or truncated values and record a quick baseline from the source inspection, such as the station count and 3-5 sample IDs.
   - Treat that loaded station set as the only allowed processing scope; do not rely on a script's broader default station source.
1a. Record the directly observed station-count/cardinality from `/root/data/michigan_stations.txt` after inspection. If later parsing, joins, or downloads produce more in-scope stations than were observed in that authoritative file, stop and debug the parser/scope logic before continuing.
1aa. If different inspection methods disagree about the station file itself (for example, a viewer preview shows 31 lines but a raw count/read shows 79 records), resolve the discrepancy immediately with a raw on-disk check before trusting either result. Do not treat the first preview or a downstream script summary as authoritative until the file's true structure and count are reconciled.
1ab. Treat any expansion from the inspected input scope as a hard failure signal. Example: if the source file shows 31 station IDs and any downstream step reports 79 stations, do not continue until you identify exactly where the extra IDs came from and restore the pipeline to the original input-defined scope.
1b. If the file appears to be one station ID per line, verify the parsed station list length matches the visible line count (excluding blanks/comments if present) before any downstream retrieval or analysis.
1b.i. Treat the directly observed line-based cardinality as a hard gate: if you visibly inspected about N in-scope IDs in the file and the parser later yields materially more or fewer IDs, stop immediately and debug the parser/input selection before any retrieval, threshold join, or CSV generation.
1c. After parsing `/root/data/michigan_stations.txt`, reconcile the parsed station count and a spot-check/all-check of IDs against the raw file inspection before doing any downstream retrieval or joins; if the parser yields extra IDs, missing IDs, or a materially different count than the source you inspected, stop and fix the parse/input selection first.
1d. If any station ID looks truncated or malformed (for example, much shorter than the dominant ID length), inspect the raw bytes/lines directly (`repr`, direct Python read, or equivalent) before continuing. Do not launch external retrieval until you have either repaired the parse with direct evidence, excluded the bad row with justification, or explicitly recorded it as a limitation.
1e. Record the exact in-scope `input_ids` set immediately after parsing and reuse that same set in every downstream filter, join audit, and final CSV validation; do not rebuild scope later from a different source or script default.
1f. After each major stage that can change scope (download, threshold join, flood-detection script, CSV write), compare the current station set/count to the original loaded input set. Any unexplained increase in station count or appearance of out-of-scope IDs is a hard failure, not a warning.
1g. Make the parser/reporting stage observable: print or inspect the parsed station count and a few sample IDs immediately after load so an empty or malformed in-scope set is caught before retrieval or analysis.
- Before choosing between steps 2 and 3, do a short feasibility preflight: confirm the interpreter/tooling you plan to use is available and directly import any non-stdlib packages your approach depends on.
- If the file proves to be station IDs only, pivot immediately to a retrieval workflow rather than forcing a direct-parser approach.
2. If the file contains measurements, parse them directly; inspect the dataframe/schema before choosing the measurement column, identify the requested series by name rather than position, and prefer stage/gage-height observations when that matches the task
   - Before scaling to all stations, inspect one returned sample (for example, one station) to confirm the dataframe/index shape and the exact measurement column you will use; for USGS-style data, verify the gage-height/stage field (such as parameter `00065`) rather than assuming column position.
3. If the file is only a station list or scope file, use it to define station scope and obtain the required thresholds and observations separately only when the task allows or requires that
   - Before scripting the full workflow, quickly verify whether the intended libraries/tools (for example `pandas` and any retrieval library you plan to use) are already importable so you can choose the simplest validated implementation path.
4. Determine each station's flood threshold from authoritative station metadata or task-provided data before classifying any day; record threshold provenance, normalize join keys on every input to the same string format, spot-check that leading zeros survived parsing, and verify measurement type/units match before comparison
   - Treat threshold validation as a blocking gate: before any full run or final CSV, print/inspect several concrete `station_id -> threshold` examples from the exact data structure used in the comparison. If you cannot show real retrieved thresholds, do not finalize.
   - Prefer a lookup-based threshold join keyed by `station_id` (for example, a dictionary or indexed table) and verify coverage before time-series processing: inspect matched vs unmatched station counts and a few sample `station_id -> threshold` pairs.
   - Before joining thresholds to observations, coerce every `station_id` source to trimmed string form with preserved leading zeros, then compare matched/unmatched counts so formatting drift cannot silently masquerade as missing data.
   - If one source uses unpadded IDs, normalize to the authoritative formatting from `/root/data/michigan_stations.txt` before the join and spot-check a few exact key pairs end-to-end.
   - When thresholds/observations come from separate acquisitions, normalize `station_id` on every artifact the same way before any merge (for example, string type plus zero-padding to the observed source width) and verify the join on a few sample IDs.
   - If thresholds are needed for many stations, prefer one authoritative bulk metadata/report download and then filter it locally to the station IDs from `/root/data/michigan_stations.txt` instead of making many station-by-station requests.
   - If threshold retrieval failed earlier and you changed methods, re-run the sample-threshold check on the new method before trusting any flood-day counts.
   - If it improves traceability, save acquired observations and threshold/reference data as separate intermediate artifacts inside an allowed directory before running the final flood-day computation; use those artifacts to isolate acquisition problems from analysis problems.

   - Before processing all stations, explicitly verify the threshold source worked by printing or inspecting a few sample `station_id -> threshold` values and confirming the units/series used in the comparison.
   - If threshold retrieval fails, is incomplete, or returns values you cannot inspect and validate, stop and report that limitation rather than switching to an unverified method.
5. Normalize observation timestamps to a consistent datetime representation before resampling or slicing by calendar date
   - Do a lightweight feasibility preflight before the full run: confirm the station file's basic shape/count and that the needed libraries/imports for the planned workflow are available.

6. Filter the exact requested date range (April 1-7, 2025); if data appears missing or unusable, debug parsing, measurement selection, and data-source assumptions first, but do not substitute another year or window unless the user explicitly authorizes it
   - Treat inability to retrieve the requested window from one endpoint, parameterization, or product as a retrieval/problem-solving issue. Try other valid endpoints, products, or aggregation methods that still compute April 1-7, 2025; do not pivot the final analysis to 2024, another nearby period, or any self-selected fallback.
   - Do not interpret the requested 2025 window as invalid merely because a source lacks one product for that period. Exhaust task-appropriate methods that still answer the original 2025 question before concluding there is a limitation.
   - Treat any alternate-date or known-good historical run as debug-only evidence. Never write `/root/output/flood_results.csv` from a substitute period; before writing the final CSV, re-check that every retrieval/filter step is still using the exact requested window (April 1-7, 2025).
   - If you temporarily change dates to test parsing, aggregation, or threshold logic, revert those parameters and rerun the production pipeline on the requested dates before finalizing; otherwise report the limitation instead of delivering surrogate results.

   - Do not replace April 1-7, 2025 with April 1-7, 2024, a nearby window, or any other fallback period based on your own judgment.
   - You may use alternate dates or known-good stations only for diagnosis, never for the final deliverable.
   - Keep diagnostic experiments separate from production outputs: after any debugging run on substitute data, switch back to the exact requested window before writing `/root/output/flood_results.csv`.
   - If one endpoint or product lacks the needed records, try other methods that still answer the April 1-7, 2025 question; treat source failure as an implementation problem, not permission to redefine the task.
   - If the requested window cannot be completed with authoritative data, report that limitation explicitly rather than shipping results for another period.
7. When source observations are sub-daily or instantaneous, reduce them to one daily value or daily exceedance indicator per station first; for flood-day counting, typically use each station's daily maximum and count distinct calendar dates with at least one exceedance rather than raw exceedance rows
   - Preferred proven pattern for multi-source tasks: run one end-to-end script or pipeline that loads the authoritative station list, retrieves thresholds and observations, computes daily maxima/exceedance days, writes `/root/output/flood_results.csv`, and then reads that file back for validation rather than stitching the result together across many disconnected commands.
   - Prefer this default pattern unless the prompt says otherwise: `sub-daily stage/gage height -> daily maximum per station -> compare to fixed flood threshold -> count exceedance dates`.
   - Do not count raw exceedance timestamps/rows as flood days; flood-day counts must be based on distinct calendar dates after aggregation.
8. Count flood days as days in that window where the daily event metric meets or exceeds the station's fixed threshold
8a. Enforce the date-window bound as a blocker: for April 1-7, 2025, every final `flood_days` value must be an integer from 0 to 7 inclusive. If you see 8+ or any other impossible value, treat the date filter or daily aggregation as wrong and rerun after fixing it.
8b. Do not explain away impossible counts as likely off-by-one behavior; correct the windowing or aggregation logic before proceeding.
9. If a small number of stations fail due to timeout or transient retrieval/processing issues, retry just those stations once before finalizing exclusions or zero-flood conclusions
   - Do not rerun the full workflow when only a few stations are incomplete; isolate the specific timed-out or partial stations, rerun checks just for them, and then merge that resolution back into the validated main result.
10. Keep only stations with >= 1 flood day and output only the requested columns (`station_id`, `flood_days`) unless the prompt explicitly asks for more
11. Restrict analysis to station IDs present in `/root/data/michigan_stations.txt` and verify every output `station_id` is a member of that input list

   - Treat the original input station list/count as an invariant. If a retrieval, join, or threshold step suddenly produces more stations than were in scope, fewer matched stations than expected, or reformatted IDs, debug that mismatch before proceeding.
12. Validate the final CSV before declaring success: required columns, requested sort/order, exact `station_id` formatting including leading zeros, membership of every output `station_id` in the input station list, plausible station counts relative to the inspected input, `flood_days` bounds of 0-7 for the April 1-7 window, and exactly the required output columns with no extra diagnostic fields; if results look suspicious (for example, nearly every station floods), re-check threshold provenance and logic
- Verify the artifact directly, not just by path existence: open `/root/output/flood_results.csv`, confirm it is readable, and inspect its columns/row shape before finalizing.
- Re-open `/root/output/flood_results.csv` after writing it and inspect the actual saved header, row count, and a few sample rows instead of relying on in-memory tables or log messages alone.
- Do not stop at a head/tail preview. Read enough of the written CSV to verify there are no out-of-scope station IDs and no impossible `flood_days` values anywhere in the file.
- Do not treat truncated processing logs, partial progress messages, or mere file existence as evidence of success. Require a clean execution signal plus requirement-level CSV checks before finalizing.
- Reconcile narrative claims with artifacts before finalizing: any station ID mentioned in logs, previews, or the final summary must appear in the inspected input scope and in the written CSV when applicable; if you see an unexpected ID or row-count jump, treat it as a blocker and investigate.
- Reconcile logs with artifacts: if script stdout/stderr says a station had `0 flood days` or reports a different processed-station count than the CSV implies, treat that contradiction as a blocker and debug before delivery.
- Perform an end-to-end ID audit on 3-5 sample stations from input -> threshold/joined data -> final CSV, confirming the exact same zero-padded string survives every step (for example, `04031000` must never silently become `4031000`).
- Make the membership check explicit: compute `unexpected_ids = output_ids - input_ids` and treat any non-empty `unexpected_ids` as a failure that must be fixed before delivery.
- Treat any `flood_days` value outside 0-7 for the April 1-7 window as a hard failure requiring debugging before completion.
- Treat count mismatches as blockers, not warnings: reconcile input station count, parsed in-scope station count, analyzed station count, and output row count before finishing.
- If a script's stdout/log summary conflicts with the generated CSV or intermediate tables, treat that as a blocker: inspect the underlying data/join logic, rerun after fixing, and do not declare success until the results are reconciled.
- If results look plausible only because a CSV was produced, but the threshold inputs were not visibly validated, do not finalize.
13. For workflows that combine multiple sources, prefer one reproducible end-to-end pipeline that loads the station IDs first, performs joins/calculations in one place, writes `/root/output/flood_results.csv`, and then inspects the written CSV directly
   - A strong default is: do a quick dependency/import check first, then use one small validated Python script or inline Python workflow that loads station scope, retrieves thresholds/observations, computes daily exceedances, filters to `flood_days >= 1`, writes `/root/output/flood_results.csv`, and reads that CSV back for validation before finalizing.
   - Before committing to that pipeline, do a quick viability check on the planned access method (for example, import the required client library such as `dataretrieval`) so you can switch methods early if the dependency is unavailable.
   - If a needed library for the chosen approach is already importable, use it rather than spending effort on installation.
   - Prefer this single end-to-end pipeline over manually stitching together many partial commands when processing many stations or multiple data sources.
   - A staged workflow is also acceptable when it improves validation: separate acquisition, threshold retrieval, and analysis into a small number of checked steps, but validate each intermediate artifact and then rerun the full final audit on the written `/root/output/flood_results.csv`.
   - In multi-step scripts, emit simple stage-level counts (for example: input stations loaded, thresholds matched, stations with observations, output rows written) so a zero-count stage immediately identifies where the pipeline failed.
   - If the analysis logic is sound but the run yields empty results or retrieval/API errors, keep the validated input/output contract and counting logic fixed; replace or debug only the retrieval layer, then rerun the same end-to-end pipeline.
   - Do not redesign station scope, date window, threshold semantics, or output schema just because one retrieval method failed.
   - If execution fails because the host Python is externally managed, create and use a virtual environment in an allowed writable directory, install there, then rerun the same end-to-end pipeline instead of retrying blocked system-wide installs.
   - If you rewrite or replace the pipeline after failures/timeouts, treat the new workflow as untrusted until it passes a fresh invariant audit against the final artifact: required columns, exact requested date window, `processed_ids ⊆ input_ids`, and `output_ids ⊆ input_ids`.
   - Do not assume a rewritten script preserved the original station filter. After each major approach change, explicitly compute and inspect set differences such as `processed_ids - input_ids` and `output_ids - input_ids` before declaring success.
- If you abandon one approach and switch to a rewritten script or retrieval method, re-run the final artifact audit from scratch on the written CSV: required columns, exact date-window logic, and especially `output station_id ⊆ input station_id`.
14. If authoritative thresholds or required data for the requested window are unavailable, report the limitation explicitly rather than inventing criteria, using alternate heuristics, or changing the scope

15. Do not ask the user for permission to perform substeps already implied by the task, such as fetching required observations or thresholds; execute them when needed and allowed
16. If you generate helper scripts, confirm the on-disk contents are actual executable code, not a prose description; read the file back and run a quick syntax/import check (for example, `python -m py_compile` when available) before executing or depending on it
   - After every file write intended as code, inspect the saved file directly (for example with `cat`, `sed`, or a Python readback) before execution. Never assume a write tool produced code just because the plan said "write a script."
17. Add a scope guard before finalizing: compare the station IDs actually processed and the station IDs written to `/root/output/flood_results.csv` against the IDs loaded from `/root/data/michigan_stations.txt`; if any processed or output ID is outside the input set, the run is invalid
18. Perform a procedural finalization gate after validating the CSV: confirm that all prior tool interactions used the exact runtime-required action schema, then send the exact required completion string alone (for example, `ACTION: TASK_COMPLETE` if specified). Do not add a narrative success summary before or after that marker.
19. Keep the final CSV limited to the requested positive cases only: include stations with `flood_days >= 1` and exclude zero-flood stations unless the prompt explicitly asks for the full evaluated population

0. If relevant local skill/guide documentation is available in the environment, scan the task-relevant guides first to confirm the intended end-to-end workflow before implementing anything; for this task family, preserve the sequence: load station scope -> obtain authoritative flood thresholds -> fetch observations for the requested window -> aggregate to daily exceedance/flood days -> write and validate `/root/output/flood_results.csv`.


## Tips

- Check for flood stage/threshold values
- A reliable pattern is: build a `station_id -> flood threshold` map first, normalize the observation series to one value per day when needed (typically daily max for sub-daily stage/height data), then count April 1-7 exceedance days.
- Before expensive retrieval, do a quick preflight: confirm the input file structure/count and test-import the libraries you plan to use so you can switch methods early if needed.
- When joining the provided station IDs to external thresholds, prefer a keyed lookup/table and explicitly check coverage (`matched`, `unmatched`) before fetching or aggregating observations.
- A proven implementation pattern is to put station loading, threshold retrieval, observation download, daily-max aggregation, flood-day counting, and CSV export into one reproducible script/pipeline, then validate by reopening the written CSV.

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
- When data comes from multiple sources, pick one canonical `station_id` representation early and enforce it everywhere before saving intermediates; this prevents late-stage fixes and silent merge failures.
- When external sources return IDs in inconsistent formats, explicitly coerce them back to the canonical station format observed in `/root/data/michigan_stations.txt` before comparing, merging, or filtering.
- When external retrieval is explicitly required, prefer the source whose temporal granularity matches the metric: for day-level flood counts, use sub-daily observations when needed and aggregate to daily maxima rather than relying on daily summaries that can miss peaks.
- For high-frequency records, derive `flood_days` from unique exceedance dates or a daily exceedance indicator, not the raw number of exceedance rows or timestamps.
- A reliable working pattern for sub-daily stage data is: convert timestamps to station-local calendar dates consistently, compute each station's daily maximum stage, compare that daily max to the fixed flood threshold, then count exceedance dates within April 1-7, 2025.

- If the task explicitly requires retrieving thresholds for many stations from external sources, prefer a bulk metadata export/report over station-by-station requests, then filter it to the station IDs in `/root/data/michigan_stations.txt`.
- When a bulk threshold file is used, inspect a few filtered rows after normalization to confirm the join worked as intended and that the retained station IDs still exactly match the in-scope input IDs.

- Do not change core task parameters (date range, dataset, station scope) unless the user explicitly authorizes it.
- After loading data, inspect dataframe columns and index explicitly, and verify intermediate counts are consistent with the input you observed.
- Normalize datetimes before resampling or date filtering so timezone-aware timestamps do not cause off-by-one day errors or slicing failures.
- If command output is truncated or partial, verify generated files directly (exists, row count, sample rows) before proceeding.
- For workflows that combine multiple sources, prefer one validated pipeline that loads inputs, performs joins, computes daily metrics, and writes the final CSV.
- After writing `/root/output/flood_results.csv`, explicitly compare output `station_id` values to the IDs loaded from `/root/data/michigan_stations.txt`; fail the run if any output ID is outside that source list.
- After writing `/root/output/flood_results.csv`, read it back and verify the required columns, row filtering, and station IDs before declaring success.
- Make the readback check concrete: inspect row count, columns, and 3-5 sample `station_id` values, and confirm the written IDs still match the authoritative input formatting rather than a normalized-but-altered variant.
- Do not rely on console progress logs alone; open the written CSV itself to confirm the file path, schema, and representative rows match the intended final deliverable.
- Treat direct inspection of the written `/root/output/flood_results.csv` as mandatory after any script run or rerun: confirm the file was regenerated and reflects the latest execution rather than an earlier partial output.
- If an end-to-end run produces empty results or an unexpected zero count, use the stage-level counts/messages to localize the failure before changing data sources or task parameters.
- Sanity-check output against hard bounds and semantics: for April 1-7, `flood_days` must be between 0 and 7 for every station; if nearly every station floods, re-check the threshold method.
- Treat empty or missing results as a debugging signal about path, parser, column choice, or threshold method, not as justification to change dates or produce a substitute-period CSV.
- If you write Python for the analysis, perform a quick syntax/quoting sanity check and confirm the output file was actually created before concluding.
- Never rely on a just-written script without a readback. If the file contents say things like "created a script" or otherwise summarize intended logic instead of implementing it, treat that as a failed write and replace it with real code before proceeding.
- Do not treat successful CSV creation as sufficient; validate schema, confirm all output station IDs come from the input file, and always write `/root/output/flood_results.csv` even if the correctly processed result is empty.
- Validation is not complete until both are true: the CSV is correctly formatted, and the flood/non-flood logic is justified by an external or task-provided threshold definition.

- Keep a simple invariant checklist during the run: original station count, exact set membership, and `station_id` string formatting. Re-check these after each major load, join, retrieval, or pipeline rewrite.
- Do not rely on a script's default station source. Pass the IDs loaded from `/root/data/michigan_stations.txt` explicitly into the processing pipeline, or verify the script is reading that file directly.
- Preserve `station_id` as a zero-padded string in every dataframe, file, join key, log, and CSV. Spot-check 3-5 IDs end-to-end from input file to final CSV; if you ever see a form like `4031000` for input ID `04031000`, treat that as a bug and debug before proceeding.
- Prefer an explicit set-based audit over visual inspection, e.g. compare `set(output.station_id)` to `set(input_ids)` and investigate any non-empty difference before concluding.
- Make the scope audit two-stage when possible: first verify the station IDs actually processed by the pipeline are a subset of `input_ids`, then verify the written CSV IDs are also a subset of `input_ids`. Catching drift before CSV export is preferable to discovering it only at the end.
- When the input preview shows an anomalous ID like a truncated-looking value, treat that as a parsing/file-integrity issue to resolve before expensive downloads, not as harmless noise.
- If intermediate outputs, logs, and the written CSV disagree with each other, do not trust any one of them by default; reconcile the contradiction first, then regenerate the CSV.
- If requested data seems unavailable, keep the requested period and scope fixed while testing alternate retrieval methods, endpoints, or aggregation approaches that still produce the requested result.
- If threshold retrieval had earlier failed or returned missing data, add a visible checkpoint showing several retrieved threshold values before trusting downstream flood-day counts.
- Separate debugging validation from final analysis: a historical or known-good flood period can help verify parsing/threshold logic, but must not be used for the final CSV unless the user explicitly changes the task.
- Impossible outputs are hard failures: for an April 1-7 analysis, `flood_days > 7` means the date window or aggregation is wrong and must be corrected before completion.
- If a quick file preview is truncated, re-open the written CSV with a full structured check (row count, columns, sample IDs, out-of-scope IDs) before declaring success.
- Before finalizing, perform a last checklist: output file exists, schema is correct, all `flood_days` are within the task's date-window bounds, threshold provenance was validated, and the exact required completion marker will be emitted.


- A reliable opening pattern is: inspect `/root/data/michigan_stations.txt` to determine whether it is IDs-only or contains observations, then do a quick interpreter/package import check before writing the main workflow.
- Proven working pattern for multi-step jobs: dependency/import check first, then one end-to-end script or inline Python pipeline, then inspect `/root/output/flood_results.csv` directly after execution.
- Before trusting a bulk external-data pipeline, inspect one returned station sample to confirm the index layout and the exact stage/gage-height measurement column being aggregated.
- If a bulk run succeeds except for a few timed-out or incomplete stations, retry only those edge cases and confirm their status rather than recomputing every station.
- If dependencies are missing, use a venv in an allowed writable directory as the default fallback; keep the script and the environment local to allowed paths.
- When the task is event detection, keep the proven pattern: join authoritative per-station thresholds to observed measurements, aggregate observations to the reporting unit required by the task (here, daily exceedance/daily max), then count qualifying days.