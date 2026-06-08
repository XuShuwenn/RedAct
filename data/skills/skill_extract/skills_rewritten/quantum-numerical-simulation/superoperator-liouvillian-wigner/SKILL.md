---
name: superoperator-liouvillian-wigner
description: "Build composite Liouvillians and compute large-grid Wigner functions robustly by using consistent superoperator tensoring, symmetry reduction, validation, and chunked output."
---

# Robust Composite Liouvillian and Wigner Workflow

This skill helps avoid common failure modes when constructing open-system Liouvillians for coupled subsystems (e.g., cavity + spin ensembles) and computing large-grid Wigner functions. It focuses on consistent superoperator construction, symmetry-based reductions, solver selection, incremental verification, and streaming CSV output to handle heavy workloads.

## When to Use

Use this skill when you need to:
- assemble a composite Liouvillian for coupled quantum subsystems (e.g., cavity + atoms)
- include local and collective dissipation consistently
- solve for a steady state and trace out a subsystem (e.g., the cavity field)
- compute and export large Wigner-function grids (e.g., 1000×1000) without exhausting resources

## Core Workflow

1) Environment and Interface Checks
- Import your quantum toolkit (e.g., QuTiP). Verify availability of key functions (superoperator construction, steady-state solver, Wigner computation).
- Record library versions and solver signatures to confirm supported methods. Avoid guessing; inspect the function signature and documentation.

2) Choose a Consistent Representation
- Work in superoperator space for open systems: build the Liouvillian L, not just a Hamiltonian H.
- Do not mix Hilbert-space operators and superoperators. All terms added together must be superoperators.
- For identical spin ensembles, prefer a symmetry-reduced representation (e.g., permutationally invariant Dicke basis) to keep dimensions manageable.

3) Subsystem Construction (Hilbert operators)
- Cavity: define its Hilbert-space dimension and create ladder operators (e.g., a, a†) and H_cav.
- Spins: define collective operators (e.g., J±, Jz) in a consistent basis. If the toolkit provides a reduced basis generator for identical atoms, use it.

4) Dissipators
- Cavity dissipation: create collapse operators (e.g., √κ·a) for the cavity.
- Spin dissipation: handle local channels (e.g., dephasing, pumping, emission) and collective channels (e.g., collective emission/pumping) carefully. Avoid double counting by choosing a single consistent builder (local vs collective) per channel and matching the representation.

5) Compose the Full Liouvillian
- Convert the joint Hamiltonian to a commutator superoperator: L_H = −i [H_total, ·] using superoperator builders (i.e., spre/spost).
- Build subsystem Liouvillians/dissipators as superoperators.
- Combine the parts with superoperator tensor products: L_total = L_cavity ⊗ I_spin + I_cavity ⊗ L_spin + L_coupling.
- Ensure dimensions align and types remain "super" throughout.

6) Steady-State Solve
- Use a steady-state solver that accepts superoperators (e.g., a Liouvillian). Confirm this by reading the function signature.
- Start with a small test (reduced Hilbert space or a single loss case) to validate convergence and runtime.
- Select a solver method appropriate for problem size (e.g., iterative) and confirm convergence before scaling up.

7) Partial Trace to Subsystem
- After obtaining the full steady state ρ_ss, trace out the unwanted subsystem to get the target subsystem state (e.g., the cavity density matrix).
- Verify subsystem dimensions and ordering before ptrace.

8) Wigner Function on Large Grids
- Create x/p (phase-space) vectors. For very large grids, compute in chunks (rows or columns) to avoid holding the entire matrix in memory.
- Write results incrementally to CSV (append rows/columns as they are computed). Do not wait for the full matrix in memory.

9) Scale Up with Monitoring
- Run and export one case first to benchmark runtime. Add progress logging.
- Only then scale to all cases. Keep resource usage bounded by chunking and sequential processing.

## Verification

Perform these checks at each stage before proceeding:
- Type and space consistency: ensure every term combined into L has type "super" and compatible dims. Avoid mixing Hilbert operators with superoperators.
- Shape checks: L must be square in the vectorized operator space. Confirm subsystem tensoring produces expected composite dimensions.
- Steady-state validity: ρ_ss should be Hermitian with trace ≈ 1 and non-negative eigenvalues within tolerance.
- Subsystem state: after ptrace, confirm the resulting density matrix has expected dimension and is valid (same checks as above).
- Wigner sanity: the Wigner grid has the requested shape; values are finite (no NaN/Inf). For a basic normalization check, ensure the integral/sum over the grid is reasonable within method-specific conventions.
- CSV completeness: confirm the file exists and has the expected number of rows and columns. Avoid buffered writes by flushing during chunked output.

## Common Pitfalls (and Avoidance)

- Mixing spaces: adding Hilbert-space operators directly to superoperators causes type/size mismatches. Always convert Hamiltonians to commutator superoperators and ensure dissipators are superoperators before summation.
- Wrong solver input: calling a steady-state solver with H instead of L leads to failures or hangs. Verify the solver expects a Liouvillian.
- Dimension mismatches: tensoring subsystems inconsistently produces incorrect shapes. Use superoperator-aware tensoring and verify dims before solving.
- Collapse-operator confusion: local versus collective dissipation must be defined consistently in the chosen basis. Avoid building both for the same channel unless the physics requires it and the representation supports it.
- Ignoring symmetry reduction: building full explicit spin spaces for many atoms can make the problem intractable. Use reduced bases where valid (e.g., identical atoms).
- Monolithic Wigner grids: computing a 1000×1000 grid in one call can exhaust memory/time. Compute in chunks and stream to CSV.
- No incremental verification: running a heavy four-case computation without a single-case smoke test increases failure risk. Validate each step on smaller sizes first.
- Silent long runs: lack of progress logs and checks leads to wasted time. Add periodic status messages and checkpoint outputs.

## Success Criteria

- Composite Liouvillian is constructed solely from superoperators with consistent dimensions.
- Steady-state solver returns a valid density matrix (Hermitian, trace 1, positive semidefinite within tolerance).
- Subsystem density matrix has correct dimension and passes validity checks.
- Wigner CSVs match the requested grid size, and values are numeric and finite.
- Runtime remains tractable via symmetry reduction, solver selection, and chunked output.

## Optional Script Usage

The included helper provides reusable utilities for:
- safe commutator superoperator construction from a Hilbert-space Hamiltonian
- basic density-matrix validation
- chunked Wigner computation and streaming CSV output

Example sketch:
- Build L_total using superoperator tools from your main script.
- Solve for ρ_ss and reduce to the target subsystem.
- Use `chunked_wigner_to_csv(rho_sub, xvec, pvec, 'output.csv')` to stream results without large memory spikes.
