---
name: exoplanet-detection-period
description: "Detect exoplanet periods in TESS lightcurve data by filtering, removing stellar activity variability, and identifying orbital periods."
---

# Exoplanet Period Detection from Lightcurve

## Environment/Protocol First

- Before using this skill, read the task and environment instructions for required tool-call syntax, output format, and completion signaling.
- Follow any prescribed action/tool format literally for every tool call; do not substitute another style.
- If the task requires an exact final completion string or token, output it exactly when finishing.
- Treat protocol compliance as mandatory: a correct period in `/root/period.txt` does not complete the task if the interface contract is violated.


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

   - Flatten long-timescale stellar variability with a gentle window/filter sized from the measured cadence, expected transit duration, and stellar-variability timescale so it suppresses rotation/starspot structure without erasing short transit dips.
   - If major time gaps are present, detrend segments separately or use a method that does not smooth across the gaps.
3. Inspect the dataset enough to estimate cadence, time span, variability amplitude, and plausible transit timescales before locking detrending or search settings
3a. Estimate any dominant stellar-variability/rotation timescale early (for example with a coarse Lomb-Scargle check) and use it to guide detrending and to avoid mistaking stellar modulation for a planet period.
   - If the file is large, use a quick script or summary statistics on the filtered data rather than relying on a tiny header sample.
4. Use a staged search: start with cheap diagnostics or coarse scans, then refine only promising periods

4a. For transiting exoplanets, use a transit-sensitive search (BLS/TLS) for the final candidate; use Lomb-Scargle only for variability/alias diagnostics, not as the sole final picker.
5. Validate candidate periods before finalizing: inspect other strong peaks, check harmonic/alias relationships, and phase-fold plausible candidates

   - Do not write `/root/period.txt` from the first top-scoring peak alone.
   - For transit-search results, re-test candidates whose fitted duration/depth is physically implausible or pinned to the search-grid boundary.
   - If sigma clipping or other outlier rejection was used, compare at least one conservative/no-clipping variant when feasible so real transit dips were not removed.
   - Before finalizing, check at least one competing peak or harmonic candidate (for example `P/2`, `2P`, or a nearby strong peak) and confirm the chosen period gives the clearest repeated transit-like dips when phase-folded.
   - If transit-specific tooling is unavailable, only use a fallback candidate after a direct coherence check shows repeated transit-like dips at that period in the folded light curve and after checking obvious aliases/harmonics.
6. If detrending or search settings materially affect the result, compare a small number of reasonable alternatives and prefer a period that remains consistent

   - Do not rely on a single hard-coded detrending window or search range when stellar variability is strong; test at least one nearby reasonable alternative or justify the bounds from the observed baseline/cadence.
   - Treat a candidate that shifts substantially across reasonable detrending choices as unvalidated; keep testing rather than finalizing immediately.
   - After trying a small set of reasonable detrending/search variants, stop expanding the search space: choose the candidate that is most stable across those checks and move to output.
   - Once a candidate is validated enough for the task, write `/root/period.txt` and finish; do not let optional extra validation block delivery.
7. Identify the most plausible validated exoplanet orbital period.
   - For transit-like signals, treat a validated BLS-derived candidate from the detrended lightcurve as the default primary result unless stronger transit-specific evidence favors another period.
8. Round to 5 decimal places and write exactly one numeric value to `/root/period.txt` as soon as a defensible result is available.
9. Re-open `/root/period.txt`, verify it exists and contains exactly one plausible numeric value, then finish instead of planning open-ended refinements.

## Output Format

Single value to `/root/period.txt`.


Only write `/root/period.txt` after the period-search run has visibly completed and the selected period has been checked against the search diagnostics.


## Output Format

## Execution Checklist

