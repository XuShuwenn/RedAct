---
name: gravitational-wave-detection
description: "Detect gravitational wave signals from binary black hole mergers using matched filtering with PyCBC."
---

# Gravitational Wave Detection with Matched Filtering

## When to Use

- Detect gravitational wave signals from LIGO/Virgo data
- Perform matched filtering with waveform templates
- Search for binary black hole merger signals

## Input Data

- `/root/data/PyCBC_T2_2.gwf`: Detector data in channel `H1:TEST-STRAIN`

- Read the `.gwf` frame with PyCBC frame I/O (for example `pycbc.frame.read_frame(...)`). Do **not** assume a generic time-series reader exists in `pycbc.types`.
- Before building the full search pipeline, run a tiny smoke test that opens `/root/data/PyCBC_T2_2.gwf` and confirms `H1:TEST-STRAIN` can be read successfully in this environment.

- In that smoke test, verify the exact import path you will use (for example, `from pycbc import frame` then `frame.read_frame(...)`) before embedding it in the main script.
- Do not write the full search script until this import-and-read probe succeeds without `ImportError` or attribute errors.


## Template Search

Approximants: "SEOBNRv4_opt", "IMRPhenomD", "TaylorT4"

- Use these approximant names exactly as written; do not substitute near-matches such as `SEOBNRv4` for `SEOBNRv4_opt`.
- Before the full search, verify that each requested approximant is actually available in the installed PyCBC/LAL environment.

Mass grid: mass1 and mass2 from 10 to 40 solar masses (integer steps)

- Treat the listed approximants and mass grid as fixed task requirements: run the full Cartesian grid for `mass1=10..40` and `mass2=10..40` in integer steps for every listed approximant.
- Benchmarking or smoke-test subsets are encouraged for feasibility, but they are not a substitute for the required final search unless the task explicitly allows approximation.
- Do **not** reduce coverage with coarser mass steps, narrowed windows, or `m2 <= m1` shortcuts just to reduce runtime.

- Do **not** change other search-defining settings per model to chase runtime unless the task explicitly authorizes it; for example, do not introduce model-specific `f_lower` changes, coarse localization passes that restrict the final grid, or mixed-coverage fallback plans.
- Do **not** substitute different waveform models if one is unavailable or errors; report that blocker explicitly rather than relabeling another model's result.

- If availability checks fail for any required approximant, stop and report the blocker clearly; do **not** map it to another approximant and keep the original name in output.
- Do **not** write a CSV row for an approximant unless that exact approximant produced at least one successful matched-filter result.


## Process

1. Validate data loading first with a minimal script that reads `/root/data/PyCBC_T2_2.gwf` from `H1:TEST-STRAIN` successfully.
2. Build one faithful serial baseline pipeline using PyCBC: condition detector data (whiten, bandpass), generate templates, and run matched filtering end-to-end on a tiny subset.

- Prefer one reproducible Python script that performs the full workflow end-to-end: read frame data, condition strain, estimate PSD, run the template search, and write the final CSV.
- In that baseline, use standard detector-data conditioning before matched filtering (for example: highpass/bandpass as appropriate, resample if needed, and crop filter transients before PSD/matched-filter steps).

3. Before the full sweep, benchmark a small representative subset (for example, one approximant and a few mass pairs) to estimate runtime and confirm progress/logging and CSV-writing behavior.
3a. Do not start the full `(approximant, mass1, mass2)` sweep until one complete end-to-end trial has succeeded for at least one approximant and one mass pair, has produced a non-trivial interpretable SNR, and has emitted useful diagnostics.
3b. Turn that pilot into an explicit execution plan before launching the full search: estimate the rough full-grid runtime, decide whether to stay serial or split by approximant/batch, and define how intermediate best-per-approximant results will be checkpointed and merged into `/root/detection_results.csv`.
3c. If the estimate is too large for the remaining session budget, switch immediately to a resumable plan instead of launching the monolithic full sweep and later aborting it.
3d. If you write or edit a Python script, inspect the saved file and run a quick syntax/import smoke test before launching any expensive search.
3e. Instrument the pilot with explicit stage logs around waveform generation, PSD estimation, and matched filtering so a later stall can be localized quickly.
3f. Once one baseline path works, keep that implementation stable and scale it up; do not repeatedly rewrite core search logic unless a concrete observed failure requires a fix.
4. Reuse conditioned strain data and PSD where possible instead of recomputing preprocessing inside the mass-grid loop.
4a. If you split work by approximant or batch, compute frame loading, conditioning, and PSD estimation once and reuse or persist those shared artifacts; do not repeat identical preprocessing in each worker unless you have confirmed it is negligible.
5. Run the full required search over all listed approximants and the full integer mass grid, keeping one stable implementation path rather than repeatedly restarting with unvalidated changes.
   - If a simple serial or batched baseline is already producing valid progress, prefer letting it finish or resuming from its checkpoints rather than replacing it with an unproven rewrite.
