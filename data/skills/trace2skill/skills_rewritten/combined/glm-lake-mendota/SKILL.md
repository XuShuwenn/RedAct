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
- Before the first tool call, lock in the required execution syntax and use only that exact schema for every action in the session. If the environment allows only shell via `Action:` JSON, do not invoke unsupported tool names, XML-like wrappers, or pseudo-tool formats.
- For shell tools, send only literal shell syntax or executable paths with arguments. If you write a helper file, include the real file contents in that executable step or immediately read the saved file back; for a new Python helper, prefer a concrete validation step such as `python3 -m py_compile /root/script.py` with the actual available interpreter before execution.
- Treat empty, quiet, or truncated tool output as unknown status, not success: verify with the direct return code, file freshness, log contents, or an explicit metric before proceeding.
- If a command or script fails, do not guess the cause from a partial traceback or `Exit code != 0` alone. Rerun or inspect with enough logging to identify the actual failing line or component before editing scripts, changing parameters, or retrying.
- After any quiet, ambiguous, or corrective retry, do not stop at launch: wait for completion, check return status and logs, verify the expected files changed, and recompute the relevant metric before moving on or emitting the completion signal.

- Emit only concrete executable actions/commands, and use only tools and action formats explicitly allowed by the task.
- Send only executable shell commands to shell/bash tools.
- Before relying on a script, verify the interpreter/runtime you plan to use exists in this environment and that required input files are present at the exact `/root/...` paths.
- As an immediate preflight, verify the required action schema, the exact executable names you will use (for example `python3` vs `python`), and that any needed analysis libraries are importable in this environment before writing or invoking helper scripts.
- If a required runtime, command, or library is missing, switch to an available equivalent executable or simpler install-free workflow before proceeding; do not keep issuing failing placeholder commands.
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
1a. Before the first run, inspect `/root/glm3.nml`, sample `/root/field_temp_oxy.csv`, and confirm the expected forcing files exist under `/root/bcs/` so variable names, dates, paths, and driver availability are verified before expensive runs.
2. Load field observations from CSV
3. Configure GLM parameters in `glm3.nml`
4. Run simulation
5. Calculate RMSE against observations
6. Adjust parameters if RMSE > 2°C


