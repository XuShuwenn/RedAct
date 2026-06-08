# Validation Workflow for SeisBench Association

Use this when building or debugging the pipeline.

## 1) Dependency preflight

Run a minimal import check before committing to a design:

```python
import obspy, pandas, seisbench
print('imports ok')
```

If you plan to use any extra package for association, verify it first:

```python
import importlib
print(importlib.util.find_spec('gamma'))
```

If it is missing, do **not** build the workflow around it unless you can install it within the task.

## 2) Probe SeisBench outputs before parsing

Use a small sample and inspect the returned object type and available fields.

```python
from obspy import read
import seisbench.models as sbm

st = read('/root/data/wave.mseed')
st_small = st[:1]
if len(st_small) and st_small[0].stats.npts > 2000:
    st_small[0].data = st_small[0].data[:2000]

model = sbm.PhaseNet.from_pretrained('original')
result = model.classify(st_small)
print(type(result))
print(result)
```

Then write conversion logic based only on what you actually observed.

## 3) Smoke test before full run

Before processing all data:
- Use one station or a short time slice
- Run picking
- Convert picks
- Validate pick/station identifier compatibility
- Produce a small `/root/results.csv`
- Re-open the CSV and confirm the required `time` column exists and uses ISO format without timezone

## 4) Scale up only after success

Only after the smoke test succeeds should you:
- run the full waveform set
- try heavier models
- spend time waiting on long inference jobs

## 5) Debugging order

If association fails or returns zero events:
- capture the full traceback
- inspect sample pick IDs and sample station IDs
- verify required columns and datetime parsing
- confirm picks actually join to station metadata
- only then adjust association parameters

## 6) Do not leave the task half-finished

After script edits:
- run the script successfully
- inspect `/root/results.csv`
- confirm at least one row or an intentionally empty but valid CSV with `time` column
- only then finish the task