---
name: adaptive-cruise-control
description: "Implement adaptive cruise control systems with PID controllers for vehicle speed and distance regulation."
---

# Adaptive Cruise Control

## When to Use

- Implement PID control loops for vehicle speed regulation
- Maintain safe following distance from lead vehicle
- Simulate vehicle dynamics with acceleration constraints

## Key Concepts

- **PID Controller**: output = Kp×error + Ki×∫error + Kd×d(error)/dt
- **Setpoint**: target speed (e.g., 30 m/s)
- **Error**: setpoint - measured_value
- **Anti-windup**: prevent integral term from exceeding bounds

- **Sensor data role**: treat provided sensor logs as exogenous inputs (for example timestamps, lead-vehicle behavior, and measured gap) unless the task explicitly defines them as the ego vehicle's reference trajectory
- **Acceptance criteria**: explicit metric thresholds, safety limits, artifact requirements, and required output formats are hard gates for completion, not documentation notes

## Workflow

1. Read vehicle parameters from YAML (mass, acceleration limits, etc.) and confirm the actual schema before using keys in code; do not assume sections such as `simulation` or fields such as `dt` exist unless verified.

   - If the task or environment specifies an exact action/tool-call syntax, allowed tool names, message structure, or exact completion token, treat that protocol as a hard requirement from the first step to the last. Use only the permitted format and emit the required completion string literally when the task is complete.
   - If a required value is missing from the observed schema, re-open the config to confirm, then derive it only from the task/spec or use an explicit guarded default and document that choice in code; do not introduce unchecked dependencies on imagined paths.
 Preserve the task's required runtime interfaces, file roles, class/function signatures, and runtime loading paths instead of hard-coding values or collapsing files for convenience.
2. Read sensor data (time, ego_speed, lead_speed, distance) and inspect enough of the dataset to map regime changes, signal availability over time, row count, timestep behavior, missing-data patterns, and when lead-vehicle interaction first becomes valid/present; do not infer missing signals from only the first few rows.

   - If any inspection output is truncated, empty unexpectedly, or only shows an early prefix, treat the data interpretation as unverified. Re-run with a reliable full-file, CSV-aware check until you confirm row counts, where lead-vehicle signals first become non-null/present, and whether any columns are truly absent before designing controller or mode logic around that assumption.
3. Implement PID controller class with configurable gains, and keep controller behavior, ACC mode/safety logic, and simulation/evaluation orchestration separated so gains, mode conditions, and metrics can change without entangling plant updates.
4. Implement ACC system with cruise/follow/emergency modes from the stated spec/config; in follow mode, make spacing/safety control the primary objective and use speed regulation only as a limiter/cap unless the task specifies a different control law. Handle mode transitions explicitly by resetting or reinitializing PID state as needed to avoid derivative kick or stale integral carryover.
5. Simulate closed-loop vehicle dynamics: propagate ego state from the previous simulated state and `accel_cmd`, while treating recorded data only as exogenous inputs unless the task explicitly specifies replay semantics. If follow behavior must respond to controller changes, initialize from the measured gap if needed and propagate compatible ego/lead motion dynamically (for example via positions/gap) instead of mixing logged per-step ego outcomes or incompatible sampled gaps into the simulated plant.

   - If logged ego speed or ego state is being replayed inside the controlled plant, treat that as a blocking model bug. Fix state propagation and output wiring so reported trajectories come from the simulated closed loop; do not fall back to measured ego outputs merely to make CSVs or plots look expected.
6. After each file write or major edit, immediately reopen the file and confirm the concrete implementation/content is present, complete, untruncated, and syntactically/import-valid before building on it; treat malformed content, escaped newlines, partial writes, suspicious truncation, placeholder prose, or summary-style write/edit descriptions as blocking errors.
7. Tune PID parameters using measured simulation outcomes only after the closed-loop simulation is behaving plausibly, and verify that materially different gain sets produce different trajectories or metrics; if they do not, treat that as a blocking implementation bug. Inspect saved traces around cruise→follow transitions, emergency entry, and steady-state regions to distinguish tuning issues from state/update or command-arbitration bugs.

   - Keep tuning evidence-driven and reproducible: use a consistent evaluation loop, record resulting metrics, and keep the best validated configuration. If multiple retuning attempts leave metrics nearly unchanged, still far outside spec, or traces show physically implausible/unsafe behavior, stop tuning and debug structure instead—controller coupling, desired-gap/sign conventions, state propagation, mode transitions, safety overrides, and metric computation—before changing gains again.
