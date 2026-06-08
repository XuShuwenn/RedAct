---
name: gw-matched-filtering
description: "Condition gravitational-wave strain data and run a matched-filter grid search over waveform approximants and masses to find peak SNRs."
---

# Gravitational-Wave Matched Filtering (Binary Black Holes)

Reusable workflow for detecting compact-binary signals in noisy strain data using matched filtering with a small template bank defined by waveform approximants and integer mass grids.

## When to Use

Activate this skill when you need to:
- read strain data (e.g., from a GWF frame and channel)
- condition the data (high-pass, resample, crop) and estimate PSD
- generate time-domain templates across a mass grid for common approximants
- run matched filtering and extract peak signal-to-noise ratio (SNR)
- report the best template per approximant with SNR and total mass

## Core Workflow

Follow these steps deterministically:

1) Load and condition data
- Read the strain TimeSeries from the frame/channel.
- High-pass filter at O(10–30 Hz) to remove low-frequency noise (typical: 15 Hz).
- Resample to a manageable sample rate (typical: 2048 Hz) to reduce compute.
- Crop a few seconds from each end to remove filter wraparound (typical: 2–4 s).

2) Estimate PSD
- Use short segments (e.g., 4 s) to estimate the power spectral density.
- Interpolate PSD to the data's delta_f.
- Apply inverse spectrum truncation with a low-frequency cutoff near the high-pass corner to stabilize division by PSD at low frequencies.

3) Prepare data in frequency domain (recommended)
- Convert the conditioned time series to a FrequencySeries using the PSD's delta_f.
- Resize to match the PSD length to avoid frequency-resolution mismatches.

4) Template generation and alignment
- For each approximant (e.g., IMRPhenomD, SEOBNRv4_opt, TaylorT4), loop over integer mass1, mass2 within the specified range.
- Enforce mass1 >= mass2 to avoid duplicate symmetric templates.
- Generate time-domain template with get_td_waveform using the conditioned delta_t and a lower frequency cutoff (typical: 20 Hz). Distance can be fixed (e.g., 1) since SNR normalization handles amplitude.
- Align the template (e.g., cyclic_time_shift to place merger near start) for consistent filtering.
- Convert the time-domain template to FrequencySeries with delta_f equal to PSD delta_f, then resize to PSD length.

5) Matched filtering and peak picking
- Run matched_filter on the frequency-domain template and data (with the PSD and the chosen low-frequency cutoff).
- Crop edges (e.g., 4 s) to remove corrupted SNR samples due to PSD/windowing.
- Compute the peak absolute SNR (e.g., abs(snr).numpy().max). Track the best SNR and corresponding masses per approximant.

6) Report results
- For each approximant, output the best approximant name, peak SNR, and total mass (mass1 + mass2) in a CSV with columns: approximant,snr,total_mass.

## Verification

Perform these checks to ensure correctness and robustness:
- Data conditioning invariants:
  - After resampling, verify sample_rate and delta_t are as intended.
  - Cropped duration is positive and sufficient for PSD segmenting.
- PSD consistency:
  - PSD.delta_f > 0 and matches the FrequencySeries delta_f used for data and templates.
  - Inverse spectrum truncation applied with a reasonable low-frequency cutoff to avoid zeros in PSD.
- Frequency resolution alignment:
  - Ensure both data_fd and template_fd have identical delta_f and length.
  - If mismatched, convert/rebuild template FrequencySeries with delta_f=psd.delta_f and resize.
- Matched filtering:
  - matched_filter returns a complex SNR time series; peak is taken from abs(SNR).
  - Crop several seconds at both ends before computing the peak to avoid edge artifacts.
  - Guard against NaN/Inf peaks; skip such cases.
- Output:
  - Exactly one line per approximant, with numeric SNR and integer total_mass in the required CSV header/format.

## Common Pitfalls and How to Avoid Them

- Resizing TimeSeries alters delta_t:
  - Avoid resizing time-domain templates and then reusing their delta_f implicitly. Instead, convert templates to FrequencySeries with delta_f=psd.delta_f and resize in frequency domain.
- Frequency resolution mismatches (delta_f):
  - Always align template and data frequency resolutions to PSD.delta_f before matched_filter.
- Missing edge cropping:
  - Not cropping SNR edges leads to spurious peaks. Crop at least a few seconds (e.g., 4 s) from both ends.
- Slow performance from repeated FFTs:
  - Precompute the frequency-series of the conditioned data once. Use frequency-domain templates to avoid repeated FFTs of long time series.
- Excessive compute from duplicate mass pairs:
  - Enforce mass1 >= mass2 to halve the grid without losing unique combinations.
- Incorrect SNR extraction:
  - Use peak_snr = abs(snr).numpy().max (or equivalent). Avoid indexing mistakes or maxima on complex numbers without absolute value.
- PSD zeros or unstable low-frequency behavior:
  - Apply inverse spectrum truncation and choose a sensible low-frequency cutoff. Avoid dividing by near-zero PSD values.
- Output buffering hides progress:
  - Flush progress logs (e.g., print(..., flush=True)) or run Python unbuffered to avoid timeouts in long loops.
- Over-aggressive sampling-rate reduction:
  - Reducing sample rate too far can push relevant frequencies above Nyquist. Use a rate that safely captures inspiral/merger-ringdown for the target masses.
- Overcomplicated multiprocessing on constrained systems:
  - If parallelism causes instability (e.g., forking FFT libraries), prefer a stable sequential run with the above optimizations.

## Success Criteria

- The conditioning and PSD steps complete without errors and produce consistent delta_t and delta_f.
- For each specified approximant, the grid search completes and yields a finite peak SNR and a total mass value.
- Results are saved in a CSV file with the exact header and fields: approximant,snr,total_mass.

## Optional Script Usage

A generic helper is provided to run the full pipeline end-to-end.

Example:
- Minimal usage:
  - python scripts/gw_matched_filter.py --frame /path/to/data.gwf --channel H1:STRAIN --output /path/to/detection_results.csv
- With custom parameters:
  - python scripts/gw_matched_filter.py \
    --frame /path/to/data.gwf --channel H1:STRAIN \
    --approximant SEOBNRv4_opt --approximant IMRPhenomD --approximant TaylorT4 \
    --mass-min 10 --mass-max 40 \
    --sample-rate 2048 --highpass 15 --f-lower 20 --psd-seg-len 4 --crop-sec 4 \
    --progress-every 200 --output /path/to/detection_results.csv

The helper prints progress periodically and writes a CSV with one line per approximant containing the peak SNR and total mass.
