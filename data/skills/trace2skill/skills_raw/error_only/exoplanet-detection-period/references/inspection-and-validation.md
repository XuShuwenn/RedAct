# Inspection and Validation Workflow

Use this when preprocessing choices are not obvious or the lightcurve file is too large to inspect manually.

## Quick inspection before detrending/search

Check these properties first:
- total time span: `t.max() - t.min()`
- typical cadence: median of `np.diff(t)` after sorting/filtering
- flux scatter: robust std or MAD of flux
- variability scale: coarse Lomb-Scargle peak(s) to estimate stellar rotation / low-frequency structure

Use those measurements to choose parameters:
- detrending window should be comfortably longer than expected transit duration and short enough to remove slow stellar variability
- period search bounds should fit within the observed baseline and cadence; avoid arbitrary narrow ranges unless justified by the data
- sigma clipping should remove clear outliers without erasing shallow transit points

## Minimum validation before writing the answer

After coding the pipeline:
1. Run it
2. Inspect stdout/stderr for failures or missing dependencies
3. Confirm a specific best period was returned
4. Write `/root/period.txt` with one numeric value rounded to 5 decimals
5. Re-open `/root/period.txt` and verify format

## Anti-patterns

Do not:
- choose a detrending window from a canned default without checking cadence/baseline
- search only a hard-coded period range without evidence from the data
- stop after writing a script but before observing its execution result