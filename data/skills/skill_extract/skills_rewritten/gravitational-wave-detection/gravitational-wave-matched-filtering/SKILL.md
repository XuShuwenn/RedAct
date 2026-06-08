---
name: gravitational-wave-matched-filtering
description: "Detect compact-binary gravitational-wave signals in noisy strain data by conditioning data, grid-searching template families, matched filtering, and exporting peak SNR summaries."
---

Gravitational-wave matched filtering skill for compact-binary coalescences (CBC) using PyCBC. This skill guides you to condition detector strain, generate and align templates, perform matched filtering across a parameter grid, extract peak SNRs robustly, and export concise results.

When to Use
- The user asks to detect or rank potential CBC signals in noisy strain data.
- You are given a frame file and channel, waveform approximant families, and a parameter grid (e.g., mass ranges).
- The required output is a small report or CSV summarizing the strongest candidate(s) per approximant.

Core Workflow

Phase 0: Plan the Search
- Confirm inputs: data file path, channel name, approximant list, parameter ranges, grid spacing, f_low, target sample rate, crop and PSD settings, and the required output format.
- Estimate runtime: count templates (grid size per family) and approximate per-template cost. Optionally test a tiny sub-grid to validate the pipeline end-to-end.

Phase 1: Load and Inspect Strain
- Read the strain time series from the frame file and channel (e.g., with pycbc.frame.read_frame).
- Log basic properties: duration, delta_t, sample_rate, start_time. These inform resampling, PSD windowing, and template alignment.

Phase 2: Condition the Strain
- Apply a high-pass filter to remove low-frequency trends (e.g., HP cutoff below but near f_low).
- Resample to a target delta_t (e.g., corresponding to a standard sample rate). Choose the same delta_t for all generated templates to avoid misalignment.
- Crop leading and trailing seconds to remove filtering transients.
- Estimate the PSD from the conditioned strain (Welch/segment-based). Interpolate PSD to strain.delta_f and apply inverse spectrum truncation for stability. Use a consistent low-frequency cutoff (f_low) for PSD, waveform generation, and matched filtering.
- Reuse the same conditioned strain and PSD across all templates and approximants.

Phase 3: Generate and Align Templates
- For each approximant and each parameter pair in the grid:
  - Optionally enforce symmetric-parameter de-duplication (e.g., mass1 >= mass2) to halve the grid if appropriate for the task.
  - Generate time-domain templates (e.g., with pycbc.waveform.get_td_waveform) using the same delta_t as the conditioned strain and f_lower = f_low; set distance to a fixed reference (e.g., 1) since matched filtering rescales.
  - Align the template start and pad or trim to match the strain length without altering delta_t. Prefer zero-padding to match length; avoid resampling or operations that change the sampling representation.

Phase 4: Matched Filtering and Peak Extraction
- Compute the matched filter SNR time series with the PSD and the same f_low used elsewhere.
- Crop SNR edges to remove artifacts from PSD truncation and template edges. A robust default is to crop several seconds from the start and end (for example, crop_front ≈ 2 × psd_trunc_sec, crop_back ≈ psd_trunc_sec), or more conservatively crop by the template duration near the start if needed.
- Extract the peak SNR as the maximum of the absolute value of the cropped SNR series. Record the peak value and the associated parameters.
- Track the best (highest) SNR per approximant.
- Add progress logging every N templates to monitor long runs.

Phase 5: Select and Export Results
- For each approximant, select the highest-SNR result and compute any requested summary values (e.g., total mass).
- Write a CSV or requested format with the specified header and fields. Round numeric values sensibly, but preserve their magnitude.

Verification
- Pre-flight checks:
  - Strain sample_rate and delta_t are known and finite.
  - Conditioned strain duration is sufficient relative to template lengths.
  - PSD length and resolution are compatible with the conditioned strain.
- Consistency checks during filtering:
  - Template delta_t matches strain delta_t (set during generation; do not resample afterward).
  - Template length equals strain length after zero-padding/trimming; avoid operations that change frequency resolution.
  - f_low used for PSD, waveform generation, and matched_filter is identical.
  - SNR cropping removes known transient regions; ensure resulting series still has positive duration.
- Output validation:
  - CSV exists, has the exact required header, and one row per requested approximant.
  - Reported SNRs are finite, non-negative magnitudes; totals/parameters are within the searched grid.
  - Re-running with the same settings yields consistent best SNRs within numerical tolerance.

Common Pitfalls (and Remedies)
- Misaligned sampling: Generating templates at a different delta_t than the strain or resampling templates after generation can break frequency compatibility. Remedy: Generate templates directly at the target delta_t matching the conditioned strain; zero-pad/trim only.
- Incorrect peak extraction: Taking the maximum before cropping or not using absolute SNR can select edge artifacts. Remedy: Crop first, then compute max(abs(SNR))).
- Inconsistent f_low: Using different f_low values between PSD, waveform generation, and filtering produces biased SNRs. Remedy: Define a single f_low and reuse it everywhere.
- Edge artifacts: Failing to crop SNR edges leads to spurious peaks. Remedy: Systematically crop front/back based on PSD truncation and template duration.
- Redundant grid search: Evaluating both (m1, m2) and (m2, m1) when the model is symmetric wastes time. Remedy: Enforce m1 >= m2 where appropriate.
- Waveform generation failures: Some parameter/approximant combos may fail. Remedy: Catch exceptions, log, and continue.
- Performance stalls and silent runs: No progress logging makes diagnosis hard. Remedy: Print periodic progress updates and run Python unbuffered when needed.
- Output format drift: Missing header or wrong column names. Remedy: Write the exact requested header and verify after writing.

Success Criteria
- The pipeline runs end-to-end on a small validation subset, then completes on the full grid within resource limits.
- For each approximant, the best SNR is extracted post-cropping and is reported alongside the requested summary (e.g., total mass) in the exact output format.
- The conditioned data, PSD, and templates are all consistent in sampling and f_low, with no runtime alignment errors.

Optional Script Usage
- Use scripts/gw_matched_filter_grid.py to run a parameterized search:
  - Provide: data file, channel, approximants, mass range/step, f_low, resample rate, crop, PSD settings, and output path.
  - Example:
    python scripts/gw_matched_filter_grid.py \
      --data-file input.gwf \
      --channel H1:STRAIN \
      --approximant SEOBNRv4_opt --approximant IMRPhenomD --approximant TaylorT4 \
      --mass-min 10 --mass-max 40 --mass-step 1 \
      --f-low 20 --resample-rate 2048 \
      --hp-cutoff 15 --crop-sec 2 --psd-seg-len 4 --psd-trunc-sec 4 \
      --output results.csv
- Start with a very small grid (e.g., a handful of mass pairs) to validate correctness, then scale to the full search.
