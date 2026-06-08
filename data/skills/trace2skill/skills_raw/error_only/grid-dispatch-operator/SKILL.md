---
name: grid-dispatch-operator
description: "Optimize generator dispatches for power grid with DC power balance, transmission limits, and spinning reserve requirements."
---

# Power Grid Generator Dispatch Optimization

## When to Use

- Optimize economically efficient generator dispatch
- Satisfy power market constraints (DC balance, reserves)
- Analyze transmission line loading


## When to Use

## Execution Rules

- Follow the task's required interaction/output protocol exactly. If the environment specifies an exact completion string, emit it verbatim as the final line.
- Use the task/environment-specified absolute paths. Treat `/root/report.json` as an example unless the runtime explicitly requires it.
- Before sending shell or Python commands, do a quick syntax check for broken quotes, truncated text, or malformed conditionals.
- Prefer the simplest constraints-compliant workflow first. Do not assume extra packages are installed; probe the runtime and prefer a verified available solver or pure-stdlib approach over assuming `numpy` or `scipy` exist.

## Input

- `network.json`: MATPOWER format power network snapshot


- Inspect `network.json` and task data for explicit reserve requirements, reserve semantics, generator statuses, branch limits, and MATPOWER generator cost data before choosing modeling assumptions.
- If a reserve target, market rule, or cost treatment is not specified, state any assumption explicitly and do not present it as given input.


## Constraints

1. DC power balance at each bus
2. Generator and transmission limits
3. Spinning reserve requirements (standard capacity coupling)


4. Final dispatch must be network-feasible: enforce nodal DC power balance, generator bounds, transmission limits, and reserve-capacity coupling in the optimization model itself, not only as a post hoc check.
5. If transmission compliance is required, use bus-angle variables and DC flow relations or an equivalent PTDF/shift-factor formulation.
6. Restrict dispatch and reserve decisions to online generators only (`GEN_STATUS > 0`); exclude offline units from feasible capacity, reserve totals, and operating margin.
7. Preserve MATPOWER `gencost` semantics in the objective; if costs are quadratic/polynomial, optimize that objective or clearly state any unavoidable approximation.

- Do **not** replace the requested constrained optimization with merit-order, proportional, copper-plate, or other heuristic dispatch.
- Do **not** optimize on system-wide balance alone and then merely check flows afterward.
- Couple reserves with headroom explicitly (for example, `dispatch + reserve <= pmax`).
- If post-checks show any overload or violated required constraint, the dispatch is invalid and must be re-solved so the reported dispatch itself satisfies the limits.


## Output Format

JSON at the task-specified absolute output path (use `/root/report.json` only if the runtime instructions explicitly direct that path), for example:
```json
{
  "generator_dispatch": [
    {"id": 1, "bus": 1, "output_MW": 100.0, "reserve_MW": 30.0, "pmax_MW": 150.0}
  ],
  "totals": {
    "cost_dollars_per_hour": 8000.0,
    "load_MW": 259.0,
    "generation_MW": 259.0,
    "reserve_MW": 500.0
  },
  "most_loaded_lines": [{"from": 1, "to": 2, "loading_pct": 85.0}, ...],
  "operating_margin_MW": 50.0
}
```


Use the exact top-level keys shown above: `generator_dispatch`, `totals`, `most_loaded_lines`, `operating_margin_MW`.
Do not rename keys. After writing the report, re-open and parse the JSON to confirm it is readable, complete, and contains the required nested fields such as `output_MW`, `reserve_MW`, and `loading_pct`.
If any requirement is ambiguous, especially reserve obligation or reserve-capability semantics, report the assumption explicitly instead of presenting it as given input.


## Key Metrics

- Generator dispatch MW and reserve MW
- Total cost, load, generation
- Top 3 most loaded transmission lines
- Operating margin (uncommitted capacity)

## Tips

- Use optimization (scipy.optimize or linear programming)
- Check transmission line loading percentages
- Verify spinning reserve requirements


- Build a DC network-constrained dispatch/OPF, not a single-bus economic dispatch: include generator outputs, reserve variables, bus angles, nodal DC balance, branch thermal limits, and one fixed reference bus in one model.
- Use the same optimized dispatch for any post-solution flow/loading report; do not invent heuristic, capped, or placeholder `most_loaded_lines` values.
- Check transmission line loading percentages after solving, but only as validation of constraints already enforced in the model.
- Treat implausible outputs as model bugs, not success. If line loadings or angles look nonphysical, re-check units, PTDF/DC flow calculations, sign conventions, and whether line constraints were actually enforced.
- Do **not** clamp, rescale, or otherwise manually edit dispatch/reserve outputs after solving to "fix" balance or limit issues; fix the formulation and re-solve.
- If a solve fails, debug the current formulation first: check array shapes, index alignment, bounds, online/offline filtering, and solver status before changing solvers or algorithms.
- Do not claim the optimizer succeeded unless you observed explicit completion evidence, such as a success status, exit code, or verified output file with expected contents.
- Read [references/dc-opf-pattern.md](references/dc-opf-pattern.md) when implementing transmission-constrained dispatch or debugging suspicious flow magnitudes.



## Tips

## Final Validation

Before concluding success:

- Confirm the accepted dispatch is the direct solver result, not post-processed by ad hoc clamping or proportional rescaling.
- Confirm every bus satisfies DC nodal balance in the solved model.
- Confirm no transmission line exceeds its limit.
- Confirm no offline generator has nonzero dispatch or reserve.
- Confirm totals are internally consistent (`generation_MW == load_MW` within tolerance) and reserve coupling holds.
- Confirm reported line loadings come from the same DC-constrained dispatch being reported.
- If any required constraint is violated or results cannot be physically validated, do not present the run as completed successfully; revise the model or report the limitation clearly.
- End with the exact required completion string when one is specified by the environment.
