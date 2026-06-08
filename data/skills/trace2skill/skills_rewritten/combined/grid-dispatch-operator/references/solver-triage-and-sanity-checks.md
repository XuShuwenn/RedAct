# Solver triage and sanity checks

Use this when the model has script errors, repeated solver non-convergence, or a long-running stalled solve.

## After each model edit

Run quick checks before a full solve:
- confirm the script parses/runs without `SyntaxError` or `IndentationError`
- print key dimensions: number of buses, online generators, in-service branches, variables, and constraints
- verify matrix/vector shapes match the intended formulation
- verify bound/objective arrays align with the variable ordering
- confirm one reference angle is fixed and online/offline filters were applied consistently

If any structural check fails, fix that first instead of launching the optimizer.

- Verify the execution environment you will actually use for the solve: confirm the intended interpreter can import the selected optimization libraries and backend.
- Prefer a tiny preflight script before the full model build that prints and checks: bus count, generator count, in-service branch count, `gencost` row count, reserve-capability vector count if present, and whether reserve requirement data is explicitly present.
- If filtered generator counts no longer match the cost, reserve, or bus-mapping arrays, stop and fix the alignment before invoking the solver; do not rely on implicit row correspondence after masking.
- Keep the workflow in one executable script when possible: parse inputs, solve, compute validations, and write the report from the same run so reruns are reproducible and diagnostics stay tied to the exact artifact.
- Before saying an edit fixed anything, confirm all three: the saved script re-opens and parses cleanly, the targeted structural property changed as intended (shape/count/alignment), and the next run produces a new explicit outcome rather than the same old failure signal.
- After a nominally successful solve, print or compute a compact acceptance summary: max nodal-balance residual, max branch-limit violation, max generator bound violation, reserve-coupling violation, and total generation minus load.

## Repeated failure escalation

If the same path fails twice with the same signal (`primal infeasible`, repeated iteration limit, or numerically meaningless output):
1. stop rerunning the same setup with minor edits
2. inspect indexing, signs, units, and required constraints
3. rebuild a minimal validated version of the model
4. if available, switch to another compatible installed solver before spending more time tuning the failing one

Do not keep retrying the same solver just because it is already wired up.

- If recovery requires extra Python packages and system installation is blocked, stop retrying failing global installs. Prefer a project-local virtual environment, re-check imports with that exact interpreter, and then use that same interpreter consistently for solve runs and validations.
- Practical escalation rule: on the first repeated failure, inspect the exact current script and structural outputs before changing anything else; on the second repeated failure with the same pattern, stop editing around the edges of that setup and choose one decisive recovery path only: rebuild a minimal but still requirement-complete model or switch to another installed compatible solver.

## Stalled-run rule

If a solve is still running after earlier similar runs already stalled or failed:
- do one brief purposeful check
- if there is no new evidence of progress, terminate it
- spend the time on diagnosis, simplification, or solver change

Repeated polling is not progress.

## Minimal structural checklist

Before any serious solve, confirm:
- generator-to-bus map exists and matches filtered online generators
- branch model uses only in-service branches
- each variable block has the expected length
- nodal balance rows equal the number of buses (or reduced buses if one angle is eliminated)
- branch-limit rows match the implemented branch set
- reserve vectors/constraints exist only when reserves are required
- aggregate load/generation quantities are on a consistent MW/base-MVA convention
