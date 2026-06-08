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
7b. Inspect `/root/field_temp_oxy.csv` header and sample rows early, then compute RMSE by aligning simulation and observations on shared `datetime` and depth bins: read the real NetCDF time units/origin and variable names, convert GLM layer structure into physical depths comparable to the observations, standardize depths only to the observation resolution if needed, handle duplicate time-depth pairs consistently, and score only matched pairs rather than index-aligned arrays.
7c. Do this before trusting any custom RMSE script: do not hard-code start dates, lake depth, array indexing, or assumed coordinate names without confirming them from the actual files.
8. Start with a baseline run and baseline RMSE before changing parameters.
9. After the first successful baseline run, keep that run and its RMSE as the calibration baseline; if the baseline RMSE is already close to 2°C, inspect signed bias or residual structure by depth/time so you can choose the next parameter change direction.
10. If the baseline RMSE misses the target, convert diagnosis into at least one concrete calibration trial: make a small number of confirmed parameter edits in `/root/glm3.nml`, rerun GLM, and recompute RMSE from the new `/root/output/output.nc`; do not treat analysis alone as progress.
11. For each calibration trial, restore a known-good baseline `glm3.nml`, apply only that trial's edits, reread or diff the file to confirm the intended parameter change persisted, run GLM, confirm fresh readable `/root/output/output.nc`, and compare the new RMSE against the previous best.
12. Prefer one-parameter or small bounded trials before broad optimization, especially when the baseline RMSE is already close to 2°C; start with physically meaningful high-impact parameters such as light extinction, mixing, wind, or modest `sw_factor`/`lw_factor` adjustments if present.
13. Before any automated search or expensive optimization, validate one complete edit -> run -> verify -> score cycle: confirm the target parameter exists, make one small edit, rerun GLM once, confirm readable fresh `/root/output/output.nc`, and recompute RMSE with the same evaluator.
14. If a run stops early or `/root/output/output.nc` does not span 2009-01-01 to 2015-12-30, check both the configured start/stop times in `glm3.nml` and the actual date ranges in the forcing files under `/root/bcs/` before recalibrating.
15. After every run, verify the command exited successfully, `/root/output/output.nc` was regenerated and is readable, and the output covers 2009-01-01 to 2015-12-30 before using the RMSE.
16. Treat the task as complete only after a fresh final run with the saved best configuration, `/root/glm3.nml` left in that final best reproducible state, and an explicitly recomputed RMSE < 2°C if claiming the target is met.

17. When a trial improves RMSE, write the winning values back into `/root/glm3.nml`, rerun GLM from that saved file, and recompute RMSE from the fresh output before claiming success.
18. If you expect to test more than a couple of parameter sets, script the full loop (edit `glm3.nml` -> run GLM -> recompute RMSE -> record result) so trials are reproducible and the final saved configuration matches the best-scoring run; see [RMSE alignment and bounded calibration](references/rmse-alignment-and-bounded-calibration.md).


## Calibration Guardrails

- Once you have a baseline RMSE above target, do not end on a diagnosis-only state; make at least one verified parameter edit and rerun unless the model is currently unrunnable and you are fixing that first.
- Record calibration trials in a simple table or notes block: parameter(s), old value(s), new value(s), run status, RMSE, and current best.
- Keep the RMSE alignment method fixed across calibration trials; reuse one validated RMSE script so improvements reflect parameter changes rather than changed scoring logic.
- When editing parameters programmatically, confirm each target name exists in `/root/glm3.nml` with the expected syntax before relying on text substitution, and inspect the modified file to ensure only the intended value changed.
- Do not score raw GLM layers directly against observations unless they already share the same depth definition; convert or round to the observation depth grid first, then evaluate only matched time-depth pairs.
- Prefer parameters with clear physical influence on thermal structure and mixing before editing many unrelated settings, and use broader multi-run searches only after one full run/evaluation cycle has been proven to work.
- Do not launch background, unconstrained, or open-ended full-model calibration as your primary strategy. Prefer bounded manual trials or a very small grid with explicit run limits and visible per-trial logging; only scale up after one monitored edited run succeeds end to end.
- If a long-running step shows no new logs, no file growth, no updated `/root/output/output.nc`, or no updated metric, treat it as a debugging failure state and switch to a simpler, more monitorable approach.
- When reverting experiments, restore `glm3.nml` from the saved backup or known-good runnable copy; do not reconstruct the full namelist manually from memory or a heredoc.
- If a trial breaks execution, first restore the last verified runnable `glm3.nml`, rerun once to confirm recovery, and only then resume parameter testing.
- Keep the best-found parameter values written in `/root/glm3.nml`, and treat a candidate as the new best only after a rerun from that saved file reproduces the recorded RMSE.

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
- If you capture logs, do so without obscuring the program's return code.
- Treat missing, unchanged, or stale `/root/output/output.nc` after a run as evidence that the run did not complete as required, even if no error was printed.
- Treat a good RMSE from partial coverage as invalid; confirm `/root/output/output.nc` reaches the requested end date before accepting any score.
- Before starting a costly calibration loop, estimate whether at least one full edited run plus RMSE recomputation can finish within the remaining session; if not, fall back to smaller controlled trials.
- Before reporting success, confirm both that RMSE was explicitly recomputed from the fresh final `/root/output/output.nc` and that the output spans the full required 2009-01-01 to 2015-12-30 period.
- Keep a final completion checklist: (1) last run finished successfully, (2) `/root/output/output.nc` is fresh and readable, (3) RMSE was recomputed from that output, and (4) if the environment requires a specific completion string such as `ACTION: TASK_COMPLETE`, emit that exact string only after all checks pass.

## Execution and Verification

- Use the task environment's exact required tool/action syntax for executable steps.
- If you launch GLM, calibration, or evaluation in the background, treat that as incomplete work: wait for completion and inspect logs, outputs, and metrics.
- Check the real shell return code instead of assuming success from quiet, empty, or truncated output.
- If `/root/output/output.nc` is missing, stale, or unreadable, inspect `glm3.nml` output settings and treat the run as failed until fixed.
- Do not report an RMSE or claim the target is met unless the value is explicitly computed from completed output or clearly shown by your evaluation step.
- Before ending, verify whether the environment requires a specific completion signal and output that exact string only after all checks pass.