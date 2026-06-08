---
name: pid-acc-simulation
description: "Design, implement, and validate an adaptive cruise control (ACC) simulation with PID control, mode logic, segmented metrics, and reproducible I/O."
---

# PID-Based Adaptive Cruise Control Simulation

This skill provides a reusable workflow for building an ACC simulation that:
- maintains a set speed when no lead vehicle is present
- follows a lead vehicle at a safe time-headway + minimum gap
- triggers emergency braking when time-to-collision (TTC) is critically low
- logs results with an exact, reproducible CSV format
- evaluates performance with phase-segmented metrics

It distills robust patterns from multiple implementations, emphasizing anti-windup, mode-specific PID state handling, correct distance modeling, and stable metric definitions.

## When to Use

Use this skill when you need to:
- implement an ACC controller with cruise/follow/emergency modes
- integrate PID controllers for speed and distance with physical limits
- simulate ego/lead motion using configuration + sensor data
- compute performance metrics without bias from transient/unstable segments
- ensure outputs match strict format/time-step requirements

## Core Workflow

1) Inspect inputs and configuration
- Parse the configuration (e.g., YAML) to obtain:
  - vehicle limits (max_acceleration, max_deceleration)
  - ACC settings (set_speed, time_headway, min_distance, emergency_ttc_threshold)
  - simulation dt
- Parse sensor data (e.g., CSV) to obtain time series with columns:
  - time (monotonic)
  - lead_speed, distance (may be missing/blank when no lead)
  - any additional fields are optional
- Identify lead presence windows by checking for non-empty lead_speed and distance.

2) Implement a robust PID controller
- Include:
  - proportional, integral, derivative terms
  - output clamping (min/max)
  - integral anti-windup (e.g., conditional integration or back-calculation) and optional integral clamp
  - reset() to clear state on mode transitions
- Derivative term: compute from error difference with dt>0; suppress spike on first call.
- Pause or limit integral accumulation when output saturates or when controller is inactive for the current mode.

3) ACC mode logic (compute function)
- Inputs: ego_speed, optional lead_speed, optional distance, dt.
- Desired gap: desired_distance = min_distance + time_headway * ego_speed.
- TTC: If closing (ego_speed > lead_speed), ttc = distance / (ego_speed - lead_speed); otherwise treat as infinite/not applicable.
- Mode selection:
  - cruise: no valid lead inputs
  - emergency: ttc below threshold and closing
  - follow: lead present but not emergency
- Control actions:
  - cruise: speed_error = set_speed - ego_speed → speed PID → clamp to acceleration limits
  - emergency: command max deceleration; do not rely on PID
  - follow: 
    - distance_error = distance - desired_distance (positive = too far, negative = too close)
    - distance PID is primary to regulate gap
    - speed PID acts as cap/limit to avoid exceeding set_speed and to smooth transitions
    - blending pattern:
      - if distance_error < 0 (too close): braking must dominate → accel_cmd = min(dist_accel, speed_accel)
      - if distance_error >= 0 (too far): allow acceleration up to the speed limit → accel_cmd = min(dist_accel, speed_accel)
    - reset or freeze the speed PID integral when it is not the active controller to prevent windup
- Always clamp accel_cmd within physical limits.

4) Distance modeling in simulation
- Track positions dynamically:
  - Integrate ego position from the simulated ego_speed
  - Integrate lead position using lead_speed from the sensor
  - Initialize lead position when the lead first appears: lead_pos = ego_pos + measured_distance_at_appearance
  - Compute simulated distance = lead_pos - ego_pos while lead is present; set distance to None when lead is absent
- Update order per time step (dt):
  - Compute control using current states
  - Record the current state to the CSV (time-aligned logging)
  - Update ego_speed and positions for the next step
- This avoids the pitfall of using a static sensor distance that cannot respond to control.

