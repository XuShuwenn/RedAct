---
name: robust-seismic-phase-picking
description: "Pick P and S arrivals from three-component traces using lightweight preprocessing and STA/LTA, avoiding heavy dependencies and brittle assumptions."
---

# Robust Seismic Phase Picking (Lightweight Baseline)

This skill distills a dependable workflow for P/S phase picking on three-component seismic traces using only NumPy (no heavy installs). It addresses common failure modes seen when agents lean on large ML stacks or make brittle assumptions about data scale, sampling rate, or channel order.

Use this when you need to:
- Process many NPZ traces with fields like data (N×3), dt (sampling interval), and channels
- Produce a CSV of picks without relying on heavy deep-learning frameworks
- Avoid stalls from package downloads and environment issues

## Core Workflow

1) Enumerate and Load Traces
- Read .npz files from the provided directory.
- Expect keys: data (N×C), dt (float), channels (string or array). Allow C ≥ 3.
- Coerce dt to float via float(np.array(dt).item()).
- Parse channels robustly: handle bytes/np arrays/strings; split comma-separated if needed.

2) Channel Mapping (Z/E/N)
- Try to map indices by channel suffixes: Z → vertical; E and N → horizontals.
- Fallback if unknown: assign any remaining columns deterministically.
- Use H = sqrt(E^2 + N^2) as horizontal energy proxy.

3) Preprocessing (Scale-Invariant)
- Replace NaN/Inf with 0.
- Robust-scale each channel: subtract median, divide by MAD + epsilon.
- High-pass via moving-average subtraction over ~0.5 s (no SciPy needed).
- Build simple energy envelopes: moving average of squared signal over ~0.2 s.

4) Detection via STA/LTA (ratio-based, scale-robust)
- Compute STA/LTA on squared amplitudes:
  - P detector: on Z channel
  - S detector: on H
- Typical windows: STA ~0.3 s, LTA ~3.0 s (ensure LTA > STA in samples).
- Thresholds (tunable): P thr ~3.0, S thr ~2.5.
- Find contiguous-above-threshold regions; pick local maxima; enforce minimum separation (e.g., 0.15 s).

5) Picking Logic and Constraints
- Start searching after a small buffer (e.g., 0.1–0.5 s) to avoid edge artifacts.
- P picks: take first one or top-K maxima as needed.
- S picks: require they occur after P by at least a small gap (e.g., ≥0.2 s).
- Optional validation: local H/Z envelope ratio around S pick should exceed a minimum (e.g., ≥1.2) to prefer horizontal dominance.

6) Output Results CSV
- One row per pick with columns: file_name, phase, pick_idx (0-based index).
- Index bounds: 0 ≤ pick_idx < N.
- Ensure header present; write all files’ picks into a single CSV.

## Verification

Before finalizing:
- File-level checks:
  - data has shape (N, C) with C ≥ 3; dt > 0.
  - Channel mapping resolved to three indices (Z, E, N).
  - Computed windows in samples are ≥ 1 and LTA > STA.
- Detector sanity:
  - Ratio arrays are finite (no NaN/Inf); thresholds applied as intended.
  - P appears before S for each file where both exist; S respects minimal gap from P.
- Output integrity:
  - results.csv exists and has the header: file_name,phase,pick_idx
  - All pick_idx are integers within [0, N-1].
  - Non-empty output for typical datasets (unless data is truly silent).
- Tolerance reasoning:
  - Index tolerance for grading = round(0.1 / dt). Confirm it is reasonable (e.g., > 0).

## Common Pitfalls and How to Avoid Them

- Heavy dependency installs stall/hang
  - Avoid installing large packages (torch, obspy, seisbench) under time or network constraints. Use NumPy-only STA/LTA baseline.

- Assuming fixed sampling rate (dt)
  - Always read dt per file and convert all time-based windows to samples via round(seconds / dt).

- Misreading channels
  - channels can be bytes, ndarray, or strings. Parse robustly and fall back deterministically if suffix heuristics fail.

- Scale issues (near-zero amplitudes)
  - Use robust scaling (median/MAD) and ratio-based detectors (STA/LTA). Avoid absolute thresholds tied to raw amplitudes.

- Poor S-pick precision
  - Gate S after P by a minimal time. Prefer horizontal energy detector and validate with H/Z envelope ratio.

- Invalid or missing CSV structure
  - Include header exactly once; ensure integer indices; no out-of-bounds values.

- Edge artifacts and multiple close peaks
  - Begin search after a small buffer. Group contiguous detections and pick the local maximum; enforce minimal separation between picks.

## Optional Script Usage

A reusable NumPy-only picker is included.

Example:
- python scripts/seismic_sta_lta_picker.py --data-dir /root/data --out /root/results.csv

Key parameters (seconds unless noted):
- --sta-sec (default 0.3), --lta-sec (3.0), ensure LTA > STA
- --hp-sec (0.5) moving-average high-pass window
- --envelope-sec (0.2) smoothing for energy envelopes
- --min-sep-sec (0.15) minimal separation between picks
- --p-thr (3.0), --s-thr (2.5) STA/LTA thresholds
- --s-after-p-sec (0.2) minimal S gating after P
- --hz-min-ratio (1.2) minimal H/Z envelope ratio near S
- --max-picks-per-phase (1)

Success criteria:
- Produces a well-formed CSV with plausible P and S indices per file.
- Picks are consistent with detector logic, constraints, and within-array bounds.
- Parameters can be tuned quickly without extra dependencies if initial recall/precision needs adjustment.
