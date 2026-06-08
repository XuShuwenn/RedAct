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

## pymoo Components

- Problem: define bounds and constraints
- Algorithm: NSGA-II with population size
- Termination: number of generations

## Tips

- Subclass `pymoo.core.problem.ElementwiseProblem` (or another real pymoo problem class), not `pymoo.OptimizationProblem`
- Define constraints in pymoo's inequality form
- Set bounds with `xl` and `xu`
- Before formatting output, normalize `res.X`/`res.F` so scalar and array returns both work:

```python
x = res.X
f = res.F

if hasattr(x, "ndim") and x.ndim > 1:
    x = x[0]
if hasattr(f, "ndim") and f.ndim > 0:
    f = f[0]

x1, x2 = float(x[0]), float(x[1])
obj = float(f)
```

- Do not assume `res.X[0]` is always valid without checking shape first
