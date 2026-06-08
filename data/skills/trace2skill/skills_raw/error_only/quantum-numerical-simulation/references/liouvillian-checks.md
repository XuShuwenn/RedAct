# Liouvillian Composition and Runtime Checks

## When to read this
Read this when combining cavity and spin terms, especially with composite cavity-spin constructions, or when steady-state solves are slow/failing.

## Composite-construction rules

- Build the full model in one mathematically consistent space before solving.
- Verify both `shape` and `dims` for every Hamiltonian, collapse operator, and superoperator you plan to sum.
- If two superoperators have different tensor structure in `dims`, treat that as a construction error, not metadata noise.
- **Do not** "fix" compatibility by assigning to `.dims` unless you have independently verified the superoperator action is identical; in practice for this task, rebuild instead.

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
