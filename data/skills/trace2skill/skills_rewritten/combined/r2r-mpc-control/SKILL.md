---
name: r2r-mpc-control
description: "Implement MPC controller for roll-to-roll manufacturing to stabilize web tensions during roller changes."
---

# Roll-to-Roll MPC Controller

## When to Use

- Control web tensions in manufacturing
- Implement Model Predictive Control
- Handle roller change disturbances

## Protocol Gate (read before any action)

- Before the first tool/action, identify the environment's required interaction contract and mirror it literally: required `Thought/Action` labels, JSON wrapper/schema, allowed tool names, path conventions, single-action cadence, and exact completion token.
- If the instructions require a specific wrapper such as `Action:` followed by JSON, use that exact wrapper on every action; do not substitute XML tags, tool-call shortcuts, `Read`/`Write`/`TodoWrite`, alternate helper interfaces, or any other familiar format even once.
- Before the first tool/action, explicitly lock in two items from the instructions: the only allowed tool-call wrapper/tool name(s) and the exact final completion token. Keep both fixed until the task ends.
- Hard stop before first write: identify a workspace path explicitly permitted by the environment and keep all scripts and generated artifacts there. Do **not** use defaults such as `/root/...` unless explicitly authorized.
- First-turn rule: your very first response must already use the environment's exact required action format. Do not preface it with freeform prose or an alternate syntax.
- Before sending any structured action, do a literal syntax check: confirm required labels are present, JSON/brackets/quotes are balanced, allowed tool names are exact, and the payload contains a concrete executable command only.
- Only issue concrete, executable commands/actions. Do **not** write pseudo-commands, natural-language placeholders, or descriptive text as if they were shell commands.
- Treat procedural compliance as part of correctness: technically correct controller work can still fail if the required interaction/completion format is wrong.
- When the environment requires single-action cadence, wait for each tool observation before issuing the next action.
- Do not declare success from partial stdout, initialization messages, warnings, or truncated output alone; confirm execution completed cleanly from direct evidence such as exit status, an explicit completion message, or a fresh readback/verification of regenerated artifacts.
- If command or file output is truncated, reopen the relevant saved files directly, use a narrower inspection/parsing method, or rerun until completion and file regeneration are confirmed.
- If any protocol detail is uncertain, resolve that uncertainty from the instructions before proceeding with file inspection or coding.
- Completion is a protocol step, not a summary step: if an exact completion token/action is required, reserve the final response for exactly that token and nothing else.

## Execution Protocol