- Verify the input file exists and inspect a few rows before analysis.
- Validate incrementally before committing to a full pipeline: confirm schema and row count, estimate baseline/cadence/flux scatter, inspect dominant low-frequency variability, and check for major time gaps before fixing preprocessing/search settings.
- If the input is too large to print fully, inspect a small sample to confirm schema, then run a script or shell pipeline that reads the full file directly from disk; do not base the final result on the sample alone.
- Use quality-flag filtering and detrending before period search.
- Prefer BLS as the main detector for repeating transit dips; use Lomb-Scargle mainly as a supporting variability/alias diagnostic.
- Do not make the core detection step depend only on an unverified external package.
- If you try an unfamiliar transit-search library, first inspect the installed callable signature or a minimal confirmed example before wiring it into the full search; do not guess method names, positional arguments, or constructor kwargs.
- Confirm optional dependencies before making them part of the core search plan; otherwise start with standard available libraries (`numpy`, `scipy`, `astropy`) and use optional transit packages only after a quick import/API check.
- After any failed package attempt, return to an end-to-end path within one short retry: use the corrected confirmed call or immediately switch to a verified fallback (prefer `astropy.timeseries.BoxLeastSquares`) instead of continuing open-ended library exploration.
- Wait for the analysis/search to actually finish before trusting logs or output files.
- Treat a run as incomplete unless you see a final search summary, a specific reported candidate period/statistic, or a confirmed clean completion plus final result lines; progress bars, initialization lines, partial output, or an existing `/root/period.txt` do not prove the detection step finished.
- If using a heavy search (for example TLS), cap parallelism first to reduce kill/memory risk.
- Do not stop at script creation or launch; inspect the completed run output, confirm a specific candidate period was returned, then verify `/root/period.txt`.
- If command output is truncated, rerun with reduced verbosity or save the summary/result to an allowed file under `/root/` rather than inferring success from partial logs.
- Treat `/root/period.txt` as valid only if you also observed a substantive completion signal from the run.
- If logs are partial, noisy, or truncated, rerun so the script prints or saves a short final summary under `/root/`, then verify that summary before trusting `/root/period.txt`.
- If you write or modify a script, inspect the saved file once before execution; fix truncation, malformed imports, or incomplete lines first.
- After running the analysis, confirm `/root/period.txt` exists and contains exactly one numeric value rounded to 5 decimal places.
- Re-open `/root/period.txt` directly and inspect the exact contents; only trust it if the just-finished run visibly reached the file-writing code path.
- If the first method fails, is too heavy, or the run is incomplete, switch promptly to a lighter verified fallback (prefer `astropy.timeseries.BoxLeastSquares` / BLS over prolonged debugging of heavier or optional transit packages), re-run end-to-end, and re-check the output file before concluding.

- Distinguish timeout from resource kill before retrying: if the process is killed (for example exit code 137 or `Killed`), do not rerun unchanged with a longer timeout.
- If a heavy search is killed, stalls, or appears to overuse CPU/RAM, first reduce workload or cap workers/threads (for example via tool settings or environment variables such as `OMP_NUM_THREADS`), then rerun; if still blocked, switch to a lighter fallback that can finish in the current run.
- Ensure every search branch and fallback path ends in one of two states: it writes `/root/period.txt` with a single numeric value, or it raises a clear error that you then handle with another method.
- Do not read tool-exposed session/log paths outside the task's allowed directories, even if a command says full output was saved there.
- Do not treat script creation or launch as completion. Observe the run result, confirm `/root/period.txt`, and only then emit any exact required completion string.
## Techniques

- Box least squares (BLS) algorithm for transit detection
- Lomb-Scargle periodogram for frequency analysis
- Filtering: sigma clipping, quality flag filtering
- Detrending: remove low-frequency stellar variability

- On activity-dominated light curves, explicitly flatten the light curve before transit search (for example median-filter detrending or `LightCurve.flatten(...)` when available); choose a window long enough to preserve short transits and convert from days to samples first when the API expects sample counts.

- Prefer transit-specific searches (Box Least Squares / BLS, or TLS when available) for orbital period detection

- If TLS is available and its API is confirmed quickly, use it to locate the candidate period region, then refine the final numeric value with a denser BLS scan around that region before writing `/root/period.txt`.
- Use Lomb-Scargle primarily as a supporting diagnostic for stellar variability or cross-checking, not as the sole final period picker for transit signals

- Do not finalize a transit period from Lomb-Scargle alone; treat it only as a hint for variability, aliases, or candidate windows to confirm with a transit-sensitive search or clear phase-folded transit evidence.
- Prefer a coarse-to-fine workflow: Lomb-Scargle or downsampled/coarse BLS first, then narrow-range refinement
- Detrend gently: remove low-frequency stellar variability while preserving short box-shaped transit features
- Compare the best period across a few reasonable detrending windows or duration ranges; only finalize when the candidate is consistent rather than drifting with preprocessing

- Do not select the final period solely because one detrending setup gives the highest BLS/TLS power; prefer candidates that remain present across reasonable preprocessing choices and pass an independent transit check.
- If the best-fit transit duration lands on the minimum or maximum searched duration, treat that solution as under-validated: adjust the duration grid or detrending and re-check before accepting the period.
- Treat BLS/TLS solutions whose best duration hits the search-grid maximum or minimum as suspicious; re-detrend or tighten to physically plausible durations instead of accepting the peak
- Use standard scientific Python tools first (`numpy`, `scipy`, `astropy`); if an optional transit package is unavailable, fall back to another valid period-search workflow that can complete in the current run
- If the lightcurve file is large, inspect a small sample to confirm the schema, then process the full file with a script or shell pipeline

