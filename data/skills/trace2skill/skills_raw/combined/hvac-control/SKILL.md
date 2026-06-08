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

- When evaluating settling or steady-state accuracy, use the band explicitly stated by the task requirements; do not silently tighten it beyond spec or loosen it for convenience.

## Workflow

1. **Calibration**: Run a fixed-power heater step test (commonly ~50% power) long enough to capture the thermal rise clearly; prefer 30+ seconds and enough samples for model fitting (dense logging such as ~20+ points minimum, more when feasible) → `calibration_log.json`
2. **Parameter Estimation**: Fit thermal model (K, tau) → `estimated_params.json`

   - Prefer fitting the explicit first-order step-response model directly to the logged trajectory, e.g. `T(t) = T0 + K*u*(1 - exp(-t/tau))`, estimating `T0` if needed. Check for `scipy` first and prefer `scipy.optimize.curve_fit` or equivalent library fitting before writing custom estimation code; record fit quality such as `r_squared` or RMSE.

3. **Gain Tuning**: Start from the identified first-order model and use a standard model-based rule (prefer IMC/lambda; PI is a strong default for first-order thermal plants) before doing manual retuning → `tuned_gains.json`
4. **Closed-loop Control**: Run to 22.0°C → `control_log.json` + `metrics.json`

   - Plan the closed-loop run length up front so settling and duration targets are actually observable; 180s is a good default when allowed because it exceeds the minimum control-duration requirement.
   - Match the simulator's step semantics exactly. In discrete step-based simulators, a safe default is: apply current command → read resulting measurement from that step → compute next command. If loop timing/order is wrong, fix that before retuning gains.
   - Run in a way that exposes full closed-loop completion and final metrics. If stdout is truncated or tailed before metrics appear, rerun without truncation or inspect the generated JSON files directly before making any performance claim.
   - Do not describe overshoot, settling, steady-state error, or improvement/regression for a tuning change unless you inspected the corresponding `metrics.json` or raw `control_log.json` from that run.



5. **Verification & Finalization**: Confirm the control run finished end-to-end; inspect `estimated_params.json`, `tuned_gains.json`, `control_log.json`, and `metrics.json` directly; compare every item in **Targets** against observed values using the original task-specified metric definitions; if evaluation code appears inconsistent with the spec, change it only to restore exact alignment with the stated definitions, then rerun and cross-check settling time, overshoot, and steady-state error against the raw trajectory before trusting `metrics.json`; ensure `control_log.json` and `metrics.json` come from the same latest completed run; and only then report success or emit any exact runtime/task-specified completion token.

If any required metric fails, do not present the task as complete. Continue tuning and rerun, or explicitly report the unmet requirement.

If 2-3 retuning attempts produce the same failing pattern (especially settling time, oscillation, or noise-driven non-settling), stop sweeping one gain knob and change the design: add measurement filtering, strengthen anti-windup, or switch tuning/control structure. Do not keep retrying the same PI/PID form with only a new lambda or gain scale once the failure pattern is unchanged.
0. **Protocol + plant/task pre-flight**: Before any tool use, extract any task-mandated action schema, command wrapper, turn-taking rule, allowed tools, and exact completion token/string. Use that interface verbatim for every step. Also read the simulator/model and configuration files before choosing identification or tuning logic; extract the governing thermal equation when available, plus timestep, ambient conditions, noise, safety limits, and setpoint so the controller matches the actual process assumptions.

Prefer one reproducible end-to-end entry point that performs calibration, parameter estimation, gain tuning, closed-loop control, metrics calculation, and all required JSON writes in sequence, while keeping phases logically separable for targeted reruns.

- Between every closed-loop run and every tuning change, read the saved JSON artifacts (`estimated_params.json`, `tuned_gains.json`, `control_log.json`, `metrics.json`) and base the next adjustment on those contents, not on truncated stdout or file existence alone.
- Use a grounded tuning loop: inspect verified metrics/raw trajectory, identify the dominant failure mode (slow rise, overshoot, oscillation, offset, saturation/windup), choose one targeted change tied to that failure mode, rerun, and re-verify. Avoid blind gain sweeps or repeated aggressiveness increases without new evidence.
- Use reruns to validate robustness, not to hunt for a lucky pass. If results vary materially across runs, report the variability and tune for consistent compliance under the original metric definitions instead of looping until one run passes.


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

