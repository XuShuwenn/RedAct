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


## Template Search

Approximants: "SEOBNRv4_opt", "IMRPhenomD", "TaylorT4"

- Use these approximant names exactly as written; do not substitute near-matches such as `SEOBNRv4` for `SEOBNRv4_opt`.
- Before the full search, verify that each requested approximant is actually available in the installed PyCBC/LAL environment.

Mass grid: mass1 and mass2 from 10 to 40 solar masses (integer steps)

- Treat the listed approximants and mass grid as fixed task requirements: run the full Cartesian grid for `mass1=10..40` and `mass2=10..40` in integer steps for every listed approximant.
- Benchmarking or smoke-test subsets are encouraged for feasibility, but they are not a substitute for the required final search unless the task explicitly allows approximation.
- Do **not** reduce coverage with coarser mass steps, narrowed windows, or `m2 <= m1` shortcuts just to reduce runtime.
- Do **not** substitute different waveform models if one is unavailable or errors; report that blocker explicitly rather than relabeling another model's result.


## Process

1. Validate data loading first with a minimal script that reads `/root/data/PyCBC_T2_2.gwf` from `H1:TEST-STRAIN` successfully.
2. Build one faithful serial baseline pipeline using PyCBC: condition detector data (whiten, bandpass), generate templates, and run matched filtering end-to-end on a tiny subset.
3. Before the full sweep, benchmark a small representative subset (for example, one approximant and a few mass pairs) to estimate runtime and confirm progress/logging and CSV-writing behavior.
4. Reuse conditioned strain data and PSD where possible instead of recomputing preprocessing inside the mass-grid loop.
5. Run the full required search over all listed approximants and the full integer mass grid, keeping one stable implementation path rather than repeatedly restarting with unvalidated changes.
6. If runtime is high, use batching, checkpointing, or per-approximant execution that still preserves the required final search and supports a final merge.
7. Extract the strongest signal (highest SNR) per approximant.
8. Write `/root/detection_results.csv` with the final best row for each approximant.
9. Finish only after directly verifying the CSV exists, is non-empty, and contains the intended final rows.


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

## Output Format

CSV at `/root/detection_results.csv`.


- Write the final file to exactly `/root/detection_results.csv`.
- Required columns: `approximant,snr,total_mass`.
- Include exactly one strongest-signal row for each required approximant: `SEOBNRv4_opt`, `IMRPhenomD`, and `TaylorT4`.
- Include one final strongest-signal row per approximant only after that approximant's search has completed.
- Temporary files, logs, or partial outputs are not substitutes for the required final CSV.
- Before finishing, verify `/root/detection_results.csv` exists, is readable, and is non-empty.


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
- Read [Runtime Search Guide](references/runtime-search.md) when the template sweep may be expensive.




## Tips

## Failure Handling

- Do not use broad `except Exception: continue` inside the mass-grid loop without surfacing diagnostics.
- Record representative errors per approximant and count failed vs. successful templates.
- Treat "no successful templates for an approximant" as a blocking error to debug, not a completed search result.
- Only write the final CSV after the search completes and diagnostics have been checked.

## Preflight Checks

## Implementation Guardrails

- Use PyCBC's built-in conditioning and matched-filter primitives as the default correctness baseline.
- Do **not** replace `matched_filter` with a custom FFT/SNR implementation for final results unless you first show numerical agreement with PyCBC on the same data/template within a small tolerance.
- Do **not** introduce empirical calibration or scale factors to force SNR agreement; fix normalization or API usage directly.
- Optimize only after a correct end-to-end baseline exists.


## Implementation Guardrails

## Runtime-Safe Execution

- Build one correct baseline pipeline first; avoid repeated script churn while a valid run is in progress.
- If you create or patch a script, validate it before expensive execution: inspect the written file and run a quick syntax/import check.
- Prefer the simplest validated execution path and staged scaling: verify one approximant and a very small mass subset first, then expand.
- Treat this as a potentially long-running computation: add progress logging, checkpoints, or partial-result writes rather than assuming quiet stdout means failure.
- Do not interrupt or restart a run merely because it is slow; stop only with concrete evidence of failure such as an exception, invalid configuration, deadlock, or invalid output state.
- If computation must be split into batches because of runtime limits, track completion carefully and merge results into one final CSV.
