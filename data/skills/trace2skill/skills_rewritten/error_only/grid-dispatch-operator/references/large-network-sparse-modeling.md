# Large-network sparse modeling patterns

Use this when `network.json` is large or the dispatch model must scale to many buses/branches.

## Fast input inspection

Inspect structure before modeling:
- print top-level keys
- count buses, generators, branches, and gencost rows
- print 1 to 3 representative records from each table
- confirm available fields for generator status, branch ratings, and any reserve data
- determine whether `gencost` is piecewise linear, linear polynomial, or higher-order polynomial

Avoid pasting or manually scanning the full JSON when targeted queries answer the modeling questions.

## Sparse DC-OPF build pattern

Prefer sparse matrices when available:
- generator-to-bus incidence matrix
- branch-to-bus incidence matrix
- branch susceptance / flow matrix
- reduced bus-balance system after fixing one reference angle, if convenient

Keep the formulation equivalent to the required model:
- nodal DC balance
- branch flow equations and limits
- generator bounds
- reserve coupling and reserve requirement

## Post-solve checks

After solving:
- compute reported branch loadings from the same optimized dispatch
- verify slack/reference treatment did not change physical feasibility
- verify totals and per-generator outputs map back to original MATPOWER row ordering
