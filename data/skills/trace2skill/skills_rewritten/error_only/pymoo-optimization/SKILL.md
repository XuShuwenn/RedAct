---
name: pymoo-optimization
description: "Solve multi-objective optimization problems using pymoo with NSGA-II to find Pareto front solutions."
---

# Multi-Objective Optimization with pymoo

## When to Use

- Find Pareto front for multi-objective problems
- Use NSGA-II algorithm for optimization
- Handle multiple objectives and bounds

## Problem Example

- f1(x) = (x1 - 2)²
- f2(x) = (x1 + 2)²
- Subject to: -10 ≤ x1 ≤ 10

## Using pymoo

```python
from pymoo.optimize import minimize
from pymoo.algorithms.nsga2 import NSGA2


## Using pymoo

## Execution Workflow

- For fully specified tasks, prefer one self-contained script that defines the problem, runs `minimize`, extracts results, formats them, and writes `/root/output.txt` in the same run.
- If you need a helper script and the first location is not writable, use a confirmed writable scratch path such as `/tmp`.
- Create outputs only in confirmed writable locations, but ensure the final artifact is written to `/root/output.txt` when required.
- Build the final deliverable from the solver result rather than from exploratory prints or manual post-processing.
- If `minimize` fails early, check the pymoo problem interface and the shape of `out["F"]` first.
# Define problem with 2 objectives
# Run NSGA-II: population=50, generations=3
```

## Output Format

To `/root/output.txt`:
```
{x1_value}={f1_value},{f2_value}
```

Sorted by x1 ascending, x1 to 3 decimal places.

- Write results to `/root/output.txt`, not just to stdout.
- Extract paired solution data from `res.X` and `res.F` directly after optimization rather than recomputing objectives separately.
- Handle result shapes defensively: check for `None`, single-solution arrays, and multi-row arrays before iterating.
- Convert NumPy values to Python scalars before rounding or formatting when needed.
- Do not rely on pymoo's returned order; collect `(x1, f1, f2)` rows, sort by `x1` ascending, and then write the file.
- Format each line exactly as `{x1_value}={f1_value},{f2_value}`, with `x1` rounded to 3 decimal places.
- After writing, reopen `/root/output.txt` and verify ordering, delimiters, rounding, and exact line structure.


## Pareto Front

- Non-dominated solutions
- Trade-off between objectives
- NSGA-II finds Pareto-optimal set

## Tips

- Use pymoo.algorithms.nsga2
- Set proper population and generations
- Extract Pareto front from results

- Mirror the prompt exactly: objectives, bounds, algorithm, population size, generation count, and required file format.
- Do not treat a successful optimization run as the finished deliverable; explicit post-processing and file validation are part of the task.
- Keep optimization, formatting, and file writing in the same script for reproducibility.
- Sanity-check the Pareto front against the objective geometry; for `(x1-2)^2` vs `(x1+2)^2`, expect a trade-off region rather than a single clustered point.
