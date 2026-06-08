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

Practical implementation rules:
- Apply the online-generator filter everywhere consistently: variable creation, bounds, capacity totals, reserve totals, objective terms, and final report rows. Reading `GEN_STATUS` without using it in the model is not sufficient.
- Read the actual input schema first and translate MATPOWER tables directly:
  - bus table -> demands, bus labels, reference/slack selection, internal bus indexing
  - gen table -> online/offline filtering, `Pmin`, `Pmax`, bus attachment
  - branch table -> in-service filtering, reactance/susceptance, MW limits
  - `gencost` -> objective coefficients using MATPOWER semantics
- Build a generator-to-bus incidence matrix `Cg` with shape `(nbus, ngen)` after consistent online/offline filtering, compute bus generation as `Cg @ Pg`, and use that mapped vector in nodal DC balance constraints instead of manually scattering generator terms bus by bus.
- Treat external bus numbers as labels and use one consistent dense internal ordering in every matrix/vector.
- Preserve consistent base-MVA/unit conversions for loads, flows, limits, and objective coefficients.
- Also enforce or verify aggregate balance `sum(Pg[g] for online generators) = total_load` within tolerance as a backstop against slack/reference-bus mishandling.
- If reserve requirement or reserve compensation is not present in the task/input data, do not insert a numeric default and present it as required market data.
- If one compatible solver is unavailable or fails numerically, try another installed compatible solver before changing the model.
- After solve, compute branch flows, loading percentages, totals, and operating margin directly from the same solved `Pg`, `R`, and `theta` values.


## Non-negotiable checks

- Do not omit `theta` variables if transmission limits must be enforced.
- Do not claim nodal DC balance was satisfied if the optimization enforced only `sum(Pg) = sum(load)`.

- Do not replace nodal balance with only `sum(Pg) = sum(load)`; that ignores network feasibility.
- Do not compute `most_loaded_lines` from a different dispatch than the reported optimum.
- Do not substitute heuristic or capped loading percentages if the DC flow results appear wrong.

- Keep one consistent dispatch throughout: the reported `generator_dispatch`, branch-flow validation, and `most_loaded_lines` must all come from the same solver solution.
- Do not debug flow calculations with substitute injections unless clearly labeled as diagnostics only; do not report those results as the task answer.
- Do not accept a model that uses only `sum(Pg) = sum(load)` and then runs DC flow afterward; nodal balances and line limits must be inside the optimization.
- If the initial constrained model is infeasible, do not remove branch constraints to get a dispatch. Instead check bus-generator/load mapping, slack/reference-bus handling, susceptance/sign conventions, branch rating units/base-MVA conversion, online-generator filtering, and reserve semantics.
- Solver success on a relaxed copper-plate/system-balance model does not satisfy a task that requires transmission-feasible dispatch.
- Do not treat solver status alone as proof the model is correct; verify aggregate balance, reserve sufficiency, and generator headroom/coupling before accepting the dispatch.
- Inspect MATPOWER inputs before coding assumptions: confirm which reserve fields actually exist and preserve `gencost` model semantics rather than guessing a simplified cost form.
- Do not silently linearize or replace MATPOWER `gencost` data with ad hoc defaults when the task asks for economic dispatch.


## Debugging suspicious flow magnitudes

If you see absurd loading values, check before reporting results:
- line susceptance/reactance units and base-MVA conversions
- sign convention in nodal balances and flow equations
- whether branch ratings and flows are in the same MW base
- whether parallel lines / transformer data were interpreted correctly
- whether the reported dispatch actually came from the constrained optimization

If you cannot validate the physical calculation, say so clearly rather than fabricating line-loading outputs.

- If using a symbolic optimization package, avoid patterns like `if expr:` or `a if expr else b` when `expr` may be symbolic; track unset state with `None` or separate flags, then build the final equality/inequality explicitly.

