---
name: hvac-control
description: "Implement PID temperature controller for HVAC system to maintain 22.0C with specific performance requirements."
---

# HVAC Temperature Controller

## When to Use

- Implement PID control loops for temperature regulation
- Calibrate thermal system parameters
- Tune controller gains for specific performance criteria

## Targets

- Steady-state error < 0.5°C
- Settling time < 120s
- Overshoot < 10%
- Control duration >= 150s
- Max temperature < 30°C
- Initial temperature ~ 18.0°C (±2°C noise)
- Heater power: 0-100%


- Treat task-specified metric definitions as fixed acceptance criteria.
- Do not loosen settling bands, add smoothing, redefine overshoot, or otherwise change pass/fail measurement logic just to make results pass.
- If performance misses a target, tune the controller, model, duration, or anti-windup behavior instead of changing the metric definition.
- Only change analysis/evaluation code when correcting a clear bug, and keep the corrected logic aligned with the original task specification.

## Workflow

1. **Calibration**: Run test (30+ seconds, 20+ data points) → `calibration_log.json`
2. **Parameter Estimation**: Fit thermal model (K, tau) → `estimated_params.json`
3. **Gain Tuning**: Calculate Kp, Ki, Kd → `tuned_gains.json`
4. **Closed-loop Control**: Run to 22.0°C → `control_log.json` + `metrics.json`


5. **Verification & Finalization**: Confirm the control run finished end-to-end; inspect `estimated_params.json`, `tuned_gains.json`, `control_log.json`, and `metrics.json` directly; compare every item in **Targets** against observed values using the original metric definitions; cross-check key requirements against the raw trajectory when needed; and only then report success or emit any exact runtime/task-specified completion token.

If any required metric fails, continue tuning and rerun or explicitly report the unmet requirement. If 2-3 retuning attempts produce the same failing pattern (especially settling time or oscillation), stop sweeping one gain knob and change the design: add measurement filtering, strengthen anti-windup, or switch tuning/control structure.


## Execution Discipline

## Execution Discipline

- Follow any task- or environment-specific execution instructions exactly. If a strict tool/action schema, command wrapper, response format, or exact completion token is required, use it verbatim.
- Do not substitute alternate tool syntaxes, wrappers, or informal prose actions when a strict protocol is specified.
- After each action, wait for the observation/result before issuing the next action when the environment requires turn-by-turn interaction.
- Treat interface and completion requirements as part of task success. When the required output files are complete, stop and emit the exact mandated completion string if one is specified.
- Do not declare success or failure from partial/truncated stdout, file existence alone, or intermediate artifacts. First confirm the run completed, then inspect the generated JSON outputs.
- Preserve the original metric definitions from the task statement. Do not change settling bands, smoothing, overshoot calculation, or other pass/fail logic just to make results look acceptable unless explicitly authorized.
- Do not delete scripts, logs, or generated artifacts unless the task explicitly requests cleanup.
- If task/environment instructions conflict with this skill's generic guidance, obey the task/environment instructions.
## Model

First-order thermal system:
- K: system gain
- tau: time constant
- u: heater power (0-100%)

## Output Files

- `calibration_log.json`: Phase, heater power test, data array
- `estimated_params.json`: K, tau, r_squared, fitting_error
- `tuned_gains.json`: Kp, Ki, Kd, lambda
- `control_log.json`: Phase, setpoint, data array
- `metrics.json`: rise_time, overshoot, settling_time, steady_state_error, max_temp


- Before any final summary, read `estimated_params.json`, `tuned_gains.json`, `control_log.json`, and `metrics.json` directly. Do not rely on file existence, partial output, or expected code paths.
- Only state requirement pass/fail after inspecting `metrics.json` values; if output is incomplete or metrics are missing, report that verification is incomplete instead of assuming success.

## Tips

- Use scipy.optimize for curve fitting
- Ziegler-Nichols or model-based tuning for PID
- Anti-windup for integral term
- Clamp heater power to [0, 100]


- Treat all listed targets as mandatory pass/fail gates, not advisory goals.
- Base tuning changes on verified artifact contents, not partial console output or guessed failures.
- If a run appears truncated, verify completion and inspect artifacts before interpreting results.
- Freeze metric definitions early; tune the controller, not the scoring rule.
- Treat `metrics.json` as a summary, not proof: if results look unexpected or metric code changed, verify against raw `control_log.json` data.
- If noise prevents settling detection, filter the measured temperature used by the controller and/or metrics (for example, a short moving average or 1st-order low-pass) and document it.
- If a proposed model-estimation fix barely changes fitted `K`/`tau` or closed-loop behavior, shift focus to controller design rather than repeating the same estimation idea.
- Before finishing, check whether the task requires a specific final-output token or action format.
