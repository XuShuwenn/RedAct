---
name: gravitational-wave-detection
description: "Detect gravitational wave signals from binary black hole mergers using matched filtering with PyCBC."
---

# Gravitational Wave Detection with Matched Filtering

## When to Use

- Detect gravitational wave signals from LIGO/Virgo data
- Perform matched filtering with waveform templates
- Search for binary black hole merger signals


## New Section

## Environment / Tool Protocol

- Use only the tool interface explicitly provided by the current environment or system prompt, and use its required syntax exactly.
- Do **not** invent or assume extra tools for job control, monitoring, or completion signaling.
- Express every execution step as a concrete runnable shell/Python command supported by the available interface; do not emit pseudo-tool wrappers or natural-language placeholders.
- If you background a run, monitor and complete it using the same documented interface plus file/log inspection; do not stop at "job started".
- Do not treat background-job launch or status checks as completion. Finish only after reading the produced artifacts, especially `/root/detection_results.csv`, and then follow the environment's required completion protocol exactly.
## Input Data

- `/root/data/PyCBC_T2_2.gwf`: Detector data in channel `H1:TEST-STRAIN`

- Read the `.gwf` frame with PyCBC frame I/O (for example `pycbc.frame.read_frame(...)`). Do **not** assume a generic time-series reader exists in `pycbc.types`.
- Before building the full search pipeline, run a tiny smoke test that opens `/root/data/PyCBC_T2_2.gwf` and confirms `H1:TEST-STRAIN` can be read successfully in this environment.

- In that smoke test, verify the exact import path you will use (for example, `from pycbc import frame` then `frame.read_frame(...)`) before embedding it in the main script.
- Do not write the full search script until this import-and-read probe succeeds without `ImportError` or attribute errors.

- Treat import validation as a hard gate: before drafting the main script, run a minimal Python probe that imports the exact PyCBC symbols you plan to use and successfully exercises the key read path on `/root/data/PyCBC_T2_2.gwf`.
- Before coding against any PyCBC function you have not already exercised in this session, run a minimal probe from the exact module path you plan to use.
- Do **not** guess near-match entry points such as `pycbc.types.read_timeseries`; if the probe fails, inspect the installed package and switch to the verified import path before writing the main script.

- Treat lookalike import names as untrusted until exercised. If you are about to use a symbol resembling a remembered API path, first run a tiny Python probe that imports that exact symbol and performs the intended call.


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
- Treat the requested approximant name as the executed model identity. Do **not** create alias maps such as `requested_name -> substitute_approximant` for the final search.
- Wrong: run `SEOBNRv4` (or any other model) and write the row as `SEOBNRv4_opt`.
- Right: either run `SEOBNRv4_opt` successfully and label it `SEOBNRv4_opt`, or stop and report that `SEOBNRv4_opt` is unavailable in this environment.
- Do **not** write a CSV row for an approximant unless that exact approximant produced at least one successful matched-filter result.


## Process

0. Before touching data or writing code, restate the concrete task contract to yourself: required input file/channel, fixed approximants, full mass grid, exact output path/schema, and completion criteria. Do not commit to a workflow until these are explicit.

0a. Make that restatement operational before proceeding: enumerate the exact input path/channel, required approximants, full `mass1=10..40`, `mass2=10..40` coverage, final CSV path/schema, and what counts as completion; choose the implementation path only after this is explicit.
0b. Treat the agent/runtime protocol as part of the contract too: if the environment requires exact tool-call syntax or a specific final completion token, follow that protocol exactly.
0c. Do **not** start with generic environment or process discovery. First ground yourself in the visible task artifacts and required deliverable.
0d. Before editing an existing script, reread the current file contents and patch real source text that actually exists in the file. Do **not** make blind replacements against invented labels or remembered blocks.

1. Validate data loading first with a minimal script that reads `/root/data/PyCBC_T2_2.gwf` from `H1:TEST-STRAIN` successfully.
2. Build one faithful serial baseline pipeline using PyCBC: condition detector data (whiten, bandpass), generate templates, and run matched filtering end-to-end on a tiny subset.