5) I/O and format guarantees
- Load PID gains from an external file at runtime (e.g., tuning_results.yaml). Do not embed auto-tuning in the main simulation.
- Produce a CSV with a fixed column order and blanks for missing values, e.g.:
  - time, ego_speed, acceleration_cmd, mode, distance_error, distance, ttc
- Ensure the first logged row reflects the initial state before any update.
- Ensure the number of rows equals the simulation time span divided by dt plus one, and that times are monotonic.

6) Metrics (segmented and stable)
- Separate metrics by phase to avoid mixing cruise and follow dynamics:
  - Speed rise time: time to reach 90% of set_speed during the initial cruise segment
  - Speed overshoot: maximum speed above set_speed only during pure cruise segments
  - Speed steady-state error: late portion of a stable cruise segment (e.g., final few seconds)
  - Distance steady-state error: a stable portion of a follow segment (e.g., middle/latter part, excluding emergency and large transients)
  - Minimum distance: minimum of distance where valid
- If available, prefer a “settled” follow window where modes are continuously follow, and optionally filter out emergency steps.

## Verification Checklist

Pre-simulation
- Config fields present and sane (limits, set_speed, dt, thresholds)
- PID gains loaded from external file; within allowed ranges
- Sensor time monotonic and dt consistent (within tolerance)

Controller and mode logic
- PID has output clamps and anti-windup
- PID reset on mode changes
- Emergency mode bypasses PID to guarantee max decel
- Follow blending respects set_speed cap and allows gap closing when too far

Simulation dynamics
- Lead position initialized on first detection and integrated thereafter
- Distance computed from positions while lead present; None otherwise
- Logging happens before updating state (first row shows true initial state)
- Acceleration commands clamped to physical limits

Output format
- CSV column order exact and stable
- Missing values serialized as blanks
- Row count and time column consistent with dt and total duration

Metrics
- Speed metrics computed on cruise segments only
- Distance metrics computed on stable follow windows; exclude emergency steps
- Minimum distance strictly above safety threshold in results

## Common Pitfalls and Fixes

- Pitfall: Using sensor distance directly throughout → control cannot affect distance
  - Fix: Track lead/ego positions; compute distance dynamically after initialization

- Pitfall: Integral windup causing overshoot and slow recovery
  - Fix: Add anti-windup (conditional integration, integral clamp), reset or freeze integral on mode change/inactivity

- Pitfall: Blending logic prevents gap closing (e.g., always taking min of controllers)
  - Fix: Use distance controller as primary in follow; apply speed controller as cap; ensure acceleration is allowed (up to limit) when too far

- Pitfall: Overshoot calculated across follow/emergency periods
  - Fix: Restrict speed overshoot to cruise segments only

- Pitfall: Incorrect logging order (updating before recording)
  - Fix: Record current state, then update; ensures time-aligned telemetry

- Pitfall: Mismatched CSV schema or non-blank missing values
  - Fix: Enforce exact column order and blank strings for missing numeric fields

## Optional Script Usage

This skill includes two helper scripts.

1) PID utility (scripts/pid.py)
- Provides a reusable PID controller with anti-windup and output clamps.
- Example:
  - from scripts.pid import PIDController
  - pid = PIDController(kp, ki, kd, output_min=-8.0, output_max=3.0, integral_limit=100.0)
  - u = pid.compute(error, dt)
  - pid.reset() on mode changes

2) Segmented metrics (scripts/segmented_metrics.py)
- Computes phase-segmented metrics from a simulation CSV with columns:
  - time, ego_speed, acceleration_cmd, mode, distance_error, distance, ttc
- CLI example:
  - python3 scripts/segmented_metrics.py --csv simulation_results.csv --set-speed 30 --dt 0.1 --follow-stable-window 10
- Outputs JSON with rise_time_90, overshoot_pct_cruise, speed_ss_error_cruise, distance_ss_error_follow, min_distance, and basic validations.

Adopt or adapt these scripts to your project; they are generic and configuration-driven.
