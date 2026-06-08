---
name: glm-lake-mendota
description: "Run General Lake Model (GLM) to simulate vertical water temperature with RMSE < 2 degrees Celsius against observations."
---

# General Lake Model (GLM) Simulation

## When to Use

- Simulate vertical water temperature in lakes
- Calibrate lake models against field observations
- Run GLM (General Lake Model) for water quality modeling

## Required Execution Protocol

- Before any tool use, read the task prompt for the exact execution interface and completion signal, then use that format exactly for every action.
- Do not substitute other tool-call styles, wrappers, or unsupported helper commands if the task requires a specific `Action` schema, JSON call structure, or `Thought` + `Action` pattern.
- Do not emit the completion signal until the final GLM run and RMSE verification are finished.
- If the environment requires `Thought:` then `Action:` with a JSON object, use exactly that format for every executable step; do not switch to XML-like tool tags, pseudo-tool wrappers, unsupported helper actions, or informal command narration.
- If the environment specifies an exact completion string such as `ACTION: TASK_COMPLETE`, emit that exact string only after all required runs, verification, and RMSE checks are complete.
- Every executable step must contain a literal runnable command, script path, or inline script body. Do not use natural-language placeholders like `run calibration script`, `inspect output`, or `update the configuration` in place of a real command.
- Treat empty, quiet, or truncated tool output as unknown status, not success: verify with the direct return code, file freshness, log contents, or an explicit metric before proceeding.

- Emit only concrete executable actions/commands, and use only tools and action formats explicitly allowed by the task.
- Send only executable shell commands to shell/bash tools.
- Before relying on a script, verify the interpreter/runtime you plan to use exists in this environment and that required input files are present at the exact `/root/...` paths.
- If you create a helper script, write the actual script body to a file, then read it back or syntax-check it before running it; do not summarize the script in prose or rely on unwritten or unchecked code.

## Input Files

- `/root/bcs/`: Meteorological and hydrological forcing data
- `/root/field_temp_oxy.csv`: Field water temperature observations
- `/root/glm3.nml`: GLM configuration file

**Use these exact absolute paths consistently in every command and script. Do not switch to relative paths like `output/output.nc`, `glm3.nml`, or `field_temp_oxy.csv` when the task specifies `/root/...` locations.**

## Output

- Simulation output: `/root/output/output.nc`
- Target: RMSE < 2°C between simulation and observation
- Simulation period: 2009-01-01 to 2015-12-30

## Key Steps

1. Load forcing data from `/root/bcs/`
2. Load field observations from CSV
3. Configure GLM parameters in `glm3.nml`
4. Run simulation
5. Calculate RMSE against observations
6. Adjust parameters if RMSE > 2°C


