---
name: mpc-simulator-controller
description: "Design, implement, and verify a linearized MPC controller that works with a provided simulator, generates required JSON outputs, and meets task-defined performance targets."
---

# MPC Controller Workflow for Simulator-Based Tasks

This skill guides an agent to derive a linearized model, implement a compatible predictive controller (MPC/LQR-style), run a simulator for the required duration, log results in the task-defined schema, compute metrics, and validate outputs against performance targets.

## When to Use

Activate this skill when the task:
- provides a simulator and a configuration file for an engineered system
- requires deriving a linearized state-space model at a specified operating point
- asks for designing an MPC-style controller with a prediction horizon and cost weights
- mandates generating specific JSON outputs (controller parameters, control log, metrics)
- defines performance targets (e.g., steady-state error, settling time, bounds on signals)

## Core Workflow

1. Inspect the Environment
- Read the simulator source to understand dynamics, interfaces, timestep, and available signals.
- Read configuration to obtain the initial reference operating point and any reference schedule (e.g., step changes) used for evaluation.
- Do not modify the simulator. Design your controller to integrate with the existing API.

2. Derive the Linearized Model
- Identify the state vector x and input vector u at the reference operating point.
- Compute the continuous-time linearization (A, B) using the simulator’s dynamics at the operating point and the provided references.
- Discretize the model using the simulator timestep dt to obtain (A_d, B_d). If exact matrix exponential is unavailable, use a stable forward Euler fallback and document the choice.
- Verify dimensions: A_d is (n_x × n_x), B_d is (n_x × n_u).

3. Choose Controller Structure and Weights
- Select a prediction horizon N within task-specified bounds.
- Choose positive weights Q (emphasize key states) and R (penalize control effort). For diagonal weights, ensure lengths match n_x and n_u.
- Compute a stabilizing feedback gain. If a full MPC optimizer is not required by the task, a discrete-time LQR gain (K) computed from (A_d, B_d, Q, R) is often sufficient as a baseline in a receding-horizon loop.
- Optionally add integral augmentation if offset-free tracking is required and permitted.

4. Implement the Control Loop
- Initialize simulator at the reference state.
- At each timestep:
  - Read current state and reference (ensure reference is aligned with simulator’s schedule).
  - Compute control action (e.g., u = u_ref − K(x − x_ref)). If using MPC, solve the finite-horizon problem and apply the first control move.
  - Apply control to the simulator and advance one step.
  - Log data per the task schema: time, tensions, velocities, control_inputs, references.
- Ensure the loop runs for at least the required duration (e.g., 5 seconds), including the final timestep. Account for floating-point precision when deciding stop conditions.

5. Compute Metrics
- Steady-state error: compute mean tracking error versus the reference after transients (or as specified by the task). Use task-defined tolerance windows and reference values from configuration.
- Settling time: the earliest time when signals enter and remain within the specified tolerance band around their references.
- Peak/minimum values: compute maxima and minima over the logged window and verify bounds.
- Write metrics to metrics.json exactly as required by the task.

6. Write Controller Parameters
- Save controller parameters to controller_params.json, including:
  - horizon_N (an integer within bounds)
  - Q_diag (n_x positive floats)
  - R_diag (n_u positive floats)
  - K_lqr (n_u × n_x matrix or the final controller gain matrix expected by the task)
  - A_matrix (n_x × n_x)
  - B_matrix (n_x × n_u)
- Validate shapes and positivity before writing.

7. Validate Outputs
- Verify JSON schema compliance:
  - controller_params.json contains required keys with correct shapes
  - control_log.json has phase set appropriately and data entries spanning the required duration
  - metrics.json contains all required metrics fields
- Confirm performance targets are met per task specifications.

## Verification

Perform these checks before finalizing:
- Linearization point: Model derived exactly at the initial reference operating point from configuration.
- Discretization: Use simulator dt; confirm numerical stability and correct shapes.
- Controller bounds: horizon_N adheres to task bounds; Q_diag and R_diag lengths match n_x and n_u and have positive entries.
- Gain shape: K has shape (n_u × n_x) and is consistent with A_d, B_d.
- Logging window: last_time − first_time ≥ required_duration − epsilon (epsilon for float tolerance). Include the final timestep in logging.
- Log schema: every entry contains the required fields; lengths are consistent across entries; references align in dimension with the state vector.
- Metrics correctness: computed against the proper reference signals; no reliance on instantaneous pre-step values; settling time computed with “remain within band” semantics.

## Common Pitfalls

- Wrong operating point: Deriving the model at a different state than the initial reference leads to large errors. Always read the reference from configuration and linearize there.
- Mixing continuous and discrete models: Applying continuous-time gains to discrete dynamics (or vice versa) breaks stability. Always discretize with simulator dt.
- Dimension mismatches: K must be (n_u × n_x); Q_diag length = n_x; R_diag length = n_u; references must match the state dimension used.
- Off-by-one duration: Logging up to but not including the final timestep can produce slightly under-5-second logs. Include the final step and use a small epsilon for float comparisons.
- Overly strict verification: Comparing durations or tolerances with exact equality fails due to floating-point precision. Use tolerance margins.
- Ignoring reference schedule: Computing metrics against the wrong reference (e.g., not updating after a step change) corrupts results.
- Simulator modification: Changing simulator code invalidates the setup. Keep the simulator unmodified and adapt the controller interface instead.

## Success Criteria

- Controller parameters file includes all required fields with correct shapes and positive weights.
- Control log spans the full required duration and conforms to the task schema.
- Metrics meet all task-defined targets.
- No modifications to the simulator; controller integrates via documented interfaces.

## Optional Script Usage

Use the helper script in scripts/mpc_utils.py to:
- compute a discrete-time LQR gain (dlqr)
- discretize (A, B) with exact or Euler fallback
- validate controller_params.json, control_log.json, and metrics.json
- compute settling time from logged signals in a task-agnostic manner

This utility encodes reusable algorithms and validations across similar tasks.
