# Liouvillian Composition and Runtime Checks

## When to read this
Read this when combining cavity and spin terms, especially with composite cavity-spin constructions, or when steady-state solves are slow/failing.

## Composite-construction rules

- Build the full model in one mathematically consistent space before solving.
- Verify both `shape` and `dims` for every Hamiltonian, collapse operator, and superoperator you plan to sum.
- If two superoperators have different tensor structure in `dims`, treat that as a construction error, not metadata noise.
- **Do not** "fix" compatibility by assigning to `.dims` unless you have independently verified the superoperator action is identical; in practice for this task, rebuild instead.

- For this task, treat the presence of local dissipation as a representation check, not just an operator-construction detail: site-resolved local channels require the full tensor-product spin Hilbert space, not a symmetric Dicke-sector model built from collective `J` operators.
- Preferred pattern for this task: embed cavity operators and each site-resolved/collective spin operator into the full cavity ⊗ spin Hilbert space, then pass the full-space `H` and full-space `c_ops` to `liouvillian(...)` or `steadystate(...)`.
- Avoid hybrid composition where one contribution is built as a composite superoperator with different tensor-structure metadata than the others unless you have explicitly checked that both the action and `dims` match.
- For this task, local spin dissipation implies the spin space must remain the full tensor-product space of 4 qubits. Do **not** switch to `jmat(N/2, ...)` / symmetric-Dicke operators to bypass a `dims` mismatch, because that changes the model and invalidates site-resolved channels.

## Minimum checks before `steadystate`

For a reduced test case, print/inspect:

```python
print(H.dims, H.shape)
for c in c_ops:
    print(c.dims, c.shape)
print(L.dims, L.shape)
```

Use these checks:
- Hamiltonian and collapse operators must act on the same composite Hilbert space.
- The final Liouvillian must be a superoperator on that same composite space.
- If a spin-only object must act in the full cavity-spin space, embed it properly; do not rely on relabeling metadata.


Add these task-specific checks when local dissipation is present:
- Verify the spin-space factor is the full tensor-product space (`2^N` states), not just the symmetric Dicke sector (`N+1` states).
- Verify requested local channels appear as one embedded collapse operator per spin site.
- If you see only `Jz`, `J+`, or `J-` in place of local dephasing/pumping/emission, the model is not implementing the requested Liouvillian.

## Case-by-case dissipator compliance checklist

Use this quick checklist before the expensive run. If the code fails any line below, fix the model before trusting outputs.

- Case 1: include cavity loss plus `N` separate local dephasing operators and `N` separate local pumping operators.
- Case 2: include cavity loss plus `N` separate local dephasing operators and `N` separate local emission operators.
- Case 3: same as Case 2, plus one additional collective pumping operator `J+`.
- Case 4: same as Case 2, plus one additional collective emission operator `J-`.
- For all four cases with local channels: spin space must be the full tensor-product space, not only the permutation-symmetric/Dicke sector.
- Reject constructions that replace local channels by scaled collective operators such as `sqrt(rate*N) * Jz`, `J+`, or `J-`.

## Runtime de-risking

Before the final 4-case run:
- reduce `n_max`
- use a much smaller Wigner grid
- complete one case fully
- verify the CSV has the expected 2D array shape

Then scale up to:
- `n_max = 16`
- Wigner grid over `[-6, 6]`
- `1000 x 1000`
- outputs `1.csv` through `4.csv`

- After editing the production script, reopen it and run a fast syntax/import check before any expensive solve.
- Keep the reduced test structurally faithful to the real task: same Hamiltonian form, same local-vs-collective collapse-operator pattern, and same cavity-spin tensor construction.
- If you want to alter `steadystate` kwargs or method selection, first test that exact call on the reduced case and confirm the local QuTiP install accepts it.
- Keep `steadystate` as the production method for this task; use `mesolve` only for diagnostics unless you explicitly prove stationarity.
- Make the reduced test truly end-to-end: steady state → cavity `ptrace` → small Wigner grid → CSV write → verify non-empty file.
- Time the reduced steady-state solve and use that result to judge whether one full case is plausible in the current environment.
- Once the reduced pipeline works, keep that version as the baseline and change only one execution or performance variable at a time.
- Add stage-level progress/timing prints around: case setup, Liouvillian construction, `steadystate`, `ptrace`, Wigner computation, and CSV save.
- If a solver run fails, save the full traceback/log before changing construction or solver settings.
- For hard timeout environments, progress case-by-case: reduced faithful test → one full-parameter case with CSV saved → remaining full cases until `1.csv`-`4.csv` all exist.
- After diagnostics, restore the exact required parameters and rerun the final production cases.
- After launching the full production run, confirm the process reached normal completion before trusting any CSVs already present in the directory.
- Do **not** accept outputs from exploratory runs with reduced `n_max` or reduced grid as final deliverables.

During both reduced tests and final runs, emit flushed progress markers from inside the script, for example:

```python
print(f"case {case_id}: build start", flush=True)
print(f"case {case_id}: Liouvillian ready", flush=True)
print(f"case {case_id}: steadystate done", flush=True)
print(f"case {case_id}: ptrace done", flush=True)
print(f"case {case_id}: wigner start", flush=True)
print(f"case {case_id}: wigner done", flush=True)
print(f"case {case_id}: wrote {filename}", flush=True)
```

Use these markers to distinguish "slow but progressing" from "failed". Do not rewrite the model or terminate the run unless you have concrete failure evidence such as a traceback or a validated repeated stall at the same checkpoint.

- Before using an unfamiliar QuTiP or PIQS object in a benchmark/workaround, confirm its real interface in the installed version with a minimal probe, for example:

```python
from qutip.piqs import Dicke
obj = Dicke(N=4)
print(type(obj))
print([name for name in dir(obj) if 'op' in name.lower()])
```

- Build benchmark code only from methods/attributes you have actually observed. If a guessed method is missing, stop and inspect the object/API docs before continuing.
- Prefer targeted probes that answer the blocking question (for example, "can this module represent the required local channels in full spin space?" or "which call is slow?") over generic system-information checks that do not change the implementation plan.
