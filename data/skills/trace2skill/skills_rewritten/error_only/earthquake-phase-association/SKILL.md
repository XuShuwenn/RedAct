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

- Follow the host task's execution interface exactly. If the system or task specifies a required action/tool protocol, response schema, or completion signal, use only that protocol and emit it only after verifying `/root/results.csv` and the output requirements.
- Treat the host-specified action format as mandatory infrastructure, not style guidance. Do not emit unsupported tool syntaxes, alternate wrappers, XML-style tool tags, pseudo-tool markup, or prose substitutes; every command and the final completion signal must use the exact required protocol.
- Every shell step must be a concrete executable command or script invocation with visible arguments and absolute paths. Do not send natural-language placeholders such as "inspect station data" or "run the association workflow" in place of an actual command.
- Do not state that an issue is "fixed" or "resolved" without evidence from a successful rerun, a visible traceback-based diagnosis, or a reopened `/root/results.csv`.
- Use only the mandated absolute paths in code and commands; never switch to relative paths like `data/wave.mseed` or `data/stations.csv`.
- After any final code change, rerun the full pipeline, re-open `/root/results.csv`, and only then finish the task.
- If a command runs in the background or asynchronously, wait for completion, inspect the final exit status, and verify the output before treating the step as done.
- When creating or editing a script, write complete executable Python code only; never use placeholder prose, TODO summaries, or partial fragments as file content.
- Immediately after each edit, read back the saved file or edited region and confirm it is complete, not truncated, and matches the intended code before running it.
- Do not finish on a launched job, partial run, or pending background process. Finish only after a successful rerun, reopening `/root/results.csv`, and emitting the exact required completion signal.

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

   - Inspect dataset coverage immediately after loading: count traces, count unique stations, inspect the station CSV header, sample trace IDs, sample rates, and note the overall time span. Confirm waveform IDs and station metadata use compatible naming before writing conversion or join logic.


   - First verify core imports in the current environment before designing the pipeline (for example `obspy`, `seisbench`, `pandas`, `numpy`). If a planned library cannot be imported, switch to an available approach instead of writing the full solution around the missing package.
   - Before building the full pipeline, run a tiny smoke test on one trace or short window and inspect the actual library contracts: what SeisBench inference method is available (for example `annotate` or `classify`), what it returns, where picks are stored, and what timestamp and identifier fields look like.

   - Treat the probe as valid only if it exits cleanly with no traceback. Do not call guessed inference methods such as `predict`; call only methods you confirmed exist in the current environment.
   - In that probe, print one concrete returned pick/example and a few real fields needed downstream (for example identifier, phase label, time representation, and score/probability if present) before writing conversion code.
   - If the plan depends on extra packages beyond the core stack (for example GaMMA dependencies such as `gamma` or `pyproj`), verify those imports using the exact installed import names before coding around them. Either install the missing dependency within the task or switch to a simpler association path.
   - Treat dependency installation as unresolved until a minimal import/API probe succeeds in the current environment. After installing or changing imports, run a tiny command that imports the exact module path and prints the specific symbol or method you plan to use before returning to the full script.
   - If `classify` returns a structured object, inspect native pick containers such as `.picks` first and only use fields you directly observed on sample picks instead of guessing a dict/list schema.
   - Before writing a full script around any external associator or extra package, verify importability and inspect the actual API in this environment with a minimal probe. If it is missing or unclear, switch immediately to a simpler travel-time-consistency fallback instead of designing around guesses.

2. Use SeisBench for P/S wave picking

   - Preserve original pick identifiers unless the downstream associator explicitly documents a different required format.
   - Do not assume fields like `waveform_id`, `phase_hint`, uncertainty attributes, or guessed column names without observing them in a successful probe.
   - Filter ML picks by confidence/probability when available, and suppress near-duplicate picks per station/phase in short time windows before association.
   - Preserve the full observed pick source identifier across conversion boundaries and split or coarsen it only after inspecting real examples from the current run.
   - Immediately after extraction, print a few rows and verify the join-key fields you will need later are populated. If channel/location information is missing where matching requires it, stop and fix extraction before creating association inputs.
   - Before generating association-ready station tables, prove the common identifier granularity that actually exists in both datasets. If picks only contain network/station or network/station/location, deduplicate stations to that observed level first; do not expand station IDs to channel level unless the picks also carry matching channel information.
   - Print a few unmatched pick IDs whenever join coverage is incomplete, and treat zero or low overlap as a schema-construction bug to fix before association.
   - Treat unusually dense raw picks as a failure signal, not automatic evidence of many events. Compare pick count to data duration and station count; if density is implausibly high, tighten confidence thresholds and deduplicate before association.
   - If S picks are absent or severely imbalanced relative to P picks, treat the association output as provisional and inspect picker behavior before accepting the catalog.

