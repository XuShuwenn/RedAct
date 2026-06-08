---
name: transit-period-detection
description: "Detect exoplanet orbital periods in light curves dominated by stellar variability using robust filtering, detrending, transit search, and alias checks."
---

# Exoplanet Transit Period Detection in Stellar-Variable Light Curves

Recover planetary orbital periods from light curves with strong stellar variability (e.g., rotation and starspots) by combining quality filtering, outlier rejection, careful detrending, a transit-focused period search, and alias/harmonic validation.

## When to Use

Use this skill when you need to:
- find an exoplanet period from a light curve with long-timescale variability
- remove stellar activity to reveal transits
- run a transit-focused period search (BLS/TLS) and refine the best period
- avoid common pitfalls such as selecting a harmonic/alias or over-detrending away transits

## Core Workflow

Follow these phases and checks. Compute from the provided data; do not guess values.

1) Load and Inspect
- Read time, normalized flux, quality flag, and flux uncertainty columns.
- Verify array sizes match and values are finite. If any column is missing, adapt (e.g., assume unit weights) but record the assumption.
- Summarize cadence: median time step (dt) and baseline (max(time) - min(time)).

2) Quality Filtering and Outliers
- Keep only good-quality points (e.g., quality flag equals the dataset's good value) and finite time/flux/uncertainty.
- Sigma-clip outliers on flux or flattened residuals (e.g., 5-sigma) to remove cosmic rays and flares.
- If large time gaps exist, segment the data at gaps (e.g., gaps > 5× median dt) to avoid filter edge artifacts.

3) Detrend Stellar Variability (Flattening)
Goal: remove long-timescale trends while preserving short, box-like transit dips.
- Choose a detrending window much longer than expected transit duration and shorter than stellar variability timescale. Practical defaults:
  - window length in days such that window_points ≈ window_days / median_dt is large (hundreds of points if possible)
  - if using Savitzky–Golay, ensure window is odd and polyorder low (e.g., 2)
- Apply per-segment detrending to avoid bleeding across gaps. Divide flux by the trend (not subtract) to keep transit depths fractional.
- After flattening, run another sigma-clip on flattened flux to remove residual outliers.

4) Initial Transit Search (Broad Scan)
- Use a transit-focused periodogram (e.g., Box Least Squares). Set a broad but plausible period range for the dataset’s baseline (ensure at least 2–3 expected transits within the baseline when possible):
  - period_min: avoid unrealistically short periods for the cadence; typical lower bound ~0.3–0.5 days for TESS-like data
  - period_max: a fraction of baseline so ≥2 transits are possible; if baseline is long, choose upper bound relevant to task
- Use reasonable transit duration fractions (q = duration/period), e.g., qmin ~ 0.005, qmax ~ 0.1.
- Control resources: limit threads via environment variables, omit progress bars, and start with moderate grid density.

5) Candidate Validation and Alias Control
Perform these checks before refining:
- Harmonics and aliases: compare power/SNR at P, 2P, and P/2; also examine 3/2 P and 2/3 P if needed.
- Odd-even depth test: fold at P; compare odd vs even transit depths. If significantly different, a binary or harmonic (2P) may be implicated.
- Phase-folded coherence: fold the light curve at the candidate period. Confirm repeatable transits with consistent depth and duration across epochs.
- Events count: ensure multiple transits across baseline. A single dip is insufficient for a robust orbital period.
- Duration plausibility: ensure duration fraction q lies in the search range and is reasonable for the period and cadence.
- Boundary check: if the best period is at the edge of the scanned range, widen and rescan.

6) Refinement (Narrow Scan)
- Center a narrower, higher-resolution scan around the selected candidate (e.g., ±1–2% of P) with higher oversampling.
- Re-run alias and odd-even checks post-refinement.
- Stability: repeat detrending with slightly varied windows (e.g., ±20%) and confirm the period is stable within uncertainty. If unstable, reassess detrend settings and outlier treatment.
- Optional cross-check: confirm with an independent method (e.g., TLS if available) in a narrow window around the candidate.

7) Finalize and Output
- Pick the period that passes alias, coherence, and stability checks.
- Round to 5 decimal places and write a single numeric value (days) to the specified output.

## Verification
Use these concrete checks before finalizing:
- Data integrity: lengths of time/flux/err match; all arrays finite after filtering; at least a few thousand points, or enough for multiple transits.
- Baseline sufficiency: baseline / period ≥ 2 (preferably ≥ 3) to avoid one-off events.
- Folded consistency: visually or numerically confirm that transit depth and duration are consistent across all epochs.
- Harmonic decision:
  - Compute metrics at P, 2P, P/2; choose the period with higher power and consistent odd/even depths.
  - If odd-even depths differ at P but match at 2P, prefer 2P.
- Stability to detrending: period consistent across reasonable detrending parameter variations.
- Edge guard: ensure best period is not at search boundary; if it is, expand and re-scan.
- Output format: exactly one number in days, newline-terminated, rounded to 5 decimals.

## Common Pitfalls and How to Avoid Them
- Selecting a harmonic or alias (e.g., P/2 or 2P): always compare power at P, 2P, and P/2; run odd-even tests and check phase-folded consistency.
- Over/under-detrending: too-short windows erase transits; too-long windows leave stellar trends. Set window >> expected transit duration and test small variations.
- Detrending across gaps: filtering across large gaps causes edge artifacts. Detrend per segment.
- Removing in-transit points during trend estimation: fit trend robustly or mask likely in-transit points iteratively to avoid diluting transits.
- API misuse: verify period search library signatures on a small subset before full runs; prefer a simple BLS autopower call and add TLS only if available.
- Resource overuse/timeouts: start with coarse scans; control threads; narrow the refinement window around the candidate.
- Baseline mismatch: claiming a period longer than the baseline or with <2 observed transits leads to unreliable results.
- Formatting errors: forgetting to round to 5 decimals or outputting extra text.

## Optional Script Usage
The provided helper script implements a robust, resource-aware BLS workflow with detrending and alias checks.

Example usage:
- Broad scan and write result:
  - python scripts/transit_period_tools.py --input path/to/lightcurve.txt --period-min 0.5 --period-max 12 --output period.txt
- With custom columns and detrending window:
  - python scripts/transit_period_tools.py --input lc.txt --time-col 0 --flux-col 1 --qual-col 2 --err-col 3 --quality-good 0 --detrend-window-days 1.0 --period-min 0.3 --period-max 20 --output period.txt

Success criteria:
- The selected period remains strongest after alias checks and odd-even depth validation.
- Multiple transits are present and consistent in the phase-folded light curve.
- The period is stable across small detrending parameter changes.
- The output file contains a single numeric period in days, rounded to 5 decimals.
