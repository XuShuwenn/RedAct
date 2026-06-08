---
name: acc-simulation-workflow
description: "Design, simulate, and verify an adaptive cruise control (ACC) system with PID loops, safe mode switching, correct gap dynamics, and reproducible CSV/YAML I/O."
---

# Adaptive Cruise Control (ACC) Simulation Workflow

This skill provides a reusable blueprint to implement and validate an ACC system driven by recorded lead-vehicle data. It emphasizes modular PID control, robust mode switching (cruise/follow/emergency), physically consistent gap dynamics, strict I/O contracts, and metric-based verification.

## When to Use

Activate this skill when you need to:
- Build a closed-loop ACC simulation that tracks a set cruising speed when unimpeded, and maintains safe following distance when a lead vehicle appears.
- Combine speed and distance feedback controllers with emergency braking logic.
- Use external data (e.g., CSV time series for lead speed and initial gap) while simulating the ego vehicle state.
- Produce standardized outputs (CSV logs, YAML PID gains, written report) and verify performance metrics.

## Core Workflow

1. Input and Configuration Inspection
- Load the configuration (e.g., YAML) for vehicle limits, ACC settings (set speed, time headway, minimum gap, emergency thresholds), and simulation step size.
- Inspect the input data (e.g., CSV) to confirm:
  - Column names exist for at least: time, lead_speed, and distance (initial gap when available).
  - Row count and uniform timestep match expectations.
  - Periods of lead-vehicle presence (where distance/lead_speed are valid) and absence.
- Identify transition windows (lead appears/disappears; hard braking) to guide tuning and verification.

2. PID Controller Module
- Implement a generic PID controller with:
  - initialize(kp, ki, kd)
  - reset() to clear internal state
  - compute(error, dt) -> output
- Add practical control protections:
  - Output clamping to configured limits.
  - Optional anti-windup: freeze or back-calculate integral when saturating; reset integrator on mode changes.
  - Small deadband near zero error to reduce jitter.

3. ACC Mode Logic
- Implement `compute(ego_speed, lead_speed, distance, dt)` that returns `(acceleration_cmd, mode, distance_error)`:
  - Cruise mode (no lead): Use speed PID to drive toward set speed. Prevent positive acceleration when at/above set speed (outside emergency). Clamp output to acceleration limits.
  - Follow mode (lead present):
    - Desired gap = min_gap + time_headway * ego_speed.
    - distance_error = distance - desired gap (omit if not applicable).
    - Make distance control primary in follow mode. Use speed control only as an upper-speed safeguard (e.g., cap acceleration when near/above set speed). Avoid blending that lets speed control dominate.
  - Emergency mode (collision risk):
    - Compute TTC only when closing (relative_speed > 0). If TTC below threshold (or other risk condition), command strong braking within deceleration limits.
    - Reset/disable integrators while in emergency, and on transition.
- On mode transitions: reset controllers (or at least the integrator) to prevent stale accumulated action.

4. Physically Consistent Simulation Loop
- States: ego_speed, ego_position; lead_position (derived), distance.
- Initialization:
  - Set ego initial speed from config (e.g., near zero).
  - Use lead_speed from input at each step.
  - When a lead vehicle first appears, initialize distance from the first valid recorded gap and align lead_position = ego_position + distance.
- Time stepping (fixed dt): for each timestamp in input data:
  - Compute TTC if lead present and closing; else leave TTC blank/unset.
  - Call ACC.compute(...) to obtain acceleration_cmd, mode, distance_error.
  - Record current row BEFORE state update to ensure the first line reflects the initial state.
  - Update states for next step with kinematics and clamps:
    - a = clamp(acceleration_cmd, [min_accel, max_accel])
    - ego_speed_next = max(0, ego_speed + a * dt)
    - ego_pos_next = ego_pos + ego_speed * dt + 0.5 * a * dt^2
    - lead_pos_next = lead_pos + lead_speed * dt (assume provided as piecewise-constant over dt)
    - distance_next = lead_pos_next - ego_pos_next (omit if no lead)
- Logging invariants:
  - Produce a fixed header and column order (e.g., time, ego_speed, acceleration_cmd, mode, distance_error, distance, ttc).
  - Use empty fields for N/A values (e.g., no lead → no distance, TTC, or distance_error).
  - Ensure the expected number of rows and time coverage per requirements.