7. Inspect `glm3.nml` and `output.nc` metadata before scoring so your RMSE method matches the real variable names, time units/origin, depth structure, and simulation period.
7a. Build one reusable deterministic evaluation script or command sequence early, then use that same scoring pipeline for the baseline and every calibration trial.
7a1. If you create or rewrite an evaluation or calibration script, immediately read it back or print the key sections before executing it; verify the real code contains the intended paths, variable names, date handling, parameter edits, and output locations.
7a2. Do not rely on a script whose contents you have only described in prose or assumed were written correctly.
7b. Inspect `/root/field_temp_oxy.csv` header and sample rows early, then compute RMSE by aligning simulation and observations on shared `datetime` and depth bins: read the real NetCDF time units/origin and variable names, convert GLM layer structure into physical depths comparable to the observations, standardize depths only to the observation resolution if needed, handle duplicate time-depth pairs consistently, and score only matched pairs rather than index-aligned arrays.
7c. Do this before trusting any custom RMSE script: do not hard-code start dates, lake depth, array indexing, or assumed coordinate names without confirming them from the actual files.
8. Start with a baseline run and baseline RMSE before changing parameters.
8a. Make the baseline measurable, not implied: run a concrete command or script that reads `/root/output/output.nc`, aligns it with `/root/field_temp_oxy.csv`, and prints the baseline RMSE before proposing any parameter edits.
8b. If you need automation, first create the evaluator or calibration script as a real file, inspect it briefly, and then call it by path; never use a placeholder shell command that only describes intended work.
9. After the first successful baseline run, keep that run and its RMSE as the calibration baseline; if the baseline RMSE is already close to 2°C, inspect signed bias or residual structure by depth/time so you can choose the next parameter change direction.
10. If the baseline RMSE misses the target, convert diagnosis into at least one concrete calibration trial: make a small number of confirmed parameter edits in `/root/glm3.nml`, rerun GLM, and recompute RMSE from the new `/root/output/output.nc`; do not treat analysis alone as progress
10a. Do not stop after bias or error interpretation. Unless the model is currently unrunnable, the next state after diagnosis must be a real trial with persisted `glm3.nml` edits, a completed rerun, and a newly computed RMSE.
10b. Do not stop after launching a calibration or optimization script. Wait for it to finish, inspect whether it actually changed parameters and produced a new run, then recompute RMSE from the resulting fresh `/root/output/output.nc`.
10c. Treat statements like "next I would tune ..." as incomplete until you have actually applied the change, run GLM again, and scored the resulting output..
11. For each calibration trial, restore a known-good baseline `glm3.nml`, apply only that trial's edits, reread or diff the file to confirm the intended parameter change persisted, run GLM, confirm fresh readable `/root/output/output.nc`, and compare the new RMSE against the previous best.
12. Prefer one-parameter or small bounded trials before broad optimization, especially when the baseline RMSE is already close to 2°C; start with physically meaningful high-impact parameters such as light extinction, mixing, wind, or modest `sw_factor`/`lw_factor` adjustments if present.
13. Before any automated search or expensive optimization, validate one complete edit -> run -> verify -> score cycle: confirm the target parameter exists, make one small edit, rerun GLM once, confirm readable fresh `/root/output/output.nc`, and recompute RMSE with the same evaluator.
13a. Do not start with a full optimization when the baseline RMSE is already close to target; first try one or a few small targeted parameter edits or a tiny bounded sweep that you can monitor end to end.
13b. Any longer calibration loop must be instrumented and bounded before you rely on it: emit per-trial logs, cap the number of trials or runtime, and verify that logs, output files, and metrics are actually updating. If logs stay empty or files do not change, stop and switch to a simpler manual or tightly bounded approach.
13c. If an automated calibration attempt stalls, times out, or produces empty logs, do not keep waiting based on guesswork; inspect process state and outputs once, then fall back to explicit short trials.
13d. For a concrete bounded pattern, see [monitorable calibration loops](references/monitorable-calibration-loops.md).
14. If a run stops early or `/root/output/output.nc` does not span 2009-01-01 to 2015-12-30, check both the configured start/stop times in `glm3.nml` and the actual date ranges in the forcing files under `/root/bcs/` before recalibrating.
15. After every run, verify the command exited successfully, `/root/output/output.nc` was regenerated and is readable, and the output covers 2009-01-01 to 2015-12-30 before using the RMSE.
15a. Treat partial-period output as invalid even if the file is readable or the RMSE looks good: confirm the NetCDF time range reaches the required end date before accepting any score or preserving a trial as working.
15b. If a configuration seems promising, preserve that exact runnable `glm3.nml` and verify metric plus full date coverage before replacing it or resetting to another configuration.
16. Treat the task as complete only after a fresh final run with the saved best configuration, `/root/glm3.nml` left in that final best reproducible state, and an explicitly recomputed RMSE < 2°C if claiming the target is met.

17. When a trial improves RMSE, write the winning values back into `/root/glm3.nml`, rerun GLM from that saved file, and recompute RMSE from the fresh output before claiming success.
18. If you expect to test more than a couple of parameter sets, script the full loop (edit `glm3.nml` -> run GLM -> recompute RMSE -> record result) so trials are reproducible and the final saved configuration matches the best-scoring run; see [RMSE alignment and bounded calibration](references/rmse-alignment-and-bounded-calibration.md).

19. If you create any helper script for RMSE or calibration, immediately read it back or print it and verify it contains real executable code, correct absolute paths, and the intended logic before running it.
20. Prefer direct one-off commands or a tiny bounded loop until one full edit -> run -> verify -> score cycle is working; do not start a long unattended calibration process unless it has explicit small bounds, visible per-trial output, and enough time to finish.
21. If you start any background job, treat the task as unfinished until you have waited for completion, checked logs and return status, verified fresh `/root/output/output.nc`, recomputed RMSE, and then emitted the required completion signal.


## Calibration Guardrails

