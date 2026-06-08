---
name: pymoo-nsga2-pareto-export
description: "Use pymoo's NSGA-II to approximate two-objective Pareto fronts and export sorted, formatted decision–objective pairs."
---

# NSGA-II Pareto Front Export with pymoo

Skill for solving simple multi-objective optimization tasks (typically 1 decision variable, 2 objectives) using pymoo's NSGA-II and exporting the resulting Pareto-approximate points in a sorted, line-oriented text format.

## When to Use

Activate this skill when the task asks you to:
- use pymoo and NSGA-II to find a Pareto front for a low-dimensional, unconstrained or bound-constrained problem, and
- output decision variable and objective values in a specified line format, sorted by the decision variable, with a rounding requirement for display.

## Core Workflow

1. Problem Modeling in pymoo
   - Subclass `ElementwiseProblem`.
   - Set:
     - `n_var` to the number of decision variables (commonly 1 in these tasks)
     - `n_obj` to 2 for two-objective problems
     - `xl`, `xu` as arrays of lower/upper bounds of shape `(n_var,)`
   - Implement `_evaluate(self, x, out, **kwargs)` where:
     - `x` is a 1D array of decision variables
     - Compute objective values as a list or 1D array `[f1, f2]`
     - Assign to `out["F"] = [f1, f2]`

2. Configure and Run NSGA-II
   - Instantiate `NSGA2(pop_size=<given>)`.
   - Call `minimize(problem, algorithm, termination=("n_gen", <given>), seed=<int>, verbose=False)`.
   - Use a seed for reproducibility when required by the task.

3. Extract Candidate Pareto Points
   - Obtain `res.X` (decision vectors) and `res.F` (objective values).
   - Optionally filter dominated solutions to ensure output is nondominated (see Verification section for a robust check).

4. Sort and Format for Output
   - Pair each `x` with its corresponding `f` from `res.X` and `res.F` without recomputing using rounded values.
   - Sort by the primary decision variable (e.g., `x1`) ascending.
   - Round only for display (e.g., `x1` rounded to the required decimals). Do not recompute objectives from the rounded value unless explicitly requested.
   - Write one line per solution in the task-specified format, e.g.: `{x1_rounded}={f1},{f2}`.

5. Write Results
   - Write to the required output path. If none is specified, use a path appropriate for the environment (e.g., `/root/output.txt` in some benchmarks).

## Verification

Perform these checks before finalizing:
- Dimensions:
  - Verify `res.X` has shape `(n_points, n_var)` and `res.F` has shape `(n_points, 2)` for two objectives.
- Bounds adherence:
  - Confirm each `x1` satisfies its bounds (e.g., `xl <= x1 <= xu`).
- Nondominance:
  - Filter out dominated points using a nondominance check. For two objectives with minimization, a point `a` dominates `b` if `a` is not worse in all objectives and strictly better in at least one.
- Sorting:
  - Ensure the file is strictly sorted by `x1` ascending.
- Formatting:
  - Ensure each line matches the expected pattern and newline-terminated.
  - Confirm rounding is applied only to the displayed `x1`.
- Sanity:
  - Spot-check a few `x1` values by recomputing objectives from the original `x` (not the rounded display) and confirm they match `res.F` numerically within floating-point tolerance.

## Common Pitfalls and How to Avoid Them

- Rounding before evaluation:
  - Pitfall: Recomputing objectives using the rounded `x1`, leading to mismatches with algorithm outputs.
  - Fix: Always use `res.X` and `res.F` from pymoo for the final numbers; round only for display.

- Wrong bounds or shapes:
  - Pitfall: Passing scalars instead of arrays for `xl/xu`, or wrong `n_var`.
  - Fix: Ensure `xl` and `xu` are arrays of length `n_var` and match the dimensions of `x`.

- Incomplete termination settings:
  - Pitfall: Using the wrong termination criterion or forgetting to set the number of generations.
  - Fix: Use `termination=("n_gen", n_gen)` for generation-based termination as specified.

- Dominated solutions in output:
  - Pitfall: Emitting dominated points if the algorithm's current population contains them.
  - Fix: Apply a nondominance filter to `res.F`/`res.X` before sorting and writing.

- Unstable results across runs:
  - Pitfall: Missing `seed` leads to non-reproducible outputs.
  - Fix: Set a fixed integer seed when the task expects consistent output ordering.

- Misformatted output:
  - Pitfall: Wrong delimiter, missing `=` sign, inconsistent decimals.
  - Fix: Build the output line format explicitly and test with a small sample.

## Optional Script Usage

This repository includes a generic CLI for two-objective, one-variable problems to speed up repeated tasks.

- Path: `scripts/pymoo_nsga2_cli.py`
- What it does:
  - Takes two objective expressions in terms of `x1`, bounds, population, generations, and output path.
  - Runs NSGA-II via pymoo and writes sorted lines in the format `{x1_rounded}={f1},{f2}`.
  - Applies a nondominance filter and sorts by `x1` ascending.

Example usage:
- python scripts/pymoo_nsga2_cli.py --f1 "(x1 - 2)**2" --f2 "(x1 + 2)**2" --xl -10 --xu 10 --pop-size 50 --n-gen 3 --seed 1 --round-x 3 --out /root/output.txt

Success criteria:
- Pareto-approximate solutions exported, correctly sorted by `x1`, rounded as requested for display, matching the required line format.
