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

- If external references or papers cannot be accessed or parsed, do **not** claim the formulation is confirmed. State which details are unavailable, use only task-specified terms plus trusted local/API documentation, and validate conventions with a minimal QuTiP check before scaling up.
- Do not invent missing Hamiltonian terms, dissipators, rate normalizations, or subsystem conventions from memory.
- Before writing scripts or outputs, confirm the allowed working/output directories from the task/environment and use only those paths; use explicit absolute paths when the environment or task requires them.
- Treat process instructions from the active environment (for example, required tool-call format or exact completion marker) as mandatory execution constraints; follow them exactly before attempting simulation work.

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
- Treat the following as a hard invalid-model check before any production run: if a case contains any local channel and your implementation uses only Dicke-sector spin operators with spin dimension `N+1`, or represents local channels only through `Jz`, `J+`, or `J-`, stop and rebuild in the full `2^N` spin space with one site-resolved collapse operator per spin.
- Use one representation for the entire run: build both the Hamiltonian and **all** collapse operators in the full cavity ⊗ spin tensor-product space with spin dimension `2^N`.
- Construct collective operators inside that same full-spin space from sums of embedded site operators, e.g. `Jz = 0.5*sum(sz_i)`, `J+ = sum(sp_i)`, `J- = sum(sm_i)`; do **not** import/build them in a separate Dicke-sector dimension.
- It is acceptable to use collective spin operators in the Hamiltonian or for explicitly collective loss channels, but not as substitutes for requested local Lindblad terms.
- Do **not** use `jmat(...)`, a single spin-`j=N/2` space, or any symmetric-sector-only reduction for the final task when local dissipation is present, even as an "equivalent" shortcut.
- In practice, case 4 must contain five emission collapse operators total: four site-resolved `sqrt(γ↓) · σ-^(i)` terms plus one separate collective `sqrt(γ⇓) · J-` term, all embedded in the same full cavity-spin Hilbert space.

## Workflow

1. Build the Hamiltonian and collapse operators strictly from the provided task parameters.
2. Preserve the requested dissipation structure exactly: local channels must act on each spin separately in the full tensor-product spin space, while collective channels act on the full spin ensemble.
3. Keep all operators in one consistent Hilbert-space representation; check composite operator/Liouvillian `dims` and shapes before calling `steadystate`, and do **not** fix incompatible superoperators by manually overwriting `.dims`.
4. Before full-scale runs, validate one reduced but structurally faithful end-to-end pipeline: read back the saved script, run a quick syntax/import check, print/inspect `dims` and `shape` for `H` and each `c_op`, then build the model, solve one steady state, confirm subsystem ordering for `ptrace`, compute a small Wigner grid, and write a test CSV.
5. Keep reduced tests structurally faithful to the real task: use the same full cavity ⊗ `2^N` spin-product-space construction, the same local-vs-collective collapse-operator pattern, and the same likely bottleneck as the final run; do **not** switch to a Dicke/symmetric basis when local dissipation is present.
6. Instrument the script with progress/timing prints around case build, Liouvillian assembly, `steadystate` start/end, `ptrace`, Wigner start/end, and CSV write; do not launch the full 4-case `1000×1000` production run until one reduced test case has successfully completed `steadystate` → `ptrace` → `wigner` → CSV write.
7. Use the reduced benchmark to choose the execution plan. In timeout-prone environments, prefer one case per process/script invocation with immediate CSV persistence, and keep one validated baseline implementation instead of restarting from speculative optimization paths.
8. Use `steadystate` for the required final results. Do **not** replace the final workflow with finite-time evolution (`mesolve`) just because the solve is slow or times out. If you use time evolution only as a diagnostic, explicitly verify stationarity before treating it as relevant evidence, then return to the required `steadystate` workflow for final outputs.
9. Solve the full-parameter steady state case-by-case.
10. Trace out spins → cavity state, confirming subsystem ordering before `ptrace`.
11. Calculate the Wigner function on grid x,p ∈ [-6,6], 1000×1000.
12. Save each finished case immediately as CSV: `1.csv`, `2.csv`, `3.csv`, `4.csv`, in the approved output directory.
13. If you used reduced settings for diagnosis, restore the exact required parameters before the final run; do **not** change `N=4`, `n_max=16`, or the final `1000×1000` grid unless the user explicitly approves it.
14. Verify that all four CSVs were actually written and are non-empty before declaring completion.
15. Write CSVs with built-in or NumPy-based output (`numpy.savetxt` or `csv`); do not add optional dependencies such as `pandas` just for file export.
16. If the surrounding instructions specify an exact final completion string, emit it immediately after verifying the four CSVs; do not perform any further experimentation once deliverables are secured.


## Workflow

## Execution Guardrails

- Treat the requested outputs as fixed requirements: compute the Wigner function on the full `1000×1000` grid over `x,p ∈ [-6,6]` for all 4 loss cases, and save exactly `1.csv`, `2.csv`, `3.csv`, `4.csv`.
- Do **not** lower grid resolution, change filenames, or skip cases for the final run. Smaller grids or reduced cutoffs are allowed only for diagnostics and must be followed by a full-spec rerun before finishing.
- Before any full `1000×1000` production run, complete one reduced end-to-end case that reaches all the way to a non-empty test CSV; do not treat model construction alone as sufficient validation.
- In environments with hard wall-clock limits, prefer per-case execution and immediate CSV persistence over one monolithic all-cases run.
- If the simulation is long-running, let it continue unless you have concrete evidence it is stuck or failed. Do **not** terminate the active production run before any required CSV outputs exist unless a corrected replacement run is ready to start immediately.
- Treat sparse stdout as inconclusive, not as proof of failure. Before rewriting code or stopping a run, obtain concrete evidence such as a traceback, an exception, repeated checkpoint logs showing the same stage forever, or missing expected intermediate artifacts after a validated test plan.
- If progress output stops for an extended period and no CSVs are being produced, use the last completed stage to localize whether the bottleneck is Liouvillian construction, `steadystate`, or Wigner evaluation; then base any change on that evidence rather than speculative polling or restart loops.
- Do not keep rerunning the same stalled formulation. First verify the Liouvillian construction and collapse list, then adjust solver settings or method based on that diagnosis.
- Kill and relaunch a heavy run only if you have concrete evidence it is stuck/failed, or you have already verified a materially changed on-disk script that justifies a rerun.
- Monitor expensive runs against deliverables, not stdout alone: in addition to reading logs, check whether `1.csv`-`4.csv` exist and have nonzero size.
- Do **not** treat a launched background job, partial progress log, or still-running process as completion; completion requires confirmed non-empty `1.csv` through `4.csv` from the full-specification run plus clean run-completion evidence.