5. Gains Management and Tuning
- Maintain gains in a YAML file read at runtime by the simulation; do not embed auto-tuning in the runtime simulation.
- Tune gains (speed and distance loops) by iterating or using a separate tuning script that:
  - Runs the simulation with candidate gains.
  - Measures performance metrics.
  - Selects gains that satisfy specified constraints.
- Keep gains within allowed bounds from the configuration.

6. Metrics and Reporting
- Compute metrics from simulation_results.csv:
  - Speed rise time: time from a lower fraction to an upper fraction of set speed (e.g., 10%→90%, configurable) after start.
  - Overshoot: (max ego_speed − set_speed)/set_speed in percent.
  - Speed steady-state error: average |ego_speed − set_speed| over a tail window (e.g., last N seconds).
  - Distance steady-state error: average |distance − (min_gap + time_headway * ego_speed)| measured only during active following windows; exclude periods with no lead and segments where the lead is well above the set speed and the ego appropriately holds at set speed.
  - Minimum distance: min recorded distance during the run (where available).
- Generate a report describing system design, controller structure, safety logic, final gains, and metric results versus targets.

## Verification

Use these checks before finalizing:
- Data and Timing
  - Confirm input columns and uniform dt.
  - Verify lead presence/absence intervals and identify emergency-like transitions.
- Controller
  - Outputs are clamped within acceleration limits.
  - Integrators reset on mode change and during emergency; no sustained windup.
  - In follow mode, distance control output dominates; speed control acts as a cap.
- Simulation Format
  - First logged row reflects initial state; log before state update.
  - Row count and time range match requirements.
  - Column order and empty fields for N/A values are consistent.
- Physics Consistency
  - Ego speed/position are simulated from commanded acceleration; do not copy recorded ego speed.
  - Distance evolves from relative motion; do not replay recorded distance directly after initialization.
  - TTC is computed only when the ego is closing (relative_speed > 0); avoid divide-by-zero.
- Metrics Validation
  - Rise time, overshoot, steady-state errors, and minimum distance satisfy the configured targets.
  - Distance SSE evaluated only during applicable follow windows.

## Common Pitfalls and Recovery

- Pitfall: Reusing recorded distance directly throughout the run.
  - Fix: Initialize from the first valid gap and propagate distance via simulated relative motion.
- Pitfall: Logging state after updating it, causing an off-by-one initial row.
  - Fix: Record the current state and command before applying the update each step.
- Pitfall: Speed controller dominating in follow mode.
  - Fix: Make distance control primary; use speed controller only to prevent exceeding set speed.
- Pitfall: Integrator windup across mode changes or during saturation.
  - Fix: Reset integral on mode transitions and suspend/inhibit integration when saturated or in emergency.
- Pitfall: Evaluating distance metrics when a lead is absent or traveling far above set speed.
  - Fix: Restrict distance SSE to active following windows where regulation is applicable.
- Pitfall: Using recorded ego speed rather than simulated dynamics.
  - Fix: Always propagate ego state from the commanded acceleration and dt.
- Pitfall: Unclamped acceleration or missing safety caps leads to unrealistic behavior.
  - Fix: Apply configured acceleration limits and speed caps consistently across modes.
- Pitfall: Incorrect TTC computation when not closing.
  - Fix: Only compute TTC if relative_speed > 0; otherwise leave it unset.
- Pitfall: Coupling auto-tuning into the runtime simulation.
  - Fix: Keep tuning separate; the simulation must load gains from YAML at runtime.

## Optional Script Usage

A helper script `scripts/acc_metrics.py` is included to compute common ACC metrics from the simulation log. It supports configurable set speed, time headway, minimum gap, steady-state window, and thresholds.

Example:
- python3 scripts/acc_metrics.py --csv simulation_results.csv --set-speed 30.0 --time-headway 1.5 --min-gap 10.0 --ss-window 20 --rise-low-frac 0.1 --rise-high-frac 0.9 --min-distance-threshold 5.0

It prints rise time, overshoot, steady-state errors, minimum distance, and optional pass/fail checks when thresholds are provided.