8. Run the full required simulation/analysis pipeline and compute the task's stated metrics from complete artifacts, not partial console logs. For mixed driving regimes, compute each metric over the task-specified interval/mask where that requirement is meaningful, unless the spec explicitly requires whole-run evaluation.

   - Use exact executable shell/Python commands with concrete filenames and arguments; do not use natural-language tool calls such as "run the tuning script" or "analyze the output".
   - Keep diagnostic sub-window metrics separate from acceptance metrics. Do not narrow the evaluation window, add favorable masks, or substitute slices such as "stable-only," "follow-only," or "non-emergency" unless the specification explicitly defines that scope.
   - Keep the evaluation pipeline and metric definitions fixed while tuning controller behavior. Change the evaluator only for a confirmed bug or explicit task requirement, then rerun the complete pipeline from the updated baseline before trusting any numbers.
   - Do not infer pass/fail from sparse progress prints or truncated output; inspect the generated artifacts or recompute metrics directly from them, and rerun after any controller, simulation, or metric-code change.
9. Keep evaluation logic, metric definitions, scenario assumptions, mode conditions, and interaction/tool-call protocol aligned with the task; if data meaning is ambiguous, validate the interpretation before changing plant or sensor semantics. Do not change metric definitions, masks, windows, detection logic, or simulation semantics just to obtain passing numbers.
10. Before finishing, inspect the final deliverables directly and verify every required metric, safety bound, filename, row count, column order, runtime wiring, file/output requirement, and exact completion/output protocol from the produced artifacts themselves; if anything is unmet or unverified, continue iterating or report it explicitly as unresolved.

   - Perform an explicit requirement-by-requirement pass/fail checklist against the original task wording. Treat artifact mismatches such as wrong row counts, missing outputs, malformed files, blank follow/safety fields when they should be populated, or missing expected mode transitions as blocking failures just like failed numeric metrics.
   - Copy reported numbers only from the latest verified run/output. If a metric is not visible in current artifacts, mark it unverified instead of reusing earlier results.
11. If any required metric or safety check fails, treat the task as unfinished: keep iterating or state explicitly which requirement remains unmet; do not present the task as successful, complete, or "working" while known failures remain. Producing the requested files is not sufficient for completion, and you must not rationalize failed metrics as close enough, likely computed differently, or acceptable due to scenario difficulty. Emit any required completion token only when the task's rules allow completion in that state.

## Modes

- **cruise**: No lead vehicle - maintain set speed
- **follow**: Lead vehicle detected - maintain safe distance
- **emergency**: TTC below threshold - apply braking

## Important Parameters

- Time headway, minimum gap, acceleration limits
- Speed rise time, overshoot, steady-state error targets

- Treat performance targets as hard pass/fail gates: rise time, overshoot, steady-state error, minimum distance, TTC, and related safety limits must be checked against stated thresholds before declaring completion.

## Tips

- Load PID gains from YAML or other task-specified artifacts at runtime rather than hard-coding them in controller logic
- Use discrete-time equations: error[t] - error[t-1] for derivative
- Clamp output to acceleration limits [-8.0, 3.0] m/s²