- Prefer one reproducible Python script that performs the full workflow end-to-end: read frame data, condition strain, estimate PSD, run the template search, and write the final CSV.
- Keep that single end-to-end script as the authoritative workflow once it passes the pilot; prefer patching the same script over splitting the pipeline across ad hoc commands or multiple partially overlapping scripts unless a validated batch/checkpoint boundary is truly needed.
- In that baseline, use standard detector-data conditioning before matched filtering (for example: highpass/bandpass as appropriate, resample if needed, and crop filter transients before PSD/matched-filter steps).

3. Before the full sweep, benchmark a small representative subset (for example, one approximant and a few mass pairs) to estimate runtime and confirm progress/logging and CSV-writing behavior.
3aa. Defer process-management debugging until after this bounded trial exists. Do not spend early turns checking monitor/kill/process utilities before you have a working micro-run, an executable script, or a validated partial artifact.
3a. Do not start the full `(approximant, mass1, mass2)` sweep until one complete end-to-end trial has succeeded for at least one approximant and one mass pair, has produced a non-trivial interpretable SNR, and has emitted useful diagnostics.
3b. Turn that pilot into an explicit execution plan before launching the full search: estimate the rough full-grid runtime, decide whether to stay serial or split by approximant/batch, and define how intermediate best-per-approximant results will be checkpointed and merged into `/root/detection_results.csv`.
3c. If the estimate is too large for the remaining session budget, switch immediately to a resumable plan instead of launching the monolithic full sweep and later aborting it.
3c.i. Define that resumable plan explicitly before launching: choose the batch boundaries up front (for example by approximant or fixed mass ranges), decide the checkpoint file(s), and state exactly how completed batches will be merged so the entire required grid can finish without ad hoc reruns after each timeout.
3c.ii. Prefer resumable **foreground** batches first because they provide direct progress and are easier to verify than silent background jobs.
3c.iii. If a pilot or full run hits the environment timeout, do **not** respond with logging-only changes or a broad rewrite. Use the last completed stage/log line to localize the stall, reduce the execution unit to a bounded batch, checkpoint results, and define the merge step to `/root/detection_results.csv`.
3c.iii.a. After one or two unchanged progress checks, do not keep waiting or just rereading the same logs. If observed throughput implies the remaining required coverage will not finish in time, stop polling and change the plan.
3c.iii.b. Do not equate better observability with a runtime fix: extra logs, separate log files, or more frequent polling are diagnostic aids only unless they accompany a bounded execution plan that can actually finish.

3c.iv. Do not respond to repeated timeouts by manually shrinking and rerunning arbitrary subranges one at a time without an overall completion plan; convert immediately to a systematic partition with durable progress tracking.
3c.v. After the first full-run timeout or stall, do not relaunch a near-identical monolithic sweep. Immediately reduce the execution unit to the smallest meaningful foreground chunk, prove one chunk completes and writes a readable checkpoint/result artifact, then use that chunked pattern for the remaining coverage.
3c.vi. Once you decide to batch, declare the full batch ledger up front, including all required approximants and mass blocks, mark batches complete only after their checkpoint exists, and define the exact merge rule to `/root/detection_results.csv` before further launches.
3c.vii. If a run remains in startup or the first approximant after more than one check and no checkpoint/final CSV has appeared, stop passive polling and auxiliary monitor jobs. Change the computation plan to a smaller foreground chunk with flushed mid-loop progress and a durable artifact.
3c.viii. Before relying on process-control or monitoring commands in a restricted shell, verify they actually exist here. If commands such as `ps`, `pgrep`, or `pkill` are unavailable, use synchronous foreground chunks plus file/log/checkpoint inspection instead.

