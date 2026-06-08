---
name: daily-threshold-exceedance
description: "Compute per-station daily exceedance counts over a date window and write a filtered CSV; use for flood-days or similar threshold analyses."
---

# Daily Threshold Exceedance Detection

This skill guides you to compute, validate, and export the number of calendar days each station exceeded a reference threshold within a specified date window. It abstracts a reliable workflow for flood-day detection (e.g., USGS stage vs NWS flood stage) and similar per-day threshold analyses.

## When to Use

Activate this skill when the task asks you to:
- find stations that exceeded a threshold during a given period
- count daily exceedances (e.g., flood days) per station
- filter to stations with at least one exceedance and produce a two-column CSV
- combine time-series observations with a station-to-threshold mapping

## Core Workflow

1. Inspect Inputs
   - Open the station list file and confirm format (one station ID per line is common). Preserve IDs as strings to keep leading zeros. Ignore blank lines and comments.
   - Identify the target variable and units for both observations and thresholds (e.g., stage in feet vs meters, or discharge). Confirm the observation parameter matches the threshold domain.
   - Clarify the date window and whether it is inclusive of both start and end dates. Treat days as calendar days in a chosen timezone (default UTC), consistently applied across all stations.

2. Retrieve/Assemble Thresholds
   - Build a mapping station_id → threshold_value (+ units if available).
   - Normalize station IDs as strings. If multiple naming schemes exist, apply consistent formatting to both sources (e.g., strip spaces, ensure leading zeros). Do not coerce to integers.
   - If units differ between observations and thresholds, convert to a common unit before comparison.
   - Exclude stations without a usable threshold from exceedance analysis.

3. Collect Observation Data
   - Fetch or read observations covering the entire date window for each station.
   - Use appropriate parameters (e.g., gage height for stage thresholds, discharge for flow thresholds) and verify units returned.
   - If using high-frequency/instantaneous data, plan to aggregate to daily maxima.
   - Handle API constraints: paginate, rate-limit, and retry transient failures. Log missing data per station.

4. Aggregate to Daily Maxima
   - Normalize timestamps to the chosen timezone.
   - Group by (station_id, calendar date) and compute the daily maximum value.
   - Decide how to treat days with sparse data. Recommended: require at least one valid observation on the day; otherwise, treat as missing (not a flood day).

5. Detect Exceedances and Count Days
   - For each station with a threshold, mark a day as an exceedance if daily_max >= threshold.
   - Count exceedance days per station. Clamp counts to [0, number_of_days_in_window].

6. Filter and Export
   - Keep only stations with count ≥ 1, as many tasks request.
   - Write a CSV with exactly two columns and a header: station_id,flood_days.
   - Sort deterministically (e.g., lexicographically by station_id) for reproducibility.

7. Post-Run Verification
   - Re-open the output file and verify:
     - Only two columns are present with the correct header names.
     - No station_id lost leading zeros.
     - No count exceeds the number of days in the window.
   - Spot-check a few stations: manually compare a day’s max to its threshold to confirm classification.

## Verification Checklist

Use these checks to catch common issues early:
- Station ID integrity
  - Treat station IDs as strings; verify leading zeros are preserved end-to-end.
  - Ensure the same ID formatting is used when joining observations to thresholds.
- Date window correctness
  - Compute expected day count as (end_date − start_date + 1). Verify no station has a count above this.
  - Confirm the window is inclusive of both endpoints and calendar-day boundaries match the chosen timezone.
- Units and parameter matching
  - Observation parameter matches the threshold domain (stage with stage, discharge with discharge).
  - Units are consistent; apply conversions if needed.
- Data quality
  - Verify daily maxima are computed only from valid numeric observations.
  - Ensure missing-data days are not counted as exceedances.
- Output conformance
  - Header is exactly: station_id,flood_days.
  - Only stations with at least one exceedance are included, if required.

## Common Pitfalls and How to Avoid Them

- Losing leading zeros in station IDs
  - Pitfall: Casting IDs to integers and writing them back without zero-padding.
  - Avoidance: Keep station IDs as strings from parsing through to output.

- ID mismatch between datasets
  - Pitfall: Joining with different formatting (e.g., prefixes, whitespace, or missing zeros).
  - Avoidance: Normalize both sides consistently; compare sample keys and confirm overlap before running the full pipeline.

- Off-by-one day counts
  - Pitfall: Treating the end date as exclusive or using UTC boundaries while thresholds/expectations assume local time.
  - Avoidance: Define a timezone (e.g., UTC), apply it consistently to timestamps, and treat both start and end dates as inclusive calendar days.

- Wrong variable or unit mismatch
  - Pitfall: Comparing stage thresholds to discharge data, or mixing feet and meters without conversion.
  - Avoidance: Confirm parameter codes and units upfront; convert units explicitly.

- Counting days with missing or non-numeric data
  - Pitfall: NaNs or empty values inflating daily maxima or being misinterpreted as exceedances.
  - Avoidance: Require at least one valid numeric observation per day; ignore invalid rows when computing maxima.

- Unrealistic results without validation
  - Pitfall: All stations show floods or counts exceed the day window due to mis-aggregation or window errors.
  - Avoidance: Apply the verification checklist; spot-check a few stations against raw values and thresholds.

## Optional Script Usage

Use the helper script when you already have:
- Observations in a CSV with columns: station_id, timestamp, value
- Thresholds in a CSV with columns: station_id, threshold (and optional units)

It computes per-station daily maxima in a date window and outputs station_id,flood_days for stations with at least one exceedance.

Example:
- observations.csv columns: station_id,timestamp,value
  - timestamp should be ISO 8601 (e.g., 2025-04-01T13:45:00Z) or a parseable datetime string.
- thresholds.csv columns: station_id,threshold[,units]

Run:
- python3 scripts/daily_threshold_exceedance.py \
  --observations observations.csv \
  --thresholds thresholds.csv \
  --start-date YYYY-MM-DD \
  --end-date YYYY-MM-DD \
  --output flood_results.csv \
  --data-units ft \
  --threshold-units ft

Script guarantees:
- Station IDs treated as strings
- Inclusive date window
- Optional unit conversion between feet and meters
- Output CSV with exactly: station_id,flood_days
