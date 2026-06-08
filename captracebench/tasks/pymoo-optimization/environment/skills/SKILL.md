---
name: pymoo
description: "Multi-objective optimization using NSGA-II. Define custom problems, find Pareto front, minimize conflicting objectives. Use when solving optimization problems with 2-3 objectives, Pareto front analysis, or NSGA-II algorithm configuration."
---

# Pymoo - Multi-Objective Optimization with NSGA-II

## Overview

Pymoo is a Python framework for optimization. This skill covers using NSGA-II for bi-objective optimization and defining custom multi-objective problems.

## Core Workflow: Multi-Objective Optimization with NSGA-II

```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
import numpy as np

# Step 1: Define custom problem
class MyProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=1,              # Number of variables (x1)
            n_obj=2,              # Number of objectives (f1, f2)
            n_ieq_constr=0,      # No inequality constraints
            n_eq_constr=0,       # No equality constraints
            xl=np.array([-10]),   # Lower bound: x1 >= -10
            xu=np.array([10])     # Upper bound: x1 <= 10
        )

    def _evaluate(self, x, out, **kwargs):
        f1 = (x[0] - 2)**2
        f2 = (x[0] + 2)**2
        out["F"] = [f1, f2]

# Step 2: Create problem instance
problem = MyProblem()

# Step 3: Configure NSGA-II
algorithm = NSGA2(
    pop_size=50,      # Population size
    n_offsprings=50,   # Offspring per generation
    eliminate_duplicates=True
)

# Step 4: Run optimization
result = minimize(
    problem,
    algorithm,
    ('n_gen', 3),      # 3 generations
    seed=1,
    verbose=False
)

# Step 5: Output results
solutions = []
for x, f in zip(result.X, result.F):
    solutions.append(f"x1={x[0]:.3f},{f[0]:.6f},{f[1]:.6f}")

# Sort by x1 ascending
solutions.sort(key=lambda s: float(s.split("=")[1].split(",")[0]))

# Write to file
with open("/root/output.txt", "w") as f:
    for sol in solutions:
        f.write(sol + "\n")
```

## Defining Custom Problems

Extend `ElementwiseProblem` class:

```python
class CustomProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2,              # Number of decision variables
            n_obj=2,              # Number of objectives
            n_ieq_constr=0,       # Number of inequality constraints
            n_eq_constr=0,       # Number of equality constraints
            xl=np.array([x1_min, x2_min]),  # Lower bounds
            xu=np.array([x1_max, x2_max])    # Upper bounds
        )

    def _evaluate(self, x, out, **kwargs):
        # Define objective functions
        out["F"] = [f1(x), f2(x)]
        # Define constraints if needed:
        # out["G"] = [g1(x), g2(x)]  # g(x) <= 0
        # out["H"] = [h1(x)]          # h(x) == 0
```

## NSGA-II Algorithm Configuration

```python
from pymoo.algorithms.moo.nsga2 import NSGA2

algorithm = NSGA2(
    pop_size=100,           # Population size (default: 100)
    n_offsprings=None,      # Offspring per generation (default: same as pop_size)
    sampling=None,           # Initial sampling strategy (default: RandomSampling)
    selection=None,          # Parent selection (default: Tournament)
    crossover=None,         # Crossover operator (default: SBX)
    mutation=None,           # Mutation operator (default: PM)
    eliminate_duplicates=True,  # Remove duplicate solutions
    n_offsprings=10         # Number of offspring per generation
)
```

**Key parameters:**
- `pop_size`: Number of individuals in population
- `n_offsprings`: Number of offspring created each generation
- `eliminate_duplicates`: Whether to eliminate duplicate individuals (default: True)

## Running Optimization

```python
from pymoo.optimize import minimize

result = minimize(
    problem,                    # Problem definition
    algorithm,                 # NSGA2 configured above
    termination=('n_gen', N), # Stop after N generations
    seed=1,                    # Random seed for reproducibility
    verbose=False               # Show progress
)
```

**Result object contains:**
- `result.X`: Decision variables of all Pareto optimal solutions (Nxvars matrix)
- `result.F`: Objective values of all Pareto optimal solutions (Nxn_obj matrix)
- `result.algorithm`: Algorithm object with history

## Output Format

For each Pareto solution, output: `x1=f1,f2`

Sorted by x1 ascending, x1 rounded to 3 decimal places:

```python
for i in range(len(result.X)):
    x1 = result.X[i][0]
    f1 = result.F[i][0]
    f2 = result.F[i][1]
    print(f"x1={x1:.3f},{f1:.6f},{f2:.6f}")
```

## Key Reference

- `ElementwiseProblem` — Base class for custom optimization problems
- `NSGA2(pop_size=50)` — Configure NSGA-II with population size
- `minimize(problem, algorithm, ('n_gen', N))` — Run optimization for N generations
- `result.X` — Decision variable values
- `result.F` — Objective function values
- `xl`, `xu` — Lower and upper bounds for variables