3d. If you write or edit a Python script, inspect the saved file and run a quick syntax/import smoke test before launching any expensive search.
3d.i. After writing a script, read back the exact saved file and confirm it is actual executable Python source, not prose, TODO text, placeholders, omitted sections, or malformed/truncated output.
3d.i.a. Treat any write/edit step as incomplete until you have inspected the saved file contents and verified it contains a full runnable program from imports through output writing.
3d.i.b. Reject the file immediately if it reads like a natural-language summary of intended steps rather than concrete Python syntax. Do not execute or patch further until a real program is present on disk.

3d.ii. Confirm the executed file still contains the intended control flow, required approximants, full mass-grid coverage, output path, and merge logic; do not trust patch operations alone without inspection.
3d.iii. Minimum pre-launch gate for any new or edited script: inspect the saved file, run `python -m py_compile <script>` or equivalent syntax/import validation, then execute one tiny foreground end-to-end case using that exact saved script path.
3d.iii.a. Make edits against exact source text read from the file, not descriptive placeholders such as `previous block` or `update logging here`.
3d.iii.b. After editing, reread the changed region and enough surrounding code to confirm the intended logic is present in the saved file before any expensive run.
3d.iii.c. On inspection, verify the file is real code end-to-end: no placeholder prose, no failed replacement markers, no omitted sections, and no accidental narrowing of required approximants or mass coverage before you trust it for a long run.

3d.iv. Do **not** background, parallelize, or batch-launch the search until that exact saved script has passed the bounded foreground validation.
3d.v. If inspection shows truncation, placeholder text, partial definitions, an unexpectedly short file, or missing imports/function bodies, stop and restore the last known-good script before making further changes.
3d.vi. When launching a long or background run, capture stdout/stderr to a concrete log file from the start and record the exact executed script path/command so you can verify later that the intended version is the one running.

3e. Instrument the pilot with explicit stage logs around waveform generation, PSD estimation, and matched filtering so a later stall can be localized quickly.
3e.a. On the first real run, inspect the emitted logs and confirm they show the intended pipeline stages in order (for example: frame load, conditioning, PSD, waveform generation, matched filtering, CSV/checkpoint write) before trusting downstream results.
3e.i. Make the pilot emit progress inside the search loop as well, such as current approximant, current `(mass1, mass2)`, success/failure counts, and current best SNR.
3e.ii. Do not launch a long run that only logs at startup or once per approximant; require observable progress at template or small-batch granularity.
3e.iii. If a pilot or full run is slow or times out, diagnose the bottleneck first on a bounded case with stage timing so you know whether frame I/O, conditioning, PSD estimation, waveform generation, or matched filtering is dominant.
3e.iv. Before changing search structure, conditioning, or execution mode for performance reasons, capture at least one concrete timing or stage-localization signal from the current pipeline. Do **not** speculate about the bottleneck.
3e.v. Distinguish `slow`, `silent`, and `failed`: if a run is still alive and emitting plausible stage or loop progress, do **not** stop it just because it is slow. Either let that validated run continue, or pivot only after comparing observed throughput against the remaining budget.
3e.vi. After any timeout, follow this recovery loop before broader changes: inspect the last completed stage/log line, rerun one materially smaller bounded case that reproduces or localizes the slowdown, make one targeted change tied to that evidence, rerun the updated script or chunk immediately, and verify a completed checkpoint or `/root/detection_results.csv` artifact.
3e.vii. The first retry after a broad timeout must materially reduce execution scope and must complete a readable chunk artifact; added logging alone is not an adequate retry strategy.
3e.viii. Do **not** infer that a silent run is 'just buffering' from empty logs alone. First inspect the exact saved script, captured logs, exit/error output, or a bounded foreground rerun.

3f. Once one baseline path works, keep that implementation stable and scale it up; do not repeatedly rewrite core search logic unless a concrete observed failure requires a fix.
3f.i. After the first bounded end-to-end case succeeds, freeze the core scientific path: approximants, conditioning/filter settings, waveform domain choice, and matched-filter interface. Optimize execution structure around that baseline rather than changing analysis-defining parameters for speed.
3f.ii. If a bounded run or chunk is already producing valid checkpoints or steady template-count progress, treat that path as the production path. Do not stop it merely because it is slow; only pivot for a concrete blocker such as a reproducible exception, invalid output, or a runtime estimate that clearly prevents completion.

