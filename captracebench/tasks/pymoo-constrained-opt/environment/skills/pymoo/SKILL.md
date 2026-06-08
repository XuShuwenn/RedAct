---
name: pymoo
description: "Constrained single-objective optimization using pymoo. Minimize objective functions subject to inequality constraints using ElementwiseProblem and NSGA-II or GA."
---

# Pymoo: Constrained Single-Objective Optimization

## Overview

Minimize a single objective function subject to inequality constraints using pymoo's `ElementwiseProblem` class.

## Problem Definition

Minimize: f(x) = x1² + x2²

Subject to: x1 + x2 ≥ 1

Which translates to constraint: -(x1 + x2 - 1) ≤ 0, i.e., -x1 - x2 + 1 ≤ 0

Bounds: 0 ≤ x1 ≤ 10, 0 ≤ x2 ≤ 10

## Workflow

### Step 1: Define the Problem

Extend `ElementwiseProblem` to define a constrained single-objective problem:

```python
from pymoo.core.problem import ElementwiseProblem
import numpy as np

class ConstrainedProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2,              # Two variables: x1, x2
            n_obj=1,              # One objective
            n_ieq_constr=1,       # One inequality constraint
            n_eq_constr=0,        # No equality constraints
            xl=np.array([0, 0]),   # Lower bounds: x1 >= 0, x2 >= 0
            xu=np.array([10, 10])  # Upper bounds: x1 <= 10, x2 <= 10
        )

    def _evaluate(self, x, out, **kwargs):
        # Objective: minimize x1^2 + x2^2
        out["F"] = x[0]**2 + x[1]**2

        # Inequality constraint: x1 + x2 >= 1
        # Written as g(x) <= 0: -x1 - x2 + 1 <= 0
        out["G"] = [-x[0] - x[1] + 1]
```

### Step 2: Create Problem Instance

```python
problem = ConstrainedProblem()
```

### Step 3: Configure Algorithm

Use NSGA-II (handles constraints well via feasibility-first approach):

```python
from pymoo.algorithms.moo.nsga2 import NSGA2

algorithm = NSGA2(
    pop_size=100,
    n_offsprings=100,
    eliminate_duplicates=True
)
```

Or use GA for single-objective:

```python
from pymoo.algorithms.soo.nonconvex.ga import GA

algorithm = GA(
    pop_size=100,
    eliminate_duplicates=True
)
```

### Step 4: Run Optimization

```python
from pymoo.optimize import minimize

result = minimize(
    problem,
    algorithm,
    ('n_gen', 200),
    seed=1,
    verbose=False
)
```

### Step 5: Extract and Output Results

```python
# Get the best (feasible) solution
best_x = result.X[0]
best_F = result.F[0]

with open("/root/output.txt", "w") as f:
    f.write(f"Optimal x1: {best_x[0]:.2f}\n")
    f.write(f"Optimal x2: {best_x[1]:.2f}\n")
    f.write(f"Objective: {best_F:.2f}\n")
```

## Complete Script

```python
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import numpy as np

class ConstrainedProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=1,
            n_ieq_constr=1,
            n_eq_constr=0,
            xl=np.array([0, 0]),
            xu=np.array([10, 10])
        )

    def _evaluate(self, x, out, **kwargs):
        out["F"] = x[0]**2 + x[1]**2
        out["G"] = [-x[0] - x[1] + 1]   # x1 + x2 >= 1

problem = ConstrainedProblem()

algorithm = NSGA2(pop_size=100, n_offsprings=100, eliminate_duplicates=True)

result = minimize(problem, algorithm, ('n_gen', 200), seed=1, verbose=False)

best_x = result.X[0]
best_F = result.F[0]

with open("/root/output.txt", "w") as f:
    f.write(f"Optimal x1: {best_x[0]:.2f}\n")
    f.write(f"Optimal x2: {best_x[1]:.2f}\n")
    f.write(f"Objective: {best_F:.2f}\n")
```

## Output Format

```
Optimal x1: X.XX
Optimal x2: X.XX
Objective: X.XX
```

Round to 2 decimal places.

## Constraint Formulation Rules

- Inequality constraints: express as `g(x) <= 0`
- `x1 + x2 >= 1` becomes `-x1 - x2 + 1 <= 0`
- `x1 + x2 <= 2` becomes `x1 + x2 - 2 <= 0`
- Pymoo uses feasibility-first ranking in NSGA-II

## Key Reference

- `ElementwiseProblem` — Base class for custom optimization problems
- `n_ieq_constr=N` — Number of inequality constraints
- `out["G"]` — List of constraint values (must be ≤ 0 for feasibility)
- `NSGA2(pop_size=100)` — Multi-objective algorithm that handles constraints well
- `GA(pop_size=100)` — Single-objective genetic algorithm
- `minimize(problem, algorithm, ('n_gen', N))` — Run optimization for N generations
- `result.X[0]` — Best feasible solution found