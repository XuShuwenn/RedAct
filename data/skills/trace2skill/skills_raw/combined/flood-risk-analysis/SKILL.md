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

## Output

CSV at `/root/output/flood_results.csv`.


## Output

## Execution Protocol Checks

- Follow the task/runtime's exact tool-call and action protocol if one is specified; do not invent alternate wrappers, tags, or markdown around tool calls.
- Do a quick preflight before any analysis: confirm the required tool/action format, allowed read/write paths, and exact required final response string if one exists.
- If the runtime specifies an exact tool-call schema, use that format verbatim for every step; do not switch to other wrappers or freeform command styles mid-task.
- Before the final response, check whether the task/runtime requires an exact completion string or token. If it does, output that exact string and nothing else.
- Write generated files only inside explicitly allowed directories. If only `/root/output` is writable, do not create helper scripts under `/root/` or elsewhere.
- Keep all helper code, temp files, and outputs inside explicitly allowed directories only; otherwise prefer inline commands so nothing is written outside allowed paths.
- Verify every command or script actually succeeded before building on it: inspect stdout/stderr and exit status, and fix syntax/quoting errors before proceeding.
- If command output is truncated, cut off, or stops mid-process, do not assume success. Confirm completion by checking exit status and inspecting the expected artifact directly.
- Do not assume a generated script ran just because the file was written; explicitly run it, inspect the result, and verify the expected output artifact was created or updated.
- Before attempting package installation or environment changes, quickly check whether the needed interpreter and Python packages are already available/importable and prefer existing dependencies when present.
- Before running any non-trivial Python block or external-retrieval workflow, do a quick viability check: confirm needed libraries import successfully, keep quoting simple, and fix syntax/quoting errors before proceeding.
- Prefer inline Python or shell commands, or a single small validated Python script inside an allowed writable directory, over scattered temporary files when directory permissions are constrained.
- If the analysis spans many stations or combines threshold lookup, time-series processing, and CSV generation, prefer one validated end-to-end Python workflow over many ad hoc commands.
- If Python package installation is blocked by an externally managed system environment, create and use a virtual environment in an allowed writable location rather than forcing a system-wide install.
- If a planned package or tool is unavailable, switch to another valid in-environment method or explicitly report the limitation instead of continuing with an unvalidated workflow.
- Do not treat a requested date as invalid, unavailable, or "in the future" unless you have direct evidence from the data source, task context, or runtime.
- Immediately before finishing, confirm the required output file exists and then emit the exact required completion marker with no extra text if the runtime specifies one.
## Key Steps

1. Inspect `/root/data/michigan_stations.txt` first to determine whether it contains station IDs only, metadata, or actual measurements, and preserve every `station_id` exactly as text
2. If the file contains measurements, parse them directly; inspect the dataframe/schema before choosing the measurement column, identify the requested series by name rather than position, and prefer stage/gage-height observations when that matches the task
3. If the file is only a station list or scope file, use it to define station scope and obtain the required thresholds and observations separately only when the task allows or requires that
4. Determine each station's flood threshold from authoritative station metadata or task-provided data before classifying any day; record threshold provenance, normalize join keys on every input to the same string format, spot-check that leading zeros survived parsing, and verify measurement type/units match before comparison
5. Normalize observation timestamps to a consistent datetime representation before resampling or slicing by calendar date
6. Filter the exact requested date range (April 1-7, 2025); if data appears missing or unusable, debug parsing, measurement selection, and data-source assumptions first, but do not substitute another year or window unless the user explicitly authorizes it
7. When source observations are sub-daily or instantaneous, reduce them to one daily value or daily exceedance indicator per station first; for flood-day counting, typically use each station's daily maximum and count distinct calendar dates with at least one exceedance rather than raw exceedance rows
8. Count flood days as days in that window where the daily event metric meets or exceeds the station's fixed threshold
9. If a small number of stations fail due to timeout or transient retrieval/processing issues, retry just those stations once before finalizing exclusions or zero-flood conclusions
10. Keep only stations with >= 1 flood day and output only the requested columns (`station_id`, `flood_days`) unless the prompt explicitly asks for more
11. Restrict analysis to station IDs present in `/root/data/michigan_stations.txt` and verify every output `station_id` is a member of that input list
12. Validate the final CSV before declaring success: required columns, requested sort/order, exact `station_id` formatting including leading zeros, membership of every output `station_id` in the input station list, plausible station counts relative to the inspected input, `flood_days` bounds of 0-7 for the April 1-7 window, and exactly the required output columns with no extra diagnostic fields; if results look suspicious (for example, nearly every station floods), re-check threshold provenance and logic
13. For workflows that combine multiple sources, prefer one reproducible end-to-end pipeline that loads the station IDs first, performs joins/calculations in one place, writes `/root/output/flood_results.csv`, and then inspects the written CSV directly
14. If authoritative thresholds or required data for the requested window are unavailable, report the limitation explicitly rather than inventing criteria, using alternate heuristics, or changing the scope

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