3g. After the pilot, record an observed throughput estimate such as templates/minute or seconds/template and use it to project full-grid wall time before any full launch.
3g.i. Base that estimate on completed template evaluations or a finished bounded batch, not on startup timing alone.
3g.ii. Convert that throughput into an explicit go/no-go check for the true required workload: `3 approximants x 31 x 31 = 2883` template evaluations. If the projected wall time is not comfortably within the remaining session budget, do **not** launch the full sweep unchanged.
3g.iii. Treat any claimed optimization as unproven until a bounded rerun shows improved observed throughput or a smaller required workload. Splitting by approximant, backgrounding, or multiprocessing does **not** by itself make the task more feasible.
3g.iv. After two interrupted, aborted, or timed-out attempts at the same broad search stage, treat the current plan as disproven and switch to a different bounded resumable structure rather than rerunning essentially the same command.

3h. Do **not** launch the full required sweep if that estimate is clearly incompatible with the remaining session budget; switch immediately to a resumable batch or per-approximant plan that still preserves the required search.
3i. When invoking shell or Python execution, use only concrete runnable commands or exact script paths. Do **not** send prose placeholders such as `run a quick check` or `python script to ...` to the shell.
3i.i. Every execution or monitoring step must be a literal command that could be pasted and run as-is: include the exact interpreter, script path, filenames, and any arguments. Do **not** use ellipses, descriptive stand-ins, or pseudo-commands.
3i.ii. If shell utilities are restricted or uncertain, use short concrete Python commands to inspect known file paths and print their contents/status; never substitute a descriptive phrase for an executable command.

3j. Keep one validated baseline pipeline authoritative. Prefer targeted fixes over full rewrites, and after any fix rerun the smallest case that exercises that exact change before broader scaling.
4. Reuse conditioned strain data and PSD where possible instead of recomputing preprocessing inside the mass-grid loop.
4a. If you split work by approximant or batch, compute frame loading, conditioning, and PSD estimation once and reuse or persist those shared artifacts; do not repeat identical preprocessing in each worker unless you have confirmed it is negligible.
5. Run the full required search over all listed approximants and the full integer mass grid, keeping one stable implementation path rather than repeatedly restarting with unvalidated changes.
   - If a simple serial or batched baseline is already producing valid progress, prefer letting it finish or resuming from its checkpoints rather than replacing it with an unproven rewrite.
6. If runtime is high, use batching, checkpointing, or per-approximant execution that still preserves the required final search and supports a final merge.
6a. If you split execution by mass range or approximant, maintain an explicit completion checklist covering all 3 approximants and the full `mass1=10..40`, `mass2=10..40` grid.
6b. If you write intermediate per-batch files, execute a final consolidation step that reads all completed batches, selects the highest-SNR result per approximant, and writes exactly `/root/detection_results.csv` with the required schema.
6c. Do not consider the task complete while results exist only in batch-specific files such as per-range or per-approximant CSVs.
6d. Do not treat partial console output, sparse logs, timeouts, or truncated captures as finished results; confirm completion from explicit artifacts, checkpoint contents, or exit evidence before proceeding.
6d.i. If stdout/stderr is truncated or ends mid-search, stop and inspect the underlying log, checkpoint, or final CSV before launching new runs or marking coverage complete.
6d.ii. Do not treat a partial `New best ...` line, startup banner, unreadable log, or cut-off progress snippet as evidence that the batch finished; retrieve the durable output and confirm the end-of-batch summary or written artifact.