- Follow any task- or environment-specific interaction/tool protocol exactly; those instructions override this skill's default workflow.
- If the environment mandates a tool/action format, JSON schema, path convention, single-action cadence, or exact completion string, use it literally and consistently.
- Treat procedural compliance as part of correctness: technically correct controller work can still fail if the required interaction/completion format is wrong.
- Hard-stop protocol rule: before any file inspection, edit, or execution step, restate the exact interaction contract to yourself and then follow it literally on every step: required wrapper/schema, allowed tool name(s), single-action cadence, path conventions, and exact completion token.
- Do not improvise alternate tool names, wrappers, XML tags, pseudo-tool markup, or helper interfaces. If the environment requires `Action:` with a JSON object calling `bash`, every file read/write, execution, and validation step must use that exact shape.
- If the environment allows only one action per turn, issue exactly one action, wait for its observation, and only then send the next action.
- Use concrete executable commands only. Do not write placeholders such as `list relevant files`, `check generated JSON files`, or `run verification`; emit the exact command that performs the action.
- During validation, never send natural-language requests as if they were commands. Use explicit shell commands such as `head`, `tail`, `python3 - <<'PY'`, `jq`, `wc`, or `ls` against the actual workspace paths.
- Use foreground, complete commands for critical validation. Do not rely on vague intentions, malformed shell snippets, backgrounded jobs you do not inspect, or truncated command fragments when deciding whether a redesign works.
- Preflight every tool/action payload before sending: verify JSON/brackets/quotes are closed, fields are complete, and the command or file content is fully specified rather than truncated.
- Put only executable file content in writes. Do not write prose placeholders such as "implemented controller" or TODO summaries inside source files.
- Hard stop on file writes: if a file will be executed or validated later, write the full concrete code/content in that command. Never create a source/artifact/document file containing only a status phrase, intent summary, or placeholder text.
- After every source-file write, immediately read back the saved file (or the edited section) from disk before execution or before describing what it implements. Treat the write as unverified until the readback shows actual runnable code rather than a placeholder description.
- When editing files, anchor every change to exact text you have already read from disk. Use concrete surrounding lines, exact filenames, and executable write/edit commands; do not use placeholders such as `...`, `existing block`, `previous section`, or natural-language descriptions of intended edits.
- Prefer scoped edits over unchecked global replacement. When renaming identifiers or cost terms, edit the exact lines, then grep/read back affected names and rerun; do not use broad replace-all on code symbols without verification.
- Make every material claim auditable in the session log: when you create a file, show the write command; when you run code, show the execution command; when you claim outputs exist, show a listing or direct file read.
- Keep final claims evidence-bound: only describe controller structure/features that you directly inspected in source or that are explicitly shown in saved artifacts.
- Do not claim requirements are satisfied from truncated stdout, startup banners, partial tables, assumed verifier behavior, or partial success lines that appear alongside an exception. Reopen saved artifacts or run a targeted command that prints the missing evidence first.
- Planning is not completion: after outlining an approach, actually create/run the controller, regenerate the required artifacts, and verify them from disk before moving toward completion.
- If the runtime/interpreter is not explicitly specified, verify it before execution (for example, confirm whether `python3` rather than `python` exists) and then use the confirmed executable consistently.
- Make runtime detection an explicit preflight step before the first script run: probe the interpreter/entrypoint you plan to use and switch immediately if unavailable; do not spend a full execution attempt on an unverified command such as assuming `python` exists.
- Before committing to an MPC implementation path, verify critical numerical dependencies the chosen approach needs (for example `scipy`) with a concrete command, and adapt the design if unavailable.
- Stop once the required artifacts pass validation. Do not add optional extras such as plots, visualization scripts, README files, or dependency-heavy analysis unless the task explicitly requires them.
- Final gate before completion: re-open the task instructions and verify, one by one, the required artifacts, required controller type/interface, validation method, and exact completion signal.
- Hard-stop completion rule: do not emit the completion signal if any required metric fails, any required artifact is missing, unreadable, truncated, or stale, or the final controller class does not match the requested method.
- Final handoff rule: after the last successful artifact and metric check, send the mandated completion token as the very next response. Do not append a prose summary, JSON, code fence, or extra explanation before or after it when the environment requires an exact token.

## Problem

- 6-section manufacturing line
- Section 3 roller changes from 20N to 44N at t=0.5
- Must stabilize tensions with MPC

