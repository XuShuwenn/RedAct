---
name: dc-opf-scenario-comparison
description: "Compare a base-case DC-OPF market clearing to a counterfactual with a modified network constraint (e.g., line limit), extract prices and congestion, and produce an impact analysis."
---

# DC-OPF Scenario Comparison with Reserve Co-optimization

This skill provides a reusable workflow to run a day-ahead market clearing based on DC-OPF with spinning reserve co-optimization for two scenarios (base and counterfactual) and to produce a structured impact analysis. It is designed for tasks where a specific network constraint (typically a transmission line limit) is adjusted in the counterfactual to assess congestion relief and price impacts.

## When to Use

Use this skill when asked to:
- Run DC-OPF with reserve co-optimization on a provided network snapshot (e.g., MATPOWER-format JSON)
- Modify one network constraint (e.g., increase a line thermal limit) in a counterfactual scenario
- Compare base vs counterfactual results: total cost, nodal LMPs by bus, reserve MCP, binding (near-limit) lines, and impact metrics

## Core Workflow

Follow these phases. Compute results directly from the input data and optimization outputs. Do not guess values.

### Phase A: Input Loading and Normalization

1. Load network data (e.g., MATPOWER-style JSON) and parse core tables:
   - Buses (bus IDs, types, demands, reference bus)
   - Generators (Pmin/Pmax, costs, reserve capability/limits if provided)
   - Branches/lines (from-bus, to-bus, reactance/X, thermal limits)
   - Reserve requirement (single system-wide up-reserve or multiple zones if present)

2. Build a robust bus ID mapping:
   - External bus IDs are often non-contiguous. Create an index map: ext_id -> [0..N-1] and a reverse map for reporting.
   - Verify exactly one reference bus (or select from designated candidates) and record it for angle fixing.

3. Identify the target element(s) for the counterfactual:
   - If the task specifies a line by its two endpoint buses, match by unordered pair so orientation does not matter.
   - Handle parallel lines by matching all branches with the same endpoints; you may need to adjust all matching elements.
   - Validate that at least one matching element exists; if multiple, record all matches explicitly.

### Phase B: Model Formulation (DC-OPF with Reserves)

Formulate an optimization with variables for generator power Pg, spinning reserve Rsp, and either bus angles theta or line flows via PTDF.

1. Objective (hourly cost):
   - Energy production cost: sum of generator offer cost at Pg (linear and/or quadratic terms correctly interpreted from input)
   - Reserve cost: sum of reserve offer cost at Rsp when present
   - Ensure units consistency: if costs are in $/MWh and variables are in MW, the hourly objective is consistent without extra scaling.

2. Constraints:
   - Nodal power balance: sum(Pg at bus) − Demand(bus) − NetFlow(bus) = 0 for all buses
     - If using theta: NetFlow = Bbus * theta or branch flows from Bf * theta
     - Fix reference bus angle to 0 (or eliminate it) to avoid singularity
   - Generator limits: Pmin ≤ Pg ≤ Pmax
   - Line thermal limits: |Flow_line| ≤ Limit (use reactance and angle difference or PTDF-based flow)
   - Reserve requirement: sum(Rsp) ≥ Requirement (and per-zone if applicable)
   - Capacity coupling (standard): Pg + Rsp ≤ Pmax per generator (ensure reserve does not exceed headroom)
   - Optional reserve caps: 0 ≤ Rsp ≤ (Pmax − Pg) and any additional unit-specific reserve limits

3. Solver and numerical setup:
   - Use an LP/QP solver that exposes duals (shadow prices) to extract LMPs and reserve MCPs
   - Set tolerances (optimality/feasibility) suitably tight; enable presolve/scaling to improve conditioning
   - For large systems, prefer PTDF formulation for performance and conditioning when available

### Phase C: Scenario Runs

1. Base case:
   - Solve the model and collect outputs
   - Extract LMPs per bus from the duals of nodal balance constraints
     - Sign convention check: depending on how balance is written, LMP may be +dual or −dual. Validate via a small load perturbation test or by comparing with generator marginal costs; flip sign if needed.
   - Extract reserve MCP from the dual of the reserve requirement constraint (apply proper units)
   - Compute branch flows and identify binding lines: those at or above the threshold (e.g., loading ≥ 99% of limit)

2. Counterfactual:
   - Modify the targeted constraint(s) (e.g., multiply selected line limit(s) by the requested factor)
   - Re-solve and collect the same outputs (LMPs, reserve MCP, flows, binding lines)

