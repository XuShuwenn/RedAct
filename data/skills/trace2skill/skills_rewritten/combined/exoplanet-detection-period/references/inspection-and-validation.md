# Inspection and Validation Workflow

Use this when preprocessing choices are not obvious or the lightcurve file is too large to inspect manually.

## Quick inspection before detrending/search

Check these properties first:
- read header/comment lines first, if present, to confirm column meanings and ordering before loading with fixed assumptions
- verify that the columns you plan to treat as time, flux, quality flag, and uncertainty match the observed file documentation

- major gaps or discontinuities in time sampling (for example, unusually large `np.diff(t)` values after sorting/filtering)
- total time span: `t.max() - t.min()`
- typical cadence: median of `np.diff(t)` after sorting/filtering
- flux scatter: robust std or MAD of flux
- variability scale: coarse Lomb-Scargle peak(s) to estimate stellar rotation / low-frequency structure

- resource risk: data length/density and whether a planned transit search needs an explicit worker cap

If one variability timescale dominates, record it explicitly and use it in two ways:
- choose detrending windows short enough to suppress that modulation but still longer than the expected transit duration
- down-rank period-search peaks at the same period or simple harmonics unless the folded signal shows a clearly transit-like narrow dip

If you find a major gap, do not force one smoothing model across it by default. Prefer detrending each continuous segment separately, or use a detrending method whose support does not bridge the gap.

Use those measurements to choose parameters:
- detrending window should be comfortably longer than expected transit duration and short enough to remove slow stellar variability

- if a coarse variability period is visible, use it to set the detrending window instead of guessing blindly
- if using a parallel transit search on a dense light curve, cap workers early so the run finishes reliably
- period search bounds should fit within the observed baseline and cadence; avoid arbitrary narrow ranges unless justified by the data
- sigma clipping should remove clear outliers without erasing shallow transit points

- If initial inspection only shows a few rows, follow it with one compact whole-file summary before coding. Minimum useful summary: row count, count of usable `quality==0` rows, sorted time span, median cadence, and largest time gap.

## Minimum validation before writing the answer

After coding the pipeline:
1. Run it
2. Wait for the execution observation to return fully
3. Inspect stdout/stderr for failures, truncation, or missing dependencies
4. Confirm a specific best period was returned
5. For transit candidates, confirm the fitted duration is plausible and not just the widest/narrowest allowed grid value
6. If preprocessing used clipping, compare with a milder or no-clipping run when feasible to ensure transit dips were not removed
7. If the candidate came from a coarse scan, run a narrower or higher-resolution refinement around that candidate and keep the refined value only if it stays consistent
8. Phase-fold or otherwise inspect predicted transit epochs in the original timeline to confirm repeated dips occur when expected; treat events landing in known data gaps separately from true misses
9. If multiple alias periods remain plausible, perform one explicit comparison (for example P vs P/2 vs 2P with folded-dip coherence or targeted local searches) before choosing
10. Write `/root/period.txt` with one numeric value rounded to 5 decimals
11. Re-open `/root/period.txt` and verify format
12. If output was truncated, rerun so the final summary is written to an allowed `/root/` file and verify the result there
13. Report only diagnostics that were explicitly printed or saved by the completed run you verified
14. If the task environment requires a specific completion message or terminator, send it only after step 11 succeeds

## Anti-patterns

Do not:
- choose a detrending window from a canned default without checking cadence/baseline
- search only a hard-coded period range without evidence from the data
- stop after writing a script but before observing its execution result