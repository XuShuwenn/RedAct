---
name: r2r-mpc-control
description: "Implement MPC controller for roll-to-roll manufacturing to stabilize web tensions during roller changes."
---

# Roll-to-Roll MPC Controller

## When to Use

- Control web tensions in manufacturing
- Implement Model Predictive Control
- Handle roller change disturbances


- Follow any task- or environment-specific interaction/tool protocol exactly; those instructions override this skill's default workflow.
- If the environment mandates a specific Thought/Action schema, JSON wrapper, allowed tool names, path convention, single-action cadence, or exact completion string, mirror it literally on every step; do not switch to another tool-call style or wrapper mid-run.
- Treat procedural compliance as part of correctness: technically correct controller work can still fail if the required interaction/completion format is wrong.
- Before the first tool/action, identify the required interaction contract and use that exact format for every step.
- When the environment requires single-action cadence, wait for each tool observation before issuing the next action.
- Do not declare success from partial stdout, initialization messages, or truncated output alone; verify results from saved artifacts first.
- If command or file output is truncated, reopen the relevant saved files directly, use a narrower inspection/parsing method, or rerun until completion and file regeneration are confirmed.
- Before the final response, re-check the task instructions for the exact completion contract.
- If an exact completion token is required, make the final response exactly that token and nothing else.## Execution Protocol

## Execution Protocol

- Follow any task- or environment-specific interaction/tool protocol exactly; those instructions override this skill's default workflow.
- If the environment mandates a tool/action format, JSON schema, path convention, single-action cadence, or exact completion string, use it literally and consistently.
- Treat procedural compliance as part of correctness: technically correct controller work can still fail if the required interaction/completion format is wrong.
- Do not declare success from partial stdout, initialization messages, or truncated output alone; verify results from saved artifacts first.
- If an exact completion token is required, output that token verbatim as the final response and nothing else.

## Problem

- 6-section manufacturing line
- Section 3 roller changes from 20N to 44N at t=0.5
- Must stabilize tensions with MPC

