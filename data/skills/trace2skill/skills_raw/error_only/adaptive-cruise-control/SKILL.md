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
2. Read sensor data (time, ego_speed, lead_speed, distance) and inspect enough of the dataset to find regime changes; do not infer missing signals from only the first few rows.
3. Implement PID controller class with configurable gains.
4. Implement ACC system with cruise/follow/emergency modes from the stated spec/config.
5. Simulate closed-loop vehicle dynamics: propagate ego state from the previous simulated state and `accel_cmd`, while treating recorded data only as exogenous inputs unless the task explicitly specifies replay semantics.
6. After each file write or major edit, reopen the file or run a syntax/import check to confirm the change saved correctly before building on it.
7. Tune PID parameters using measured simulation outcomes, and verify that materially different gain sets produce different trajectories or metrics; if they do not, treat that as a blocking implementation bug.
8. Run the full required simulation/analysis pipeline and compute the task's stated metrics from complete outputs, not partial console logs.
9. Keep evaluation logic, metric definitions, scenario assumptions, and mode conditions aligned with the task; if data meaning is ambiguous, validate the interpretation before changing plant or sensor semantics.
10. Before finishing, verify every required metric, safety bound, file/output requirement, and exact completion/output protocol; if anything is unmet or unverified, continue iterating or report it explicitly as unresolved.

## Modes

- **cruise**: No lead vehicle - maintain set speed
- **follow**: Lead vehicle detected - maintain safe distance
- **emergency**: TTC below threshold - apply braking

## Important Parameters

- Time headway, minimum gap, acceleration limits
- Speed rise time, overshoot, steady-state error targets

- Treat performance targets as hard pass/fail gates: rise time, overshoot, steady-state error, minimum distance, TTC, and related safety limits must be checked against stated thresholds before declaring completion.

## Tips

- Load PID gains from YAML file at runtime
- Use discrete-time equations: error[t] - error[t-1] for derivative
- Clamp output to acceleration limits [-8.0, 3.0] m/s²

- Use simplified scenarios only for quick debugging; always close the loop with end-to-end validation on the actual task dataset, full simulation, and original success metrics
- Tune gains from measured results, not intuition alone; keep a best-known validated configuration and replace it only with gains that pass the current controller version's checks
- Do not assume config paths or nested fields exist unless you verified them; prefer validated keys or explicit guarded defaults
- Do not infer controller quality from partial console output; if output is truncated, inspect saved CSV/YAML/results files as the source of truth
- Do not replay controlled ego states from logs inside a closed-loop simulation unless the task explicitly requires replay semantics
- Treat recorded lead-vehicle behavior, timestamps, and measured gap as inputs; keep controlled ego states, logged outputs, and computed metrics consistent with the same simulation state
- If the dataset includes per-step `distance`, use that measured series directly for follow-distance evaluation unless the task explicitly requires reconstruction from positions
- When generating time-series CSV output, confirm whether each row should record pre-update or post-update state, and ensure the first row matches the required initial-state semantics
- Before accepting tuning results, run a sanity check with two very different gain sets; if rise time, steady-state error, or spacing metrics are unchanged, the evaluation loop is not properly coupled to the controller
- If safety metrics or spacing behavior stay nearly constant across retuning attempts, debug model/state-update logic first: check sign conventions, desired-gap formula, emergency triggers, distance initialization, and mode transitions
- Do not rewrite plant/sensor semantics, cruise/follow definitions, evaluation windows, or metric formulas to make results look better unless the task specification explicitly requires it
- Treat physically impossible outputs, contradictory row counts, malformed files, unsafe collisions, or mismatched timestamp/row semantics as bugs to fix, not acceptable artifacts
- If the task specifies an exact final response token, completion string, or output protocol, emit it exactly as required

## Validation and Spec Compliance


- Preserve the task's metric definitions exactly. Do **not** redefine overshoot, steady-state error, evaluation windows, masks, thresholds, or success criteria unless the task explicitly instructs you to.
- Preserve required class/function signatures, file names, and input semantics unless the task explicitly allows changes.
- Only claim requirements are met when the current run's visible outputs or recomputed produced data explicitly show the required metrics; if output is partial, truncated, or missing a metric, report it as unverified.
- Check generated artifacts for integrity, not just existence: confirm files are complete, rows and columns match the spec, formatting is correct, and tails are not truncated.
- Verify that required scenarios and modes (`cruise`, `follow`, `emergency`) are actually exercised when applicable, and report the requested performance and safety metrics explicitly.
- If repeated runs show unchanged results, stop and inspect whether your edits were actually applied or whether the simulation/evaluation is disconnected from the controller.
- Do not explain away failed metrics; treat misses as evidence to change gains, mode logic, data handling, or simulation setup and then re-validate.
- Follow any task-specific execution or interaction protocol exactly, including required tool formats and exact completion tokens.