7. Inspect `glm3.nml` and `output.nc` metadata before scoring so your RMSE method matches the real variable names, time units/origin, depth structure, and simulation period.
7a. Build one reusable deterministic evaluation script or command sequence early, then use that same scoring pipeline for the baseline and every calibration trial.
7a1. If you create or rewrite an evaluation or calibration script, immediately read it back or print the key sections before executing it; verify the real code contains the intended paths, variable names, date handling, parameter edits, and output locations.
7a1b. Before executing a new Python helper, prefer a concrete validation step such as `python3 -m py_compile /root/script.py` with the actual available interpreter, then inspect the saved file directly if validation fails or output is ambiguous.
7a2. Do not rely on a script whose contents you have only described in prose or assumed were written correctly.
7b. Inspect `/root/field_temp_oxy.csv` header and sample rows early, then compute RMSE by aligning simulation and observations on shared `datetime` and depth bins: read the real NetCDF time units/origin and variable names, convert GLM layer structure into physical depths comparable to the observations, standardize depths only to the observation resolution if needed, handle duplicate time-depth pairs consistently, and score only matched pairs rather than index-aligned arrays.
7b1. Before calibration, also inspect the forcing files under `/root/bcs/` enough to confirm they exist and cover the intended simulation period; do not spend time tuning a setup whose drivers cannot support 2009-01-01 to 2015-12-30.
7b2. When validating the RMSE pipeline, print a small alignment sanity summary before trusting the score: matched-pair count, simulation date range, observation date range used, and a few merged `datetime`/`depth` rows. If matches are unexpectedly sparse, fix alignment before tuning parameters.
7c. Do this before trusting any custom RMSE script: do not hard-code start dates, lake depth, array indexing, or assumed coordinate names without confirming them from the actual files.
8. Start with a baseline run and baseline RMSE before changing parameters.
8a. Make the baseline measurable, not implied: run a concrete command or script that reads `/root/output/output.nc`, aligns it with `/root/field_temp_oxy.csv`, and prints the baseline RMSE before proposing any parameter edits.
8a1. Do not propose calibration, optimization, or parameter changes until the transcript contains an explicit baseline RMSE calculation from `/root/output/output.nc` versus `/root/field_temp_oxy.csv`.
8a2. Treat existing files alone as insufficient evidence: baseline evaluation requires a real command or script whose output visibly prints the computed metric or writes it to a file that you then read back.
8b. If you need automation, first create the evaluator or calibration script as a real file, inspect it briefly, and then call it by path; never use a placeholder shell command that only describes intended work.
8c. Before any iterative calibration, optimization, or script-driven rewriting of `/root/glm3.nml`, save a backup or known-good copy, and confirm the GLM executable/runtime you plan to call is actually available in this environment; treat a missing executable as an environment problem to fix before tuning parameters.
8d. Prefer one inspected reusable script that performs the full measurable cycle from saved `/root/glm3.nml`: run GLM, verify fresh readable `/root/output/output.nc`, align output with `/root/field_temp_oxy.csv`, and print RMSE. Use this same script first for the baseline and again after each accepted parameter change and for the final confirmation run.
9. After the first successful baseline run, keep that run and its RMSE as the calibration baseline; inspect signed bias or residual structure by depth/time before the next trial so parameter choice follows the observed error pattern rather than a blind sweep. Larger deep-water bias often points first toward light-extinction or mixing-related parameters; near-surface bias may justify surface heat-flux factors such as modest `sw_factor`/`lw_factor` adjustments if present.
10. If the baseline RMSE misses the target, convert diagnosis into at least one concrete calibration trial: make a small number of confirmed parameter edits in `/root/glm3.nml`, rerun GLM, and recompute RMSE from the new `/root/output/output.nc`; do not treat analysis alone as progress
10a. Do not stop after bias or error interpretation. Unless the model is currently unrunnable, the next state after diagnosis must be a real trial with persisted `glm3.nml` edits, a completed rerun, and a newly computed RMSE.
10b. Do not stop after launching a calibration or optimization script. Wait for it to finish, inspect whether it actually changed parameters and produced a new run, then recompute RMSE from the resulting fresh `/root/output/output.nc`.
10c. Treat statements like "next I would tune ..." as incomplete until you have actually applied the change, run GLM again, and scored the resulting output..
10d. If baseline RMSE is above 2°C and the model is runnable, do not end the session on analysis alone: complete at least one explicit edit to `/root/glm3.nml`, rerun GLM, and print the new RMSE before any final summary or completion signal.
11. For each calibration trial, restore a known-good baseline `glm3.nml`, apply only that trial's edits, reread or diff the file to confirm the intended parameter change persisted, run GLM, confirm fresh readable `/root/output/output.nc`, and compare the new RMSE against the previous best.
12. Prefer one-parameter or small bounded trials before broad optimization, especially when the baseline RMSE is already close to 2°C; start with a compact set of physically meaningful high-impact parameters such as light extinction (`Kw`), mixing coefficients (for example `coef_mix_hyp` if present), wind scaling (`wind_factor` or `coef_wind_stir`), longwave/shortwave scaling (`lw_factor`/`sw_factor`), or related surface exchange coefficients that you have confirmed exist in `/root/glm3.nml`.
13. Before any automated search or expensive optimization, validate one complete edit -> run -> verify -> score cycle: confirm the target parameter exists, make one small edit, rerun GLM once, confirm readable fresh `/root/output/output.nc`, and recompute RMSE with the same evaluator.
13a. Do not start with a full optimization when the baseline RMSE is already close to target; first try one or a few small targeted parameter edits or a tiny bounded sweep that you can monitor end to end.
13b. Any longer calibration loop must be instrumented and bounded before you rely on it: emit per-trial logs, cap the number of trials or runtime, and verify that logs, output files, and metrics are actually updating. If logs stay empty or files do not change, stop and switch to a simpler manual or tightly bounded approach.
13c. If an automated calibration attempt stalls, times out, or produces empty logs, do not keep waiting based on guesswork; inspect process state and outputs once, then fall back to explicit short trials.
13c1. After one timeout or two non-informative status checks, stop passive polling and switch to a bounded foreground workflow you can finish in-session.
13d. For a concrete bounded pattern, see [monitorable calibration loops](references/monitorable-calibration-loops.md).
13e. Before trusting any automated calibration, show at least one concrete trial command end to end in the transcript: exact parameter edit, exact GLM run command, exact RMSE command or script path, and the resulting metric.
14. If a run stops early or `/root/output/output.nc` does not span 2009-01-01 to 2015-12-30, check both the configured start/stop times in `glm3.nml` and the actual date ranges in the forcing files under `/root/bcs/` before recalibrating.
15. After every run, verify the command exited successfully, `/root/output/output.nc` was regenerated and is readable, and the output covers 2009-01-01 to 2015-12-30 before using the RMSE.
15a. Treat partial-period output as invalid even if the file is readable or the RMSE looks good: confirm the NetCDF time range reaches the required end date before accepting any score or preserving a trial as working.
15b. If a configuration seems promising, preserve that exact runnable `glm3.nml` and verify metric plus full date coverage before replacing it or resetting to another configuration.
15c. Verify any reported RMSE with an independent check after model execution: run a separate read-only command or script that reopens fresh `/root/output/output.nc`, realigns it with `/root/field_temp_oxy.csv`, and recomputes RMSE before trusting scores produced by a calibration or optimization script.
15d. If the independent verification disagrees, or reveals stale or partial output, trust the independent recomputation and debug run completion, file freshness, date coverage, or scoring alignment before continuing calibration.
16. Treat the task as complete only after a fresh final run with the saved best configuration, `/root/glm3.nml` left in that final best reproducible state, and an explicitly recomputed RMSE < 2°C if claiming the target is met.
16a. Final verification must check both metric attainment and artifact persistence: confirm the saved `/root/glm3.nml` still contains the winning parameter values and that `/root/output/output.nc` came from a fresh rerun of that saved file, not from a temporary intermediate trial.

