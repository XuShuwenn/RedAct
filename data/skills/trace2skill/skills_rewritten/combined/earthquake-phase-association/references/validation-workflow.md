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
After any install or import-path change, run a minimal proof for the exact module path and symbol your script will use, for example:

```python
import importlib
m = importlib.import_module('gamma.utils')
print(hasattr(m, 'association'))
```

Do not resume the full pipeline until this probe succeeds cleanly.


If you intend to use GaMMA-style association, also verify common dependencies explicitly:

```python
import importlib
for name in ['gamma', 'pyproj']:
    print(name, bool(importlib.util.find_spec(name)))
```

Use the real import name reported by the environment; do not guess package/import naming from memory.

If you already have a traceback naming the missing module, treat that as the primary signal. Resolve that exact import first; do not start with nearby package names, deprecated package-search commands, or a redesign around an unverified alternative.


If you are considering a specific associator or helper stack, verify the full critical set before writing the pipeline around it. Example:

```python
import importlib
for name in ['gamma', 'pyproj']:
    print(name, bool(importlib.util.find_spec(name)))
```

If an import is missing, resolve it in this order:
1. confirm the exact module name your code needs
2. inspect which distribution provides it (`python -m pip show ...`, package docs, or installed module metadata)
3. verify the imported API you plan to call
4. only then install the confirmed distribution

Do not validate one dependency, ignore the rest, and proceed anyway. Do not try similarly named packages speculatively. If provenance is unclear or any required package is missing, either install it within the task or immediately use the simpler fallback workflow.


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
If your first assumption is wrong, treat that as a hard stop for pipeline construction. Keep probing until you can show:
- the exact container to iterate
- one concrete example element
- the exact attribute names you will read downstream

A good probe ends with evidence like `result.picks[0]` plus printed values for identifier, phase label, time, and score/probability if present.

Also confirm the required input object type before building the pipeline. SeisBench models commonly operate on an ObsPy `Stream`; passing a bare `Trace` or a plain list can trigger downstream attribute errors such as missing `merge()`.

Minimal rule:
- if you slice to one trace for a probe, keep or reconstruct it as a `Stream`
- do not rewrite the whole pipeline around an object-type error until you have checked the model's expected container on the live object

Do not proceed with parser or pipeline code that assumes unverified methods like `predict`. First confirm the callable inference entrypoint and inspect one concrete returned pick/example.

If the probe raises an exception or exits nonzero, do not treat any partial printed output as success. Fix that exact issue first, and only then proceed to pipeline construction.

In particular, check whether `classify()` returned a structured object with a `.picks` attribute. If so, iterate over `result.picks` and inspect one element before mapping fields into your DataFrame rather than assuming the result itself is directly iterable.

Also inspect a few pick elements directly before choosing dataframe columns or time conversion rules, and print the identifier field you will join on so you can compare it to station metadata before writing the association step.

Keep time fields in a downstream-compatible native form during intermediate stages. If the associator expects datetimelike values, convert observed pick times to `pd.Timestamp` in the working table and verify the dtype before association; do not stringify them early and then debug avoidable parsing issues later.

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


Add one hard gate before scaling up:
- run the probe on a real ObsPy `Stream`, not a bare `Trace` or plain Python list
- call only an inference method you just confirmed exists on the live model object
- if the probe yields zero picks, do not build or rerun the full association pipeline yet; first diagnose picker behavior on the tiny sample and print the exact result object, sample-rate/time-span context, and one concrete access path such as `result.picks[0]` when available
- treat repeated zero-pick smoke tests as a blocker for scaling up, not as a reason to keep rewriting the downstream associator

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
- Print the specific associator settings used in that smoke test (for example search ranges, clustering radius/epsilon, minimum picks, projected-coordinate fields, or worker/process settings) so you can confirm the configuration matches both the installed API and the observed data scale.
- If the tiny associator run fails, fix the contract or configuration mismatch first; do not assume the defaults are appropriate simply because imports succeeded.



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




If the failure comes from a third-party associator call, add one contract check before any workaround:
- print the exact callable/module path being invoked
- inspect its signature or available help/docstring in the live environment
- print the config dict keys and representative value types
- print the pick/station dataframe columns actually passed into that call

Do not respond first with ad hoc changes such as worker-count changes, broad numeric casting, compatibility flags, or threshold tuning unless the full traceback and API/contract check point to that exact fix.
Before rerunning after a code edit:
Add a file-integrity checkpoint before expensive execution:
- read back the first 20 to 40 lines and the edited region of `/root/associate_events.py`
- confirm imports are complete, no lines are visibly truncated, and no placeholder prose was written into the file
- only then run `py_compile` and the next smoke test

