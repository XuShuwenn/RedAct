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

- If `network.json` is large, inspect it selectively with lightweight shell checks or small Python probes: confirm top-level keys, array sizes, representative `bus`/`gen`/`branch`/`gencost` rows, any `column_info` or reserve-related metadata, and the exact branch record for **64→1501** before coding.
- Before writing solver code, inspect enough of `network.json` to directly locate and confirm the fields/columns used for bus demand, generator min/max output, generator status, branch endpoints, branch reactance/susceptance inputs, branch thermal limits, and `gencost` coefficients. Do **not** proceed from a truncated header/sample alone.
- Record one explicit mapping from MATPOWER sections/columns to model inputs and use it consistently in both scenarios; do **not** mix cost data from `gen` in one run and `gencost` in another.
- If `network.json` includes `column_info`, reserve tables, or other metadata blocks, read them before coding and map every referenced field from that metadata.
- Do **not** invent reserve costs, reserve requirements, extra generator economics, or unsupported reserve fields unless the input explicitly defines them. If reserve-related inputs are ambiguous after inspection, stop guessing and resolve the ambiguity from the provided data first.
- Treat MATPOWER `bus`, `gen`, `branch`, and `gencost` values as already expressed in the case's native power units unless the file metadata clearly requires conversion. Do **not** multiply only generator limits, only some costs, or only some flows by `baseMVA` while leaving related quantities unchanged.
- Check generator and branch status fields before modeling; exclude out-of-service elements rather than assuming every row is active.
- Parse `gencost` by its declared model/order and coefficient layout; do **not** guess linear/quadratic terms from `gen` columns or undocumented positions. Inspect at least one actual `branch` row, one `gencost` row, and any reserve-related records you rely on before finalizing the parser.

## Market Model

DC-OPF with reserve co-optimization:
1. Power balance at each bus
2. Temperature limits on generators and lines
3. Spinning Reserve Requirements


## Formulation Requirements

- Build both scenarios from one shared parsing/model-building workflow so the base case and counterfactual use identical formulation, indexing, and post-processing except for the verified **64→1501** thermal-limit increase.
- For every bus, add exactly one nodal power-balance equation; the reference/slack bus still needs its own balance equation.
- Apply the angle reference as a separate constraint only (`theta[ref] = 0` or equivalent); never skip the slack-bus balance row when assembling constraints.
- When constructing susceptance, admittance, or PTDF matrices, convert every bus label and branch endpoint through a dense `bus_id -> internal_index` map first. Never index matrices with raw MATPOWER bus numbers unless contiguity was explicitly verified.
- Keep explicit handles to every bus power-balance constraint and the reserve-requirement constraint so you can extract LMPs and reserve MCP from solver duals or native exact solver outputs after each successful solve.
- Use the inspected `gencost` data to formulate costs exactly: LP is acceptable only if the verified cost model is linear; if quadratic/polynomial terms are present, include them exactly.
- Check dual sign conventions and any `baseMVA` scaling before reporting prices so LMPs and reserve MCP are in `$ / MWh` rather than a mis-scaled dual convention.
- If the full model is hard to debug, use a smaller mathematically faithful DC-OPF only to validate indexing, constraints, units, and dual extraction, then return to the full required model; do **not** replace the market-clearing formulation with heuristics.

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

- After any fix that affects formulation, scaling, prices, outputs, or environment setup, treat all prior artifacts as stale until a new full run completes and rewrites `/root/report.json`.
- Treat truncated stdout/stderr, abruptly cut-off printed values, `tail` output, or incomplete solver logs as execution anomalies; investigate and rerun rather than assuming success from a created file.
- If the preferred solver is unavailable or fails, try a deliberate fallback solver sequence for the same convex DC-OPF formulation before changing the model.
- Gate all downstream steps on solver success for each run: if termination is infeasible, failed, inaccurate, unknown, or accompanied by blocking warnings, stop extraction, fix the formulation/data issue, rerun, and only then continue.
- Accept results only from runs with clearly successful solve/termination status and the complete primal/dual information needed for dispatch, flows, LMPs, and reserve MCP.
- Do **not** read dispatch vectors, duals, LMPs, reserve MCP, binding lines, or write `/root/report.json` from missing variables, stale outputs, unsuccessful solves, or partial logs.
- Verify artifact regeneration with direct evidence such as successful process exit plus a fresh `/root/report.json` modification time or an explicit report-written message before reading the file.
- If `report.json` is large, verify required sections with targeted reads/searches (for example `base_case`, `counterfactual`, `impact_analysis`, and `reserve_mcp_dollars_per_MWh`) rather than relying on a truncated full-file view.
- After each solve, do a quick sanity pass before accepting the run: confirm both scenarios solved, the modified line limit changed only in the counterfactual, and key outputs are not obviously degenerate (for example unchanged results after the line-limit increase, flat/uniform LMPs without congestion evidence, generation-load mismatch beyond tolerance, or line-flow violations beyond tolerance).
- If outputs look suspicious, treat that as a blocking modeling error: fix the formulation, rerun both cases, and regenerate `/root/report.json` before summarizing.

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

