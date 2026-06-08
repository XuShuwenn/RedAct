---
name: pymoo-nsga2-pareto-export
description: "Use pymoo’s NSGA-II to compute a Pareto front for simple multi-objective problems and export sorted, formatted points."
---

# NSGA-II Pareto Front with pymoo

This skill describes a robust workflow to set up and run a short NSGA-II optimization using the pymoo library for simple multi-objective problems, extract a non-dominated set, and export results in a predictable, sorted format.

## When to Use

Activate this skill when the user requests:
- A Pareto front for a small multi-objective problem using pymoo
- NSGA-II with specific population size and generation count
- Exporting solutions as lines containing decision variable and objective values, sorted by the decision variable and with specified rounding requirements

## Core Workflow

Follow these steps to ensure a correct and reproducible export of Pareto solutions.

1. Define the problem
   - Use pymoo’s Problem or ElementwiseProblem to encode decision variables, bounds, and objectives.
   - For a single decision variable x and two objectives f1(x), f2(x), a minimal ElementwiseProblem keeps shapes simple.

   Example using ElementwiseProblem:
   ```python
   import numpy as np
   from pymoo.core.problem import ElementwiseProblem

   class TwoObj1D(ElementwiseProblem):
       def __init__(self, xl, xu, f1, f2):
           super().__init__(n_var=1, n_obj=2, n_constr=0, xl=xl, xu=xu)
           self.f1 = f1
           self.f2 = f2
       def _evaluate(self, x, out, *args, **kwargs):
           xi = float(x[0])
           out["F"] = np.array([self.f1(xi), self.f2(xi)], dtype=float)
   ```

2. Configure NSGA-II and termination
   - Respect requested parameters (population size, number of generations).
   - Optionally set a random seed for reproducibility when needed.

   ```python
   from pymoo.algorithms.moo.nsga2 import NSGA2
   from pymoo.termination import get_termination
   from pymoo.optimize import minimize

   algorithm = NSGA2(pop_size=POPULATION)
   termination = get_termination("n_gen", N_GENERATIONS)

   res = minimize(
       problem, algorithm, termination=termination, seed=SEED if SEED is not None else None,
       save_history=False, verbose=False
   )
   ```

3. Extract candidate solutions
   - Obtain decision variables `X` and objectives `F` from the result.
   - Flatten shapes for a single variable: `X = res.X.reshape(-1)` and `F = res.F` with shape `(n, 2)`.

   ```python
   import numpy as np
   X = np.array(res.X).reshape(-1)
   F = np.array(res.F)
   ```

4. Filter to the non-dominated set
   - NSGA-II’s final population can contain dominated points; filter explicitly.
   - Use a nondomination check (see helper script or snippet below).

   ```python
   def is_nondominated(F):
       # Minimization: i is dominated if exists j with F[j] <= F[i] for all objectives
       # and strictly less for at least one objective.
       n = len(F)
       keep = np.ones(n, dtype=bool)
       for i in range(n):
           if not keep[i]:
               continue
           for j in range(n):
               if i == j:
                   continue
               if np.all(F[j] <= F[i]) and np.any(F[j] < F[i]):
                   keep[i] = False
                   break
       return keep

   mask = is_nondominated(F)
   X_nd, F_nd = X[mask], F[mask]
   ```

5. Sort by the decision variable and format output
   - Sort by the raw decision variable values (do not round before sorting).
   - Round the decision variable to the requested precision for display.
   - Keep objective values unrounded unless the task requests rounding.

   ```python
   order = np.argsort(X_nd)
   X_sorted = X_nd[order]
   F_sorted = F_nd[order]

   lines = []
   for xi, (f1, f2) in zip(X_sorted, F_sorted):
       lines.append(f"{xi:.3f}={f1},{f2}")
   # Write lines to the requested output path
   ```

## Verification

Before finalizing, perform these checks:
- Bounds: all decision variable values are within the declared lower/upper bounds.
- Shapes: `X` is 1D of length n; `F` is an array of shape `(n, 2)`.
- Nondomination: confirm `is_nondominated(F)` is true for all returned points.
- Sorting: confirm the lines are sorted by the raw decision variable (not by the rounded value). For example:
  ```python
  assert np.all(np.diff(X_sorted) >= 0)
  ```
- Formatting: each line matches the exact schema `"{x}={f1},{f2}"` with x rounded to the required decimals.
- Consistency: if objectives are simple analytic functions, optionally recompute f1(x), f2(x) from the exported x and compare to the stored objective values within a small tolerance.

## Common Pitfalls

- Rounding before sorting: sorting by rounded x can change order or merge distinct points; always sort by raw x and round only for display.
- Skipping nondomination filtering: the final population may include dominated points; explicitly filter to the non-dominated set.
- Shape mistakes in `_evaluate`: objective output must be a length-2 vector per point; ensure `out["F"]` is a numeric vector of the correct length.
- Ignoring bounds: if the problem is defined with bounds, verify all `X` obey those bounds.
- Wrong objective orientation: pymoo minimizes by default. If you intend maximization, negate objectives or transform appropriately.
- Non-determinism: short evolutionary runs can yield a variable count of Pareto points or duplicates. If the task requires exact counts, set a seed and consider additional filtering.
- Incorrect formatting: missing `=` or `,` separators, extra spaces, or unexpected rounding. Validate the line schema before writing.

## Optional Script Usage

Use the provided helper scripts to streamline verification and export:
- `scripts/pareto_utils.py`: nondomination check, sorting assertions, and line formatting utilities.
- `scripts/nsga2_1d_two_obj.py`: a reusable runner for 1D two-objective problems that accepts objective expressions, bounds, algorithm parameters, and writes a sorted export. Example:
  ```
  python scripts/nsga2_1d_two_obj.py \
      --f1 '(x-2)**2' --f2 '(x+2)**2' \
      --xl -10 --xu 10 --pop 50 --gen 3 \
      --out output.txt --round-x 3
  ```

Success Criteria:
- Uses pymoo NSGA-II with requested settings.
- Correctly encodes objectives and bounds.
- Outputs only non-dominated solutions.
- Sorted by raw decision variable and rounded per specification.
- Passes verification checks without errors.
