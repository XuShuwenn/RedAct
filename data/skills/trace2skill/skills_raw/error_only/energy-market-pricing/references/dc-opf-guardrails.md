# DC-OPF Guardrails

Use this reference when implementing the market-clearing model or constructing network matrices.

## Faithful formulation

Required outputs must come from the specified DC-OPF with reserve co-optimization, not from approximations.

Do:
- Solve base and counterfactual with the same model, changing only the specified line limit.
- Compute LMPs from the optimization model solution.
- Report binding lines from solved flows versus thermal limits.

Do not:
- Substitute economic dispatch plus guessed congestion effects.
- Infer flows from load differences or other heuristics.
- Hard-code reserve MCP or assign identical/flat LMPs without model support.

## MATPOWER indexing

MATPOWER bus identifiers are labels, not guaranteed zero-based or contiguous array indices.

Pattern:
1. Extract bus IDs in model order.
2. Build `bus_to_idx = {bus_id: i for i, bus_id in enumerate(bus_ids)}`.
3. Convert every branch endpoint and generator bus from bus ID to internal index before filling matrices.
4. Build `Bbus`, `Bf`, or PTDF only with internal indices.

Wrong:
- `Y[f_bus, t_bus] += ...` using raw bus numbers.

Right:
- `i = bus_to_idx[f_bus]`
- `j = bus_to_idx[t_bus]`
- `Y[i, j] += ...`

## Minimum sanity checks before reporting

Before trusting results, check:
- Objective/total generation cost is positive and within a plausible range.
- Power balance holds.
- Number of binding lines is not wildly implausible.
- Counterfactual changes at least the modified line limit and any dependent outputs when that constraint is active.
- If results look broken, stop and debug the formulation; do not write the final report from those outputs.