6e. If a simple serial or batched baseline is showing real progress, prefer completing or resuming that path rather than replacing it with multiprocessing for speculative speedups.
6f. If a new execution mode shows only repeated startup or initialization lines without real progress on more than one check, stop using that mode and diagnose it on a tiny batch or revert to the last validated baseline.
6f.i. Treat repeated startup-only logs in multiprocessing/background mode as a hard warning of launch or worker-entrypoint failure. Check the exact executed script path, `if __name__ == "__main__":` protection where relevant, and whether workers emit per-batch progress before trusting that mode.
6f.ii. If two checks still show only initialization lines and no completed templates or chunks, revert to the last validated serial or simple batched implementation instead of redesigning again.

6g. If the same full-search approach times out twice or stalls twice at the same stage, stop relaunching that monolithic plan. Switch to a clearly bounded resumable strategy with checkpoints.
6h. Treat splitting, backgrounding, or multiprocessing honestly: they are not runtime fixes unless measured throughput or total completion time actually improves.
6i. Do **not** use parallelism as the first response to a timed-out brute-force sweep. First prove that one bounded serial chunk completes within budget and measure its throughput; only then consider parallel execution of the same validated chunk pattern.
6j. If a run is showing real template-level or batch-level progress and outputs remain plausible, prefer letting it finish or checkpoint naturally. Do **not** kill and restart it based only on liveness polling or impatience.

7. Extract the strongest signal (highest SNR) per approximant.
   - During the sweep, keep only online best-so-far values per approximant unless detailed per-template output is explicitly required.
8. Write `/root/detection_results.csv` with the final best row for each approximant.
9. Finish only after directly verifying the CSV exists, is non-empty, and contains the intended final rows.
9a. Treat `/root/detection_results.csv` as the completion artifact: explicitly list/read it after execution and verify plausible contents before declaring progress or success.
9b. Empty files, missing files, stale files from earlier attempts, logs, or background-job status are **not** evidence that the task is complete.
10. If a script was written or patched for the search, actually execute it (or equivalent commands) and inspect its outputs; do not stop at code drafting or an unexecuted fix.
10a. After any bug fix or import-path change, rerun the updated script or the smallest affected pipeline stage immediately and inspect the new output or error before moving on.
10a.i. For import/API fixes specifically, rerun the exact saved script or a minimal executable probe that uses the corrected import path on the real frame file before doing anything else.
10b. Do **not** treat "edited the file" or "found the fix" as progress toward completion; a repair only counts after the updated code has been executed and validated.
10c. After any timeout-driven rewrite or bug fix, the very next step must be execution of the edited script on the smallest representative affected case and inspection of its output, traceback, or written artifact before any further redesign.
10d. Once one bounded execution path has produced a real matched-filter result for a required approximant, stop redesigning the workflow unless a new concrete blocker appears. Use that same validated path to complete the remaining approximants/batches, merge results, and finish the final CSV verification.

11. Use an explicit completion checklist before finishing: data read succeeded, conditioning and matched filtering ran, the full required search completed, one strongest row was selected for each approximant, and `/root/detection_results.csv` was verified on disk.
11a. Keep a live coverage checklist during execution listing every required approximant and each planned batch/range; do not stop while any item remains incomplete.
11b. Do not treat "remaining ranges will be run later" as acceptable progress. Finish only after all planned batches have been executed, merged, and verified in the final CSV.
11c. Before any final response, compare the live coverage ledger against the required task contract and verify there are no unchecked approximants or mass blocks. Do not end on a statement like 'remaining ranges will be run later'; if anything is unfinished, continue executing or explicitly report the blocker.
11d. Finish with the required explicit completion signal only after the final CSV has been read back and verified; do not end on running/monitoring status alone.


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

