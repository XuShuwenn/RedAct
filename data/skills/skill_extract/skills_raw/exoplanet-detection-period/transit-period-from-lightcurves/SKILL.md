---
name: transit-period-from-lightcurves
description: "Detect exoplanet orbital periods in noisy stellar light curves by filtering, detrending, Box Least Squares search, harmonic checks, and refinement."
---

# Transit Period Detection from Noisy Light Curves

This skill provides a robust workflow to recover a transiting exoplanet's orbital period from a light curve dominated by stellar variability (e.g., rotation with starspots). It focuses on resilient preprocessing and uses the Box Least Squares (BLS) periodogram for period identification, with safeguards against common pitfalls and aliases. Transit Least Squares (TLS) can be used when resources allow, but BLS is prioritized for reliability and speed.

## When to Use

Activate this skill when you have:
- A photometric light curve (e.g., TESS/Kepler/ground-based) with columns for time, normalized flux, quality flags, and flux uncertainty.
- Significant stellar variability masking a potential transit signal.
- A need to output a single orbital period value to fixed precision (e.g., 5 decimals).

## Core Workflow

Follow these steps end-to-end. Keep units consistent (days for time).

1) Data ingestion and initial QA
- Parse a whitespace- or CSV-like file, ignoring comment lines.
- Columns (typical): time [days], flux [normalized], quality [0=good], flux_err.
- Sort by time and drop non-finite values.
- Apply quality mask (keep quality == 0, or equivalent "good" flag per dataset).

2) Outlier removal
- Sigma-clip the flux at 4–5 sigma (median-based or standard deviation) to remove flares/spikes.
- Recompute masks and keep time, flux, and flux_err arrays aligned.

3) Detrending/flattening to remove stellar variability
- Goal: preserve short-duration transits while removing longer-timescale rotational modulation.
- Choose (and possibly iterate over) window lengths shorter than the stellar variability but longer than transit durations. Practical starting set: 0.3, 0.5, 0.75, 1.0 days.
- Implementation options:
  - Savitzky–Golay filter: compute window_points = round(window_days / cadence); enforce odd and >= 5; polyorder 2–3.
  - If available, use a dedicated flattener (e.g., biweight/boxcar) or a package that handles gaps (e.g., wotan.flatten).
- Detrend by dividing flux by the trend. After detrending, re-clip outliers (5-sigma) to remove residuals.

4) BLS period search (Astropy)
- Use astropy.timeseries.BoxLeastSquares(time, flux, dy=flux_err). Time should be in days; if using astropy units, pass time as time*u.day and durations in days too.
- Choose durations grid representing plausible transit durations (for short-cadence data, a good sweep is 0.02–0.12 days). Example: np.linspace(0.02, 0.12, 8) days.
- Coarse search:
  - Use autopower with a wide period range (e.g., minimum_period=0.5 days, maximum_period = baseline/2).
  - Record the best period candidate for each detrending window; select the highest-power candidate overall.
- Fine refinement:
  - Around the best period, run model.power over a narrow window (e.g., ±0.2–1% or a small ±delta in days) with the same durations grid; pick the max power result.

5) Candidate validation and harmonic checks
- Compute statistics at the refined best period using model.compute_stats.
  - Astropy versions differ; depth SNR may not be present as a key. Compute a robust SNR if needed using depth and its error, or out-of-transit scatter.
- Check:
  - Number of observed transits ≈ baseline / period ≥ 2.
  - Transit duration is physically plausible (duration/period fraction typically a few percent; flags if > ~10%).
  - Phase-folded light curve at the candidate period shows a distinct, narrow dip. Optionally bin phase for clarity.
- Harmonic resolution:
  - Evaluate P/2 and 2P with a narrow grid to compare power and coherence. Choose the period with sharper, more coherent transits across multiple events.
  - Prefer fundamentals that produce consistent transit depth across events; deprioritize broad, sinusoid-like dips matching stellar rotation.

6) Output
- Write the final period value rounded to the required precision (e.g., 5 decimals) as a single numeric line with a trailing newline.

## Verification

Before finalizing:
- The period is stable across reasonable detrending windows (e.g., 0.3–0.75 days) and not an artifact of a single preprocessing choice.
- There are ≥ 2 inferred transits across the baseline, and the transit depth SNR is meaningful (finite and positive).
- Harmonic check does not prefer P/2 or 2P when comparing power and transit shape.
- If available, a phase-folded view shows a sharp, box-like dip; odd-even depths are consistent within noise for single-planet scenarios.
- Output file contains exactly one numeric value at the requested precision and no extra text.

## Common Pitfalls and How to Avoid Them

- Using TLS by default on large datasets can stall or exhaust memory. Prefer BLS for initial detection; use TLS only for later refinement if resources permit.
- Misusing APIs or relying on version-specific keys (e.g., expecting "depth_snr" in compute_stats). Fall back to computing SNR from depth and its error or out-of-transit scatter.
- Overly long detrending windows can leave rotational power that aliases into the BLS peak; overly short windows can distort or remove transits. Try multiple windows around 0.3–1.0 days and compare stability.
- Relying on Lomb–Scargle for transit discovery yields sinusoidal periods (e.g., rotation), not box-like transits. Use BLS for transit search; LS can inform rotation-timescale only.
- Ignoring quality flags, NaNs/Infs, or data gaps leads to spurious detections. Always filter quality and finite values, and use detrenders that tolerate gaps (or process segments).
- Wrong units or missing uncertainties can degrade BLS performance. Keep time in days and pass dy=flux_err when available.
- Forgetting harmonic checks can result in reporting P/2 or 2P instead of the fundamental. Always test nearby harmonics with refinement.

## Optional Script Usage

A helper script is included to run this workflow end-to-end with configurable options:
- Inputs: path to light curve, column indices, quality value, detrending method and windows, BLS bounds.
- Outputs: writes the rounded period to the requested output path.

Example:
- python scripts/bls_period_search.py --input data.txt --output period.txt --min-period 0.5 --max-period 15 --windows 0.3,0.5,0.75 --method savgol

The script prints diagnostics (candidate periods, power, basic SNR, harmonic check results) and writes the final period as a single line to the output file.
