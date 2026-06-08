---
name: earthquake-phase-association
description: "Group seismic waveform picks from multiple stations to identify earthquake events using SeisBench deep learning models."
---

# Seismic Phase Association

## When to Use

- Associate seismic waveform picks with earthquake events
- Use deep learning for P/S wave picking (SeisBench)
- Group picks from multiple stations into coherent events


## Execution Requirements

## Execution Requirements

- Use absolute paths exactly as specified: `/root/data/wave.mseed`, `/root/data/stations.csv`, and `/root/results.csv`.
- Do not claim success until `/root/results.csv` exists and has been checked against the output requirements.
## Input Data

- `/root/data/wave.mseed`: Seismic waveform data (MSEED format)
- `/root/data/stations.csv`: Station info (network, station, channel, lon, lat, elevation_m, response)

## Velocity Model

- P wave velocity: vp = 6 km/s
- S wave velocity: vs = vp / 1.75

## Key Steps

1. Load waveform and station data

   - First verify core imports in the current environment before designing the pipeline (for example `obspy`, `seisbench`, `pandas`, `numpy`). If a planned library cannot be imported, switch to an available approach instead of writing the full solution around the missing package.
   - Before building the full pipeline, run a tiny smoke test on one trace or short window and inspect the actual library contracts: what SeisBench inference method is available (for example `annotate` or `classify`), what it returns, where picks are stored, and what timestamp and identifier fields look like.

2. Use SeisBench for P/S wave picking

   - Preserve original pick identifiers unless the downstream associator explicitly documents a different required format.
   - Do not assume fields like `waveform_id`, `phase_hint`, uncertainty attributes, or guessed column names without observing them in a successful probe.
   - Filter ML picks by confidence/probability when available, and suppress near-duplicate picks per station/phase in short time windows before association.

3. Associate picks across stations by travel time

   - Before association, validate join keys between picks and station metadata. Print a few pick IDs and station IDs and confirm they use the same schema and intended level of detail.
   - Normalize station identifiers to match the picker output before association; do not fabricate arbitrary channel mappings or collapse distinct channels by accident.
   - If association returns zero events or unexpectedly few events, check structural preconditions first: required columns, timestamp parseability/types, station lookup coverage, and successful pick-to-station joins before tuning thresholds.

4. Group into unique earthquake events
5. Output to `/root/results.csv` with `time` column (ISO format, no timezone)


Before accepting results, perform basic quality control and stage verification:
- Confirm traces were read, picks exist, association produced plausible event candidates, and `/root/results.csv` was actually written
- Inspect pick density versus data duration; extremely high pick counts usually indicate noise or over-triggering
- Verify each output row represents one event time, not raw picks
- If a preferred associator is unavailable or brittle, use a fallback that still relies on station geometry plus the vp/vs model to check travel-time consistency across stations; do not replace association with fixed-width time clustering alone



## Preflight and Validation

## Preflight and Validation

- Start with the simplest viable end-to-end pipeline: load MSEED with ObsPy, run a SeisBench picker, associate/group picks using travel-time consistency, and write `/root/results.csv` before adding optional libraries.
- Validate generated Python before long runs, for example with `python -m py_compile /root/associate_events.py`.
- Prefer a small end-to-end test first: one station or a short time window to confirm picks, joins, and association behavior.
- Make one evidence-based fix at a time, verify the file actually changed, then rerun.

Read `references/validation-workflow.md` when implementing SeisBench picking or association logic.
## Output Format

CSV at `/root/results.csv`:
- Required column: `time` (ISO 8601 without timezone)
- Other columns allowed
- Each row = one earthquake event


- `time` values must be ISO 8601 without timezone, e.g. `2019-07-04T19:00:02.500`.
- Do not write timezone-bearing strings such as `2019-07-04T19:00:02.500+00:00`.
- Always write the final event catalog to `/root/results.csv` before finishing, even if only the required `time` column is produced.

## Evaluation

- Match events within 5 second tolerance to ground truth
- F1 score >= 0.6 required to pass


## Execution Guardrails

## Execution Guardrails

- Verify unfamiliar library APIs before building the full pipeline. Inspect method signatures, return types, and required inputs for SeisBench or association libraries; do not assume wrappers or methods from memory.
- When a run fails, capture the full traceback and fix the observed error before making further changes. If output is truncated, rerun in a simpler mode or redirect stdout/stderr to a log so the full error is visible.
- Debug the failing stage in isolation before rerunning the full end-to-end pipeline. Prefer a minimal reproduction of the association step over repeated full pipeline runs.
- Do not edit installed third-party package files or monkey-patch associators speculatively unless the traceback shows the failure originates there and you cannot solve it in your own code.
- Do not start by tuning thresholds, clustering parameters, or deduplication rules unless diagnostics point there.
- Do not consider the task finished until you have run the pipeline successfully and confirmed `/root/results.csv` exists, is readable, and is non-empty or at least a valid CSV with the required `time` column.
## Tips

- Use ObsPy for MSEED reading
- SeisBench pretrained models: EQTransformer, PhaseNet, GPD

- SeisBench pretrained models: EQTransformer, PhaseNet, GPD
- Treat SeisBench outputs as library-specific objects: inspect actual example elements instead of assuming list/dict structure.
- Add quick diagnostics early: sample pick, sample station ID, sample pick ID, and total matched picks.
- When using GaMMA or similar associators, verify that every pick can map to a station record before tuning `dbscan_eps`, min-picks, or other hyperparameters.
- Prefer simple, verified association logic over unverified external wrappers. If a third-party associator API is unclear or unstable, fall back to travel-time-based grouping you can inspect end-to-end.
- Finish with a verified `/root/results.csv`; do not stop after launching long or background jobs.
