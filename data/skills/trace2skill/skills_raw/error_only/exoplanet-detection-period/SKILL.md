---
name: exoplanet-detection-period
description: "Detect exoplanet periods in TESS lightcurve data by filtering, removing stellar activity variability, and identifying orbital periods."
---

# Exoplanet Period Detection from Lightcurve

## When to Use

- Find periodic signals hidden in stellar activity noise
- Analyze TESS space telescope lightcurve data
- Apply period-finding algorithms to astronomical time series

## Input Format

File `/root/data/tess_lc.txt` with columns:
- Time (MJD)
- Normalized flux
- Quality flag (0 = good)
- Flux uncertainty

## Key Steps

1. Filter data by quality flags and outliers
2. Remove stellar activity variability (rotational modulation, starspots)
3. Inspect the dataset enough to estimate cadence, time span, variability amplitude, and plausible transit timescales before locking detrending or search settings
4. Use a staged search: start with cheap diagnostics or coarse scans, then refine only promising periods
5. Validate candidate periods before finalizing: inspect other strong peaks, check harmonic/alias relationships, and phase-fold plausible candidates
6. If detrending or search settings materially affect the result, compare a small number of reasonable alternatives and prefer a period that remains consistent
7. Identify the most plausible exoplanet orbital period
8. Round to 5 decimal places and write exactly one numeric value to `/root/period.txt`
9. Verify `/root/period.txt` exists and contains exactly one plausible numeric value

## Output Format

Single value to `/root/period.txt`.


Only write `/root/period.txt` after the period-search run has visibly completed and the selected period has been checked against the search diagnostics.


## Output Format

## Execution Checklist

- Verify the input file exists and inspect a few rows before analysis.
- Use quality-flag filtering and detrending before period search.
- Do not make the core detection step depend only on an unverified external package.
- Wait for the analysis/search to actually finish before trusting logs or output files.
- If command output is truncated, rerun with reduced verbosity or save the summary/result to an allowed file under `/root/` rather than inferring success from partial logs.
- After running the analysis, confirm `/root/period.txt` exists and contains exactly one numeric value rounded to 5 decimal places.
- If the first method fails or the run is incomplete, use an available fallback method and re-check the output file before concluding.
## Techniques

- Box least squares (BLS) algorithm for transit detection
- Lomb-Scargle periodogram for frequency analysis
- Filtering: sigma clipping, quality flag filtering
- Detrending: remove low-frequency stellar variability

- Prefer transit-specific searches (Box Least Squares / BLS, or TLS when available) for orbital period detection
- Use Lomb-Scargle primarily as a supporting diagnostic for stellar variability or cross-checking, not as the sole final period picker for transit signals
- Prefer a coarse-to-fine workflow: Lomb-Scargle or downsampled/coarse BLS first, then narrow-range refinement
- Detrend gently: remove low-frequency stellar variability while preserving short box-shaped transit features
- Compare the best period across a few reasonable detrending windows or duration ranges; only finalize when the candidate is consistent rather than drifting with preprocessing
- Treat BLS/TLS solutions whose best duration hits the search-grid maximum or minimum as suspicious; re-detrend or tighten to physically plausible durations instead of accepting the peak
- Use standard scientific Python tools first (`numpy`, `scipy`, `astropy`); if an optional transit package is unavailable, fall back to another valid period-search workflow that can complete in the current run
- If the lightcurve file is large, inspect a small sample to confirm the schema, then process the full file with a script or shell pipeline


## New Section

## Validation Before Final Answer

- Confirm the search actually completed and produced a candidate period; do not assume success from truncated logs, progress-only output, or from the mere existence of an output file.
- Treat invalid or unfinished search output as no result: examples include best power `-inf`, boundary-hit best periods exactly at the grid minimum/maximum, inconsistent summary fields, or missing final optimum reporting.
- Before finalizing, perform at least one sanity check: compare with a second method or detrending setting, inspect phase-folded behavior, or check obvious aliases/harmonics and stellar-rotation-like periods.
- If a heavy method is killed or exceeds resources, change strategy: narrow the period range, downsample safely, simplify the search, or switch to a lighter method.
- If a later exploratory run is invalid but an earlier valid run produced a strong candidate, fall back to the earlier valid candidate.
- Always have a fallback path that still writes the best available validated period estimate to `/root/period.txt` if the preferred search fails.
## Tips

- scipy.signal for periodogram/BLS
- astropy for lightcurve analysis
- Watch for periods matching stellar rotation (false positives)


- Inspect the data before locking in detrending: estimate the dominant variability timescale and choose filter/window lengths that remove stellar activity without erasing short transit signals.
- Sigma clipping can remove real transit dips; compare results with and without clipping, or use mild clipping, before locking in preprocessing.
- For transiting exoplanets, do not accept the strongest generic periodogram peak without transit checks.
- Report only diagnostics you actually observed (for example best period, SDE/SNR/FAP, top peaks); do not infer or invent metrics.
- After finding a candidate period, phase-fold the lightcurve and confirm repeated transit-like dips before finalizing the answer.
- Re-run the search with at least two reasonable detrending setups when possible, and check nearby harmonic/alias candidates explicitly (P, P/2, 2P, adjacent strong peaks); prefer periods that remain stable and give the clearest repeated transit-like dip.
- Use Lomb-Scargle mainly to characterize stellar rotation/variability; confirm transit periods with a transit-sensitive search plus phase-folded inspection.
- If `transitleastsquares` or another specialized package has import/API issues or is unavailable, fall back to a simpler BLS-style search with available libraries instead of prolonged debugging.
- Do not end after launching a script; inspect `/root/period.txt` directly before considering the task complete.
- For a concise workflow on inspection and parameter selection, see [references/inspection-and-validation.md](references/inspection-and-validation.md).
- For concrete implementation patterns and fallback order, read [references/implementation-patterns.md](references/implementation-patterns.md).

