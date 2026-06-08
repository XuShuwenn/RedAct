---
name: seismic-phase-association
description: "Detect and associate seismic phase picks into earthquake events from waveform and station data, then output event times in ISO format."
---

# Seismic Phase Association

This skill turns raw seismic waveforms and station metadata into a list of earthquake event origin times by: picking P/S arrivals with a pretrained model, associating picks across stations using a simple velocity model, and writing a results CSV with ISO timestamps.

## When to Use

Activate this skill when you need to:
- Load MSEED (or similar) waveforms and station metadata to detect local/regional earthquakes
- Run a pretrained phase picker to obtain P/S arrival times
- Group picks across stations into events (phase association) using a basic velocity model
- Produce a results file with event times in ISO 8601 format (no timezone)

## Core Workflow

Follow these phases. Test each phase on a small subset before scaling up.

1) Environment and Dependencies
- Use a waveform I/O library (e.g., ObsPy), a deep-learning picker (e.g., a SeisBench model), and an association tool (any standard associator). Coordinate utilities (e.g., a projection library) are optional but helpful.
- Cache or pre-download model weights to avoid repeated downloads.

2) Load Station Metadata
- Read the station table with columns similar to: network, station, channel, longitude, latitude, elevation_m, response.
- Normalize a consistent station-channel identifier. Recommended canonical form: NET.STA.CHAN (optionally include location if present). Uppercase all parts, strip whitespace. Deduplicate rows by this ID.
- Validate coordinates: latitude in [-90, 90], longitude in [-180, 180], and no NaNs.

3) Load and Inspect Waveforms
- Read the waveform file(s). Inspect a few trace headers to verify network, station, channel names match your station table’s identifier scheme.
- Check sampling rates and trace lengths. If your picker expects a specific sampling rate, resample accordingly.
- Preprocess: detrend, taper, and bandpass to a typical picking band (domain-appropriate). Normalize per trace (e.g., standardize) to stabilize the picker.
- Chunk long recordings into manageable windows to prevent picker memory issues and to enable progress tracking.

4) Run Phase Picking
- Apply a pretrained picker to each window/component as needed.
- Verify the model output structure on a small sample before full runs. Extract for each detection:
  - station_id (matching the canonical form)
  - phase_type (P or S)
  - pick_time as a datetime object (not a string)
  - quality/score (if provided)
- Filter picks by minimum score/confidence to reduce false positives. Log counts per phase/station.

5) Prepare Association Inputs
- Compute local Cartesian coordinates for stations (project lon/lat to meters). If a projection utility isn’t available, a simple equirectangular approximation is acceptable for short ranges.
- Compute coordinate bounds (x/y min/max, and depth range). Add a small margin to bounds to allow for event locations near the edge.
- Use a uniform velocity model, e.g., vp = 6 km/s and vs = vp/1.75. Keep units consistent (km vs. m).
- Estimate a time association window from the network span: window_seconds ≈ (max inter-station distance) / vs, then add a safety factor (e.g., +20–50%). The helper script below can estimate this.

6) Run Association
- Configure the associator with:
  - station coordinates and metadata
  - pick table (with datetime pick times, station_id, phase type)
  - velocity model (vp, vs), coordinate bounds, depth range
  - clustering/association window, residual tolerances
  - minimum number of stations per event (e.g., ≥3) to improve precision
- Ensure any count-like configuration values are integers. If you derive them by scaling, cast with int(...) to avoid slicing/type errors.
- Start with single-threaded execution for reliability; scale up only if stable.

7) Postprocess and Export
- Deduplicate events that are closer than a small temporal window by keeping the best-scored one or the first origin time.
- Sort events by time. Convert event times to ISO 8601 without timezone (naive datetime) only at the export step.
- Write results to a CSV with at least a column named time. Additional columns (e.g., num_picks, quality) are optional.

## Verification

Perform these checks before finalizing:
- Station/pick alignment: ratio of pick station_ids present in the station table should be high (target > 95%). If not, fix identifier normalization.
- Picker sanity: nonzero P and/or S picks; reasonable pick rates per station; no NaN times.
- Association sanity: nonzero events; events spread across the recording; min-stations-per-event satisfied.
- Time format: in the CSV, time must parse with datetime.fromisoformat and have tzinfo is None (no timezone). Use scripts/validate_events_csv.py.
- Sorting and duplicates: ensure sorted ascending and no duplicates within a small threshold (e.g., ≤ 5 s). The validator checks this.
- Configuration integrity: coordinate bounds cover all stations; integer-only config values are ints; units consistent (km vs m, s vs ms).

## Common Pitfalls

- Mismatched identifiers: Treating station/channel IDs differently between picks and station metadata (e.g., missing network, inconsistent casing). Define a canonical ID and enforce it everywhere.
- Timestamp type errors: Converting picks to strings too early. Keep pick times as datetime objects for association; stringify only when exporting.
- Integer vs float config: Any count-like parameter (e.g., number of initial centers, subsampling factors) must be int. Casting avoids slicing/type errors.
- Missing coordinate/depth bounds: Some associators require explicit x/y/z bounds. Derive from station coordinates with a margin; set depth range realistically.
- Sampling-rate mismatch: Pickers often expect specific sampling. Resample traces beforehand and confirm model requirements.
- Runtime stalls: Too many low-confidence picks or overly large association windows cause slowdowns. Increase pick thresholds, reduce window, or require more stations per event.
- Long windows: Picking entire very long records at once can exceed memory. Chunk and merge results.
- Timezones: Do not include timezone indicators (e.g., Z or +00:00) in the output time column.

## Success Criteria

- A CSV is produced with at least the column time in ISO 8601 format without timezone.
- Events are sorted, unique (no near-duplicates), and within the data’s time span.
- Internal checks pass (alignment, nonzero picks/events, valid bounds, integer configs).
- Thresholding/min-stations choices yield a reasonable balance of precision and recall.

## Optional Script Usage

- Validate output CSV times and basic integrity:
  - python scripts/validate_events_csv.py --file results.csv --max-dup-sec 5
- Estimate an initial association window from station geometry and velocity model:
  - python scripts/estimate_assoc_window.py --stations stations.csv --vp-km-s 6.0 --vs-km-s 3.4286 --safety 1.3

Adjust parameters based on network geometry and observed pick density.