17. When a trial improves RMSE, write the winning values back into `/root/glm3.nml`, rerun GLM from that saved file, and recompute RMSE from the fresh output before claiming success.
17a. After saving a winning trial, reread or diff the relevant `glm3.nml` lines to confirm the exact tuned values persisted; do not rely on the edit command alone as evidence.
17b. Before ending, verify that the tuned values visible in `/root/glm3.nml` match the best-scoring trial you are reporting, and that `/root/output/output.nc` from that saved configuration was freshly regenerated and still spans the full required period.
18. If you expect to test more than a couple of parameter sets, script the full loop (edit `glm3.nml` -> run GLM -> recompute RMSE -> record result) so trials are reproducible and the final saved configuration matches the best-scoring run; see [RMSE alignment and bounded calibration](references/rmse-alignment-and-bounded-calibration.md).
18d. For focused near-target manual trials or tiny sweeps over high-impact terms, see [focused high-impact parameter selection](references/focused-high-impact-parameter-selection.md).
18a. Once one manual baseline edit -> run -> verify -> score cycle works, prefer a small reproducible script that bundles parameter edits, GLM execution, and RMSE recomputation in one bounded loop so every candidate is scored with the same pipeline.
18b. Keep that automation inspectable and bounded: print or save one record per trial with parameter values, run status, RMSE, and current best; preserve the best runnable configuration as trials improve; and stop using the loop if it no longer produces fresh output or updated metrics.
18c. After any automated search completes, do not trust an optimizer's in-memory best alone: load the saved best configuration, rerun GLM once from that file, and recompute RMSE from the fresh `/root/output/output.nc` before claiming improvement or success.

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
- Let residual structure guide the next trial: choose parameters that plausibly affect the depth/season pattern of the observed error, rather than sampling unrelated settings broadly.
- Favor a compact search over a few influential parameters already confirmed in `/root/glm3.nml` (for example `Kw`, `coef_wind_stir`, `wind_factor`, or `coef_mix_hyp`) before trying many weakly motivated edits.
- Keep the calibrated parameter set compact unless evidence suggests otherwise; small searches over confirmed high-impact terms are usually easier to verify and reproduce than broad many-parameter sweeps.
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