0. First confirm the environment contract: required action syntax, allowed tools, path conventions, and exact completion string. Treat this as a gate before file inspection or coding.
0a. Write your first response/action in that exact required format, and keep using it literally for every subsequent step. Do not improvise alternate tool syntaxes even once.
0b. Also confirm the allowed read/write directories and execution assumptions at this stage: choose script/artifact paths within the permitted workspace and check which interpreter/entrypoint names actually exist in the environment (for example `python3` vs `python`) instead of assuming defaults.
0c. If the contract requires an exact completion token, reserve the final response for exactly that token and nothing else.
0c1. Treat the exact completion token as a deliverable equal in importance to the JSON artifacts: after final file validation passes, stop and emit that token immediately with no narrative wrap-up.
0c2. If the environment requires `Action:` plus JSON on every turn, keep using that exact casing and wrapper for the very first command and every later command; one malformed turn can invalidate an otherwise correct run.
0d. Do not stop at intentions such as "I will create/run ...". Completion requires actually executing the steps, generating `controller_params.json`, `control_log.json`, and `metrics.json`, and validating those saved files from disk.
0e. Any file edit must be grounded in exact source text already inspected from disk. Do not issue placeholder replacements or vague edit intents; identify the real code region first, then apply a concrete, auditable modification.
0f. If the contract requires `Thought`/`Action` JSON with one action per turn, preserve that exact wrapper even for file edits and finalization; do not switch to XML-style tool calls, pseudo-commands, or free-text action descriptions.
1. Derive linearized state-space model at reference operating point
1a. Inspect `r2r_simulator.py` enough to confirm the actual class/interface before coding: constructor, state representation, initialization/reset behavior, how to advance simulation, what outputs are returned, and how disturbances/reference values are exposed. Read the portions that define the class methods you will call; do not code against assumed methods or return signatures from partial inspection.
1b. Record the exact simulator methods and return signatures you verified from source or safe runtime inspection, and code against those verified names only. If the file view is partial or a call fails, keep inspecting until constructor, step/reset flow, returned values, and time/state access are confirmed.
1c. Do not treat a docstring, header, or truncated snippet as sufficient simulator inspection. Keep reading until the concrete integration surface is visible in source: class name, constructor arguments, reset/step usage, returned object shapes/types, timestep handling, and where references/disturbances come from.
1d. Before writing or replacing controller code, finish inspecting the relevant simulator/config source sections that define the methods you will call and the artifact/output conventions you must satisfy. Do not implement against a partially viewed file or inferred API.
1e. Minimum inspection before coding: read enough source to identify the simulator class name, constructor arguments, reset/init method, step/advance method, returned values, timestep source, and where disturbance/reference settings are defined. If any one of these is still inferred rather than observed, keep inspecting before implementation.
1f. Read task/source-of-truth configuration files (for example `system_config.json` or equivalent) before controller design so timestep, nominal tensions, disturbance timing/magnitude, limits, and reference values come from the environment rather than assumption.
1g. Write the controller against the combined contract from config plus simulator source: confirm state/input dimensions, disturbance timing, reference operating point, and logging horizon before deriving the model.
1h. Before control tuning, numerically sanity-check the derived/discretized model from the chosen operating point: inspect matrix dimensions and a few representative entries/signs, and confirm they are finite and qualitatively plausible.
2. Design an actual MPC controller with horizon N in [3, 30]: formulate a finite-horizon receding-horizon optimization and solve it at each control step. Do not substitute a fixed LQR/state-feedback law and label it MPC.
2a. Make the runtime implementation visibly MPC: construct and solve the horizon optimization online each step (or via an explicitly equivalent receding-horizon QP formulation), apply only the first control action, and log/export parameters consistent with that implementation.
2b. Architecture check before tuning: inspect the executed control loop and confirm it actually builds and solves a finite-horizon optimization each step. If the runtime law is only `u = u_ref - K @ x_err` (or equivalent fixed gain), do not call it MPC and do not continue tuning it as if it were MPC.
2c. If repeated tuning attempts tempt you toward PI/PID/heuristic corrective laws, stop and reassess the MPC formulation instead of silently changing controller class. Either keep a genuine receding-horizon solve in the runtime loop or explicitly report that MPC was not achieved.
3. Run controller for at least 5 seconds
3a. Treat the full 5-second closed-loop simulation as the acceptance test. Use short smoke tests only for debugging; make final tuning and validation decisions from the required full simulation and reported metrics.
3b. For fixed-step simulations, determine whether each log sample is recorded before or after stepping, then choose the sample count so `control_log.json` includes timestamps spanning at least 5.00 seconds. Read back the first and last timestamps from the saved log to confirm coverage.
3c. Treat `5.00 seconds` as an exact acceptance floor, not a rounding target. If validation says `4.99...` or otherwise reports `< 5.00`, the run fails and must be rerun/fixed; do not reinterpret it as passing.
3d. Use an unambiguous duration fix: choose the sample count / loop bounds so the saved final timestamp is strictly at or above `5.00` in `control_log.json` (prefer a small margin over landing at `4.999999...`). Do not declare success from rounded display text; parse the saved final timestamp from disk.
4. Log tensions and compute metrics
4a. Use the required deliverables as a completion checklist: write `controller_params.json`, `control_log.json`, and `metrics.json` from the final controller run, then reopen and validate them before finishing.
4b. Validate deliverables by direct inspection from the workspace, not by summaries alone: list the files and reopen each required JSON/artifact after the final run.
4c. Treat file creation as unverified until readback succeeds from disk in the allowed workspace. If a write command only echoes a placeholder message or truncated content, do not assume the script or artifact exists or is correct.
5. After any code or parameter edit, rerun the final selected controller to confirmed successful completion before trusting any existing artifacts.
5b. After writing or editing any controller/evaluation file, read back the saved file (or the relevant sections) from disk before claiming what it implements. Do not describe model structure, MPC logic, metrics code, or output schema from memory or from write intent alone.
5c. After any substantive controller/code overwrite, treat all prior artifact validation as stale. Reopen and inspect `controller_params.json`, `control_log.json`, and `metrics.json` again from the latest run before making any success claim.
5d. Minimum post-overwrite verification rule: after replacing controller logic or rerunning the final script, re-open all three required artifacts from disk in the latest run and verify them again. Reading only `metrics.json` is insufficient to support claims about controller type, log coverage, or generated parameters.
5a. Inspect the executed controller code/control loop directly before claiming MPC: confirm the runtime controller actually applies a receding-horizon optimization or equivalent MPC law each step, rather than only exporting LQR-related matrices, weights, or a fixed state-feedback controller.
6. Reopen generated artifacts from the latest successful run and verify full required content, not just file existence or a truncated preview: inspect enough of `controller_params.json`, `control_log.json`, and `metrics.json` to confirm required top-level keys, plausible dimensions, and that the control log spans at least 5.00 seconds.
6a. Cross-check key trajectory-derived metrics—especially settling time after the disturbance at `t=0.5`—against `control_log.json`. If the log disagrees, recompute or fix the metric and do not report the stale value.
6aa. Treat implausible scalar metrics as a debugging trigger. Examples: `settling_time = 0.0` despite a visible post-disturbance transient, or low steady-state error while the final logged tension remains far from reference. In these cases, inspect the metric code and recompute from the saved log before making any pass/fail claim.
6b. If any file view is truncated, that is not verification. Reopen the file with a narrower query, parse it programmatically, or inspect specific required keys until you have confirmed full schema/content from disk.
6c. Before any success claim, obtain direct evidence for each required target from executed outputs: either parse the saved JSON files or run a focused verification command whose output explicitly shows the relevant metrics and pass/fail status.
6d. Never infer a pass from truncated stdout. If the run output cuts off before metrics or pass/fail evidence appears, reopen `metrics.json` and `control_log.json` directly or run a narrow parser that prints the exact saved values you need.
7. Compare computed metrics against every stated target before declaring success; if any requirement fails, output is truncated/unverified, required fields/duration are missing, or artifact freshness is unclear, rerun or continue debugging.
7a. Treat any failed threshold in `metrics.json` as a hard stop: do not end the task, claim success, or emit a completion summary while any requirement is unmet or only "close enough".
7b. Treat validator/checker output as authoritative evidence. If any explicit check reports failure, missing coverage, bad schema, or unmet threshold, do not override it with your own optimistic summary; fix the producing code/artifacts first and rerun validation.
7c. Make the acceptance check explicit from the saved files: compare measured steady-state error vs `< 2.0N`, settling time vs `< 4.0s`, max tension vs `< 50N`, and min tension vs `> 5N`. Do not claim the controller passes unless each comparison is individually checked against the task thresholds.
7d. If any one required comparison fails, stop completion immediately. Do not write a success summary, deployment claim, or final completion token; continue debugging until every required threshold passes from the latest saved artifacts.
7e. Do not summarize metrics as "good" or "meeting targets" without an explicit pass/fail comparison for each required threshold. Show or compute each comparison from the saved artifacts first, then decide completion from those comparisons.
7f. If metrics have fluctuated materially across recent tuning runs or a result is only narrowly passing, rerun the final selected controller and confirm the regenerated saved artifacts still satisfy every threshold before completing.
7g. Do not convert a failing run into a claim that the plant or target is "unreachable", "physically limited", or "not fully reachable" unless the task explicitly asks for such an analysis and the saved evidence proves it.
8. If behavior is unstable, biased, produces `nan`/`inf`, or suspicious metrics, validate the model/control formulation before further retuning.
8a. Check root-cause assumptions explicitly: verify equilibrium/reference offsets, discretization, feedback sign, state ordering, and that the linearized model qualitatively matches the simulator near the operating point before more weight or gain tuning.
8b. Treat severe instability as a stop condition, not a tuning hint: if a full run shows `nan`/`inf`, overflow warnings, extreme tension excursions, or obvious unbounded growth, stop iterative retuning and first fix the controller structure, model, or safety issue.
8b1. Do not respond to instability by editing simulator state after `step()` or clamping logged tensions/states to pass checks. Fix the model, offsets, constraints, discretization, or controller formulation so the simulator evolves safely on its own.
8c. If performance stays poor across iterations, stop ad hoc rewrites and do one evidence-based diagnosis pass from the latest `control_log.json`: identify whether the dominant issue is offset, oscillation, saturation, wrong disturbance handling, or too-slow response, then change the controller to address that diagnosed cause and rerun the full 5-second test.
9. Perform a final end-to-end deliverable and procedural validation from saved files: load each JSON fully, confirm required keys and structure, verify `control_log.json` reaches at least 5.00 seconds using actual first/last timestamps, confirm the latest artifacts support the claimed metrics, and only then complete the task using the environment's exact required completion signal.
9a. Separate substantive success from protocol success: even if metrics pass and artifacts are valid, the task is not complete until you have also used the required tool/action format throughout and emitted the exact mandated completion string at the end.
9b. Final-step priority rule: after step 9 passes, immediately emit the exact required completion signal/action. Do not add a narrative summary, extra tool calls, or more validation unless the environment explicitly requires them as part of completion.
9c. In any status update before the final token, distinguish verified facts from assumptions: report inspected file contents, parsed metrics, and observed runtime behavior only. Do not state that the controller has terminal costs, constraints, or other design elements unless you actually reopened the implementing code or an artifact that explicitly shows them.
9d. Treat any post-pass action as a risk to completion unless the environment explicitly requires it. After you have direct evidence that the latest saved artifacts satisfy the task, stop and send the exact completion signal immediately.## Workflow