### Phase D: Post-processing and Report Assembly

1. lmp_by_bus: return a list of objects [{"bus": ext_id, "lmp_dollars_per_MWh": value}, …] for all buses using external IDs
2. total_cost_dollars_per_hour: report the optimized objective value using standard numeric types (float)
3. reserve_mcp_dollars_per_MWh: report the system-wide reserve price from the reserve dual (if no reserve feature is present, this may be zero)
4. binding_lines: list lines where |flow|/limit ≥ threshold (e.g., 0.99), each as {"from": ext_fbus, "to": ext_tbus, "flow_MW": f, "limit_MW": lim}
5. impact_analysis:
   - cost_reduction_dollars_per_hour = base_total_cost − counterfactual_total_cost
   - buses_with_largest_lmp_drop: compute delta = cf_lmp − base_lmp; sort by most negative deltas and report top 3 as {"bus", "base_lmp", "cf_lmp", "delta"}
   - congestion_relieved: true if none of the targeted lines appear in the counterfactual binding list (compare by unordered bus pairs with tolerance)

## Verification

Perform these checks before finalizing the report:

- Feasibility and physics:
  - Power balance residuals near zero at all buses within numerical tolerance
  - No branch flow exceeds its limit beyond tolerance; lines reported as binding have loading close to the threshold
  - Pg within [Pmin, Pmax] and Rsp within feasible bounds; Pg + Rsp ≤ Pmax holds

- Pricing correctness:
  - Sign convention: add a small load at a bus in a diagnostic run; the incremental objective change should match the reported LMP at that bus (within tolerance). If opposite, flip the sign of extracted duals for LMPs.
  - LMP magnitudes align with generator marginal costs in uncongested areas; congestion introduces spatial differences
  - Reserve MCP reflects scarcity: if the requirement is slack, MCP ~ 0; if binding, MCP > 0

- Report structure:
  - All required fields present with standard Python numeric types (no numpy scalars)
  - lmp_by_bus covers all buses exactly once using external IDs
  - binding_lines only include lines at or above the threshold; no duplicates due to opposite orientation
  - congestion_relieved matches whether the adjusted line(s) are binding in the counterfactual

## Common Pitfalls and How to Avoid Them

- Dual sign error for LMPs:
  - Root cause: nodal balance written with different sign conventions. Fix by verifying with a small load perturbation; flip sign if needed.

- Units and scaling mistakes:
  - Ensure costs are in $/MWh and power variables are in MW; do not accidentally rescale by baseMVA unless model requires it
  - Keep reserve price units consistent with energy price units

- Reference bus handling:
  - Forgetting to fix one angle (or equivalent) yields singular systems or uniform prices. Always fix the reference bus angle to 0 or eliminate it from the system.

- Bus indexing mismatches:
  - External bus IDs may be sparse or non-sequential. Always use an ext↔int mapping and convert back to external IDs for output.

- Target line identification errors:
  - Orientation and parallel lines can cause mismatches. Match by unordered bus pairs and handle all parallel elements explicitly.

- Incorrect binding-line detection:
  - Using approximate flows or stale values leads to false negatives. Use solver-reported flows; apply a threshold (e.g., ≥ 99% of limit) and absolute value of flow.

- Reserve coupling omissions:
  - Failing to enforce Pg + Rsp ≤ Pmax inflates reserve capability and distorts MCP. Always apply standard capacity coupling for spinning reserves.

- Numerical and performance issues on large cases:
  - Use presolve/scaling; choose a solver that returns duals; prefer PTDF formulation for large networks; tighten tolerances if prices look unstable

## Success Criteria

- Both scenarios solve to optimality without violations of generator or line limits
- LMPs and reserve MCP are in plausible ranges given offers; sign verified
- The report contains all required fields with correct schema and numeric types
- Impact analysis correctly identifies cost change, top LMP drops, and congestion relief status of the adjusted line(s)

## Optional Script Usage

You can use the helper in scripts/report_utils.py to:
- Identify binding lines at a chosen threshold
- Compute top-k LMP drops between two scenarios
- Match target lines by unordered bus pairs (robust to orientation)
- Validate the final report structure prior to submission

Example (pseudocode):
- binding = report_utils.binding_lines(records, threshold=0.99)
- drops = report_utils.top_k_lmp_drops(base_lmps, cf_lmps, k=3)
- targets = report_utils.match_branches_by_buses(branches, u, v)
- ok, errors = report_utils.validate_report_structure(report_obj)