- Once you have a baseline RMSE above target, do not end on a diagnosis-only state; make at least one verified parameter edit and rerun unless the model is currently unrunnable and you are fixing that first.
- Record calibration trials in a simple table or notes block: parameter(s), old value(s), new value(s), run status, RMSE, and current best.
- Keep the RMSE alignment method fixed across calibration trials; reuse one validated RMSE script so improvements reflect parameter changes rather than changed scoring logic.
- When editing parameters programmatically, confirm each target name exists in `/root/glm3.nml` with the expected syntax before relying on text substitution, and inspect the modified file to ensure only the intended value changed.
- Do not score raw GLM layers directly against observations unless they already share the same depth definition; convert or round to the observation depth grid first, then evaluate only matched time-depth pairs.
- Prefer parameters with clear physical influence on thermal structure and mixing before editing many unrelated settings, and use broader multi-run searches only after one full run/evaluation cycle has been proven to work.
- Do not launch background, unconstrained, or open-ended full-model calibration as your primary strategy. Prefer bounded manual trials or a very small grid with explicit run limits and visible per-trial logging; only scale up after one monitored edited run succeeds end to end.
- If a calibration script or optimization run times out, produces no visible per-trial metrics, or leaves ambiguous status, abandon that approach and fall back to a bounded, directly observable workflow; do not keep polling the same opaque background job.
- If a long-running step shows no new logs, no file growth, no updated `/root/output/output.nc`, or no updated metric, treat it as a debugging failure state and switch to a simpler, more monitorable approach.
- When reverting experiments, restore `glm3.nml` from the saved backup or known-good runnable copy; do not reconstruct the full namelist manually from memory or a heredoc.
- If a trial breaks execution, first restore the last verified runnable `glm3.nml`, rerun once to confirm recovery, and only then resume parameter testing.
- Keep the best-found parameter values written in `/root/glm3.nml`, and treat a candidate as the new best only after a rerun from that saved file reproduces the recorded RMSE.

- Diagnosis is not a completion state. After identifying likely causes of error, execute at least one concrete parameter-change trial and recompute RMSE unless you are still restoring basic model runnability.
- Do not describe intended calibration actions as if they were completed; verify the file edit, rerun, and new RMSE before reporting progress.
- Do not convert critical execution steps into prose-only placeholder scripts. Any generated `.py` file must contain visible runnable code and be inspected before execution.
- Before launching any automated calibration script, prove the exact interpreter command works in this environment and that one manual scripted RMSE computation already succeeds end to end.
- Use explicit, inspectable commands for file inspection, GLM runs, RMSE scoring, and parameter edits so each step can be reproduced and debugged from the transcript alone.
- Treat an empty or non-growing calibration log as a failure signal, not as evidence that a long job is still initializing.
- When close to target RMSE, keep a fallback path of manual targeted trials or a very small sweep instead of depending entirely on a heavyweight automated optimizer.

## Calibration Guardrails

- Save a backup of `glm3.nml` before calibration and keep a known-good runnable copy until the final run is verified.
- Read the full relevant namelist sections before claiming dates, depths, output settings, or tunable parameters are correct; do not infer them from partial file views.
- If editing `glm3.nml` programmatically, first make one small change, run GLM once, and confirm the file still parses and produces `/root/output/output.nc`.
- Restore the baseline or known-good config before each trial so parameter changes do not accidentally accumulate across experiments.
- Only optimize parameters that you have confirmed actually exist in the namelist with valid editable syntax.
- Do not start broad multi-parameter optimization until your parameter-editing and evaluation workflow has been validated by at least one successful test run.
- If you compute RMSE with a custom script, derive timestamps and depth coordinates from `output.nc` when possible, or confirm them from `glm3.nml` before coding; avoid hard-coded assumptions.
- Calibration is only complete after a fresh final run with the chosen `glm3.nml` and a recomputed RMSE from the new output.
## Tips

- GLM outputs NetCDF format
- Use xarray or nczip to read output
- Calibration may require parameter tuning


- Record each tested parameter set and resulting RMSE so you can keep the best configuration.
- Before committing to a multi-run search, observe one full GLM run so you know the cost, expected outputs, and how progress appears.
- If a run or script shows no new output, no updated files, or no measurable progress, treat that as a debugging signal and switch to a simpler, more monitorable strategy.
- After any failed calibration attempt, restore or confirm a runnable `glm3.nml` before trying again.
- Never report success based on an intermediate, backgrounded, or unverified run; verify the final saved configuration by rerunning GLM and recalculating RMSE.