- Use simplified scenarios only for quick debugging; always close the loop with end-to-end validation on the actual task dataset, full simulation, and original success metrics
- Tune gains from measured results, not intuition alone; keep a best-known validated configuration and replace it only with gains that pass the current controller version's checks
- Do not assume config paths or nested fields exist unless you verified them; prefer validated keys or explicit guarded defaults
- Do not infer controller quality from partial console output; if output is truncated, inspect saved CSV/YAML/results files as the source of truth
- After editing Python sources, read them back or run a quick compile/import check before any tuning; truncated or malformed files invalidate all downstream debugging
- Do not replay controlled ego states from logs inside a closed-loop simulation unless the task explicitly requires replay semantics
- Treat recorded lead-vehicle behavior, timestamps, and measured gap as inputs; keep controlled ego states, logged outputs, and computed metrics consistent with the same simulation state
- If the dataset includes per-step `distance`, first verify whether it is an exogenous measured input, a replay/evaluation signal, or a state tied to a prior ego trajectory. Use it directly only when the task defines that semantics and it stays consistent with your simulation; otherwise initialize from it if needed and propagate compatible ego/lead states so controller changes can affect spacing metrics without mixing logged and simulated trajectories
- In closed-loop follow simulations, initialize lead position from the first observed gap when needed, update lead motion from lead-speed or other exogenous inputs, and compute simulated spacing from compatible states so follow metrics remain physically meaningful
- In follow mode, ensure the spacing controller can actually drive commanded acceleration; use speed control as a cap or more restrictive limiter only when the spec requires it. If command arbitration makes spacing metrics insensitive to gain changes, fix the control structure before further retuning
- Add simple supervisory logic around PID when required by the task: anti-windup/integral clamping under saturation, integral reset on mode changes, blocking positive acceleration when already too close, TTC-triggered emergency braking, and small deadbands near zero spacing error to reduce chatter
- When generating time-series CSV output, confirm whether each row should record pre-update or post-update state, ensure the first row matches the required initial-state semantics, and inspect headers/first rows to verify column order and timestep semantics
- Before accepting tuning results, run a sanity check with two very different gain sets; if rise time, steady-state error, or spacing metrics are unchanged, the evaluation loop is not properly coupled to the controller
- If safety metrics or spacing behavior stay nearly constant across retuning attempts, debug model/state-update logic first: check sign conventions, desired-gap formula, emergency triggers, distance/position initialization, mode transitions, and whether the distance loop is being structurally suppressed
- Inspect saved time-series outputs around mode transitions and steady-state segments before changing gains; use those traces to decide whether the issue is tuning, follow logic, or simulation coupling
- Do not rewrite plant/sensor semantics, cruise/follow definitions, evaluation windows, metric formulas, or lead-detection/gating rules to make results look better unless the task specification explicitly requires it
- Treat physically impossible outputs, contradictory row counts, malformed files, unsafe collisions, or mismatched timestamp/row semantics as bugs to fix, not acceptable artifacts
- If the task specifies an exact tool-call syntax, final response token, completion string, or output protocol, use it literally


- If the environment requires a strict tool/action protocol or literal completion token, use that format exactly on every step; do not improvise alternate tool-call syntaxes or free-form completion text
- When verifying implementation files, inspect enough of each file to confirm the expected code structure exists, not just that the file exists or has nonzero length
- If a sanity check with very different gains leaves metrics unchanged, stop tuning and repair the simulation/evaluation coupling before choosing final gains
- Do not claim metrics or final conclusions from truncated output; inspect saved artifacts or rerun until every cited result is fully visible
- Keep the evaluation yardstick fixed while debugging and tuning; improvements that appear only after self-chosen masks, windows, or evaluator changes are unproven until justified by the spec

## Validation and Spec Compliance


- Treat task-environment interaction requirements as hard constraints: use the exact required tool/action syntax, command style, message structure, and final completion signal literally.
- Treat the latest full validation run as the completion gate. If any required metric is out of bounds, unreported, only partially computed, or derived from a disconnected/open-loop evaluation when closed-loop performance is required, do not say the task is complete.
- Do not replace a failing overall metric with a narrower self-selected pass metric, altered window, changed mask, or modified evaluator after the fact unless the task explicitly defines that method as the acceptance criterion.
- Validate generated artifacts for both integrity and semantics: file contents should be complete and concrete, key columns should be populated when expected, mode transitions should occur under the scenario conditions, and cited metrics should agree with the artifacts you reference.
- If the latest artifacts do not explicitly support a claimed metric value or success statement, report it as unverified or unmet rather than asserting completion.

## Validation and Spec Compliance

- Preserve the task's metric definitions exactly. Do **not** redefine overshoot, steady-state error, evaluation windows, masks, thresholds, or success criteria unless the task explicitly instructs you to.
- Preserve required class/function signatures, file names, and input semantics unless the task explicitly allows changes.
- Only claim requirements are met when the current run's visible outputs or recomputed produced data explicitly show the required metrics; if output is partial, truncated, or missing a metric, report it as unverified.
- Check generated artifacts for integrity, not just existence: confirm files are complete, rows and columns match the spec, formatting is correct, and tails are not truncated.
- Verify that required scenarios and modes (`cruise`, `follow`, `emergency`) are actually exercised when applicable, and report the requested performance and safety metrics explicitly.
- If repeated runs show unchanged results, stop and inspect whether your edits were actually applied or whether the simulation/evaluation is disconnected from the controller.
- Do not explain away failed metrics; treat misses as evidence to change gains, mode logic, data handling, or simulation setup and then re-validate.
- Follow any task-specific execution or interaction protocol exactly, including required tool formats and exact completion tokens.