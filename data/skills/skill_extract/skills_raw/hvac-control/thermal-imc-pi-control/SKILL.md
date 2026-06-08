---
name: thermal-imc-pi-control
description: "Design, tune, and verify PI controllers for first-order thermal/HVAC processes using calibration-based identification, IMC tuning, anti-windup, and noise-tolerant metrics."
---

# First-Order Thermal Control with IMC-Tuned PI

A reusable workflow to calibrate a thermal system, estimate first-order parameters, compute IMC PI gains, implement a robust PI loop with anti-windup, and verify performance with noise-tolerant metrics. Applicable to HVAC rooms, incubators, heaters, and similar processes dominated by a single time constant.

## When to Use

Activate this skill when you need to:
- Maintain temperature at a setpoint with constraints on overshoot, settling time, and steady-state error
- Identify a thermal process from an open-loop step test
- Compute PI gains using Internal Model Control (IMC) for a first-order plant
- Generate and validate JSON logs of calibration, tuning, control, and metrics

## Core Workflow

1) Inspect the environment
- Determine available interfaces: reset(), step(u), run_open_loop(u, duration), dt, setpoint, ambient, safety limits.
- Note actuator constraints (e.g., power 0–100%) and any safety temperature ceiling.

2) Calibration: Open-loop step test
- Apply a constant heater power step (typical 30–60%) for at least 30 seconds and collect ≥20 data points.
- Record an initial baseline point with heater off at t=0, then the step response at constant power.
- Log JSON (calibration_log.json) with fields:
  - phase: "calibration"
  - heater_power_test: percentage value used
  - data: list of {time, temperature, heater_power}

3) Parameter estimation (first-order model)
- Model: dT/dt = (1/τ) × (K·u + T_amb − T)
- Step response from baseline T0 (≈ ambient):
  - T(t) = T_ss − (T_ss − T0) · exp(−t/τ), where T_ss = T0 + K·u
- Procedure:
  - Find the first index where heater_power > 0 (step-on).
  - T0: mean temperature over a few samples just before the step.
  - u: the constant heater power during the step.
  - K estimate: (mean of last N temperatures − T0) / u (use N ~ 5–10).
  - τ estimate: time when T(t) reaches T0 + 0.632 × (T_ss − T0), via interpolation between samples.
  - Compute fit quality by simulating the analytical curve and reporting R² and RMSE.
- Save estimated_params.json with keys: {K, tau, r_squared, fitting_error}.

4) IMC PI tuning
- For first-order G(s) = K / (τ s + 1), IMC PI gains (no dead time) are:
  - Kp = τ / (K · λ)
  - Ki = 1 / (K · λ)  (equivalently, Ki = Kp / τ)
  - Kd = 0 (derivative is usually avoided for noisy thermal sensors)
- Choose λ (closed-loop time constant) to meet specs:
  - Settling time (to ~2%) ≈ 4·λ. If required Ts < T_target, choose λ ≤ T_target/4.
  - Larger λ → slower but lower overshoot and better noise robustness.
  - Smaller λ → faster, higher risk of overshoot and actuator saturation.
- Save tuned_gains.json with {Kp, Ki, Kd, lambda}.

5) Closed-loop PI control implementation
- Compute error e = setpoint − measured_temperature.
- PI control: u = Kp·e + Ki·∫e dt.
- Anti-windup:
  - Saturate u to actuator limits (e.g., 0–100%).
  - Conditional integration or back-calculation so the integral term does not accumulate when saturated in the wrong direction.
- Optional measurement filter (e.g., exponential moving average) to temper sensor noise before computing e.
- Safety interlocks: if approaching maximum safe temperature, cut or limit output and reset integral as needed.
- Log control_log.json:
  - phase: "control"
  - setpoint
  - data: list of {time, temperature, setpoint, heater_power, error}
- Run for at least the required control duration.

6) Noise-tolerant performance metrics
- Rise time: time from 10% to 90% of the total setpoint step (use interpolation).
- Overshoot: (max(filtered_temperature) − setpoint) / step_magnitude, clipped at ≥0.
- Settling time:
  - Use an absolute band consistent with specs (e.g., ±0.5°C) or the larger of that and 2% of the step.
  - Use a moving-average filtered temperature to mitigate noise.
  - Define settling time as the earliest time after which all filtered samples remain within the band.
- Steady-state error: average absolute error over the last window (e.g., last 20–30 s).
- Max temperature: maximum observed temperature (raw or filtered, report which you use).
- Save metrics.json with {rise_time, overshoot, settling_time, steady_state_error, max_temp}, and (optionally) total/control duration.

## Verification Checklist

Before finalizing outputs:
- Calibration
  - Duration ≥ required minimum and ≥20 samples
  - Step input is clearly applied (heater_power transitions from 0 to constant value)
  - JSON format matches expected keys
- Estimation
  - K > 0, τ > 0
  - Fit quality: R² is reasonable for noise level (often >0.95 for clean thermal steps)
- Tuning
  - λ chosen to satisfy settling-time target (Ts ≈ 4·λ)
  - Gains produce actuator outputs within limits most of the time
- Control run
  - Output constrained to actuator range, no integral windup
  - Safety temperature limit not violated
  - Control duration ≥ required minimum
- Metrics
  - Settling calculation accounts for noise (absolute band or filtered signal)
  - All target thresholds checked against metrics.json

## Common Pitfalls and How to Avoid Them

- Settling band too tight for noise
  - Symptom: Settling time appears too long or not met despite visibly stable control.
  - Fix: Use a noise-aware absolute band (e.g., ±0.5°C) or filter the temperature for metric computation; require sustained in-band samples.
- Incorrect IMC formulas
  - Use Kp = τ / (K·λ) and Ki = 1 / (K·λ) (Ki = Kp/τ). Do not omit K in Ki.
- Baseline/step detection errors
  - Ensure T0 comes from pre-step baseline. Use the first index where heater_power > 0 as the step onset.
- Integrator windup
  - Always implement anti-windup via conditional integration or back-calculation when saturated.
- Overly aggressive λ
  - Leads to overshoot and long saturation. Increase λ until overshoot/metrics meet specs.
- No safety interlock
  - Always clamp output and reset integral when approaching safety limits to avoid thermal runaway.

## Optional Script Usage

The following helper scripts implement reusable algorithms for parameter identification, IMC tuning, and noise-tolerant metrics.

- Identify first-order parameters from a calibration log (no SciPy required):
  - Input: calibration_log.json
  - Output: estimated_params.json
  - Usage:
    - python scripts/first_order_id.py --calibration calibration_log.json --out estimated_params.json

- Compute IMC PI gains:
  - Provide K and τ (and optionally λ or a settling-time target)
  - Usage:
    - python scripts/imc_pi_tuner.py --K 0.12 --tau 40 --lambda 25 --out tuned_gains.json
    - python scripts/imc_pi_tuner.py --K 0.12 --tau 40 --target-settling-s 100 --out tuned_gains.json

- Compute noise-tolerant metrics from a control log:
  - Input: control_log.json (with setpoint field) or pass --setpoint
  - Usage:
    - python scripts/metrics_noise_tolerant.py --control control_log.json --out metrics.json --band 0.5 --ma-seconds 10 --ss-seconds 30

Adopt these scripts or replicate their logic in your solution environment to ensure consistent identification, tuning, and validation.