1. Derive linearized state-space model at reference operating point
1a. Inspect `r2r_simulator.py` enough to confirm the actual class/interface before coding: constructor, state representation, how to advance simulation, what outputs are returned, and how disturbances/reference values are exposed. Do not assume methods or return signatures from naming alone.
2. Design an actual MPC controller with horizon N in [3, 30]: formulate a finite-horizon receding-horizon optimization and solve it at each control step. Do not substitute a fixed LQR/state-feedback law and label it MPC.
3. Run controller for at least 5 seconds
3a. Treat the full 5-second closed-loop simulation as the acceptance test. Use short smoke tests only for debugging; make final tuning and validation decisions from the required full simulation and reported metrics.
4. Log tensions and compute metrics
5. Reopen generated artifacts and verify that `controller_params.json`, `control_log.json`, and `metrics.json` were created from the latest successful run, are populated, and are structurally correct.
6. Compare computed metrics against every stated target before declaring success; if any requirement fails or output is truncated/unverified, rerun or continue debugging.
7. If behavior is unstable, biased, produces `nan`/`inf`, or suspicious metrics, validate the model/control formulation before further retuning.

## Required Outputs

### controller_params.json
```json
{
  "horizon_N": 9,
  "Q_diag": [100.0, ...],
  "R_diag": [0.033, ...],
  "K_lqr": [[...], ...],
  "A_matrix": [[...], ...],
  "B_matrix": [[...], ...]
}
```