6. If runtime is high, use batching, checkpointing, or per-approximant execution that still preserves the required final search and supports a final merge.
6a. If you split execution by mass range or approximant, maintain an explicit completion checklist covering all 3 approximants and the full `mass1=10..40`, `mass2=10..40` grid.
6b. If you write intermediate per-batch files, execute a final consolidation step that reads all completed batches, selects the highest-SNR result per approximant, and writes exactly `/root/detection_results.csv` with the required schema.
6c. Do not consider the task complete while results exist only in batch-specific files such as per-range or per-approximant CSVs.
6d. Do not treat partial console output, sparse logs, timeouts, or truncated captures as finished results; confirm completion from explicit artifacts, checkpoint contents, or exit evidence before proceeding.
7. Extract the strongest signal (highest SNR) per approximant.
   - During the sweep, keep only online best-so-far values per approximant unless detailed per-template output is explicitly required.
8. Write `/root/detection_results.csv` with the final best row for each approximant.
9. Finish only after directly verifying the CSV exists, is non-empty, and contains the intended final rows.
10. If a script was written or patched for the search, actually execute it (or equivalent commands) and inspect its outputs; do not stop at code drafting or an unexecuted fix.
11. Use an explicit completion checklist before finishing: data read succeeded, conditioning and matched filtering ran, the full required search completed, one strongest row was selected for each approximant, and `/root/detection_results.csv` was verified on disk.


## Process

## Preflight Checks

- Run a minimal probe before the expensive search:
  - load a short stretch of strain data
  - verify the conditioning/PSD call signatures you plan to use
  - generate one small template for each requested approximant
  - confirm one matched-filter call runs without API or attribute errors
- Do not assume PyCBC object methods from memory; inspect the installed API first if a method name is uncertain.
- For PSD/Welch-style estimation, verify parameter units carefully: `seg_len` and `seg_stride` may be sample counts rather than seconds. At 4096 Hz, 4 seconds is `seg_len=16384`, not `4`.
- If PyCBC/LAL reports a waveform domain error such as `Ringdown frequency > Nyquist frequency` or `Input domain error`, fix the configuration on a bounded test before resuming the full search.

- Smoke-test the exact data and preprocessing calls you will rely on before writing the full script: confirm the frame read works, inspect the returned object type and available attributes/methods, and verify the exact conditioning/resampling functions available in this installed PyCBC version rather than assuming object methods exist.
- Probe required approximant support explicitly before the main run by generating one tiny template with each requested approximant; treat any unavailable approximant as a blocker to report, not something to discover halfway through the full sweep.
- Do not treat a data-load-only probe as sufficient. Before any full-grid or background run, complete one end-to-end micro-run that performs: data read -> conditioning/PSD setup -> one template generation -> one `matched_filter` call -> best-row extraction -> write and read back a tiny CSV or result object.
- On the bounded end-to-end test, verify representation compatibility before scaling up: if you generate frequency-domain templates, confirm the strain and PSD passed into `matched_filter` are in the corresponding expected form with compatible sizing and sampling parameters.
- Do not proceed from a smoke test that only runs without crashing; read back one resulting SNR value and confirm the pipeline is numerically producing non-trivial output for the test case.
- On the tiny probe, print or assert the exact PSD parameters you will use in the full run so unit mistakes are caught before a long conditioning step.
- Verify output paths before the long run: confirm you can create and read a small test file under `/root` and decide how the final CSV will be written atomically or merged from batches.
- For any new execution mode you introduce (especially multiprocessing or background execution), run a tiny representative batch and confirm worker startup, visible progress, returned results, and clean completion before trusting it for the full search.
- Freeze analysis-defining parameters after the pilot succeeds; optimize batching, checkpointing, or artifact reuse first rather than changing conditioning or filter settings solely to reduce runtime.

## Output Format

CSV at `/root/detection_results.csv`.


- Write the final file to exactly `/root/detection_results.csv`.
- Required columns: `approximant,snr,total_mass`.
- Include exactly one strongest-signal row for each required approximant: `SEOBNRv4_opt`, `IMRPhenomD`, and `TaylorT4`.
- Include one final strongest-signal row per approximant only after that approximant's search has completed.
- Temporary files, logs, or partial outputs are not substitutes for the required final CSV.
- If execution is split into batches, persist durable intermediate best rows/checkpoints and then merge them into the final CSV.
- Do not spend the session only rewriting or benchmarking scripts; each major execution step should move toward producing or completing `/root/detection_results.csv`.
- Before finishing, verify `/root/detection_results.csv` exists, is readable, and is non-empty.
- Read the file back and confirm the header is exactly `approximant,snr,total_mass` and that there are exactly three final rows, one for each required approximant.
- Do not conclude from logs, background-task status, a launched process, a running job, or a "script completed" message alone; direct inspection of the final CSV is required.
- After the search starts, compare early console/log output against the intended configuration; do not let a long run continue if the printed approximant names or executed script path differ from the intended setup.


## Key Metrics

- snr: Signal-to-noise ratio
- total_mass: mass1 + mass2 (solar masses)

## Tips