- Build the evaluation script from the real observation CSV schema and NetCDF metadata, not assumed column or coordinate names.
- Reuse the same validated evaluation script for the baseline, each trial, and the final verification run so RMSE differences reflect model changes rather than changing scoring logic.
- Diagnose the baseline error structure before tuning: for example, a subsurface warm bias is more likely improved by parameters affecting light extinction or mixing than by unrelated broad changes.
- When the initial RMSE is near the target, keep the search narrow and physically interpretable rather than exploring many unrelated parameters.
- A good progression is: baseline run -> manual targeted trial(s) -> automated search only if the evaluation pipeline is reliable and more exploration is still needed.


## Execution and Verification

- Before the first GLM run, confirm the required inputs and analysis tools are available: `/root/glm3.nml`, `/root/field_temp_oxy.csv`, forcing files under `/root/bcs/`, and the NetCDF/CSV libraries or scripts you plan to use.
- Treat empty, quiet, piped, or truncated stdout/stderr as ambiguous, not as proof of success; check the real shell return code from the direct run.
- Do not write that GLM ran successfully or advance to RMSE scoring unless success is evidenced by at least one of: explicit zero exit status, fresh readable `/root/output/output.nc`, or logs showing normal completion.
- If you capture logs, do so without obscuring the program's return code.
- Treat missing, unchanged, or stale `/root/output/output.nc` after a run as evidence that the run did not complete as required, even if no error was printed.
- Treat a good RMSE from partial coverage as invalid; confirm `/root/output/output.nc` reaches the requested end date before accepting any score.
- Before starting a costly calibration loop, estimate whether at least one full edited run plus RMSE recomputation can finish within the remaining session; if not, fall back to smaller controlled trials.
- Before reporting success, confirm both that RMSE was explicitly recomputed from the fresh final `/root/output/output.nc` and that the output spans the full required 2009-01-01 to 2015-12-30 period.
- Keep a final completion checklist: (1) last run finished successfully, (2) `/root/output/output.nc` is fresh and readable, (3) RMSE was recomputed from that output, and (4) if the environment requires a specific completion string such as `ACTION: TASK_COMPLETE`, emit that exact string only after all checks pass.

- Treat tool-interface compliance as a prerequisite check: before your first command, confirm you are using the exact action schema required by the environment.
- Treat a missing explicit RMSE calculation as `not yet evaluated` even if `/root/output/output.nc` exists.
- Make calibration and scoring steps auditable in the log: show the actual executable commands or script contents that computed RMSE or changed parameters, not placeholder comment-only blocks.
- If a GLM run, Python evaluator, or optimization command fails, first capture the real stderr or traceback or rerun with logging that reveals the failing line or component before choosing a fix.
- Treat `Exit code != 0`, truncated traceback output, missing fresh output, or ambiguous failure logs as a debugging state, not as permission to retry with an assumed diagnosis.
- After writing any helper script that will drive scoring or parameter edits, inspect the saved file contents before execution; do not assume the write step produced valid code.
- Before executing a newly written Python script, prefer `python -m py_compile /path/to/script.py` or equivalent; if compilation fails or output is ambiguous, inspect the file contents directly.
- When a calibration script runs, verify completion by checking its return code, reviewing its output or logs, confirming the intended parameter changes in `/root/glm3.nml` or trial records, and recomputing RMSE from the fresh model output.
- Do not stop at launching a background calibration or monitor process. The task is complete only after the final foreground-verifiable result is observed, RMSE is recomputed from fresh output, and the exact required completion string is emitted.
- Before ending, explicitly verify that every tool invocation followed the required action schema, that the transcript contains baseline and current RMSE evidence plus at least one completed calibration attempt when needed, and that the final response includes the exact required completion token if specified.

## Execution and Verification

- Use the task environment's exact required tool/action syntax for executable steps.
- If you launch GLM, calibration, or evaluation in the background, treat that as incomplete work: wait for completion and inspect logs, outputs, and metrics.
- Check the real shell return code instead of assuming success from quiet, empty, or truncated output.
- If `/root/output/output.nc` is missing, stale, or unreadable, inspect `glm3.nml` output settings and treat the run as failed until fixed.
- Do not report an RMSE or claim the target is met unless the value is explicitly computed from completed output or clearly shown by your evaluation step.
- Before ending, verify whether the environment requires a specific completion signal and output that exact string only after all checks pass.