0. First confirm the environment contract: required action syntax, allowed tools, path conventions, and exact completion string. Treat this as a gate before file inspection or coding.
1. Derive linearized state-space model at reference operating point
1a. Inspect `r2r_simulator.py` enough to confirm the actual class/interface before coding: constructor, state representation, initialization/reset behavior, how to advance simulation, what outputs are returned, and how disturbances/reference values are exposed. Read the portions that define the class methods you will call; do not code against assumed methods or return signatures from partial inspection.
1b. Record the exact simulator methods and return signatures you verified from source or safe runtime inspection, and code against those verified names only. If the file view is partial or a call fails, keep inspecting until constructor, step/reset flow, returned values, and time/state access are confirmed.
2. Design an actual MPC controller with horizon N in [3, 30]: formulate a finite-horizon receding-horizon optimization and solve it at each control step. Do not substitute a fixed LQR/state-feedback law and label it MPC.
2a. Make the runtime implementation visibly MPC: construct and solve the horizon optimization online each step (or via an explicitly equivalent receding-horizon QP formulation), apply only the first control action, and log/export parameters consistent with that implementation.
3. Run controller for at least 5 seconds
3a. Treat the full 5-second closed-loop simulation as the acceptance test. Use short smoke tests only for debugging; make final tuning and validation decisions from the required full simulation and reported metrics.
3b. For fixed-step simulations, determine whether each log sample is recorded before or after stepping, then choose the sample count so `control_log.json` includes timestamps spanning at least 5.00 seconds. Read back the first and last timestamps from the saved log to confirm coverage.
4. Log tensions and compute metrics
4a. Use the required deliverables as a completion checklist: write `controller_params.json`, `control_log.json`, and `metrics.json` from the final controller run, then reopen and validate them before finishing.
5. After any code or parameter edit, rerun the final selected controller to confirmed successful completion before trusting any existing artifacts.
5a. Inspect the executed controller code/control loop directly before claiming MPC: confirm the runtime controller actually applies a receding-horizon optimization or equivalent MPC law each step, rather than only exporting LQR-related matrices, weights, or a fixed state-feedback controller.
6. Reopen generated artifacts from the latest successful run and verify full required content, not just file existence or a truncated preview: inspect enough of `controller_params.json`, `control_log.json`, and `metrics.json` to confirm required top-level keys, plausible dimensions, and that the control log spans at least 5.00 seconds.
6a. Cross-check key trajectory-derived metrics—especially settling time after the disturbance at `t=0.5`—against `control_log.json`. If the log disagrees, recompute or fix the metric and do not report the stale value.
7. Compare computed metrics against every stated target before declaring success; if any requirement fails, output is truncated/unverified, required fields/duration are missing, or artifact freshness is unclear, rerun or continue debugging.
7a. Treat any failed threshold in `metrics.json` as a hard stop: do not end the task, claim success, or emit a completion summary while any requirement is unmet or only "close enough".
8. If behavior is unstable, biased, produces `nan`/`inf`, or suspicious metrics, validate the model/control formulation before further retuning.
8a. Check root-cause assumptions explicitly: verify equilibrium/reference offsets, discretization, feedback sign, state ordering, and that the linearized model qualitatively matches the simulator near the operating point before more weight or gain tuning.
9. Perform a final end-to-end deliverable and procedural validation from saved files: load each JSON fully, confirm required keys and structure, verify `control_log.json` reaches at least 5.00 seconds using actual first/last timestamps, confirm the latest artifacts support the claimed metrics, and only then complete the task using the environment's exact required completion signal.## Workflow

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
- Keep artifacts internally consistent with the implemented controller. If runtime control is MPC/state-feedback, export matching parameters; do not label a PI/heuristic or fixed LQR controller as MPC.
- `control_log.json` must contain control-phase data spanning **at least 5.00 seconds**; do not treat 4.99 s as acceptable unless the task explicitly allows tolerance.
- Before completion, validate each artifact against the spec: confirm required top-level keys are present, matrices/vectors have plausible dimensions, and reported metrics are consistent with the logged trajectories.
- Do not change metric definitions, thresholds, or settling-time rules to make a weak controller look acceptable; fix controller behavior instead.

- If you claim MPC, the implementation must actually perform a receding-horizon optimization at each control step using the prediction model and horizon `N`; a fixed gain law such as `u = u_ref - Kx` is not, by itself, sufficient.
- Ensure the code and artifacts provide observable evidence of MPC rather than only tuned gains: horizon `N`, cost weights, model matrices, and a runtime receding-horizon solve path should all be consistent with the delivered controller.
- Do not stop at existence checks or rely on clipped console output or partial JSON previews as final verification. Open or parse each required JSON file enough to confirm complete validity, required fields, and full log coverage.
- Confirm these files come from the latest run after the final code state: check modification time, contents that reflect current parameters, or explicit run output showing they were rewritten.
- Do not modify task-provided verification scripts, thresholds, or acceptance checks just to make outputs pass. If a verifier exposes a real mismatch, correct the producing code and regenerate the artifacts.
- Keep metric computation fixed across debugging and final evaluation. Do not add smoothing, moving averages, alternate tolerance bands, or revised settling rules after seeing poor results unless the task explicitly requires that definition.
- If `metrics.json` reports good performance but the raw log still shows large error or out-of-band behavior near or after the disturbance, treat the metrics as invalid and debug the controller or evaluation script before proceeding.
- Prefer a single final control script/run that produces all three artifacts together, then immediately reopen them and verify content, readability, schema, and duration from disk so files are not stale or cross-run inconsistent.

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
- If the environment enforces a bash-only or other single-tool protocol, keep all inspection, editing, and validation inside that allowed tool path instead of mixing in unsupported interfaces.