## Debugging and Validation

- After writing or patching any Python script, inspect the saved file and run a quick syntax/import check before expensive runs; do not assume file writes succeeded intact.
- If you write or patch a script via shell redirection/heredoc, immediately read back the full file contents before running it; if the file looks truncated or corrupted, rewrite it first.
- Use this preflight before expensive runs: inspect the saved script on disk, run a syntax/import check such as `python -m py_compile <script>.py`, print `dims`/`shape` for `H`, each `c_op`, and `L`, complete one reduced end-to-end case, then scale to the final 4-case run.
- If a traceback follows a recent rewrite, inspect the on-disk file contents first; do not assume the edit was applied intact.
- If a run fails, read the full traceback and inspect the exact code before changing anything; do not guess the root cause from partial output.
- If command output is truncated or ambiguous, rerun or capture stderr/stdout to a log so you can inspect the actual exception before editing the script. Base each fix on observed errors, not on likely causes.
- When QuTiP reports inconsistent shapes or dims, print operator dims and fix that exact mismatch before changing approach.
- Keep all Hamiltonian and collapse operators in the same Hilbert-space representation; do not mix collective-spin dims with full tensor-product spin dims in one Liouvillian.
- Treat any attempt to reassign `.dims` on states or superoperators as a red flag: only do so after independently proving the tensor structure is already correct; otherwise rebuild the object correctly.
- Confirm subsystem ordering before `ptrace`: if `rho.dims == [[cavity_dim, spin_dim], [cavity_dim, spin_dim]]`, then the cavity state is `ptrace(rho, 0)`.
- Verify `ptrace` against the actual `rho.dims` in the live run, and align code comments with the indexing used.
- Before expensive Wigner evaluation, verify each case has the intended collapse-operator list: local per-spin terms versus separate collective terms.
- Explicitly count collapse operators for each case before the production run. For `N=4`: case 1 should include 4 dephasing + 4 pumping + cavity loss; case 2 should include 4 dephasing + 4 emission + cavity loss; case 3 should include case 2 plus one separate collective-pumping operator; case 4 should include case 2 plus one separate collective-emission operator.
- For case 4 specifically, verify the list contains both the four site-resolved `σ-^(i)` operators and one additional `J-` operator; if local and collective emission are represented by the same object family, rebuild the model.
- Treat local-channel substitutions as invalid unless explicitly proven equivalent for this task: do not replace `{σz^(i)}`, `{σ+^(i)}`, or `{σ-^(i)}` with `Jz`, `J+`, or `J-` just for convenience.
- If output is truncated or buffered, rerun with explicit stderr/stdout capture until you can identify the exact failing call or the exact stage where progress stops; do **not** switch `steadystate` methods, Wigner algorithms, or model representations based only on a partial traceback or an apparent stall.
- If a run appears hung, add or inspect stage-level timestamps and `print(..., flush=True)` checkpoints around: case start, Liouvillian build complete, steady state complete, cavity `ptrace` complete, Wigner start/finish, and CSV written.
- If a run is slow or times out, collect timing evidence first; do not switch solver methods, options, or execution structure until you know whether the bottleneck is Liouvillian construction, `steadystate`, or Wigner/CSV post-processing.
- If the same full-scale `steadystate` attempt times out more than once at the same step, stop retrying that configuration unchanged.
- Do **not** respond to per-case solver timeouts by launching all four heavy cases in parallel; first identify and change the expensive formulation or confirm a cheaper exact construction.
- If you use time evolution as a diagnostic, label it diagnostic-only unless you also verify steady-state convergence; do not use it as the final method by default when `steadystate` was requested.
- Do not claim completion until `1.csv`, `2.csv`, `3.csv`, and `4.csv` exist and match the requested configuration.

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

## Completion Checklist

Before declaring completion:
- confirm the final run used `N=4`, `n_max=16`, and the full `1000×1000` Wigner grid on `[-6,6]`
- confirm all 4 cases were executed
- confirm `1.csv`, `2.csv`, `3.csv`, and `4.csv` exist and are non-empty

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
- For a practical preflight and completion checklist on long runs, read [references/run-monitoring-checklist.md](references/run-monitoring-checklist.md) before launching the final 4-case production job.

- Read [references/liouvillian-checks.md](references/liouvillian-checks.md) before combining cavity and spin superoperators or launching expensive solves.

- Include elapsed-time prints around the expensive phases (`steadystate`, `wigner`, CSV write) so any apparent hang can be localized from evidence.
- A good exact pattern for this task is: build embedded single-spin operators in the full `2^N` spin space, sum them to form `Jz/J±`, tensor everything with the cavity space, validate one reduced case, then scale to the required grid and save each case immediately.
- If you use `mesolve` as a diagnostic, keep it clearly separate from the final required computation and do not present its endpoint as the requested steady state without an explicit stationarity/convergence check.
