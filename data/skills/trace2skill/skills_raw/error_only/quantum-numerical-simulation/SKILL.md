---
name: quantum-numerical-simulation
description: "Simulate open Dicke model steady state and calculate cavity field Wigner function for different loss cases."
---

# Open Dicke Model Quantum Simulation

## When to Use

- Simulate quantum many-body systems
- Calculate Wigner functions for cavity fields
- Solve Liouvillian for steady state

## Scope Guardrails

- Use only model details explicitly given in the task or available local materials.
- If a paper/reference cannot be accessed or parsed, do **not** invent dissipators, rates, or operator definitions from memory.
- If any model term is unspecified, state the ambiguity and use the most conservative formulation supported by the task statement.

## Model Parameters

- N = 4 (two-level systems)
- ω₀ = ωc = 1
- g = 2/√N
- κ = 1 (cavity loss)
- n_max = 16 (photon cut-off)


- Treat these values as fixed task requirements unless the user explicitly allows changes.
- Do not change `N=4` or `n_max=16` in the final script/run. If you temporarily shrink the model for debugging, restore these exact values before producing outputs.

## 4 Loss Cases

1. Local dephasing + local pumping: γφ=0.01, γ↑=0.1
2. Local dephasing + local emission: γφ=0.01, γ↓=0.1
3. Case 2 + collective pumping: γφ=0.01, γ↓=0.1, γ⇑=0.1
4. Case 2 + collective emission: γφ=0.01, γ↓=0.1, γ⇓=0.1

## Critical Modeling Constraint

- Treat **local** spin channels literally: local dephasing, local pumping, and local emission must be implemented as sums of site-resolved collapse operators on the **full spin Hilbert space** tensor the cavity space.
- For local dephasing, use one collapse operator per spin: `sqrt(γφ) · σz^(i)` (or a conventionally normalized equivalent used consistently by the solver).
- For local pumping, use one collapse operator per spin: `sqrt(γ↑) · σ+^(i)`.
- For local emission, use one collapse operator per spin: `sqrt(γ↓) · σ-^(i)`.
- Collective operators are appropriate only for the explicitly collective channels: add `sqrt(γ⇑) · J+` for collective pumping and `sqrt(γ⇓) · J-` for collective emission.
- Do **not** replace requested local Lindblad terms with collective operators such as `Jz`, `J+`, or `J-`, and do **not** restrict spins to the symmetric Dicke sector when local dissipation is present.
- Case 4 must include both the local-emission set `{σ-^(i)}` and the separate collective-emission operator `J-`; they are not interchangeable and must not be merged into the same channel.
- For `N=4`, the full spin space is small enough to model exactly in QuTiP; prefer correctness over symmetry reduction.

## Workflow

1. Build the Hamiltonian and collapse operators strictly from the provided task parameters.
2. Preserve the requested dissipation structure exactly: local channels must act on each spin separately in the full tensor-product spin space, while collective channels act on the full spin ensemble.
3. Keep all operators in one consistent Hilbert-space representation; check composite operator/Liouvillian `dims` and shapes before calling `steadystate`, and do **not** fix incompatible superoperators by manually overwriting `.dims`.
4. Before full-scale runs, validate one reduced but structurally faithful end-to-end pipeline: build the model, solve one steady state, confirm subsystem ordering for `ptrace`, compute a small Wigner grid, and write a test CSV.
5. Solve the full-parameter steady state case-by-case.
6. Trace out spins → cavity state, confirming subsystem ordering before `ptrace`.
7. Calculate the Wigner function on grid x,p ∈ [-6,6], 1000×1000.
8. Save each finished case immediately as CSV: `1.csv`, `2.csv`, `3.csv`, `4.csv`.
9. If you used reduced settings for diagnosis, restore the exact required parameters before the final run.
10. Verify that all four CSVs were actually written and are non-empty before declaring completion.


## Workflow

## Execution Guardrails

- Treat the requested outputs as fixed requirements: compute the Wigner function on the full `1000×1000` grid over `x,p ∈ [-6,6]` for all 4 loss cases, and save exactly `1.csv`, `2.csv`, `3.csv`, `4.csv`.
- Do **not** lower grid resolution, change filenames, or skip cases for the final run. If you do a smaller exploratory check, rerun at full specification before finishing.
- If the simulation is long-running, let it continue unless you have concrete evidence it is stuck or failed. Do **not** terminate the main job before any required CSV outputs exist.
- After the run, verify deliverables explicitly: check that all four CSV files were created in the expected location and have nonzero size before declaring success.
- Do not consider the task complete just because the script was launched; completion requires confirmed output files.

## Debugging and Validation

## Debugging and Validation

- After writing or patching any Python script, inspect the saved file and run a quick syntax/import check before expensive runs; do not assume file writes succeeded intact.
- When QuTiP reports inconsistent shapes or dims, print operator dims and fix that exact mismatch before changing approach.
- Keep all Hamiltonian and collapse operators in the same Hilbert-space representation; do not mix collective-spin dims with full tensor-product spin dims in one Liouvillian.
- Confirm subsystem ordering before `ptrace`: if `rho.dims == [[cavity_dim, spin_dim], [cavity_dim, spin_dim]]`, then the cavity state is `ptrace(rho, 0)`.
- Before expensive Wigner evaluation, verify each case has the intended collapse-operator list: local per-spin terms versus separate collective terms.
- If a run fails, read the full traceback and inspect the exact code before changing anything; do not guess the root cause from partial output.
- If you temporarily reduce `n_max` or grid size for testing, treat it as diagnostic only and rerun with `n_max = 16` and Wigner grid `1000×1000` for the final outputs.
- Do not claim completion until `1.csv`, `2.csv`, `3.csv`, and `4.csv` exist and match the requested configuration.
## Output

CSV files with Wigner function values:
- 1000×1000 grid
- x and p range [-6, 6]

## Tips

- Use QuTiP for quantum simulation.
- Use `steadystate` for steady-state solutions; `mesolve` is for time evolution or explicitly validated diagnostics.
- Use `wigner` for Wigner function calculation.
- If execution fails, inspect the full traceback before changing solver methods or algorithms.
- For long runs, print progress before/after each major step: Liouvillian build, steady-state solve, partial trace, Wigner evaluation, CSV write.
- Before the final `1000×1000` production run, validate one case or a smaller grid to confirm the model and identify bottlenecks.
- For `N=4`, prefer the exact full spin-space construction over symmetry reduction when local channels are present.
- Read [references/liouvillian-checks.md](references/liouvillian-checks.md) before combining cavity and spin superoperators or launching expensive solves.