- Before calibration, verify the GLM executable you plan to call is present and runnable; do not debug parameter choices until the model command itself is confirmed available.
- If the baseline is already close to 2°C, keep the search narrow: test only a few plausible values for one or two high-impact parameters, and preserve the best runnable configuration as soon as it improves RMSE.
- If you automate multiple trials, prefer a single inspected script that runs GLM and recomputes RMSE in one auditable workflow rather than separate loosely coupled steps.
- When a trial becomes the new best, confirm both the saved parameter values in `/root/glm3.nml` and the reproduced RMSE from a fresh rerun before treating that configuration as final.
- If logs are empty, not growing, or missing per-trial RMSE lines, inspect process state once and then switch to a manual trial or tiny bounded sweep; do not keep waiting on a silent optimizer.
- When showing progress, log the literal command or script path used for each critical action rather than prose like `run calibration` or `inspect output.`

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

- A reliable opening sequence is: inspect `glm3.nml` and `/root/field_temp_oxy.csv` -> confirm forcing files under `/root/bcs/` exist and span the run period -> run one baseline simulation -> compute RMSE from matched time-depth pairs -> only then choose targeted calibration edits.
- A strong default pattern is one reusable `run-and-verify` script: run GLM from the current `/root/glm3.nml`, verify fresh output, compute RMSE, and print the result. Use it for baseline measurement, each promising trial, and the final saved-configuration check.
- If the bias pattern points to a specific heat-budget or mixing imbalance, prefer a compact, physically linked parameter set over unrelated scattershot tuning.
- If one full edit -> run -> verify -> score cycle is already working, a small bounded optimization script can be better than many ad hoc manual edits, as long as each trial logs parameters and RMSE and keeps the search narrow.
- Treat an improved RMSE as provisional until you rerun from the saved best `glm3.nml` and confirm the model remains runnable with the same or better score.


## Execution and Verification

- Before the first GLM run, confirm the required inputs and analysis tools are available: `/root/glm3.nml`, `/root/field_temp_oxy.csv`, forcing files under `/root/bcs/`, and the NetCDF/CSV libraries or scripts you plan to use.
- Make that availability check concrete in the transcript: show the actual command(s) that verify the files, GLM executable, chosen interpreter, and any critical imports exist before depending on them.
- Treat empty, quiet, piped, or truncated stdout/stderr as ambiguous, not as proof of success; check the real shell return code from the direct run.
- If stdout/stderr is empty or truncated, issue a separate direct verification command before narrating success; for example inspect the newest timestamp on `/root/output/output.nc`, open the file metadata, or print the captured exit status/log tail.
- Do not write that GLM ran successfully or advance to RMSE scoring unless success is evidenced by at least one of: explicit zero exit status, fresh readable `/root/output/output.nc`, or logs showing normal completion.
- If you capture logs, do so without obscuring the program's return code.
- Treat missing, unchanged, or stale `/root/output/output.nc` after a run as evidence that the run did not complete as required, even if no error was printed.
- Treat a good RMSE from partial coverage as invalid; confirm `/root/output/output.nc` reaches the requested end date before accepting any score.
- Before starting a costly calibration loop, estimate whether at least one full edited run plus RMSE recomputation can finish within the remaining session; if not, fall back to smaller controlled trials.
- Before reporting success, confirm both that RMSE was explicitly recomputed from the fresh final `/root/output/output.nc` and that the output spans the full required 2009-01-01 to 2015-12-30 period.
- Prefer a separate verification step for the final metric: after any GLM run or calibration workflow reports a score, independently reopen fresh `/root/output/output.nc` and recompute RMSE against `/root/field_temp_oxy.csv` rather than trusting the producing script alone.
- If output ends early, inspect both the `&time` settings in `/root/glm3.nml` and the actual forcing-file date coverage under `/root/bcs/` before changing calibration parameters.
- Keep a final completion checklist: (1) last run finished successfully, (2) `/root/output/output.nc` is fresh and readable, (3) RMSE was recomputed from that output, and (4) if the environment requires a specific completion string such as `ACTION: TASK_COMPLETE`, emit that exact string only after all checks pass.