- Verify conditioning APIs against the installed PyCBC version before coding them. In particular, do **not** assume preprocessing helpers are `TimeSeries` instance methods; check whether operations such as highpass/bandpass/resampling are standalone PyCBC functions in this environment.
- On the smoke test, print `type(strain)` and inspect the exact callable you will use for conditioning/resampling before embedding it in the main script.
- If uncertain about a conditioning call, write and run a 5-10 line probe that exercises that exact API on a tiny data slice first; do not discover `AttributeError` only after wiring the full pipeline.
- Before scaling up, print and compare the exact metadata that `matched_filter` requires to agree: representation, length, and spacing (`delta_t` for time-domain or `delta_f` for frequency-domain) for template, strain, and PSD. If these do not match, stop and fix the pipeline before the full sweep.
- Do **not** resize or pad a template in a way that silently changes its `delta_f`/`delta_t` relative to the strain or PSD and then continue. Regenerate or transform objects so the final inputs share the same expected representation and spacing on a bounded test first.
- Probe required approximant support in the exact generation path you will use for the real search, such as TD vs FD generation. Do **not** assume support in one mode implies support in another.
- Treat repeated `Ringdown frequency > Nyquist frequency` / `Input domain error` failures as a hard stop on that configuration. Do not keep the broad sweep running with `except ...: continue`; first reproduce the error on one mass pair, then adjust sampling / frequency settings or otherwise verify a compatible generation path on that bounded case.
- Do not introduce representation changes merely because the baseline is slow. First prove on one tiny end-to-end case that the modified interface returns a valid matched-filter result and preserves the intended search definition.
- If the environment cancels jobs after several minutes without stdout/stderr output, treat that as a hard execution constraint from the start: require flushed mid-loop progress and favor chunked resumable execution.
- Verify version-sensitive PyCBC calls you plan to rely on, including resampling, PSD estimation, and conditioning APIs, on a tiny probe before writing the full script.
- Read [Timeout-Safe Execution](references/timeout-safe-execution.md) when the environment has no-output time limits or after any timeout/cancellation.

- Treat representation compatibility as a hard gate before any broad sweep: on one bounded case, print and compare `template.delta_f`/`delta_t`, `strain.delta_f`/`delta_t` (as applicable), PSD spacing, and lengths immediately before `matched_filter`.
- If any resize, pad, crop, FFT, or domain-conversion step changes those invariants, stop and fix that exact path first; do **not** continue into the mass grid with near-matching values.
- Probe required approximant support in the exact generation mode and configuration you intend to use in the real search, such as TD vs FD plus the planned sampling and frequency settings. If one mode fails for a required approximant, either switch to a validated compatible path or stop and report the blocker clearly.
- For PSD estimation, do not assume a `TimeSeries.psd(...)` signature from memory. Probe the exact installed API you will use on a tiny strain slice first, verify whether parameters such as `seg_len` and `seg_stride` are positional or keyword arguments, and print the resulting object type/length.
- If the same approximant or configuration hits `Ringdown frequency > Nyquist frequency` or `Input domain error` more than once, treat that exact generation path as unvalidated and stop the broad sweep. Reproduce it on one mass pair, then explicitly adjust sampling or frequency settings and prove the corrected path works before restoring that approximant to any larger batch.
- Do **not** handle repeated waveform-domain failures with broad `except ...: continue` across the full grid; first establish one successful bounded waveform-generation plus matched-filter case for that approximant under the intended final settings.
- On that bounded end-to-end test, also verify the exact peak-extraction logic you will use in the final search: crop filter-corrupted edges first, convert the matched-filter SNR series to a NumPy array, take `np.abs(...)`, and select the maximum with `np.argmax(...)`.
- On that API probe, inspect the exact module path and callable name you will use for each conditioning step before writing `condition_data`; do **not** encode guessed instance-method calls and discover `AttributeError` only in the full script.
- For the required end-to-end micro-run, prefer using the same saved script entry point you plan to use for production, configured for one approximant and one or a few mass pairs. This confirms the actual executable file works end-to-end.
- After any observed no-output timeout or waveform-domain/configuration fix, forbid yourself from relaunching the broad search unchanged. First execute and verify one smaller chunk or exact bounded template case that proves the new progress-printing/checkpoint or generation path works.