3. Associate picks across stations by travel time

   - Before association, validate join keys between picks and station metadata. Print a few pick IDs and station IDs and confirm they use the same schema and intended level of detail.
   - Normalize station identifiers to match the picker output before association; compare sample pick IDs to sample station IDs first, and only coarsen or aggregate station metadata if the picker truly emits a coarser schema.
   - If station metadata is more granular than picks (for example channel-level metadata but station/location-level pick IDs), build one explicit deduplicated station table at that exact observed identifier level before joining or association; do not silently collapse distinct rows or fabricate missing channel mappings.
   - If association returns zero events or unexpectedly few events, check structural preconditions first: required columns, timestamp parseability/types, station lookup coverage, and successful pick-to-station joins before tuning thresholds.

4. Group into unique earthquake events
5. Output to `/root/results.csv` with `time` column (ISO format, no timezone)


Before accepting results, perform basic quality control and stage verification:
- Confirm traces were read, picks exist, association produced plausible event candidates, and `/root/results.csv` was actually written
- Inspect pick density versus data duration; extremely high pick counts usually indicate noise or over-triggering
- Verify each output row represents one event time, not raw picks
- If a preferred associator is unavailable or brittle, use a fallback that still relies on station geometry plus the vp/vs model to check travel-time consistency across stations; do not replace association with fixed-width time clustering alone

   - Do not move from picking to association until you have explicit evidence that picking finished: inspect a sample pick object or saved picks file, print the pick count, and confirm any expected intermediate artifact exists.
   - Bound SeisBench probing work to one trace or a very short slice; if model loading or downloads are slow, reduce scope further rather than skipping inspection and guessing fields.
   - Do not start a full-dataset run, background job, or heavyweight model until a tiny end-to-end run has already written a readable `/root/results.csv`.
   - Prefer one reproducible Python script for the full workflow so smoke tests and full reruns exercise the same end-to-end path.

   - If your first SeisBench probe shows an unexpected wrapper object or failed assumption about iterability, stop pipeline construction and continue probing until you can print one concrete pick/example and the exact access path used to reach it (for example `result.picks[0]`).
   - For SeisBench probing, preserve the expected container type: many model APIs expect an ObsPy `Stream`, not a bare `Trace` or plain list. If a probe fails on object-shape methods like `merge`, reconstruct the sample as the required container before changing model APIs.
   - If the preferred associator fails repeatedly, do not jump straight to ad hoc clustering. Use a fallback only after the minimal travel-time-consistent path works end-to-end on a smoke test, then validate the fallback by printing event count, sample event times, supporting-station evidence if available, and confirming the saved `/root/results.csv` matches those diagnostics.




## Preflight and Validation

- Treat syntax/compile validation as mandatory before any expensive run: after each script edit, verify the file actually changed and run a fast parse check such as `python -m py_compile /root/associate_events.py` before the next full execution.
- Follow a strict debug loop: reproduce the failure, capture the full traceback, make one targeted fix, verify the file changed, then rerun.
- If a run fails, exits non-zero, or output is truncated, rerun in a way that captures complete stdout/stderr to a log or isolates the failing stage in a smaller foreground reproduction before changing code.
- On the smoke test, print a few concrete diagnostics before scaling up: picker return type, 1 to 3 sample picks, 1 to 3 sample station IDs, matched pick count, and provisional event count.
- Do not move long runs to `nohup` or background execution until a foreground smoke test has already produced a readable `/root/results.csv` on a small sample.
- Before the first full association run, print a few pick IDs, a few station IDs, and the count of picks that successfully map to station metadata.
- Prove a minimal end-to-end path before adding optional dependencies: waveform load -> SeisBench picks -> simple travel-time-consistent association/grouping -> `/root/results.csv`.
- Add external packages or more complex associators only after the minimal pipeline works in the current environment.
- Before finishing, perform a final execute-and-verify cycle: run the current script, confirm `/root/results.csv` was rewritten, reopen it, and check that the required `time` column is present.