If the visible error is a `multiprocessing.pool.RemoteTraceback` or similar wrapper, change the reproduction so the real exception appears directly before editing code. Typical options:
- force the failing stage into single-worker or single-process execution if configurable
- run only the smallest pick subset or one station that still reproduces the failure
- redirect full stdout/stderr to a log and inspect the tail after the process exits

Do not claim a root cause from the wrapper message alone.
- run `python -m py_compile /root/associate_events.py` or an equivalent fast parse check
- inspect the exact edited lines to confirm the intended change was saved
- if the prior failure was from multiprocessing or wrapped tracebacks, retry the smallest reproducible case in single-process or with traceback redirected to a log

If the script exits with code 1 but the error is truncated, rerun with explicit logging before diagnosing:
This is mandatory, not optional. Do not make configuration or schema edits until the log shows the complete exception text and failing frame. After the fix, rerun the same entrypoint again and verify that either the exact error changed or `/root/results.csv` was produced and rechecked.

Also keep shell interactions fully concrete during debugging. Use executable commands such as:

```bash
ls -l /root/data
python -m py_compile /root/associate_events.py
python /root/associate_events.py > /tmp/associate.log 2>&1
tail -100 /tmp/associate.log
```

Do not send descriptive phrases like "inspect the input data" or "run the association workflow" in place of commands.


```bash
python /root/associate_events.py > /tmp/associate.log 2>&1; tail -100 /tmp/associate.log
```

Only after the exact exception is visible should you change parsing, association, or dependency handling.
Use this exact discipline for each failure:
1. rerun until the complete traceback is visible
2. identify the specific failing line/message
3. inspect the live file and apply one targeted fix in your own script first
4. rerun and confirm that exact error is gone or changed
5. only then consider a new hypothesis

Do not patch installed libraries, add speculative dependency workarounds, or tune parameters against an unseen exception.

Do not treat partial stdout, station-processing lines, or expected side effects as proof that picking or association finished. Confirm success with exit status plus direct checks such as: saved pick file exists and is readable, pick count was printed from the completed run, or `/root/results.csv` was reopened and inspected.

Also check these structural prerequisites before tuning parameters:
- print `picks_df.columns`, representative dtypes, and sample rows
- print station metadata columns, dtypes, and sample rows
- print sample pick station IDs alongside sample station table IDs and the number of successful joins/matches
- verify coordinate units and projection when using geometry-based association
- if common pick/station IDs are zero, fix identifier construction first; this is not a threshold-tuning problem
- remove or narrow any broad exception handlers that convert real inference/association failures into misleading zero-pick outputs
- only after those checks pass should you tune epsilon, min-picks, dedup windows, or similar heuristics

- Do not invent a root cause from partial logs. If output ends mid-line or mid-traceback, treat the diagnosis as unknown until you capture the full log.
- When editing the script, do not apply blind replacements against placeholders or guessed section names. First print or open the exact target region, edit against concrete existing lines, then re-open the modified region to confirm indentation and control flow are still correct.
- If you changed identifier normalization, print the final tables actually passed downstream, not just earlier intermediate examples. Verify `columns`, `dtypes`, 3 to 5 sample rows, join or match coverage, and show a few unmatched IDs if coverage is incomplete.
- After any install step, verify both clean completion and a minimal import probe for the exact package name before rerunning the pipeline.
- After two unsuccessful zero-event runs, stop tuning and either fix a demonstrated contract problem or switch to the simpler travel-time-consistency fallback using the validated picks and station geometry.
- If the script is still running, inspect progress before interrupting it; do not assume a hang from elapsed time alone.

- If failures appear only as `multiprocessing.pool.RemoteTraceback` or another wrapper, make the next run diagnostic rather than iterative: reduce to one worker if possible or capture full logs, and do not change parameters until the real inner exception is visible.
- After applying a fix, verify it with an observed rerun outcome before summarizing progress. If the rerun has not completed successfully yet, report the change as a hypothesis or attempted fix, not a confirmed resolution.
- Do not end the task after a promising partial run or "now proceeding" message. Finish only after the completed run has produced `/root/results.csv`, you have reopened it, and the host's exact completion protocol is emitted.

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

- If the environment requires an exact final completion string, give that exact string only after tool evidence shows the run succeeded and the output file was rechecked.
- Keep status language evidence-based: say `hypothesis` or `next step` until the traceback or successful rerun is visible in the session.
