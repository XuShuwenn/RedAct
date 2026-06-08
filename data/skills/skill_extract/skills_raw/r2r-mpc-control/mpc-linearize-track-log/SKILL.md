---
name: mpc-linearize-track-log
description: "Design an MPC around an operating-point linearization, track time-varying references with feedforward, and emit validated logs/metrics for simulator-based control tasks."
---

# Operating-Point Linearization + Finite-Horizon LQR MPC with Logging

This skill packages a reusable workflow for tasks that require: (1) deriving a linearized state-space model of a known simulator around a reference operating point, (2) designing a finite-horizon LQR-based MPC for reference tracking, (3) running a closed-loop simulation for a specified duration, and (4) writing validated JSON outputs (controller parameters, control log, and performance metrics).

The pattern is broadly applicable to web-handling lines, multi-section tension/velocity chains, and other systems where the simulator offers reference trajectories and a time step.

## When to Use

Activate this skill when a task asks you to:
- derive a linearized state-space model at a reference operating point
- design an MPC (often via finite-horizon LQR) for tracking given references
- run the controller with the original simulator (do not modify the simulator)
- log time histories and compute performance metrics under specified formats

## Core Workflow

1. Inspect the simulator and references
   - Discover state and input dimensions, state ordering, time step dt, and any reference APIs (e.g., get_reference()).
   - If the simulator provides steady-state or reference trajectories (x_ref, u_ref), use them as the operating point for linearization and as feedforward during control.

2. Derive continuous-time Jacobians (linearization)
   - Let x be the state (dimension n) and u be the control input (dimension m). Linearize f(x, u) at (x_ref, u_ref):
     - A_c = ∂f/∂x |_(x_ref,u_ref)
     - B_c = ∂f/∂u |_(x_ref,u_ref)
   - For chain-like systems (e.g., tensions/velocities): pay close attention to boundary conditions and state ordering when computing partial derivatives. Ensure derivatives of coupling terms (e.g., neighbor sections) and input channels are included only where they physically apply.

3. Discretize consistently with the simulator
   - Use the same integration notion as the simulator to avoid model mismatch.
     - If the simulator integrates with forward Euler: A_d = I + dt*A_c, B_d = dt*B_c.
     - If you know the simulator assumes exact discretization for LTI models, use the augmented-matrix exponential method for (A_d, B_d).
   - Consistency between your A_d, B_d and the simulator’s step is more important than the discretization method’s formal accuracy.

4. Choose Q, R, and horizon N
   - Use diagonal Q and R for transparent tuning. Emphasize the most critical states (e.g., tensions) in Q; keep R positive and sized m×m.
   - Choose horizon N within the task’s allowed range (if specified). Typical values: 5–20 steps for fast systems.

5. Compute LQR solutions
   - Infinite-horizon (terminal) LQR via DARE: P_inf = solve_discrete_are(A_d, B_d, Q, R). K_lqr = (R + BᵀP_infB)⁻¹ BᵀP_infA.
   - If no DARE solver is available, use a discrete Riccati fixed-point iteration until P converges.
   - Finite-horizon LQR (backward recursion) with terminal cost P_terminal (use P_inf when available; else Q). Compute K_N−1..K_0 and apply K_0 at the current step.

6. Implement the tracking control law
   - At each time step:
     - Obtain x (measured/estimated), and (x_ref, u_ref) from the simulator.
     - Form deviation dx = x − x_ref.
     - Compute deviation control du = −K_0 · dx.
     - Apply u = u_ref + du (optionally clip to actuator limits if known).
   - Use feedforward (x_ref, u_ref) from the simulator to eliminate bias due to reference changes. Integral action is optional and should be added only if needed; it can slow settling or induce windup if done carelessly.

7. Run the closed-loop simulation and log
   - Simulate for at least the required duration (e.g., 5 seconds).
   - At each step, log a JSON-serializable record containing:
     - time: float seconds
     - states split into meaningful groups (e.g., tensions first, velocities after)
     - control inputs (u)
     - full reference state vector (and optionally reference inputs)
   - Ensure numeric types are Python floats, not NumPy scalars, to keep JSON compatibility.