## Output Format

CSV at `/root/detection_results.csv`.


- Write the final file to exactly `/root/detection_results.csv`.
- Required columns: `approximant,snr,total_mass`.
- Include exactly one strongest-signal row for each required approximant: `SEOBNRv4_opt`, `IMRPhenomD`, and `TaylorT4`.
- Before writing each final row, verify the approximant string came from the actual successful waveform-generation/matched-filter call for that row, not from a requested-name placeholder or fallback label.
- Include one final strongest-signal row per approximant only after that approximant's search has completed.
- Temporary files, logs, or partial outputs are not substitutes for the required final CSV.
- If execution is split into batches, persist durable intermediate best rows/checkpoints and then merge them into the final CSV.
- Do not spend the session only rewriting or benchmarking scripts; each major execution step should move toward producing or completing `/root/detection_results.csv`.
- Before finishing, verify `/root/detection_results.csv` exists, is readable, and is non-empty.
- Read the file back and confirm the header is exactly `approximant,snr,total_mass` and that there are exactly three final rows, one for each required approximant.
- Treat the contents of the read-back CSV as the authoritative final result source for any reported values; prefer quoting/parsing the artifact over reconstructing values from logs, memory, or intermediate console output.
- Do not conclude from logs, background-task status, a launched process, a running job, or a "script completed" message alone; direct inspection of the final CSV is required.
- Do not treat partial logs, startup banners, unreadable/binary/truncated logs, or one visible progress line as evidence that the run succeeded, failed, or stopped. Verify with concrete artifacts: current log tail, checkpoint contents if used, command exit evidence, and the final CSV.
- Final completion sequence: ensure the producing command has actually finished, read back `/root/detection_results.csv`, confirm the exact header `approximant,snr,total_mass`, and confirm there are exactly three rows for the required approximants before declaring completion.

- After the search starts, compare early console/log output against the intended configuration; do not let a long run continue if the printed approximant names or executed script path differ from the intended setup.

- Treat the task as incomplete until you have directly opened or read back `/root/detection_results.csv` and confirmed it contains the final rows; intending to write it later is not enough.
- If a previous run was stopped, crashed, or superseded by a rewrite, re-check whether a valid final CSV was ever produced before continuing.
- Before finishing, perform an explicit final verification sequence: confirm the producing command finished, list/read `/root/detection_results.csv`, check it is non-empty, confirm the header is exactly `approximant,snr,total_mass`, and confirm there are exactly three final rows for the required approximants.
- Minimum final check should use concrete artifact reads, not inference: run an exact command to list the file, then an exact command or Python snippet to print/read its contents and verify the three required approximant rows.
- If those concrete checks have not been run successfully in this session, do not describe the task as complete, nearly complete, or successfully processing.
- If higher-level instructions require an exact completion sentinel or final-response format, obey it exactly and with no extra prose.
- Do not rely on pilot success, launched jobs, background-job status, logs, or partial per-approximant outputs as evidence of completion; the final CSV inspection is the authoritative success check.


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

- Read [Execution Stability and Refactor Checks](references/execution-stability.md) when deciding whether to keep a slow run going, split a workflow, or add intermediate saved artifacts.
- Read [Script Editing Safety](references/script-editing-safety.md) when you are repeatedly patching the search script or recovering from a suspicious/truncated rewrite.
- In restricted shells, monitor long runs through Python/file-based methods you know exist here (logs, checkpoint files, CSV snapshots) rather than relying on commands like `ps` or `pgrep`.

- Read [Run Control and Completion](references/run-control-and-completion.md) when deciding whether to kill/restart a run, when monitoring is replacing real progress, or when you need to turn partial coverage into the final verified artifact and completion signal.



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

