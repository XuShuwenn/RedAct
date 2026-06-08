# Validation Workflow for SeisBench Association

Use this when building or debugging the pipeline.

## 1) Dependency preflight


Before designing the full pipeline, also inspect the input coverage:
- count traces
- count unique stations in `stations.csv`
- inspect the station CSV header, sample waveform trace IDs, and sample rates
- note the waveform start/end time span
- compare expected station coverage between waveform IDs and station metadata

This gives you a baseline for judging whether later pick counts and event counts are plausible.

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

If you intend to use GaMMA-style association, also verify common dependencies explicitly:

```python
import importlib
for name in ['gamma', 'pyproj']:
    print(name, bool(importlib.util.find_spec(name)))
```

Use the real import name reported by the environment; do not guess package/import naming from memory.


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

Do not proceed with parser or pipeline code that assumes unverified methods like `predict`. First confirm the callable inference entrypoint and inspect one concrete returned pick/example.

If the probe raises an exception or exits nonzero, do not treat any partial printed output as success. Fix that exact issue first, and only then proceed to pipeline construction.

In particular, check whether `classify()` returned a structured object with a `.picks` attribute. If so, iterate over `result.picks` and inspect one element before mapping fields into your DataFrame rather than assuming the result itself is directly iterable.

Also inspect a few pick elements directly before choosing dataframe columns or time conversion rules, and print the identifier field you will join on so you can compare it to station metadata before writing the association step.

```python
picks = getattr(result, 'picks', result)
if picks:
    p = picks[0]
    print(type(p))
    print(getattr(p, '__dict__', 'no __dict__'))
    for attr in ['trace_id', 'station', 'phase', 'phase_hint', 'peak_time', 'time']:
        print(attr, getattr(p, attr, None))
```

If you serialize picks to CSV for downstream association, reload that CSV immediately and verify both schema and timestamp parsing before using it downstream.


Add one identifier sanity check before moving on:
- print a few raw pick identifiers exactly as returned by the library
- print the extracted `network/station/location/channel` fields
- compare them to a few station IDs from `/root/data/stations.csv`
- if the extracted keys cannot match the station schema, stop and repair extraction before writing downstream association tables

## 3) Smoke test before full run

Before processing all data:
- Use one station or a short time slice
- Run picking
- Convert picks
- Validate pick/station identifier compatibility
- Produce a small `/root/results.csv`
- Re-open the CSV and confirm the required `time` column exists and uses ISO format without timezone

- Print 2 to 5 sample pick IDs and 2 to 5 sample station IDs.
- Confirm the identifier schema matches at the intended level.
- Compute and print station-match coverage after normalization and show a few unmatched pick IDs if coverage is not near-complete.
- Keep this run in the foreground with visible logs; do not switch to background execution until this minimal path has succeeded.
- Prefer a single script for the whole pipeline so smoke tests and full runs use the same code path.
- If using an associator with strict geometry/config requirements, run it on a tiny pick subset first and confirm required keys and coordinate conventions are accepted before scaling up.


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


Before rerunning after a code edit:
- run `python -m py_compile /root/associate_events.py` or an equivalent fast parse check
- inspect the exact edited lines to confirm the intended change was saved
- if the prior failure was from multiprocessing or wrapped tracebacks, retry the smallest reproducible case in single-process or with traceback redirected to a log

If the script exits with code 1 but the error is truncated, rerun with explicit logging before diagnosing:

```bash
python /root/associate_events.py > /tmp/associate.log 2>&1; tail -100 /tmp/associate.log
```

Only after the exact exception is visible should you change parsing, association, or dependency handling.

Also check these structural prerequisites before tuning parameters:
- print `picks_df.columns`, representative dtypes, and sample rows
- print station metadata columns, dtypes, and sample rows
- print sample pick station IDs alongside sample station table IDs and the number of successful joins/matches
- verify coordinate units and projection when using geometry-based association
- if common pick/station IDs are zero, fix identifier construction first; this is not a threshold-tuning problem
- remove or narrow any broad exception handlers that convert real inference/association failures into misleading zero-pick outputs
- only after those checks pass should you tune epsilon, min-picks, dedup windows, or similar heuristics

## 6) Do not leave the task half-finished

After script edits:
- run the script successfully
- inspect `/root/results.csv`
- confirm at least one row or an intentionally empty but valid CSV with `time` column
- only then finish the task

- If the full run is long or quiet, wait for a definite outcome or run a smaller foreground reproduction that you can observe end-to-end; do not stop the only active production run without first confirming it is truly stalled or failing.
- Reopen `/root/results.csv`, print a few `time` values, and confirm no timezone-bearing strings such as `Z` or `+00:00` remain before finishing.
- After you get an initial event catalog, do one quick quality pass: inspect a few rows, check rough event count against data duration and station coverage, and look for many events with very few supporting picks or obvious edge artifacts.
- If the task instructions require an exact completion message or protocol, emit it only after validating outputs.
