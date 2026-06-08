# DC-OPF pattern for transmission-constrained dispatch

Use this when the task requires transmission limits in the dispatch itself.

## Required model structure

Decision variables:
- `Pg[g]` generator dispatch MW
- `R[g]` spinning reserve MW
- `theta[b]` bus voltage angle

Objective:
- Minimize generation cost (and reserve cost if provided)

Constraints:
1. Generator limits: `Pmin[g] <= Pg[g] <= Pmax[g]`
2. Reserve limits/coupling: `0 <= R[g]`, `Pg[g] + R[g] <= Pmax[g]`
3. System reserve requirement: `sum(R[g]) >= reserve_requirement`
4. Nodal DC balance at each bus `b`:
   - `sum(Pg at b) - load[b] = sum(B_ij * (theta[b] - theta[j]) over incident lines)`
5. Reference bus angle:
   - fix one bus, e.g. `theta[slack] = 0`
6. Branch flows for each line `(i,j)`:
   - `F_ij = B_ij * (theta[i] - theta[j])`
7. Branch limits:
   - `-Fmax_ij <= F_ij <= Fmax_ij`

## Non-negotiable checks

- Do not omit `theta` variables if transmission limits must be enforced.
- Do not replace nodal balance with only `sum(Pg) = sum(load)`; that ignores network feasibility.
- Do not compute `most_loaded_lines` from a different dispatch than the reported optimum.
- Do not substitute heuristic or capped loading percentages if the DC flow results appear wrong.

## Debugging suspicious flow magnitudes

If you see absurd loading values, check before reporting results:
- line susceptance/reactance units and base-MVA conversions
- sign convention in nodal balances and flow equations
- whether branch ratings and flows are in the same MW base
- whether parallel lines / transformer data were interpreted correctly
- whether the reported dispatch actually came from the constrained optimization

If you cannot validate the physical calculation, say so clearly rather than fabricating line-loading outputs.
