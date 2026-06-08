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

- `/root/data/michigan_stations.txt`: USGS streamflow records


- Treat `/root/data/michigan_stations.txt` as the primary and authoritative data source unless the prompt explicitly requires external retrieval.
- Inspect enough of the file to confirm its actual structure before choosing an approach.
- Treat `station_id` and any other identifiers as strings end-to-end; do not coerce to numeric because leading zeros are significant.

## Output

CSV at `/root/output/flood_results.csv`.


## Output

## Execution Protocol Checks

- Follow the task/runtime's exact tool-call and action protocol if one is specified; do not invent alternate wrappers, tags, or markdown around tool calls.
- Before the final response, check whether the task/runtime requires an exact completion string or token. If it does, output that exact string and nothing else.
- Write generated files only inside explicitly allowed directories. If only `/root/output` is writable, do not create helper scripts under `/root/` or elsewhere.
- Verify every command or script actually succeeded before building on it: inspect stdout/stderr and exit status, and fix syntax/quoting errors before proceeding.
- Prefer inline Python or shell commands, or small validated commands, over temporary script files when directory permissions are constrained.
## Key Steps

1. Parse streamflow data by station, preserving `station_id` exactly as text
2. Inspect the parsed dataframe/schema before choosing the measurement column; identify the requested series by name, not by position
3. Determine each station's flood threshold from authoritative station metadata or task-provided data before classifying any day
4. Filter the exact requested date range (April 1-7, 2025); do not substitute another window if data is missing or unusable
5. Count days in that window where observed values exceed the fixed threshold
6. Keep only stations with >= 1 flood day
7. Restrict analysis to station IDs present in `/root/data/michigan_stations.txt` and verify every output `station_id` is a member of that input list
8. Validate the final CSV before declaring success: required columns, requested sort/order, station_id formatting, plausible station counts, and `flood_days` bounds for the 7-day window
9. If authoritative thresholds or required data for the requested window are unavailable, report the limitation explicitly rather than inventing criteria or changing the scope

## Tips

- Check for flood stage/threshold values
- Use pandas for data analysis
- Create output directory if needed
- Sort results by station_id


- When using pandas, load station identifiers with string dtype (for example, `dtype={'station_id': 'string'}` or equivalent) and re-open the output CSV to confirm leading zeros were preserved.
- Before joining station metadata or thresholds with streamflow data, spot-check a few keys to confirm leading zeros are preserved on both sides.
- Treat the provided local file as authoritative unless the task explicitly requires another source; do not introduce external downloads, alternate measurements, or substitute datasets.
- Read from and write to only task-authorized paths; keep any helper artifacts inside allowed directories.
- Do not invent flood criteria from relative statistics, percentiles, or heuristics unless the task explicitly authorizes that approximation.
- Do not compute the flood threshold from the same April 1-7, 2025 evaluation window being labeled; use an external definition, metadata, or separately established baseline.
- If no authoritative flood threshold is available, stop and state the missing requirement or limitation instead of substituting an arbitrary heuristic.
- Do not change core task parameters (date range, dataset, station scope) unless the user explicitly authorizes it.
- After loading data, inspect dataframe columns and index explicitly, and verify intermediate counts are consistent with the input you observed.
- If command output is truncated or partial, verify generated files directly (exists, row count, sample rows) before proceeding.
- Sanity-check output against hard bounds and semantics: for April 1-7, `flood_days` must be between 0 and 7 for every station; if nearly every station floods, re-check the threshold method.
- If you write Python for the analysis, perform a quick syntax/quoting sanity check and confirm the output file was actually created before concluding.
- Do not treat successful CSV creation as sufficient; validate schema, confirm all output station IDs come from the input file, and always write `/root/output/flood_results.csv` even if the correctly processed result is empty.
