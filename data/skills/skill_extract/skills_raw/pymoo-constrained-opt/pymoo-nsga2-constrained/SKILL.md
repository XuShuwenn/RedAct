---
name: pymoo-nsga2-constrained
description: "Solve bounded single-objective optimization problems with inequality constraints using pymoo's NSGA-II, extract the best solution robustly, and verify feasibility before formatting output."
---

# Constrained Single-Objective Optimization with pymoo (NSGA-II)

Reusable workflow for minimizing a scalar objective under bounds and inequality constraints using pymoo's NSGA-II. It includes robust result extraction, feasibility verification, and output formatting.

## When to Use

Activate this skill when you need to:
- Minimize a single objective f(x) with variable bounds and inequality constraints using pymoo.
- Use NSGA-II as a general-purpose evolutionary optimizer.
- Produce a formatted, rounded solution and ensure feasibility of constraints before writing results.

## Core Workflow

1. Define the problem with ElementwiseProblem
   - Use ElementwiseProblem for clarity and control of constraints.
   - pymoo expects inequality constraints in the form G(x) <= 0.
   - For a user constraint of the form h(x) >= 0, convert to G(x) = -h(x) <= 0.
   - For a linear constraint a^T x >= b, convert to G(x) = (b - a^T x) <= 0.

```python
from pymoo.core.problem import ElementwiseProblem
import numpy as np

class MyProblem(ElementwiseProblem):
    def __init__(self, n_var, xl, xu, n_ieq):
        super().__init__(
            n_var=n_var,
            n_obj=1,
            n_ieq_constr=n_ieq,
            xl=np.asarray(xl, dtype=float),
            xu=np.asarray(xu, dtype=float),
        )

    def _evaluate(self, x, out, **kwargs):
        # Define objective f(x)
        f = ...  # e.g., float expression using x

        # Define inequality constraints G(x) <= 0
        # Example placeholders (ensure length == n_ieq):
        G = [ ... ]  # each entry is a float constraint value

        out["F"] = f
        out["G"] = np.asarray(G, dtype=float)
```

2. Configure and run NSGA-II
   - Use a reasonable population size and generations.
   - Set a seed for reproducibility.
   - Use eliminate_duplicates=True to avoid redundant solutions.

```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

algorithm = NSGA2(pop_size=100, n_offsprings=100, eliminate_duplicates=True)
res = minimize(MyProblem(...), algorithm, ('n_gen', 200), seed=1, verbose=False)
```

3. Robustly extract the best solution
   - Single-objective results may return a scalar F and a 1-D X, or arrays depending on versions and settings.
   - Always coerce shapes and pick argmin(F) safely.

```python
import numpy as np

X = np.atleast_2d(res.X)
F = np.asarray(res.F).reshape(-1)
idx = int(np.argmin(F))
best_x = X[idx]
best_f = float(F[idx])
```

4. Verify feasibility and bounds before finalizing
   - Compute max constraint violation: max(0, G_i(x)). If any violation exceeds a small tolerance, treat as infeasible.
   - Ensure bounds are satisfied within a tolerance.

```python
# Recompute G(x) for best_x exactly as in _evaluate
G_best = np.asarray([ ... ], dtype=float)  # same expressions used to populate out["G"]
violation = float(np.maximum(G_best, 0.0).max()) if G_best.size else 0.0
assert violation <= 1e-6, "Best solution is not feasible within tolerance."

# Bound check
tol = 1e-8
xl = np.asarray(..., dtype=float)
xu = np.asarray(..., dtype=float)
assert np.all(best_x >= xl - tol) and np.all(best_x <= xu + tol), "Bounds violated."
```

5. Format and write output
   - Round to the required precision (e.g., 2 decimals).
   - Write exactly the expected keys and ordering as specified by the task.

```python
with open(output_path, 'w') as f:
    for i, v in enumerate(best_x, start=1):
        f.write(f"Optimal x{i}: {v:.2f}\n")
    f.write(f"Objective: {best_f:.2f}\n")
```

## Verification

- Feasibility: Evaluate the final candidate and compute max(0, G_i(x)). Require this to be below a small tolerance (e.g., 1e-6).
- Bounds: Confirm xl <= x <= xu component-wise (allow minor numerical tolerance).
- Reproducibility: Fix a random seed and keep termination criteria explicit.
- Sanity vs. baseline: Optionally evaluate a few feasible random points to confirm the selected solution has the lowest objective among them.
- Output format: Ensure required keys, order, and rounding exactly match the task specification.

## Common Pitfalls and How to Avoid Them

- Wrong constraint sign: pymoo uses G(x) <= 0. Convert constraints like "c(x) >= 0" to G(x) = -c(x).
- Mismatch in n_ieq_constr: Ensure the number of entries in out["G"] equals n_ieq_constr. Returning fewer or more entries will break evaluation.
- Shape handling of results: Single-objective minimize may yield scalar F and 1-D X. Always coerce shapes (np.atleast_2d for X, reshape(-1) for F) before argmin to avoid indexing errors.
- Infeasible "best" solution: Evolutionary algorithms can converge near, but not on, the feasible region. Explicitly compute and check constraint violations; if infeasible, increase generations, adjust population, or refine constraints.
- Ignoring bounds in verification: Do not assume the optimizer respected bounds perfectly; verify with tolerance and correct if necessary.
- Non-determinism: Omitted seeds can cause run-to-run differences and brittle tests. Set a seed for reproducibility.
- Incorrect rounding/formatting: Round to the required decimals and match the exact output schema.

## Optional Script Usage

Use scripts/pymoo_utils.py to simplify robust extraction, feasibility checks, and output formatting.

```python
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
import numpy as np
from scripts.pymoo_utils import best_from_result, max_constraint_violation, write_rounded_solution

# ... define MyProblem as above
problem = MyProblem(...)
algorithm = NSGA2(pop_size=100, n_offsprings=100, eliminate_duplicates=True)
res = minimize(problem, algorithm, ('n_gen', 200), seed=1, verbose=False)

best_x, best_f, _ = best_from_result(res)

# Recompute G(best_x) as in _evaluate
G_best = np.asarray([ ... ], dtype=float)
assert max_constraint_violation(G_best) <= 1e-6

write_rounded_solution(output_path, best_x, best_f, decimals=2)
```

## Success Criteria

- The reported solution satisfies all inequality constraints within numerical tolerance and lies within bounds.
- The objective is minimized among tested candidates (and is stable under repeated runs with the same seed).
- The output file exists and matches the expected key order and rounding.