- Use PyCBC for matched filtering
- Use PyCBC directly for the required matched-filter workflow; avoid substitute models or alternate outputs that change the requested computation
- Check data quality and conditioning


- Prefer a known-good serial implementation over multiprocessing; parallelize only after the serial path works end-to-end.
- Do not start with a naive full `(approximant, mass1, mass2)` brute-force run without timing a small sample first.
- Probe library behavior first with a short Python check before relying on an unfamiliar PyCBC method name.
- If using split jobs or background execution, define the merge step in advance and preserve best-so-far results per approximant.
- Treat logging or sparse console output as observability only; verify success from completed matched-filter results or the final CSV, not from partial progress messages.
- If an approximant has zero successful templates, treat that as a blocker to debug rather than writing a placeholder result.
- Read [Runtime Search Guide](references/runtime-search.md) when a pilot run is slow or when you need batching, checkpoints, or a final merge from partial runs.




## Tips

## Failure Handling

- Do not use broad `except Exception: continue` inside the mass-grid loop without surfacing diagnostics.
- Record representative errors per approximant and count failed vs. successful templates.
- Treat "no successful templates for an approximant" as a blocking error to debug, not a completed search result.
- Only write the final CSV after the search completes and diagnostics have been checked.

- Never use silent `except Exception: continue` behavior in the mass-grid loop. At minimum, capture representative error text per approximant and report success/failure counts.
- Treat `zero successful templates`, all-zero best results, or missing masses for any approximant as a blocking failure; do not write that approximant as a completed final row.
- If you add intermediate persistence for conditioned strain, PSD, or partial search results, smoke-test the exact save/load path on a tiny object first; do not insert unverified serialization steps into the main long-running pipeline.
- If a run is quiet, times out, or appears hung, do **not** rerun the same full command unchanged. Reduce to one approximant and one or a few mass pairs, add stage-level timing and logging, and rerun the smaller diagnostic first.
- Prefer Python-based inspection and file/log checks over assuming shell tools like `ps` or `pgrep` exist in the environment.
- Do not respond to a single template or approximant error by immediately relaunching the whole search with new heuristics.
- After any configuration change meant to fix an error or speed up execution, rerun a tiny representative validation case first and confirm the required search definition is still unchanged.
- After fixing a bug, immediately rerun the affected pipeline stage; do not treat an unexecuted patch as progress.
- Before concluding, directly read back `/root/detection_results.csv` and confirm it contains the required columns and one row for each required approximant; do not infer success from logs or intended next steps.

## Preflight Checks

## Implementation Guardrails

- Use PyCBC's built-in conditioning and matched-filter primitives as the default correctness baseline.
- Do **not** replace `matched_filter` with a custom FFT/SNR implementation for final results unless you first show numerical agreement with PyCBC on the same data/template within a small tolerance.
- Do **not** introduce empirical calibration or scale factors to force SNR agreement; fix normalization or API usage directly.
- Optimize only after a correct end-to-end baseline exists.

- Keep `pycbc.filter.matched_filter` (or the equivalent PyCBC matched-filter primitive) as the default final-results path.
- Do not mix time-domain and frequency-domain objects in `matched_filter` unless you have explicitly verified that PyCBC expects and accepts that combination on a bounded test.
- Before the full grid, run one template through the exact final pipeline shape you intend to use and verify: waveform generation succeeds, lengths and sampling parameters are compatible, `matched_filter` returns a valid series, and peak SNR extraction works.
- When extracting the peak matched-filter SNR from a PyCBC series, convert to a plain NumPy array first (for example via `snr.numpy()`), then apply `np.abs`/`np.argmax` or equivalent NumPy operations.
- Read back the selected peak value after conversion instead of assuming PyCBC series indexing behaves like a raw NumPy array.
- If you experiment with a manual FFT/SNR implementation for profiling, treat it as exploratory only until it matches PyCBC on representative data/templates within a small tolerance.
- Do **not** ship final results from a custom matched-filter path after a failed or missing agreement check.
- Do **not** apply empirical calibration or scale factors to force agreement with PyCBC; fix normalization, sampling, or API usage instead.
- If a rewritten script preview looks truncated, malformed, or otherwise suspicious, stop and validate the file before launching any expensive or parallel jobs.
- After any script rewrite or optimization, rerun a bounded end-to-end validation: one data read, one template generation, one `matched_filter` call, and one output write/read check before resuming the full sweep.


## Implementation Guardrails

## Runtime-Safe Execution

- Build one correct baseline pipeline first; avoid repeated script churn while a valid run is in progress.
- If you create or patch a script, validate it before expensive execution: inspect the written file and run a quick syntax/import check.
- Prefer the simplest validated execution path and staged scaling: verify one approximant and a very small mass subset first, then expand.
- Treat this as a potentially long-running computation: add progress logging, checkpoints, or partial-result writes rather than assuming quiet stdout means failure.
- Do not interrupt or restart a run merely because it is slow; stop only with concrete evidence of failure such as an exception, invalid configuration, deadlock, or invalid output state.
- If computation must be split into batches because of runtime limits, track completion carefully and merge results into one final CSV.
