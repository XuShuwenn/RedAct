---
name: robust-qutip-steady-wigner
description: "Use this skill to reliably compute steady-state density matrices and cavity Wigner functions for open quantum systems in QuTiP while avoiding solver, dimension, and performance pitfalls."
---

# Robust Open-Quantum Steady State and Wigner Output (QuTiP)

This skill distills failure-avoidance guidance for computing steady states of open quantum models and exporting cavity Wigner functions in CSV form. It focuses on preventing common issues observed when building Liouvillians, mixing local and collective channels, choosing solvers, tracing subsystems, and handling large phase-space grids.

## When to Use

Activate this skill when you need to:
- Build a Liouvillian for an open quantum model (e.g., light–matter systems) and compute its steady state in QuTiP
- Include both local (site-resolved) and collective (J-operator) dissipation channels correctly
- Trace out subsystems and compute a cavity field Wigner function on a dense grid
- Save large Wigner grids to CSV without timeouts or format mismatches

## Core Workflow

1) Decide the representation before building operators
- Only collective processes (e.g., J_±, J_z): a symmetric (Dicke) representation is valid.
- Any local processes (e.g., individual dephasing/pumping/emission): do NOT approximate local sums with a single collective J-operator. Either:
  - Build explicit local collapse operators in the full 2^N spin space, or
  - Use a permutational-invariance framework (e.g., QuTiP PIQS) that correctly encodes local processes in a symmetric basis.

2) Construct operators in a consistent tensor order
- Choose a fixed subsystem ordering (e.g., [cavity, spins]).
- Cavity operators: a = tensor(destroy(n_max), identity_spin).
- Local spin operators (full space): for spin j, create operators with tensor([... sig, qeye, ...]) at the j-th site.
- Collective spin operators (symmetric space): use jmat and embed with tensor(qeye(n_max), j_op) only if the Liouvillian is constructed consistently for that representation.

3) Build the Liouvillian with correct collapse operators
- Cavity loss: sqrt(kappa) * a.
- Local dephasing: sqrt(gamma_phi) * sigma_z^(i) (each site i, full space) — do not replace by a scaled J_z in the collective basis.
- Local pumping: sqrt(gamma_up) * sigma_+^(i) (each site i).
- Local emission: sqrt(gamma_down) * sigma_-^(i) (each site i).
- Collective pumping/emission: sqrt(gamma_collective) * J_± (only if using a representation consistent with collective channels).

4) Choose a steady-state strategy that scales
- Estimate the Hilbert space size d and Liouvillian size ~ d^2:
  - Symmetric spins: d ≈ n_max × (N + 1).
  - Full spin space: d ≈ n_max × 2^N.
- Steady-state solver selection:
  - Small d: use method="direct" or "eigen".
  - Larger d: try iterative methods (e.g., "iterative-bicg", "iterative-gmres", "iterative-lgmres") with use_rcm=True, suitable tolerances, and iteration caps.
- Fallback plan: if steadystate fails or stalls, time-evolve with mesolve to large times and use the final state as an approximation. Verify with a Liouvillian residual (see Verification).

5) Trace and set dimensions explicitly
- Before ptrace, ensure rho_ss.dims reflects [subsys_dims, subsys_dims] in the same order you used to build operators.
- Then use ptrace with the correct index of the cavity subsystem.

6) Wigner function on large grids without stalling
- Start with a coarse grid (e.g., 50–100 points) to validate correctness and performance.
- Only after validation, compute the large grid (e.g., 1000×1000) once.
- Compute Wigner for the cavity-reduced density matrix only; avoid passing the full state to wigner.
- Save the Wigner array directly as a numeric matrix CSV (no headers) if the specification requires just the data.

7) Export results deterministically
- Ensure the CSV contains exactly the requested numeric data (e.g., a matrix of shape grid_p × grid_x). Avoid adding headers unless explicitly requested.
- Confirm filenames match the expected convention.

## Verification

Perform these checks before finalizing results:
- Density matrix validity:
  - Hermiticity: rho ≈ rho.dag() (within tolerance)
  - Trace: abs(tr(rho) - 1) < tolerance
  - Positivity: min(eig(rho)) ≥ -epsilon (small negative values may be numerical)
- Steady-state residual: build L = liouvillian(H, c_ops). Compute r = ||L * vec(rho)|| / ||vec(rho)|| and require r < tolerance.
- Subsystem dimensions:
  - rho.dims matches your subsystem ordering
  - Cavity reduced state has dimension n_max × n_max
- Wigner grid:
  - Shape is exactly (n_points, n_points)
  - x, p ranges match the specification
- Output files:
  - One file per required case
  - Numeric-only CSV if specified; file sizes consistent with grid density

## Common Pitfalls (and How to Avoid Them)

- Mixing local and collective channels in the wrong basis
  - Symptom: Results are unphysical or solvers stall.
  - Avoidance: Use full local operators in 2^N spin space, or use a PIQS/symmetric method that explicitly supports local channels. Do not approximate local sums with a single J-operator plus an N factor.

- Tensor dimension mismatches
  - Symptom: Errors when constructing tensor operators or during ptrace.
  - Avoidance: Keep a consistent subsystem order. Build operators accordingly. Set rho.dims explicitly before ptrace.

- Prematurely computing a huge Wigner grid
  - Symptom: Timeouts and no outputs.
  - Avoidance: Validate with a small grid first, profile each step (steadystate vs Wigner), then scale up once.

- Using non-existent or incorrect API options
  - Symptom: AttributeError/TypeError (e.g., unsupported arguments like set_num_threads, or invalid wigner kwargs).
  - Avoidance: Consult QuTiP docs for steadystate and wigner. Keep method names and kwargs valid for the installed version.

- Unchecked solver convergence
  - Symptom: Solver "completes" but yields a non-steady state.
  - Avoidance: Compute the Liouvillian residual and verify normalization/positivity. If residual is large, switch method or use mesolve fallback.

- CSV format mismatches
  - Symptom: Files include headers or long-form rows when a raw matrix is expected.
  - Avoidance: Match the exact output format requirement. If only the Wigner matrix is requested, write a numeric matrix with no header.

## Optional Script Usage

The scripts/steadystate_helpers.py helper provides reusable utilities:
- solve_steadystate_with_fallback(H, c_ops, ...): Try multiple steadystate methods with sensible defaults; falls back to mesolve if needed.
- liouvillian_residual(H, c_ops, rho): Verify steady-state quality.
- check_density_matrix(rho): Quick validity checks.
- save_wigner_matrix_csv(W, path): Save a numeric matrix CSV with no headers.
- make_grid(xmin, xmax, n): Generate evenly spaced grid points.

Example sketch:
- Build H and c_ops correctly (per the chosen representation).
- rho_ss = solve_steadystate_with_fallback(H, c_ops, tol=1e-10)
- Set rho_ss.dims to your subsystem structure, then rho_cav = rho_ss.ptrace(cavity_index)
- x = make_grid(xmin, xmax, n_points); p = make_grid(pmin, pmax, n_points)
- W = qutip.wigner(rho_cav, x, p)
- save_wigner_matrix_csv(W, "caseN.csv")
- Assert liouvillian_residual(H, c_ops, rho_ss) is below tolerance

Success criteria:
- Correct operator construction for the intended dissipation model
- Converged steady state with small Liouvillian residual
- Correct cavity trace-out and Wigner grid shape/range
- Files written in the required format and count