- If a strong low-frequency or quasi-sinusoidal signal is present, measure its timescale explicitly and treat matching BLS/TLS peaks as suspect unless the phase-folded signal still looks like a narrow repeating transit.
- When stellar variability is strong, try a small set of detrending windows/scales tied to the measured variability timescale; prefer candidates that survive those changes and remain transit-plausible.
- After a coarse transit search identifies a promising peak, rerun a narrower or finer-resolution search around that period to improve precision before writing `/root/period.txt`.
- If a heavier transit search is slow, unstable, or killed, switch promptly to `astropy.timeseries.BoxLeastSquares` rather than retrying the heavy method repeatedly.
- For computationally heavy searches, set conservative worker/thread limits up front; prefer a completed lower-parallelism run over an aborted maximal-parallelism run.


## New Section

## Validation Before Final Answer

- Confirm the search actually completed and produced a candidate period; do not assume success from truncated logs, progress-only output, or from the mere existence of an output file.
- Treat command output as untrusted until you have evidence the run finished cleanly.
- Treat a submitted-but-unchecked command as no result. Finalize only from an observed completed run with a readable candidate period and a verified `/root/period.txt`.
- Treat invalid or unfinished search output as no result: examples include best power `-inf`, boundary-hit best periods exactly at the grid minimum/maximum, inconsistent summary fields, or missing final optimum reporting.
- Before finalizing, perform at least one sanity check: compare with a second method or detrending setting, inspect phase-folded behavior, or check obvious aliases/harmonics and stellar-rotation-like periods.
- Do not finalize the raw top BLS/TLS peak by itself. At minimum, compare it against one nearby competing peak or an obvious harmonic/alias candidate (`P`, `P/2`, `2P`), then inspect a phase-folded view or equivalent transit-shape check.
- Do not finalize from a single detrending+search configuration alone when a second reasonable check is feasible.
- If the measured stellar-variability period or its simple harmonics overlap the candidate, down-rank that period unless the folded signal still shows a clearly transit-like narrow dip.
- When a candidate period is found, check that predicted transit epochs recur at consistent times in the unfolded lightcurve; if an expected event is missing, verify whether it falls in a known data gap before rejecting the candidate.
- If a heavy method is killed or exceeds resources, do not just retry the same full-resolution search with minor runtime tweaks. Change strategy: cap threads/workers if appropriate, narrow the period range, reduce resolution safely, add a coarse first-pass scan, downsample only if transit sensitivity is still adequate, or switch to a lighter fallback.
- If a later exploratory run is invalid but an earlier valid run produced a strong candidate, fall back to the earlier valid candidate.
- Always have a fallback path that still writes the best available validated period estimate to `/root/period.txt` if the preferred search fails.

- For BLS/TLS-style searches, do not finalize from peak score alone; inspect the recovered duration (and depth when available) and treat implausibly broad events or boundary-hit durations as invalid until rechecked.
- If an earlier completed search produced a strong candidate and a later heavier run is killed, unavailable, or unfinished, keep the earlier validated candidate instead of blocking completion on the heavier method.
- If a later exploratory or refinement run is invalid but an earlier run produced a valid candidate, fall back to the earlier valid candidate rather than continuing open-ended optimization.
- If candidate periods disagree strongly across runs or preprocessing choices, do not finalize by picking one ad hoc; resolve the conflict with a narrowed transit-aware search or by checking harmonics/aliases explicitly.
- Use a stopping rule: once one candidate remains best after the planned lightweight checks, write `/root/period.txt` and finish instead of launching optional extra searches.
- Re-opening an existing `/root/period.txt` is only a format check, not validation of the producing analysis.
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
- For a concise workflow on inspection, gap handling, and parameter selection, see [references/inspection-and-validation.md](references/inspection-and-validation.md).
- For concrete implementation patterns and fallback order, read [references/implementation-patterns.md](references/implementation-patterns.md).

- Also inspect for large observation gaps; do not apply one continuous smoother across a major discontinuity when segmented detrending is feasible.
- When using flattening, try one or two nearby window lengths if feasible; prefer a candidate period that stays stable across those reasonable preprocessing choices.
- Preferred fallback sequence when the first attempt fails: verified `astropy.timeseries.BoxLeastSquares` run first, then use Lomb-Scargle only for variability/alias diagnostics, and only use specialized transit packages if you confirm the installed API quickly.
- If a search run is noisy or output is truncated, modify the script to print or save only final candidate summaries instead of inferring the answer from partial progress logs.
- A practical first-pass detrending choice for strong rotational variability is `LightCurve.flatten(...)` or an equivalent smoothing/median-filter trend removal, then run the transit search on the flattened flux.
- For compact examples of independent confirmation when TLS is unavailable or too expensive, see [references/independent-confirmation-patterns.md](references/independent-confirmation-patterns.md).
- For a compact pattern on flattening-window choice and TLS-to-BLS refinement, see [references/transit-refinement-patterns.md](references/transit-refinement-patterns.md).
- For concrete rules on duration-boundary failures, convergence across detrending choices, and cheap fallback transit checks, see [references/candidate-robustness-checks.md](references/candidate-robustness-checks.md).

