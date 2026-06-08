---
name: pymoo-constrained-opt
description: "Solve constrained optimization problems using pymoo with NSGA-II to minimize objective functions subject to constraints."
---

# Constrained Optimization with pymoo

## When to Use

- Solve constrained optimization with NSGA-II
- Minimize objective functions with bounds constraints
- Find Pareto-optimal solutions for constrained problems

## Problem Example

- Minimize: f(x) = x1² + x2²
- Subject to: x1 + x2 ≥ 1
- Bounds: 0 ≤ x1, x2 ≤ 10

## Using pymoo

```python
from pymoo.optimize import minimize
from pymoo.algorithms.nsga2 import NSGA2


- Prefer one compact self-contained script: define the pymoo problem class, run `minimize(...)`, extract the final result, and write `/root/output.txt` in the same script.
- Encode the objective, bounds, and inequality constraints inside the problem class using pymoo's feasibility convention `G <= 0`; for example, `x1 + x2 >= 1` becomes `out["G"] = [1.0 - x[0] - x[1]]`.
- Use `ElementwiseProblem` for simple per-point evaluations unless the task clearly needs a different pymoo problem type.

- Treat `res.X` and `res.F` as shape-variable outputs. Before any indexing or formatting, normalize them with `np.atleast_2d(res.X)` and `np.atleast_1d(res.F).reshape(-1)` (or inspect their shapes first).
- **Do not** write extraction code that assumes `res.X` is always a 1-D vector, such as `x1, x2 = res.X[0], res.X[1]`. **Do** normalize first, then select a candidate row and unpack from that row.


# Define problem with constraints
# Run NSGA-II optimizer
```

## Output Format

To `/root/output.txt`:
```
Optimal x1: X.XX
Optimal x2: X.XX
Objective: X.XX
```

Round to 2 decimal places.


After writing `/root/output.txt`, read it back once and confirm it contains exactly the required three labeled lines in order (`Optimal x1`, `Optimal x2`, `Objective`) with values rounded to 2 decimal places.


## pymoo Components

- Problem: define bounds and constraints
- Algorithm: NSGA-II with population size
- Termination: number of generations

## Tips

- Subclass `pymoo.core.problem.ElementwiseProblem` (or another real pymoo problem class), not `pymoo.OptimizationProblem`
- Define constraints in pymoo's inequality form (`G <= 0`) and translate them explicitly; for example, `x1 + x2 >= 1` becomes `G = 1.0 - (x1 + x2)`
- Set bounds with `xl` and `xu`
- Before formatting output, first verify that a solution was actually returned. If `res.X` or `res.F` is `None`, inspect the constraint setup or termination instead of writing placeholder values.
- Normalize `res.X`/`res.F` to predictable dimensions so single-solution and array-like returns both work; if constraint values are available, select the best feasible candidate before writing output:

```python
import numpy as np

X = np.atleast_2d(res.X)
F = np.atleast_1d(res.F).reshape(-1)
G_raw = getattr(res, "G", None)
G = None if G_raw is None else np.atleast_2d(G_raw)

if G is not None and G.shape[0] == X.shape[0]:
    feasible = np.all(G <= 1e-6, axis=1)
    if not np.any(feasible):
        raise ValueError("No feasible solution found")
    X = X[feasible]
    F = F[feasible]

best = int(np.argmin(F))
x = X[best]
x1, x2 = float(x[0]), float(x[1])
obj = float(F[best])
```

- Do not assume `res.X[0]` is always valid without normalization first
- Keep optimization results numeric during solving; only convert to plain floats and apply `:.2f` formatting when writing `/root/output.txt`
- Verify the extracted solution satisfies the original constraint(s) you encoded before saving `/root/output.txt`
- If the optimizer ran but formatting failed, fix result extraction first; do not change the problem or algorithm unless the solve itself failed
- If the result structure is unclear, inspect `res.X`, `res.F`, and their shapes before changing solver settings
- Save any helper script you execute in a writable location such as `/home/agent/optimize.py`; only the final required report needs to go to `/root/output.txt`
- Use pymoo/NSGA-II when the task requests it, even if the optimum is analytically obvious; use analytic reasoning only as a sanity check
- Do a quick sanity check that the solution matches the problem structure (for example, a symmetric quadratic with a linear sum constraint often yields balanced variable values)
