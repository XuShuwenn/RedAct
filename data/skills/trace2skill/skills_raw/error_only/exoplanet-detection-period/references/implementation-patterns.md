# Implementation Patterns

## When to read this
Read this when writing code for period detection, especially if you are considering an unfamiliar transit-search package or need a fallback that is likely to run on the first try.

## Preferred workflow
1. Load `/root/data/tess_lc.txt`.
2. Keep only rows with quality flag `== 0`.
3. Remove non-finite values and obvious flux outliers.
4. Detrend low-frequency variability.
5. Search periods with a confirmed callable API.
6. Write one numeric period to `/root/period.txt`.

## API verification rule
Before using any nontrivial third-party package that you do not know well:
- Inspect the exact installed API first.
- Confirm a minimal call pattern in isolation.
- Only then embed it in the full pipeline.

Do **not** guess method names or constructor kwargs.

## Safe fallback order
Use the first option whose API you can verify quickly:
1. `astropy.timeseries.BoxLeastSquares` for transit-like dips
2. `astropy.timeseries.LombScargle` for sinusoidal/rotation checks and sanity checking aliases
3. Other specialized transit packages only if you confirm the installed API first

## Robust default pattern
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
- spend at most one short inspection step confirming the signature
- update the script immediately
- rerun the full pipeline
- if still blocked, switch to the fallback above instead of continuing open-ended probing

## Final check
Before finishing, confirm:
- script ran without error
- `/root/period.txt` exists
- file contains a single numeric value rounded to 5 decimals
