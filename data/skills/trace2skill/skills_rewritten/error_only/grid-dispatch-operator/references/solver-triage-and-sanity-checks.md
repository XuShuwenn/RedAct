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

## Repeated failure escalation

If the same path fails twice with the same signal (`primal infeasible`, repeated iteration limit, or numerically meaningless output):
1. stop rerunning the same setup with minor edits
2. inspect indexing, signs, units, and required constraints
3. rebuild a minimal validated version of the model
4. if available, switch to another compatible installed solver before spending more time tuning the failing one

Do not keep retrying the same solver just because it is already wired up.

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
