---
name: usgs-nws-flood-detection
description: "Compare USGS gage-height time series to NWS flood-stage thresholds over a date range and export stations with at least one flood day."
---

USGS–NWS Flood Detection

Detect days with flooding by comparing USGS instantaneous gage-height (parameter 00065) to NWS flood-stage thresholds, aggregating to daily maxima, and counting days at/above threshold. Outputs stations with at least one flood day.

When to Use

- You have a list of USGS station IDs and need to find which experienced flooding in a given date window.
- The task expects counts of calendar days with flooding and a CSV output of station_id and flood_days.

Core Workflow

1) Inspect and normalize station IDs
- Read the station list file and confirm it contains one USGS site number per line.
- Strip whitespace; ignore blank lines and comment lines (e.g., starting with #).
- Preserve leading zeros in site numbers. If you need to compare to external sources that sometimes include decimal artifacts (e.g., "12345678.0"), normalize those external IDs to digit strings and zero-pad to 8 digits during matching.

2) Obtain NWS flood-stage thresholds (authoritative)
- Source: NWS bulk CSV of gauges and thresholds. Fetch robustly and parse even if the CSV has row-length inconsistencies by truncating data rows to the header length.
- Convert the flood-stage column to numeric; treat missing/invalid values and known sentinels (e.g., -9999) as absent.
- Normalize the CSV "usgs id" values (strip whitespace, remove ".0"/decimals, digits only, zero-pad to 8). Build a map from normalized USGS ID to flood stage (feet).
- For each input station, normalize the ID the same way and look up its threshold. Skip stations without a valid threshold.

3) Retrieve USGS instantaneous gage height (parameter 00065)
- Use the instantaneous values (IV) service. With the Python dataretrieval package, call nwis.get_iv(sites=..., parameterCd='00065', start=..., end=...). Note: get_iv may return (df, metadata). Handle both cases.
- To ensure the final day is fully included, either:
  - request endDT as the day after the inclusive end date, then later filter back to the inclusive end date; or
  - request the exact inclusive end and group by calendar date derived from timestamps (less robust if service treats end as exclusive).
- Identify the gage-height column by searching for column names containing "00065" and excluding quality code columns (names often include "_cd").

4) Aggregate to daily maxima and count flood days
- Convert gage-height values to numeric.
- Derive calendar dates from the timestamp index (e.g., group by index.date) and compute the daily maximum.
- Count the number of days where the daily maximum is at or above the NWS flood-stage threshold. Use a consistent rule (>=) to represent “at/above flood stage”.
- Keep only stations with flood_days > 0.

5) Output
- Write a CSV with exactly two columns: station_id,flood_days.
- Create the output directory if it does not exist.
- Sort rows deterministically (e.g., by station_id or by flood_days desc) if not specified.

Verification

- Sanity checks before writing results:
  - Confirm number of input stations read matches expectation from the station file.
  - Log how many stations have valid NWS thresholds.
  - For a sample station, confirm the gage-height column detection worked and inspect a few values.
  - Ensure the aggregation produces up to one value per date in the requested range; verify inclusive end-date handling by checking the last day is present.
- After writing the CSV:
  - Confirm the file exists and contains the header station_id,flood_days.
  - Spot-check at least one station where a daily maximum visibly exceeds the threshold to ensure the count increments.

Common Pitfalls and How to Avoid Them

- Using the wrong USGS service or function:
  - Pitfall: Calling APIs intended for statistics or daily values and expecting instantaneous data. Use nwis.get_iv for IV data.
- Misinterpreting get_iv return shape:
  - Pitfall: Assuming a single DataFrame is returned. Some dataretrieval versions return (df, metadata). Detect and unpack tuples safely.
- Wrong variable/column selection:
  - Pitfall: Comparing thresholds (feet) to discharge (cfs) or grabbing quality-code columns. Always use parameter 00065 and exclude columns with "_cd".
- Threshold acquisition failures:
  - Pitfall: CSV row/header mismatches or sentinel values (-9999). Truncate rows to header length; coerce numeric; drop invalids and sentinels.
  - Pitfall: ID mismatches due to formatting ("12345678.0"). Normalize external IDs to digits and zero-pad to 8 for matching.
- Date-range inclusivity:
  - Pitfall: Missing the last day because an API treats end as exclusive. Request through the next day and then filter to the inclusive end.
- Fabricating thresholds:
  - Pitfall: Substituting statistical percentiles as flood-stage thresholds when the task requires NWS thresholds. Only use such heuristics if explicitly requested.
- Empty or missing data:
  - Pitfall: Crashing or writing malformed outputs when a station lacks data or thresholds. Skip safely and still produce a valid CSV (possibly empty with just headers).
- Rate limits/timeouts:
  - Pitfall: Large sequential requests hanging or being throttled. Add light throttling, short timeouts, and progress logging; handle exceptions and continue.

Success Criteria

- Output CSV exists with only station_id and flood_days columns.
- Only stations with flood_days > 0 are present.
- Flood day counts reflect days where the daily maximum gage height is at/above the NWS flood-stage threshold within the inclusive date range.

Optional Script Usage

- A reusable script is provided to perform the end-to-end workflow.
- Example:
  - python scripts/usgs_nws_flood_detect.py --stations /path/to/stations.txt --start 2025-04-01 --end 2025-04-07 --out /path/to/flood_results.csv
- The script:
  - Reads station IDs, fetches NWS thresholds, downloads USGS IV gage height (00065), aggregates to daily maxima, counts flood days (>= threshold), and writes the CSV with required columns.