8. Compute performance metrics
   - Steady-state error (SSE): mean absolute error over the last window (e.g., last 1.0 s) between tracked variables and their references.
   - Settling time: after a known event time t_step, find the earliest time when the absolute error for all tracked channels remains within a specified band (e.g., ±2 units) for the remainder or for a confirmation window.
   - Extremes: max and min values of the tracked variables over the entire run.

9. Save controller parameters and logs
   - controller_params.json should include at least:
     - horizon_N (int, within allowed range if specified)
     - Q_diag (list of n positive floats)
     - R_diag (list of m positive floats)
     - K_lqr (list of lists, shape m×n)
     - A_matrix (list of lists, shape n×n)
     - B_matrix (list of lists, shape n×m)
   - control_log.json should include:
     - phase: "control"
     - data: an array of per-step entries with time, states, control_inputs, and references
   - metrics.json should include steady_state_error, settling_time, max and min (names per task spec).

## Verification

- Model and gain checks
  - A_matrix is n×n, B_matrix is n×m, K_lqr is m×n; dimensions are consistent.
  - R and Q are positive (diagonals > 0), with lengths matching m and n respectively.
  - Closed-loop eigenvalues of (A_d − B_dK_lqr) suggest stability (spectral radius < 1 for the linear model).

- Log checks
  - control_log data spans at least the required duration (e.g., dt×len(data) ≥ 5.0 s).
  - time increases monotonically and ends near the intended final time.
  - Each data entry has all required fields and correct lengths.

- Metrics checks
  - Steady-state error is computed over a clearly defined final window (e.g., last 1.0 s).
  - Settling time uses a clear band and requires persistence (remains within band thereafter or for a confirmation window).
  - Extremes are computed over the full run.

- File schema checks
  - All JSON is valid and uses built-in types (no NumPy arrays or scalars).
  - Any task-specific bounds (e.g., horizon range, min/max values) are satisfied.

## Common Pitfalls

- Discretization mismatch: Using a discretization scheme different from the simulator’s integration (e.g., exact exponential vs forward Euler) can cause performance gaps. Match the simulator’s integration step.
- Wrong state ordering or boundary terms: For chain dynamics, misplacing neighbor couplings or ignoring boundary conditions leads to incorrect Jacobians.
- Missing feedforward: Using u = −Kx alone ignores provided references and yields offset errors during reference steps.
- Incorrect Riccati recursion sign/order: Ensure P update uses P ← Q + AᵀP(A − BK) and K = (R + BᵀPB)⁻¹BᵀPA.
- Misusing K sequence: For finite-horizon LQR in a receding-horizon loop, apply the first-step gain K_0 at the current step.
- JSON serialization errors: Attempting to dump NumPy types directly will break JSON. Convert to Python floats/lists.
- Insufficient duration or missing fields: Logs must meet duration requirements and include all specified fields.
- Overusing integral action: Adding integral terms without anti-windup or correct tuning can degrade settling and violate constraints.

## Optional Script Usage

The provided script scripts/mpc_utils.py contains reusable primitives:
- dare_lqr(A, B, Q, R): infinite-horizon discrete LQR via SciPy’s DARE if available, else a Riccati fixed-point iteration.
- finite_horizon_gains(A, B, Q, R, N, P_terminal=None): returns a K sequence {K_0..K_{N−1}} via backward recursion.
- euler_discretize(A_c, B_c, dt) and exact_discretize(A_c, B_c, dt): discretization helpers.
- compute_metrics(times, values, refs, dt, band=2.0, ss_window_s=1.0): steady-state error, settling time (with persistence), max, min.
- validate_outputs(...) to perform shape and range checks before writing files.

Example (pseudocode):
- Derive A_c, B_c from your physics.
- A_d, B_d = euler_discretize(A_c, B_c, dt)
- K_lqr, _ = dare_lqr(A_d, B_d, Q, R)
- K_seq = finite_horizon_gains(A_d, B_d, Q, R, N, P_terminal=None)
- At each step: u = u_ref − K_seq[0] @ (x − x_ref)
- Log and compute metrics with compute_metrics.

Success criteria: logs span the required time; controller_params.json fields are present with correct shapes and positivity; metrics meet task thresholds when applicable.
