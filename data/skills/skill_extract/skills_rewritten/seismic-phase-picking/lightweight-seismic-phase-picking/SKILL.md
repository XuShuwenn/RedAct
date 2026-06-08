---
name: lightweight-seismic-phase-picking
description: "Use this to pick P and S arrivals from 3‑component waveform NPZ files when heavy ML installers are unreliable; focuses on robust preprocessing, STA/LTA, polarization cues, and validation."
---

# Lightweight Seismic Phase Picking (P and S) Without Heavy Dependencies

This skill avoids common failure modes in seismic phase picking workflows by using a robust, dependency-light pipeline based on classical signal processing. It emphasizes reliable data inspection, normalization of small-scale signals, channel handling when labels are inconsistent, STA/LTA-based candidate detection, polarization-based phase discrimination, and strict validation before writing results.

## When to Use

Activate this skill when:
- You must pick P and S arrivals from three-channel waveform arrays in NPZ files with fields like `data`, `dt`, and optional `channels`.
- Installing heavy pretrained ML pickers is slow, stalls, or fails.
- Channel labels are inconsistent or missing, and you need a resilient fallback.

## Core Workflow

1. Inspect and validate inputs
   - Open a few NPZ files and confirm:
     - `data` is shaped (num_samples, 3)
     - `dt` is present and numeric (sampling interval in seconds)
     - `channels` is a comma-separated string (optional; may be inconsistent)
   - Derive sampling rate: `fs = 1 / dt`. Use this to convert all time thresholds into samples.

2. Channel identification and fallbacks
   - Parse `channels` string. Prefer the channel containing a "Z" (case-insensitive) as the vertical component; treat the other two as horizontals.
   - If labels are missing or ambiguous, fall back to a data-driven choice:
     - Compute the standard deviation on the first 10% of samples for each channel post-detrend. The channel with the smallest early horizontal-like energy may not be reliably detectable; instead, choose vertical as the channel whose energy increases earliest around the first STA/LTA crossing during candidate search. As a simpler fallback, pick the channel with the highest early kurtosis as vertical and treat the remaining two as horizontals.

3. Preprocessing to stabilize small or variable amplitudes
   - Handle NaNs by zero-filling or interpolation.
   - Detrend and demean each channel.
   - Robustly scale each channel using median absolute deviation (MAD) or z-score with outlier clipping (e.g., clip at 3–5 robust standard deviations).
   - Light bandpass without SciPy:
     - High-pass: subtract a moving average with window ≈ 0.5–1.0 s (samples = round(0.5–1.0 × fs)).
     - Smooth (low-pass) with a short moving average (≈ 0.05–0.1 s) to reduce high-frequency noise before envelope/energy computations.

4. Noise characterization
   - Use an early noise window (e.g., first 5–10% of the record) to estimate baseline energy (RMS/MAD). Scale detection thresholds relative to this baseline.

5. Candidate detection with STA/LTA
   - Use a rectified energy measure: square the preprocessed signal and apply moving averages.
   - P-wave candidates: compute STA/LTA on the vertical channel with windows sized from `fs` (e.g., STA ≈ 0.05–0.1 s, LTA ≈ 0.5–1.0 s). Detect rising-edge threshold crossings. Apply a refractory period (e.g., ≥ 0.3–0.5 s) between detections.
   - S-wave candidates: compute STA/LTA on horizontal magnitude h = sqrt(H1^2 + H2^2) using slightly longer STA than for P. Search after the chosen P pick(s) with a minimum P→S gap (e.g., ≥ 0.1–0.3 s).

6. Pick refinement
   - Around each threshold crossing, refine the onset by minimizing a local AIC function or selecting the point of maximum slope in a small window centered at the crossing (e.g., ±0.05–0.1 s).

7. Polarization and validation filters
   - P validation:
     - Short-window SNR gain: energy after the candidate vs before should exceed a threshold (e.g., ≥ 3× baseline).
     - Vertical dominance: fraction of vertical energy vs total (V / (V + H1 + H2)) in a short window around the pick exceeds a modest threshold.
   - S validation:
     - Horizontal dominance: horizontal energy fraction h^2 / (h^2 + v^2) exceeds a threshold (e.g., ≥ 0.6) around the candidate window.
     - Enforce P→S ordering and a minimum separation in samples.
   - Apply refractory constraints to avoid clusters of spurious picks. Keep top candidates by SNR if multiple remain.

8. Output formatting
   - Write one row per pick with columns: `file_name`, `phase` ("P" or "S"), and `pick_idx` (0-based sample index).
   - Do not assume a fixed output path; accept a parameter for the output location.

## Verification

- Structural checks before batch processing:
  - `dt > 0`, `fs = 1/dt` sensible; `data.shape[1] == 3`; no all-zero channels after preprocessing.
  - Channel mapping resolved (label-based or fallback).
- Detection sanity checks on a few files:
  - At least one P candidate precedes S candidates in time.
  - P picks show a clear vertical energy rise; S picks show horizontal dominance.
  - SNR thresholds satisfied; picks are not at array edges.
- Tolerance conversion for evaluation:
  - If external evaluation uses a 0.1 s tolerance, convert to sample tolerance: `tol_samples = round(0.1 / dt)`.
- CSV checks:
  - Correct header names and types; no extra columns; indices within `[0, num_samples-1]`.

## Common Pitfalls (and Avoidance)

- Heavy ML model installs stall or time out
  - Avoid relying on large pretrained pickers when environment is constrained. Use the lightweight classical picker in this skill.
- Ignoring `dt` when sizing windows and thresholds
  - Derive every window size and tolerance from `fs = 1/dt`.
- Misusing channel labels or assuming fixed order
  - Labels may be inconsistent. Prefer parsing strings with fallbacks to data-driven channel selection.
- Picking on raw amplitude with tiny or drifting scales
  - Always detrend, robustly scale, and perform energy/STA-LTA calculations.
- Too many false S picks
  - Enforce P→S ordering, minimum separation, SNR validation, and horizontal-dominance checks.
- Writing incorrect CSV format
  - Ensure exactly `file_name, phase, pick_idx` with one pick per row.

## Success Criteria

- For each file, P picks precede S picks (when both present) and satisfy SNR and polarization checks.
- Windows and thresholds are derived from `dt` and produce consistent results across files.
- The output CSV contains valid indices and correct headers, with no dependency on heavyweight packages.

## Optional Script Usage

A helper script is provided to run the complete lightweight pipeline over a directory of NPZ files and write a standards-compliant CSV.

Example:
- Process a directory: `python scripts/lightweight_phase_picker.py --data-dir /path/to/data --output /path/to/results.csv`
- Tune thresholds if needed (see `--help`).