- Treat tool-interface compliance as a prerequisite check: before your first command, confirm you are using the exact action schema required by the environment.
- If any prior step used the wrong tool-call format, do not assume it executed; rerun the needed command in the correct schema before relying on its supposed effects.
- Treat a missing explicit RMSE calculation as `not yet evaluated` even if `/root/output/output.nc` exists.
- Treat a claimed RMSE that is not present in visible command output, script output, or a read-back results file as unverified; rerun the evaluator and display the metric before using it.
- Before declaring the current setup successful or using it as a baseline to preserve, explicitly inspect the output time range and confirm it spans through 2015-12-30.
- Make calibration and scoring steps auditable in the log: show the actual executable commands or script contents that computed RMSE or changed parameters, not placeholder comment-only blocks.
- If a GLM run, Python evaluator, or optimization command fails, first capture the real stderr or traceback or rerun with logging that reveals the failing line or component before choosing a fix.
- Do not attribute a failure to `glm3.nml` editing, optimization settings, or RMSE logic unless the observed stderr/traceback actually points there; base the next fix on the specific failing command and error evidence.
- Treat `Exit code != 0`, truncated traceback output, missing fresh output, or ambiguous failure logs as a debugging state, not as permission to retry with an assumed diagnosis.
- After writing any helper script that will drive scoring or parameter edits, inspect the saved file contents before execution; do not assume the write step produced valid code.
- Before executing a newly written Python script, prefer `python -m py_compile /path/to/script.py` or equivalent; if compilation fails or output is ambiguous, inspect the file contents directly.
- When a calibration script runs, verify completion by checking its return code, reviewing its output or logs, confirming the intended parameter changes in `/root/glm3.nml` or trial records, and recomputing RMSE from the fresh model output.
- Treat launching an updated calibration script as an intermediate step, not progress by itself: the retry counts only after the script finishes, the resulting run is verified, and a new RMSE or explicit failure diagnosis is shown.
- Do not stop at launching a background calibration or monitor process. The task is complete only after the final foreground-verifiable result is observed, RMSE is recomputed from fresh output, and the exact required completion string is emitted.
- If a background or long-running calibration attempt does not quickly produce visible per-trial metrics, stop it after one verification check and fall back to a simpler foreground run or tiny bounded loop that you can finish and verify within the session.
- Before ending, explicitly verify that every tool invocation followed the required action schema, that the transcript contains baseline and current RMSE evidence plus at least one completed calibration attempt when needed, and that the final response includes the exact required completion token if specified.

- If a step is described in words but not yet represented by a runnable shell command or saved script path, it is not done. Convert it into an executable command before proceeding.
- Do not end on a planned calibration step. The log must show an actual executed baseline scoring command, and if tuning is needed, at least one actual parameter-edit -> rerun -> rescore cycle.
- Final completion gate: exact required action protocol used throughout, concrete executable commands shown for scoring/calibration, fresh `/root/output/output.nc` verified, RMSE explicitly recomputed, and required completion token emitted only at the very end.

## Execution and Verification

- Use the task environment's exact required tool/action syntax for executable steps.
- If you launch GLM, calibration, or evaluation in the background, treat that as incomplete work: wait for completion and inspect logs, outputs, and metrics.
- Check the real shell return code instead of assuming success from quiet, empty, or truncated output.
- If `/root/output/output.nc` is missing, stale, or unreadable, inspect `glm3.nml` output settings and treat the run as failed until fixed.
- Do not report an RMSE or claim the target is met unless the value is explicitly computed from completed output or clearly shown by your evaluation step.
- Before ending, verify whether the environment requires a specific completion signal and output that exact string only after all checks pass.