- Verify artifact structure as well as control performance: confirm calibration/control logs cover the required duration and contain enough data points, not just that `metrics.json` looks acceptable.
- Compute `metrics.json` directly from the same saved closed-loop trajectory written to `control_log.json` so reported metrics and evidence stay consistent.
- If `metrics.json` passes but log duration, sample count, or required fields are missing/incomplete, treat the task as not yet complete and rerun/fix the pipeline.

## Tips

- Use scipy.optimize for curve fitting
- Ziegler-Nichols or model-based tuning for PID

- Default to model-first tuning: collect one clean open-loop step response, fit a first-order model, then compute initial gains from a standard IMC/model-based rule before hand-tuning.
- For first-order thermal plants, IMC-style PI tuning is often enough; if the response is stable but settling is too slow, reduce `lambda` stepwise and rerun verification while keeping overshoot acceptable.
- Prefer PI over PID when measurement noise is noticeable; add derivative only if it clearly improves verified metrics.

- Anti-windup for integral term; when clamping heater power to [0, 100], prefer back-calculation or equivalent integral correction so saturation does not cause slow recovery or overshoot.
- Clamp heater power to [0, 100]

- Include explicit heater saturation/safety handling, and add a hard over-temperature safeguard or power reduction near the max-temperature limit instead of relying on tuning alone to satisfy the safety bound.
- Add practical robustness by default when noise matters: use light controller-side measurement filtering if needed and document it, but do not widen acceptance bands or redefine the metrics unless the task explicitly authorizes that change.



- Treat all listed targets as mandatory pass/fail gates, not advisory goals.
- Base tuning changes on verified artifact contents, not partial console output or guessed failures.
- If a run appears truncated, verify completion and inspect artifacts before interpreting results.
- Freeze metric definitions early; tune the controller, not the scoring rule.
- Treat `metrics.json` as a summary, not proof: if results look unexpected or metric code changed, verify against raw `control_log.json` data.
- If noise makes settling behavior hard to interpret, first verify the task's metric definition and compare `metrics.json` against raw `control_log.json`. Reduce noise sensitivity with controller-side measurement filtering and document it; do not widen acceptance bands or redefine settling unless the task explicitly authorizes that change.
- If a proposed model-estimation fix barely changes fitted `K`/`tau` or closed-loop behavior, shift focus to controller design rather than repeating the same estimation idea.
- Before finishing, check whether the task requires a specific final-output token or action format.


- For simple HVAC thermal plants, a step-test → first-order fit → IMC PI workflow is a reliable default and usually better than ad hoc gain sweeping.
- Use a conservative `lambda` first to limit overshoot and oscillation, then retune from verified closed-loop results.
- In validation runs, clip heater output to `[0, 100]` and use saturation-aware anti-windup by preventing the integral term from accumulating further in the direction that would drive more saturation.
- If settling time fails under the stated definition, do not widen the settling band, add smoothing to the acceptance metric, or otherwise relax the evaluator to force a pass; improve the closed-loop response instead.
- When command output is truncated, prefer `metrics.json` plus spot-checks of `control_log.json` over narrative guesses about performance.
- Use `control_log.json` as the source of truth for debugging: confirm whether the trajectory actually enters and stays in the required band before concluding that tuning helped.
- If the identified first-order plant yields a stable IMC/PI design that is simply too slow, reduce the IMC closed-loop time constant (`lambda` or equivalent) before switching controller structure or sweeping gains blindly.
- If initial PI/PID tuning is fast enough but overshoot is the main failing metric, reduce aggressiveness before redesigning everything: lower `Kp`/`Ki`, limit or pause integration near the setpoint, and consider softer output limiting as temperature approaches the target.
- If a simple first-order fit already gives stable usable `K`/`tau`, do not overcomplicate the plant model; shift effort to controller design if repeated estimation tweaks barely change closed-loop behavior.
- If the task mandates an exact final token such as `ACTION: TASK_COMPLETE`, output that exact string and nothing else as the terminating action.