### control_log.json
```json
{"phase": "control", "data": [{"time": 0.01, "tensions": [...], ...}]}
```

### metrics.json
```json
{"steady_state_error": 0.5, "settling_time": 1.0, ...}
```


- Generate `controller_params.json`, `control_log.json`, and `metrics.json` from the final selected controller run, not from earlier trial scripts or stale artifacts.
- Prefer a single final pipeline/script that regenerates all three artifacts in one execution so the saved parameters, log, and metrics are guaranteed to match the same run.
- For any newly created controller/evaluation script, verify both sides before trusting it: read back the script itself to confirm executable code was saved, then run it, then reopen the generated JSON artifacts from disk.
- Place all generated files in the environment-permitted workspace only; if directory permissions or allowed paths are unclear, determine them first and avoid restricted locations such as `/root/` unless explicitly authorized.
- Keep artifacts internally consistent with the implemented controller. If runtime control is MPC/state-feedback, export matching parameters; do not label a PI/heuristic or fixed LQR controller as MPC.
- `control_log.json` must contain control-phase data spanning **at least 5.00 seconds**; do not treat 4.99 s as acceptable unless the task explicitly allows tolerance.
- Before completion, validate each artifact against the spec: confirm required top-level keys are present, matrices/vectors have plausible dimensions, and reported metrics are consistent with the logged trajectories.
- If any artifact read is truncated, that does not count as validation. Reopen the file with a narrower command or parse it programmatically until you have confirmed the required top-level keys and relevant contents from disk.
- Use a literal acceptance checklist from the latest saved files before completion: `(steady_state_error < 2.0)`, `(settling_time < 4.0)`, `(max_tension < 50.0)`, `(min_tension > 5.0)`, plus confirmation that `controller_params.json`, `control_log.json`, and `metrics.json` were all reopened after the last code change/run.
- When validating artifact schema, explicitly check task-critical required keys rather than only generic readability; for example, confirm `controller_params.json` contains `K_lqr` when the spec requires it.
- Include an explicit saved-log coverage check in final validation: confirm sample count is plausible for the configured timestep and that first/last timestamps in `control_log.json` span at least 5.00 seconds.
- Before any success claim, obtain explicit evidence for all three required files from the latest run: show a directory listing and reopen or parse `controller_params.json`, `control_log.json`, and `metrics.json`. Do not infer missing files from a script exit status or from checking only one artifact.
- Final artifact check must verify content, not just existence: confirm `controller_params.json` includes the MPC-related fields required by the spec, `control_log.json` has control-phase samples through at least 5.00 s, and `metrics.json` contains the reported acceptance metrics.
- Do not stop at existence checks, a few matrix dimensions, or a partial preview. Open or parse `metrics.json` and `control_log.json` directly from disk and confirm key fields, numeric plausibility, and trajectory/metric agreement from the latest run.
- Final verification is not complete if you checked only `metrics.json`; always reopen `controller_params.json` and `control_log.json` from the same latest run and confirm they support the claimed controller type, run duration, and reported metrics.
- Final verification must include direct content checks, not just existence or a few dimensions: reopen or parse `metrics.json` and `control_log.json` from the latest run, confirm required top-level keys and representative values, and verify they are consistent with the controller you actually executed.
- Evidence rule for final claims: do not describe controller structure, generated filenames, or metric values unless the session log shows the actual write command, the execution command, and a direct read/list/parse of the saved artifacts from the permitted workspace.
- Do not change metric definitions, thresholds, or settling-time rules to make a weak controller look acceptable; fix controller behavior instead.
- Keep evaluation logic stable across debugging and final validation. Do not add smoothing, moving averages, alternate tolerance bands, post-processing filters, or revised settling rules after seeing poor results unless the task explicitly requires that metric definition.
- If you must touch metric code for a task-required reason, separately validate the claimed improvement against raw `control_log.json` trajectories from the same run and confirm the unsmoothed log visibly supports the reported metric.