- If the failure was an import or missing-API error, rerun first with a minimal command that exercises that exact import/call path, then rerun the broader script once the probe passes.
- If a run's console output is truncated, incomplete, or suspicious, capture the full log to a file and inspect that log before diagnosing the failure cause.
- Base bug fixes on concrete runtime evidence: identify the exact traceback, warning, or bad output row first, then patch the specific code region responsible.
- When debugging, use only concrete executable commands; do **not** issue natural-language pseudo-commands.
- Prefer Python-based inspection when shell utilities may be unavailable; for example, use short Python one-liners to read log files, inspect `/root/detection_results.csv`, or check whether output files are non-empty.
- Do not rerun the same script repeatedly without first confirming what code was written and what error the previous execution produced.
- After any patch, reread the changed file and rerun a bounded validation case to confirm the fix actually executes.

- If the saved script contains prose, placeholder sections, malformed imports, or undefined symbols, treat it as a blocker and repair it before any further execution.
- If a diagnostic command fails because a utility is unavailable, switch immediately to a Python or file-based equivalent rather than proceeding on incomplete evidence.
- Treat binary, unreadable, or truncated output as no evidence of progress. Check concrete artifacts directly: the exact script file, plain-text logs, checkpoint files, or `/root/detection_results.csv`.
- If you have checked a long-running job a few times and it still has not produced the required artifact, stop treating monitoring as progress. Either verify a bounded chunk is still making observable forward progress toward a checkpoint, or pivot to a resumable chunk that will complete within the environment limits.
- If a shell utility is missing once, adapt immediately to environment-compatible inspection methods instead of trying nearby commands by analogy. Prefer Python/file-based checks, `/proc` if available, and captured logs over repeated unavailable-tool attempts.
- When a run seems stalled, first verify three things before waiting longer: the exact script file on disk is the intended version, the launched command references that file, and stdout/stderr logs show recent progress or a concrete failure.
- Ground every diagnosis in concrete artifacts: actual traceback text, exact saved script contents, explicit log lines, or direct file reads. Do **not** infer state from imagined command output or placeholder monitoring steps.
- If console output is truncated or ambiguous, capture and inspect the full log before deciding what failed.
- When patching a script, make concrete code edits tied to exact observed failures. Do not use content-free placeholder replacements.
- If a run is merely slow or times out, do not optimize by guesswork. First capture the last completed stage, traceback, timing output, or representative log lines from a bounded rerun, then change only the demonstrated bottleneck.
- After a timeout or bug fix, do not stop at rewriting the script. Inspect the saved file if it changed, rerun a bounded validation or resumed chunk, and confirm the new execution produces observable output before proceeding.
- If background logs stay empty or uninformative across more than one check, abandon that monitoring path quickly and return to a bounded foreground run that produces direct progress and checkpoint evidence.
- Treat repeated exact-approximant unavailability messages or repeated key API signature/type errors as hard blockers. Reduce to a minimal reproducer for that exact call/path, fix it there, and only then return to the full pipeline; do not keep unsupported approximants in broad runs.


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

- Do **not** write conditioning code from memory with assumed instance methods unless you have just verified those attributes exist in this installed version.
- Prefer a verified pattern: import the relevant PyCBC conditioning/resampling utility explicitly, run it on a tiny strain object, then reuse that exact call in the full script.
- If a preprocessing API fails once with `AttributeError`, stop and inspect the installed object/functions immediately; do not keep patching by analogy and rerunning the full script.


## Implementation Guardrails

## Runtime-Safe Execution

- Build one correct baseline pipeline first; avoid repeated script churn while a valid run is in progress.
- If you create or patch a script, validate it before expensive execution: inspect the written file and run a quick syntax/import check.
- Prefer the simplest validated execution path and staged scaling: verify one approximant and a very small mass subset first, then expand.
- Treat this as a potentially long-running computation: add progress logging, checkpoints, or partial-result writes rather than assuming quiet stdout means failure.
- Do not interrupt or restart a run merely because it is slow; stop only with concrete evidence of failure such as an exception, invalid configuration, deadlock, or invalid output state.
- If computation must be split into batches because of runtime limits, track completion carefully and merge results into one final CSV.
