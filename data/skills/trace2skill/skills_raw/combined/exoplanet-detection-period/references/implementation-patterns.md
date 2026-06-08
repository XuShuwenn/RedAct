# Implementation Patterns

## When to read this
Read this when writing code for period detection, especially if you are considering an unfamiliar transit-search package or need a fallback that is likely to run on the first try.

## Preferred workflow
1. Load `/root/data/tess_lc.txt`.
2. Keep only rows with quality flag `== 0`.
3. Remove non-finite values and obvious flux outliers.
4. Detrend low-frequency variability.

4a. If the variability timescale is unclear, run a quick Lomb-Scargle diagnostic first and choose a detrending window shorter than the stellar-activity cycle but longer than expected transit durations.
5. Search periods with a confirmed callable API.

5a. If the chosen method is heavy or parallelized, cap threads/CPUs conservatively before the first full run.
5b. Start with a coarse BLS scan to find promising peaks, then refine the best candidate on a dense local grid to reach final precision efficiently.
5c. If the surrounding task specifies a strict shell/tool protocol or completion marker, plan the run so you can still inspect results and emit that exact final marker only after `/root/period.txt` is verified.
6. Write one numeric period to `/root/period.txt`.
7. Read `/root/period.txt` back and verify the value format before concluding.

Before step 6, confirm the run actually finished and exposed a specific candidate period in logs or computed variables; do not infer success from script launch alone.

If you only inspected a sample of the input to learn the schema, make sure the actual analysis step still loads the full dataset from `/root/data/tess_lc.txt`.

If a lightweight search already gives the same candidate twice or survives a narrow recheck, finalize instead of escalating to a broader expensive search.

## API verification rule
Before using any nontrivial third-party package that you do not know well:
- Verify the import succeeds in the current environment first.
- Inspect the exact installed API.
- Confirm a minimal call pattern in isolation.
- Only then embed it in the full pipeline.

Do **not** guess method names or constructor kwargs.
If the package is optional or unfamiliar, spend at most one short inspection step and one minimal callable test; then either use it in the full pipeline or abandon it immediately in favor of the verified fallback below.

## Safe fallback order
Use the first option whose API you can verify quickly and that can complete in the current run:
1. `astropy.timeseries.BoxLeastSquares` for transit-like dips
2. `astropy.timeseries.LombScargle` for sinusoidal/rotation checks and sanity checking aliases
3. Other specialized transit packages only if you confirm the installed API first and still have a same-run fallback

Start with a standard-library path when possible instead of writing the main pipeline around an unverified optional package and catching `ImportError` later.

Do **not** add arbitrary default periods, "pick the second peak" rules, or similar tie-breakers just to force an output. If the best candidate is not supported by a completed run, revise the search and validate again.

## Resource-control pattern
For heavy searches (especially TLS or dense grid scans), control parallelism explicitly if the first run is killed or the machine becomes overloaded.
- Prefer a small bounded thread count or worker limit rather than default all-core behavior when resource use looks aggressive.
- Treat resource tuning as part of obtaining a valid run, not just an optimization.
- If a rerun with limited threads still fails, then narrow the grid or switch to the fallback order above.

## Robust default pattern
Before running the script, delete any old `/root/period.txt` so a later file read cannot accidentally reuse a stale result from a failed or interrupted run.

```python
import numpy as np
from astropy.timeseries import BoxLeastSquares
from scipy.signal import medfilt

arr = np.loadtxt('/root/data/tess_lc.txt')
time, flux, quality, flux_err = arr.T
mask = (quality == 0) & np.isfinite(time) & np.isfinite(flux)
time, flux = time[mask], flux[mask]

# simple detrending: divide by median-filter trend if cadence is dense enough
k = 101 if len(flux) >= 101 else max(3, len(flux)//2*2+1)
trend = medfilt(flux, kernel_size=k)
trend[trend == 0] = 1.0
flat = flux / trend

periods = np.linspace(0.2, 20.0, 20000)
durations = np.linspace(0.05, 0.3, 10)
bls = BoxLeastSquares(time, flat)
power = bls.power(periods, durations)
best_period = float(power.period[np.argmax(power.power)])

with open('/root/period.txt', 'w') as f:
    f.write(f'{best_period:.5f}')
```

## Debugging limit
If a library call fails:
- do not repeat the same package with guessed alternate method names or positional arguments
- spend at most one short inspection step confirming the signature
- update the script immediately
- rerun the full pipeline
- if the run was killed rather than merely slow, do not just increase the timeout and rerun unchanged
- instead reduce the workload first: narrower period limits, fewer trial periods, safe downsampling/coarse scan, limited threads/workers, or switch from TLS/specialized search to `BoxLeastSquares`
- if still blocked, switch to the fallback above instead of continuing open-ended probing

Before executing a newly written script:
- inspect the saved file once for truncation/syntax issues
- then run it end-to-end
- if it fails, fix the concrete error and rerun

Do not count script creation alone as progress toward completion.
- If a run is killed, stalls, or produces only partial logs, do not treat the existing `/root/period.txt` as trusted by itself; modify the workflow to emit a compact final summary (best period and key score) to stdout or a file under `/root/`.
- If a search command returns no observed best period yet, do not continue as if it worked. Rerun with a narrower grid, coarser scan, or fallback method that can return an actual candidate in the current session.
- As soon as you have one validated candidate period, write `/root/period.txt` and verify it before any optional extra exploration.

## Minimum scientific cross-check
Before accepting the best period from the primary pipeline, do at least one of these when feasible:
- rerun with one alternate reasonable detrending window or clipping choice
- inspect obvious aliases/harmonics (`P`, `P/2`, `2P`, nearby strong peaks)
- phase-fold the light curve and confirm repeated transit-like dips

Prefer a candidate that survives one of these checks over a numerically stronger but unstable peak.

## Finalization rule
If a refined BLS or other primary search already returns a plausible best period:
- write `/root/period.txt` immediately after the result is validated enough for the task
- only then consider optional extra diagnostics if time/resources clearly allow
- if a later optional step is killed, keep the earlier validated candidate and finish

## Final check
Before finishing, confirm:
- script ran without error
- `/root/period.txt` exists
- file contains a single numeric value rounded to 5 decimals

- the analysis was observed to finish, not merely started
- the final analysis command's output was actually inspected rather than assumed successful
- the successful run visibly reached the code that writes `/root/period.txt`
- the file was freshly produced by that run, not left over from an earlier attempt
- after the final run, reopen `/root/period.txt` and verify it contains exactly one numeric token formatted to 5 decimal places
- if the script printed an import error, installation instruction, or any message implying a second run is needed, treat that as failure and rerun with the verified fallback instead
- only finish after this explicit artifact check