- If you claim MPC, the implementation must actually perform a receding-horizon optimization at each control step using the prediction model and horizon `N`; a fixed gain law such as `u = u_ref - Kx` is not, by itself, sufficient.
- Keep the runtime policy, exported parameters, and final claim aligned. Do not ship a PI/heuristic/fixed-gain controller while labeling it MPC just because the artifacts include `Q`, `R`, `K_lqr`, or model matrices.
- Ensure the code and artifacts provide observable evidence of MPC rather than only tuned gains: horizon `N`, cost weights, model matrices, and a runtime receding-horizon solve path should all be consistent with the delivered controller.
- Do not stop at existence checks or rely on clipped console output or partial JSON previews as final verification. Open or parse each required JSON file enough to confirm complete validity, required fields, and full log coverage.
- Confirm these files come from the latest run after the final code state: check modification time, contents that reflect current parameters, or explicit run output showing they were rewritten.
- Do not modify task-provided verification scripts, thresholds, or acceptance checks just to make outputs pass. If a verifier exposes a real mismatch, correct the producing code and regenerate the artifacts.
- Do not create alternate metric scripts or refined reporting as a substitute for improving a controller that still fails the stated thresholds. If you adjust evaluation because the spec truly requires it, rerun the final controller and re-check pass/fail directly from the latest saved `control_log.json` and `metrics.json`.
- Keep metric computation fixed across debugging and final evaluation. Do not add smoothing, moving averages, alternate tolerance bands, or revised settling rules after seeing poor results unless the task explicitly requires that definition.
- If `metrics.json` reports good performance but the raw log still shows large error or out-of-band behavior near or after the disturbance, treat the metrics as invalid and debug the controller or evaluation script before proceeding.
- Prefer a single final control script/run that produces all three artifacts together, then immediately reopen them and verify content, readability, schema, and duration from disk so files are not stale or cross-run inconsistent.
- Before claiming success, ensure the observed evidence is complete: if stdout from the controller run or validator is cut off, do not infer the rest. Inspect the saved JSON artifacts directly and, if needed, rerun focused checks to confirm exact metric values and pass/fail status.

