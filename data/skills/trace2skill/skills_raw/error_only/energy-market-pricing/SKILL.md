---
name: energy-market-pricing
description: "Run DC-OPF market clearing twice (base and counterfactual) to analyze transmission constraints and congestion impact."
---

# DC-OPF Market Clearing and Congestion Analysis

## When to Use

- Analyze transmission constraint impacts on electricity prices
- Compare base vs counterfactual market clearing results
- Identify congestion patterns and LMP changes

## Input Files

- `network.json`: MATPOWER format power system
- Before coding, inspect `bus`, `gen`, `branch`, and `gencost` in `network.json` and confirm where costs, limits, statuses, and reserve-related data are stored. Do **not** assume generator cost coefficients are embedded in `gen` rows unless the file explicitly shows that.
- Thermal capacity line 64→1501 increased 20% in counterfactual


## Input Files

## Validate Inputs Before Modeling

- Inspect `network.json` structure before building the OPF: verify where buses, generators, branches, costs, reserves, and any `column_info` / metadata are stored.
- Confirm MATPOWER field meanings before using them. Do **not** guess column indices, thermal-limit fields, generator cost definitions, reserve data semantics, or whether quantities need `baseMVA` scaling.
- Use one consistent unit convention for load, generation limits, line limits, flows, reserve quantities, and prices.
- Confirm the counterfactual semantics before modeling: only the line **64→1501** thermal capacity changes, and it increases by **20%** in the counterfactual.

## Market Model

DC-OPF with reserve co-optimization:
1. Power balance at each bus
2. Temperature limits on generators and lines
3. Spinning Reserve Requirements


## Formulation Requirements

## Formulation Requirements

- Use an actual DC-OPF with reserve co-optimization for both cases. Do **not** approximate total cost, LMPs, or reserve MCP with heuristics, simplified adders, or post-hoc pricing proxies.
- Keep network power-balance and transmission line-flow constraints in both runs so the line-limit change can affect congestion and nodal prices.
- Include nodal power-balance equations for **every bus**, including the reference/slack bus.
- Fix the reference angle separately (`theta_ref = 0` or equivalent), but do **not** replace the slack-bus balance equation with only an angle-fixing constraint.
- Derive reported LMPs and reserve MCP from the solved optimization model/duals or an equivalent exact market-clearing formulation.

## Output Format

Report at `/root/report.json`, for examlple:
```json
{
  "base_case": {
    "total_cost_dollars_per_hour": 12500.0,
    "lmp_by_bus": [{"bus": 1, "lmp_dollars_per_MWh": 35.2}, ...],
    "reserve_mcp_dollars_per_MWh": 5.0,
    "binding_lines": [{"from": 5, "to": 6, "flow_MW": 100.0, "limit_MW": 100.0}]
  },
  "counterfactual": {...},
  "impact_analysis": {
    "cost_reduction_dollars_per_hour": 200.0,
    "buses_with_largest_lmp_drop": [...],
    "congestion_relieved": true
  }
}
```


## Execution Checks

## Execution Checks

- After any code or model change, rerun the full workflow and verify the run completed before trusting outputs.
- Do **not** treat truncated logs or partial file views as proof that both scenarios solved.
- Before reading `/root/report.json`, confirm the corrected run finished and rewrote the artifact via a successful exit/termination status, completion message, or fresh file timestamp.
- Only summarize results after verifying both base and counterfactual cases completed successfully and the final report was regenerated.

## Key Metrics

- Binding lines: loading >= 99% of thermal capacity
- LMP = Locational Marginal Price at each bus
- Reserve MCP: system-wide reserve clearing price


## Preflight Validation

## Preflight Validation

- Confirm the case has the expected MATPOWER sections: `baseMVA`, `bus`, `gen`, `branch`, `gencost`.
- Verify the specific branch corresponding to line **64→1501** exists before modifying its thermal limit for the counterfactual.
- Sanity-check units and sign conventions used in power balance, branch flow limits, generator limits, and reserve requirements before solving.
- Do **not** switch to a new solver just because the first run is infeasible; first inspect formulation errors such as slack-bus treatment, flow sign conventions, reserve coupling, and line-limit encoding.

## Tips

- Run market clearing twice with different constraints
- Compare LMP differences to find impacted buses
- Report top 3 buses with largest LMP drop
- Build the base-case model from verified data before applying the counterfactual line-limit change.
- If generation costs are quadratic/polynomial, read them from `gencost` and formulate the objective accordingly rather than guessing from `gen` columns.
- In MATPOWER-style data, create a dense `bus_id -> internal_index` mapping before building susceptance/PTDF matrices or indexing arrays; bus numbers may be noncontiguous.
- If the full case is difficult, debug on a reduced but mathematically faithful model first, then scale back to the full network.
- Read `references/dc-opf-guardrails.md` when implementing the optimization or network matrices.

- Before coding, inspect the input schema and map every column/field used in costs, limits, reserves, and line ratings.
- Do **not** simplify away transmission constraints or reserve co-optimization; the counterfactual must propagate through the network model.
- Validate MATPOWER conventions before solving: keep `bus[:, PD]`, `gen[:, PMIN]`, and `gen[:, PMAX]` in consistent units, and do not multiply only some quantities by `baseMVA`.
- If the base case is infeasible, debug the formulation on the verified input data before rewriting the algorithm.
- After each solve, check solver status before reading dispatch or price outputs; do **not** write `report.json` from missing variables, failed solves, stale artifacts, or incomplete logs.
- Before summarizing impacts, inspect the complete final `report.json` and verify the cited numbers actually appear there.
- Do not finish until `/root/report.json` is written with both scenarios and impact analysis.




## Minimum completion checklist

## Minimum completion checklist

1. Build the same DC-OPF with reserve co-optimization for both runs; only change the **64→1501** thermal limit in the counterfactual.
2. Solve base case and counterfactual successfully.
3. Extract total cost, bus-level LMPs, reserve MCP, and binding lines for each run.
4. Compare cases and write `/root/report.json`.

## Validation Before Finalizing

## Validation Before Finalizing

Treat these checks as mandatory before writing `/root/report.json` or claiming success:
- Confirm solver/termination status is successful for **both** scenarios before extracting dispatch, LMPs, reserve MCP, or line flows.
- Verify the counterfactual only changes the specified line **64→1501** thermal limit by **+20%**.
- Verify `/root/report.json` is complete, readable JSON and not truncated.
- Confirm physical consistency: total dispatched generation covers total load within numerical tolerance, and no reported binding/loaded line exceeds its thermal limit except negligible solver tolerance.
- Confirm economic consistency: total cost is reported in `$ / hour`, while LMP and reserve MCP are reported in `$ / MWh`; re-check signs, scaling, dual conventions, and final magnitudes if objective scaling or per-unit conversions changed during debugging.
- Treat implausible outputs as blocking issues. Examples: `$0/hr` total cost, suspiciously uniform prices, identical results after a material constraint change, implausably many binding lines, or prices/MCP that are orders of magnitude off without a clear model-based reason.
- Check that binding-line identification is consistent with the skill threshold (`loading >= 99%` of thermal capacity) and that binding lines, LMP changes, reserve MCP, and congestion relief tell a coherent network-constrained story.
- If solver warnings, infeasibility, unexplained generation-load mismatch, violated limits, or other formulation concerns appear, stop, fix the model, rerun both cases, and only then finalize. If unresolved, explicitly report that valid market results could not be established.
