---
name: pymoo-constrained-nsga2
description: "Solve constrained continuous optimization with pymoo (e.g., NSGA-II), extract the best feasible solution robustly, and produce verified formatted outputs."
---

Constrained optimization with pymoo requires careful problem encoding (objective and constraints), robust extraction of the best feasible solution from the optimizer output, and verification before finalizing results.

When to Use
- Tasks that ask to minimize or maximize a continuous function subject to constraints using pymoo (e.g., NSGA-II)
- Problems with variable bounds and one or more inequality/equality constraints
- Situations where the result must be written in a specific formatted output with rounded values

Core Workflow
1. Problem Encoding
   - Express the objective function f(x) as a deterministic computation from decision variables x.
   - Convert constraints to pymoo’s convention using G(x) ≤ 0.
     - Example rewrite rules:
       - a(x) ≥ b → G(x) = b − a(x) ≤ 0
       - a(x) ≤ b → G(x) = a(x) − b ≤ 0
       - Equality c(x) = 0 → represent as two inequalities if necessary: c(x) ≤ tol and −c(x) ≤ tol.
   - Set variable bounds for each decision variable.
   - Implement a Problem or ElementwiseProblem with _evaluate returning F (objective) and G (array of constraint values).

2. Algorithm Selection and Configuration
   - Use NSGA-II for constrained problems; set population size, sampling (e.g., random or Latin hypercube), crossover/mutation operators, and a termination criterion (e.g., n_gen).
   - Optionally set a random seed for reproducibility.
   - Ensure constraints are provided to the Problem so the algorithm can handle feasibility.

3. Run Optimization
   - Call pymoo.optimize.minimize with the problem, algorithm, termination, and any callbacks you need.
   - Capture result.X, result.F, and result.G.

4. Extract the Best Feasible Solution
   - The optimizer may return either a single solution (scalars/1D arrays) or a population (2D arrays). Do not assume one specific shape.
   - Filter by feasibility G ≤ tol (use a small tolerance like 1e-8 to handle numerical noise).
   - Among feasible solutions, select the one with the smallest F for minimization.
   - If no feasible solution is present, adjust parameters (population, generations) or algorithm settings and rerun; only finalize after obtaining a verified feasible solution.
   - Use the provided optional helper script to robustly select the best feasible solution across different return shapes.

5. Verification
   - Recompute the objective from the selected x independently to confirm the reported value matches (within a small numerical tolerance).
   - Constraint check: verify all G(x) ≤ tol.
   - Bounds check: confirm x lies within its bounds.
   - Rounding: round decision variables and objective to the required precision only at the final formatting step.

6. Output Formatting
   - Produce exactly the lines and decimal precision requested by the task. Example pattern:
     - "Optimal x1: X.XX"
     - "Optimal x2: X.XX"
     - "Objective: X.XX"
   - Ensure values are rounded to the specified number of decimals and written in the required order.

Verification
- Confirm the solution is feasible: all constraints ≤ tolerance.
- Confirm bounds are respected: each variable within its lower/upper bounds.
- Cross-check the objective by recomputing it using the selected x.
- Confirm output formatting: correct labels, order, and rounding precision.

Common Pitfalls
- Incorrect constraint direction: forgetting to convert to G(x) ≤ 0 leads to selecting invalid points.
- Ignoring numerical tolerance: strict G ≤ 0 without tolerance can reject near-feasible points due to floating-point noise.
- Misreading result shapes: treating a single solution as a list or a population as a scalar; always handle both.
- Selecting the lowest objective without feasibility filtering: may return a constraint-violating solution.
- Premature rounding: rounding internal values before verification can cause small feasibility violations; round only when formatting outputs.
- Insufficient termination: too few generations or too small a population can produce no feasible candidates; increase termination or population if needed.
- Not verifying after optimization: failing to recompute the objective and constraints can let subtle extraction bugs pass through.

Optional Script Usage
- Use scripts/pymoo_result_utils.py to robustly extract the best feasible solution regardless of whether pymoo returns a single solution or a population.
- Typical steps:
  - Run minimize and get result.X, result.F, result.G.
  - Call select_best_feasible(X, F, G, tol=1e-8) to obtain (x_best, f_best, feasible, idx).
  - If feasible is False, adjust algorithm settings (population size, generations, operators) and rerun.
  - After selection, recompute objective and constraints for verification, then format and write outputs.

Success Criteria
- A feasible solution is found (constraints satisfied within tolerance and within bounds).
- The objective value recomputed from the chosen x matches the optimizer’s value within numerical tolerance.
- Final outputs are correctly rounded and formatted as specified by the task.