- Record the baseline thermal limit of branch **64→1501** before any edits, and verify the branch identifiers and rating field match the intended asset exactly.
- Before the first full solve, sanity-test the exact formulation on the verified data: check slack/reference-bus handling, one balance equation per bus, branch-flow sign conventions, thermal-limit encoding, and reserve coupling.
- After applying the counterfactual, confirm that only this branch limit changed and that the new limit equals the baseline multiplied by **1.2**.
- If the base case is infeasible, debug the existing formulation first on the verified model/data. Do **not** replace the algorithm as the first response to infeasibility.
- If required optimization packages are missing or the system Python is managed, create and use a local virtual environment (for example `/root/.venv`), install the needed dependencies there, and rerun from that environment rather than abandoning the exact DC-OPF workflow.
- After environment setup changes, rerun the full workflow and re-verify solver availability before solving base and counterfactual cases.

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

- Use targeted schema-inspection, indexing, sparse-matrix, and dual-handling patterns from `references/dc-opf-guardrails.md` when the case is large or when price extraction is fragile.
- Read `references/solver-choice-patterns.md` when selecting a solver or deciding whether native MATPOWER-aware OPF outputs can be used directly.

- Before coding, inspect the input schema and map every column/field used in costs, limits, reserves, and line ratings.
- Do **not** simplify away transmission constraints or reserve co-optimization; the counterfactual must propagate through the network model.
- Validate MATPOWER conventions before solving: keep `bus[:, PD]`, `gen[:, PMIN]`, and `gen[:, PMAX]` in consistent units, and do not multiply only some quantities by `baseMVA`.
- If the base case is infeasible, debug the formulation on the verified input data before rewriting the algorithm.
- After each solve, check solver status before reading dispatch or price outputs; do **not** write `report.json` from missing variables, failed solves, stale artifacts, or incomplete logs.
- Before summarizing impacts, inspect the complete final `report.json` and verify the cited numbers actually appear there.
- Do not finish until `/root/report.json` is written with both scenarios and impact analysis.

- Preferred sequence: inspect schema, metadata, statuses, and units -> build one faithful DC-OPF with reserve co-optimization on verified indexing -> solve base case -> clone the same model/data and change only line **64→1501** limit by **+20%** -> solve counterfactual -> validate statuses and refreshed outputs -> write report.
- Prefer one reproducible driver script or reusable solve routine that loads/parses the network once, builds the model once, runs both base and counterfactual through the same code path, computes comparison metrics, and writes a single unified `/root/report.json`; the only intended modeled difference is the **64→1501** thermal-limit change.
- Prefer a MATPOWER-aware OPF solver/library when available instead of rebuilding every matrix and pricing output from scratch; if it exposes native economic outputs, use those exact solved-case fields for LMPs, reserve prices, branch flows, and active limits rather than estimating them from dispatch or heuristics.
- For large cases, use sparse bus/branch/generator incidence and susceptance matrices.
- If solves are numerically fragile or prices look unstable, rescale the same formulation consistently and rerun; a practical recovery pattern is to keep balance equations, generation, flows, and limits in one MW-based convention end to end.
- When using optimization software, store handles to nodal balance constraints for every bus and the reserve requirement constraint so you can extract LMPs and reserve MCP directly from dual values after each successful solve.
- Resist solver rewrites or heuristic fallbacks unless they preserve the same network-constrained market-clearing model and exact required outputs.




## Minimum completion checklist

## Minimum completion checklist

1. Build the same DC-OPF with reserve co-optimization for both runs; only change the **64→1501** thermal limit in the counterfactual.
2. Solve base case and counterfactual successfully.
3. Extract total cost, bus-level LMPs, reserve MCP, and binding lines for each run.
4. Compare cases and write `/root/report.json`.

## Validation Before Finalizing

- If you changed code after inspecting an earlier `report.json`, reopen and revalidate the newly regenerated file only after confirming the corrected run completed; never summarize a possibly stale artifact.
- Confirm the base and counterfactual runs use the same data parsing, model formulation, price extraction, and reporting logic; only the specified **64→1501** thermal limit should change in the counterfactual.
- Confirm the final report contains populated `base_case`, `counterfactual`, and `impact_analysis` sections, not just an existing file.
- When using a domain OPF solver, verify that reported LMPs, reserve prices, branch flows, and thermal limits come from the solved-case outputs, not from a separate approximation layer, stale arrays, or reconstructed debug calculations.
- Treat self-detected anomalies or obviously broken outputs as blocking formulation bugs, not usable results. Examples: `$0/hr` total cost, identical base and counterfactual outputs despite an active constraint change, implausibly many binding lines, extremely large or near-zero LMPs without clear model justification, or `$0/MWh` reserve MCP despite apparent reserve scarcity.
- If you changed cost scaling, per-unit/MW conversions, or dual-sign conventions during debugging, re-validate them end to end before using total cost, LMPs, or reserve MCP in the final report.
- Sanity-check at least a few LMPs and the reserve MCP directly after each successful solve. If prices look implausibly large or small, re-check `baseMVA` handling, objective units, and dual-to-`$ / MWh` conversions before trusting any report values.
- Validate not just JSON structure but the scenario story: confirm line **64→1501** exists in the solved input, was the only thermal-limit change in the counterfactual, compare its base vs counterfactual loading/binding status, and confirm `congestion_relieved` matches those solved results.
- Do not call outputs realistic or conclude congestion impacts are established if any blocking physical, economic, or stale-artifact validation check still fails.

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
