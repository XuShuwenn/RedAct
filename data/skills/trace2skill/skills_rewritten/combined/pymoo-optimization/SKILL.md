---
name: pymoo-optimization
description: "Solve multi-objective optimization problems using pymoo with NSGA-II to find Pareto front solutions."
---

# Multi-Objective Optimization with pymoo

## When to Use

- Find Pareto front for multi-objective problems
- Use NSGA-II algorithm for optimization
- Handle multiple objectives and bounds

- If the task depends on local code, data, or installed packages, inspect the relevant workspace files and directories first so you use the correct inputs and execution path.

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
- Before coding, restate the task requirements to yourself: objective definitions, bounds, algorithm, population size, generation count, required output path, sorting rule, and numeric formatting.
- If any of those details are specified in the prompt, mirror them exactly in the script rather than relying on defaults or example values from this skill.
- If the task provides an existing optimization script, inspect it before rewriting anything; when it already matches the prompt, prefer running and validating it over rebuilding from scratch.

- If you need a helper script and the first location is not writable, use a confirmed writable scratch path such as `/tmp`.

- Start with a quick directory check when the workspace context is unclear so you know which paths are available before creating scripts or outputs.
- Before debugging optimization logic, confirm Python runs and `pymoo` imports successfully; if the dependency is missing, install it first and then rerun the same end-to-end workflow.
- For helper scripts or temporary files, choose a known writable location immediately; prefer the current directory when confirmed writable, otherwise use a scratch path such as `/tmp`, while still writing the required final artifact to `/root/output.txt`.
- Start with a minimal end-to-end smoke run early so `minimize(...)` exposes pymoo API/interface mismatches before you polish formatting.
- Create outputs only in confirmed writable locations, but ensure the final artifact is written to `/root/output.txt` when required.
- Build the final deliverable from the solver result rather than from exploratory prints or manual post-processing.
- If `minimize` fails early, check the pymoo problem interface and the shape of `out["F"]` first.

- Use the task-specified algorithm directly: NSGA-II for this skill, and set any prompt-specified algorithm settings explicitly in code rather than relying on defaults.
- If `minimize` fails early, inspect the custom problem definition first: verify `n_var`, `n_obj`, bounds (`xl`/`xu`), numeric dtypes, and that `_evaluate` writes `out["F"]` with the expected shape.
- After `minimize`, normalize `res.X` and `res.F` into aligned row-wise arrays before formatting: if either is `None`, fail fast; if a single solution is returned, wrap it so it iterates as one row; otherwise pair rows directly from `res.X` and `res.F`.
- Build the final deliverable directly from `res.X` and `res.F`, and convert NumPy-derived values to Python scalars before rounding or formatting.
- Treat successful command output or optimizer return status as a checkpoint to begin artifact validation, not as proof the deliverable is complete.

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

- Treat the reopened file contents as the source of truth for completion rather than assuming the write succeeded from stdout or exit status alone.
- Confirm `/root/output.txt` exists at that exact path, is non-empty, each line matches `{x1_value}={f1_value},{f2_value}`, and the number of written lines matches the number of extracted solution rows.
- Inspect representative first/last or sample lines after reopening to confirm exact structure, sorting by `x1` ascending, rounding, and delimiter placement.
- If the persisted line count does not match the number of rows you expected, inspect the file ending or tail before rerunning so you can distinguish truncation from formatting issues.
- In the final response, explicitly confirm that `/root/output.txt` was written and summarize only observable facts from the verified file or tool output, such as row count, ordering, or visible Pareto trade-off structure.



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

- Resolve missing libraries and permission issues first; environment/setup problems are often the fastest blocker to clear.
- When summarizing results, report structural properties you verified from the file or solver output, such as row count, ordering, range, or visible trade-off pattern, instead of restating unverified details.
