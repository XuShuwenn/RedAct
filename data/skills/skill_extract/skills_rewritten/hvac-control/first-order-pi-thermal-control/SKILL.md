---
name: first-order-pi-thermal-control
description: "Design, tune, and verify a PI controller for first-order thermal systems using calibration data, simple model identification, and noise-robust performance metrics."
---

# Model-Based PI Control for Thermal Systems

This skill provides a reusable workflow to implement a temperature controller for single-zone HVAC-like systems. It covers: running a calibration step test, estimating a first-order model, computing PI gains with a closed-loop time constant target, implementing a safe controller with anti-windup, and evaluating performance with noise-robust metrics.

Use this when you need to: 1) identify simple thermal dynamics from a step test, 2) tune a PI controller for setpoint tracking, and 3) satisfy constraints on steady-state error, settling time within a specified band, overshoot, control duration, and maximum temperature.

## When to Use

- A simulator or plant exposes a single actuator (e.g., heater power 0–100%) and temperature readings with noise.
- You must design a controller to achieve a setpoint with constraints on steady-state error, overshoot, settling time, control duration, and safety limits.
- The plant is approximately first-order (thermal rooms often are) and you can run an open-loop step test for identification.

## Core Workflow

1. Inspect the environment
   - Read the simulator interface to learn: time step or update cadence, actuator bounds (e.g., 0–100%), available measurements, and noise characteristics.
   - Confirm how to initialize the environment and how to log time, temperature, and actuator values.

2. Calibration (open-loop step test)
   - Choose a moderate heater step (e.g., not near saturation) to avoid nonlinear behavior and ensure safe temperatures.
   - Run at least 30 seconds and collect at least 20 samples. Include the pre-step baseline and the step transition in the log.
   - Log JSON with keys such as: phase, heater input level, and an array of samples [{time, temperature, heater_power}].

3. Parameter estimation (first-order model)
   - Assume a first-order plus gain model without delay: y(t) ≈ y0 + K·Δu·(1 − exp(−(t − t_step)/τ)) for t ≥ t_step.
   - Identify the step time and compute:
     - Initial temperature y0 from pre-step samples (mean).
     - Final temperature y∞ from late samples (mean).
     - Δy = y∞ − y0, Δu = u1 − u0 → process gain K = Δy/Δu.
     - Time constant τ from the 63.2% time: find when y reaches y0 + 0.632·Δy after the step.
   - Assess fit quality (e.g., RMSE and R² on post-step data). Save parameters to JSON (e.g., {K, tau, r_squared, fitting_error}).

4. Controller tuning (PI)
   - Select a closed-loop time constant target λ to balance speed and overshoot. Rule of thumb for first-order plants without significant delay:
     - Kp = τ / (K·λ)
     - Ki = Kp / τ = 1 / (K·λ)
     - Kd = 0 (usually unnecessary for thermal systems)
   - Choosing λ: smaller λ yields faster responses but more overshoot and risk of saturation; larger λ is slower and more robust. For a settling time requirement Ts within a ±band, start with λ ≈ Ts/4 to Ts/5 and adjust based on observed overshoot and saturation.
   - Save tuned gains to JSON (e.g., {Kp, Ki, Kd, lambda}).

5. Closed-loop control implementation
   - PI update (parallel form): u_unsat = Kp·e + I, where e = setpoint − measured; I ← I + Ki·e·dt.
   - Clamp actuator: u = clip(u_unsat, min_output, max_output).
   - Anti-windup: prevent integrator windup by either:
     - Only integrating when u is not saturating, or
     - Back-calculation: I ← I + Ki·e·dt + kaw·(u − u_unsat)·dt with a small kaw.
   - Safety: never exceed actuator limits; monitor and enforce a max temperature safety bound.
   - Run for a duration that satisfies the minimum control time requirement and log time, temperature, setpoint, heater power, and error.

6. Performance evaluation (noise-robust)
   - Apply a light smoothing (e.g., moving average over ~1–2 seconds) to the measured temperature for metric calculations only.
   - Metrics:
     - Steady-state error: absolute mean error over the last window (e.g., last 10–15 seconds), using the filtered signal.
     - Overshoot: max(0, max_temp − setpoint) / |step_amplitude|, where step_amplitude = setpoint − initial_temp.
     - Settling time: earliest time the filtered temperature enters and remains within the required band (e.g., ±0.5°C) for a dwell duration (e.g., ≥5 seconds).
     - Control duration: total simulated time span.
     - Max temperature: maximum temperature observed.
   - Save a metrics JSON with the above quantities.

7. Iterate if needed
   - If overshoot is too high or actuator saturates frequently, increase λ (less aggressive), reduce Kp, or lower Ki.
   - If settling time is too long or steady-state error persists, decrease λ (more aggressive) and ensure integral action is active (Ki > 0) without windup.
   - Re-run the closed-loop test and re-check metrics.

## Verification

- Calibration log:
  - Contains ≥30 seconds and ≥20 samples.
  - Includes baseline, step event, and sustained post-step data.
- Estimated parameters:
  - K > 0, τ > 0, fit quality reasonable (e.g., R² high, RMSE small relative to step size).
- Tuned gains:
  - Kp, Ki non-negative; Kd set to zero unless justified; λ documented.
- Control run:
  - Duration meets or exceeds the minimum requirement.
  - Actuator always within bounds; safety temperature never exceeded.
- Metrics:
  - Computed with a noise-tolerant settling-time algorithm using the specified band.
  - Overshoot normalized by step amplitude.
  - Steady-state error computed from a late-time window.

## Common Pitfalls and How to Avoid Them

- Too-short calibration or too few samples → leads to poor parameter estimates.
  - Ensure duration and sample count minima are met and that the response approaches a new steady value.
- Misdetecting step time or step sizes in calibration → corrupts K and τ.
  - Detect the largest actuator change and compute pre/post means for robust Δu and y0/y∞.
- Overly aggressive tuning causing overshoot or actuator saturation → violates overshoot/safety limits.
  - Increase λ or add modest anti-windup; ensure actuator limits are respected.
- Windup of the integral term when output saturates → long recovery and large overshoot.
  - Use conditional integration or back-calculation anti-windup.
- Settling time failing due to sensor noise in a very tight band.
  - Use a small smoothing filter for metrics and require the signal to remain within the band for a dwell period.
- Incorrect overshoot calculation.
  - Normalize by the step amplitude (setpoint − initial temperature), not by the setpoint alone.
- Forgetting to write required JSON outputs or using wrong keys.
  - Validate all output files for required keys and JSON validity before finalizing.

## Optional Script Usage

- Parameter estimation from a calibration log:
  - scripts/first_order_fit.py reads a calibration JSON and writes estimated_params.json with K and τ plus fit diagnostics.
- Noise-robust metrics from a control log:
  - scripts/noise_robust_metrics.py reads a control JSON and computes steady-state error, settling time (with band and dwell), overshoot, and max temperature.

## Success Criteria (example set)

- Required files are generated with valid JSON structures for calibration, estimated parameters, tuned gains, control log, and metrics.
- Controller meets specified targets (e.g., steady-state error within band, overshoot within limit, settling time within limit, control duration ≥ minimum, and max temperature below safety limit).
- Control implementation includes actuator clamping and anti-windup to avoid windup-induced instability.