- Final validation must check contents, not just existence: confirm each JSON is readable from disk, has the required top-level keys, and that values/structures are consistent with the latest controller run.
- Never claim a duration pass from rounded console text alone; parse `control_log.json` and compare the exact saved final timestamp against the requirement.
- Do not modify task-provided verification scripts, thresholds, acceptance checks, smoothing, moving averages, alternate tolerance bands, revised settling rules, or other evaluation logic just to make outputs pass. If the task explicitly requires a metric-code change, separately validate the controller against raw `control_log.json` trajectories and make sure the reported improvement is visible in the unsmoothed log.
- If any final verification or smoke test emits an exception, traceback, `NameError`, or similar runtime error, treat the run as failed/incomplete even if some later lines look normal. Fix the error and rerun before drawing conclusions from that output.
- When verification output contains both an exception and seemingly successful lines, treat the exception as authoritative evidence that validation is incomplete. Resolve the error first; do not summarize the run as successful or use the partial output as acceptance evidence.

## Performance Targets

- Mean steady-state error < 2.0N
- Settling time < 4.0s
- Max tension < 50N, Min tension > 5N


- Treat these thresholds as pass/fail acceptance criteria for completion; do not declare success if observed metrics miss a required threshold.
- Measure settling time from the disturbance time (`t = 0.5`) to when the affected tensions enter and remain within the chosen tolerance band, unless the task explicitly specifies a different definition.
- If computed metrics conflict with the logged trajectory, treat the result as invalid and debug the controller/model before claiming success.

- Treat these thresholds as pass/fail acceptance criteria for completion; do not declare success if observed metrics miss a required threshold.
- Do not try to rescue a failing run by redefining settling time, tolerance bands, or other pass/fail calculations unless the task explicitly requires a different definition.
- Treat implausibly small settling times with suspicion; verify from the logged post-disturbance samples that the affected tensions actually enter and stay within tolerance, rather than trusting a reported scalar blindly.

- Before declaring success, perform and record a literal pass/fail check for each target using the saved metrics/log values; do not infer success merely because the numbers look reasonable.
- A controller that misses even one required threshold is not complete. Do not use phrases like "ready," "successful," or "complete" while any saved pass/fail check still shows `False`.
- A near-miss is still a failure: if `settling_time` is 4.50 s against a `< 4.0 s` target, do not say the task is complete.

## Tips