- Write runnable code from the first save. Do not put natural-language pseudocode or placeholder lines inside `/root/associate_events.py`; every saved version must be valid Python that can pass `python -m py_compile`.
- After any substantial file write or edit, reopen the script from disk and inspect the affected region or full file before running it; do not rely on edit-tool summaries or assumed prior content.
- If a run fails, exits non-zero, or output is truncated, do not diagnose from a partial traceback. First retrieve the full exception text and failing stack frame by rerunning with explicit logging or a smaller foreground reproduction, then make one targeted fix.
- Use an evidence-based debug loop: inspect the current script, reproduce the failure, capture the full traceback, map it to specific lines, make one focused edit, verify the file changed, run `python -m py_compile /root/associate_events.py`, then rerun the exact same script file you edited.
- Before choosing any dependency-heavy associator path, verify the full critical import set for that path up front. If any required import is missing or uncertain, either install it within the task or switch immediately to the simpler travel-time-consistency fallback.
- If association produces `0 events` more than once, stop parameter tweaking and run a contract check before any further edits: print the exact columns, dtypes, and sample rows passed into the associator; print pick-to-station match coverage; and show a few unmatched IDs.
- If a dependency or import error occurred, do not resume the full pipeline until a minimal short Python probe has successfully imported the exact module path and accessed the intended callable.
- Before finishing, reconcile final counts with the saved artifact: rerun the full pipeline, confirm `/root/results.csv` was rewritten, reopen it, verify the required schema/content, and ensure any reported event count matches the row count in that final file.


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

- Before declaring success, reopen `/root/results.csv` and verify: file exists, `time` column exists, strings contain no timezone suffix (`Z`, `+00:00`, etc.), and rows represent events rather than raw picks.

## Evaluation

- Match events within 5 second tolerance to ground truth
- F1 score >= 0.6 required to pass


## Execution Guardrails

- Do not infer counts, field names, root causes, or success from partial stdout, truncated repr output, progress lines, or a nonzero-exit command that printed some intermediate results.
- Do not build conversion logic around guessed pick attributes such as `get_id()`, `waveform_id`, or assumed relative-time semantics; inspect the actual returned pick objects first.
- Do not treat an association run that returns zero events as a tuning problem until join-key overlap, station lookup coverage, and actual association inputs have been printed and checked.
- Do not wrap core picking, pick conversion, or association in broad `except Exception: continue` blocks during development. Let the traceback surface, or log the exception with station/channel context and stop that stage.
- Verify stage completion explicitly before advancing: after picking, confirm picks were returned or written, inspect at least one sample pick, and record a total count.
- Avoid long or background runs as the first proof of correctness. First obtain a completed foreground run on a reduced sample with visible logs and a verified output file.
- If a long run is quiet, check for ongoing progress or rerun a smaller foreground case before assuming a hang.
- Do not end the task immediately after launching a background job or seeing partial progress output. Finish only after a completed run has produced and verified `/root/results.csv`.
- For associators with structured configuration, do a minimal configuration smoke test first and confirm geometry fields, dimensional bounds, and clustering parameters are all accepted before launching a full association run.
- After you have a valid `/root/results.csv`, avoid major refactors or swapping associators unless the current output is demonstrably invalid; preserve the working result and only make targeted fixes.

- If stdout/stderr is truncated or the failure point is unclear, stop guessing. Rerun with explicit log capture, inspect the actual exception, and patch only that observed error.
- Base debugging claims only on observed evidence. Do not conclude `no picks`, `missing package`, or any other root cause unless a traceback, explicit import test, printed count, or inspected object supports it.
- When traceback shows `ModuleNotFoundError` or similar import failure, resolve that exact missing module first using its reported import name. Do not guess neighboring packages or redesign around an unverified dependency before checking whether the named module can be imported or installed.
- Do not respond to associator failures with ad hoc parameter or parallelism changes until you have printed the actual input schema, config values, and confirmed they match the installed API.
- If you changed identifier normalization, prove the fix reached the real association inputs: print the final pick table IDs, final station table IDs, match coverage, and the exact columns handed to the associator.
- If repeated runs still yield zero events, escalate by simplifying to a verified fallback association path using the validated pick/station tables and station geometry; do not stay in a loop of speculative threshold changes without a working result.


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
- When using GaMMA or similar associators, verify that every pick can map to a station record and that the station table matches the associator's required coordinate/depth schema before tuning `dbscan_eps`, min-picks, or other hyperparameters.
- Prefer simple, verified association logic over unverified external wrappers. If a third-party associator API is unclear or unstable, fall back to travel-time-based grouping you can inspect end-to-end.
- Finish with a verified `/root/results.csv`; do not stop after launching long or background jobs.

- When connecting SeisBench to an associator, treat the handoff as a schema-matching step: inspect actual pick fields, required station columns, and config keys before the full run.
- For associators that operate in Euclidean space, build a deduplicated station table with projected coordinates in km and verify each pick maps to one station record.
- If full probabilistic association is too slow or unstable, first reduce complexity with higher-confidence pick filtering or simpler runtime settings before abandoning association entirely.