- Use r2r_simulator.py (don't modify it)
- Linearize around operating point
- Use scipy for control design


- Implement actual MPC: discretize the linearized model, define prediction horizon `N`, construct stage/terminal costs, solve the finite-horizon problem each control step, and apply only the first control move.
- LQR may be useful for terminal cost or comparison, but do not present pure fixed-gain LQR/state-feedback as MPC.
- When runs show `nan`, extreme tensions, persistent offsets, or instability, check the linearization operating point, discretization, equilibrium/input offsets, and feedback sign/structure before more tuning.
- Validate that the linearized model predicts simulator behavior qualitatively near the reference point.
- Prefer reading `metrics.json` and `control_log.json` over abbreviated console output; cross-check metrics against raw trajectories before reporting success.
- For fixed-step runs, verify whether logging occurs before or after each simulator step and confirm first/last timestamps explicitly to avoid off-by-one duration mistakes.
- Do not clamp or overwrite simulator state/tension values after stepping just to keep logs or metrics in range; fix the controller/model instead.

- Minimum MPC checklist: prediction model, finite horizon, optimization solved online each step, first-control-move application, then horizon shift and repeat. If your code cannot point to those elements, do not present it as MPC.
- If you use LQR, use it only as a terminal cost, warm start, fallback for analysis, or baseline comparison; do not represent a pure fixed-gain policy as MPC in code or artifacts.
- When runs show `nan`, extreme tensions, persistent offsets, or instability, prefer root-cause checks over repeated scalar retuning: verify the operating point, offsets, discretization, sign conventions, and simulator/model agreement first.
- Never overwrite, clamp, or post-process simulator state/tension values after `step()` just to keep logs, plots, or metrics within limits; this invalidates evaluation.
- When validating the model against the simulator, run a small near-equilibrium perturbation or open-loop check and confirm the predicted direction and magnitude are at least qualitatively consistent before trusting MPC tuning results.
- Read simulator configuration/source-of-truth inputs as well as `r2r_simulator.py` so nominal tensions, disturbance magnitude/timing, timestep, and operating references match the real environment.
- When available, use simulator-provided `x_ref` and `u_ref` to formulate deviation-coordinate control around the true equilibrium.
- If the environment returns truncated file content, keep reading until you have the full simulator implementation before deriving the model or coding against the interface.
- After any file write, prefer a quick reopen/readback or `python -m py_compile`-style check before first execution.
- When deriving the linear model, explicitly differentiate each additive term separately; Jacobian sign mistakes in velocity-coupling terms are a common cause of immediate divergence.
- Keep the final pipeline reproducible: one rerunnable script should generate `controller_params.json`, `control_log.json`, and `metrics.json` together so the artifacts correspond to the same controller execution.
- Prefer a standalone driver script for the full workflow—model construction, MPC solve loop, simulation rollout, logging, metrics, and JSON export—without modifying the provided simulator. This reduces integration errors and makes final reruns reproducible.
- When validating `control_log.json`, check structure as well as duration: confirm the expected entry count for the chosen timestep/run length and verify representative per-step keys such as time, tensions, inputs, and references are present.
- If the environment enforces a bash-only or other single-tool protocol, keep all inspection, editing, and validation inside that allowed tool path instead of mixing in unsupported interfaces.

- When creating or editing Python files, write runnable code only. Never place narrative placeholders, TODO-style summaries, or status descriptions inside files that are supposed to be executed.
- After writing a source file, immediately reopen or print enough of that exact file to confirm the saved contents are executable code, then run that file with an explicit command.
- Prefer targeted edits anchored to exact code you just inspected. Avoid blind global rewrites or abstract replacement instructions; after each patch, read back the changed function/block and confirm the runtime logic still matches the intended MPC, simulation, and metric flow.
- If performance is still failing after a run, base the next change on specific evidence from the latest code, simulator interface, and `control_log.json`; do not stop at a narrative explanation for failure while required thresholds remain unmet.
- DO NOT edit simulator state after `step()` to force pass conditions. Wrong: `x[:6] = np.maximum(x[:6], 5.0)` or similar post-step clipping to improve min/max tension or avoid NaNs. Right: change the controller, operating-point offsets, discretization, or numerical handling so the simulator itself evolves safely.
- A controller that repeatedly shows huge overshoot, negative tensions, overflow, or `nan` on full-run validation should trigger a structure/formulation review, not more blind gain retuning around the same law.
- Use explicit, reproducible validation commands for the final pipeline; avoid backgrounded, partial, or malformed commands when deciding whether the latest controller works.
- Environment checklist before acting: required action wrapper/schema, allowed tool names, single-action cadence, exact completion token, available interpreter/executable names, and permitted workspace paths. Treat any unknown item as something to verify first, not assume.

- Read the simulator equations first, then read the config/source-of-truth parameters, and only then derive the model or tune the controller.
- Use the provided configuration file for sampling time, nominal tensions/references, disturbance details, constraints, and physical constants instead of recreating them from memory.
- Run a real closed-loop simulation early, before extensive tuning. A quick end-to-end run often exposes structural problems faster than inspection alone.
- When MPC performance is poor, co-tune the linear model/discretization, horizon and cost weights, and actuator/input clipping or limits together; these choices interact strongly.
- If you add actuator clipping/limits for realism or stability, keep them inside the controller/optimization or commanded input path and reflect them consistently in the final controller behavior and exported artifacts.
- Keep a copy of the best observed controller settings from a passing or near-passing full run. If subsequent edits worsen settling time, error, or stability, restore that known-good version instead of continuing to tune a degraded controller.
- Use an evidence-based revision loop: after each full run, identify the dominant failure mode from `control_log.json` and `metrics.json` (offset, oscillation, saturation, instability, insufficient duration, schema mismatch), make one targeted change for that cause, then rerun the full acceptance test.
- Do not accept a "closest so far" controller. Keep iterating, or explicitly report inability to meet the required thresholds, if any saved metric still fails its pass/fail target.
- If reported metrics improve dramatically after metric-code changes but the raw trajectory still shows visible error or oscillation, treat that as a metric bug or evaluation drift, not a controller success.
- On the final turn, re-check the required completion string and send exactly that string with no summary or explanation attached.
