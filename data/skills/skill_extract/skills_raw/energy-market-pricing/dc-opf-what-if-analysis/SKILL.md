---
name: dc-opf-what-if-analysis
description: "Run DC-OPF with reserve co-optimization to compare a base case and a counterfactual with modified transmission limits, extracting LMPs, binding lines, and cost impacts."
---

# DC-OPF What‑If Analysis with Reserves

Use this skill to evaluate how relaxing or tightening a transmission constraint affects total system cost, locational marginal prices (LMPs), and congestion. It solves a DC-OPF with spinning reserve co-optimization twice: once for the base case and once for a counterfactual where specified branch thermal limits are modified.

## When to Use

Activate this skill when you need to:
- assess the price and cost impact of changing a transmission line limit
- compare base versus counterfactual market outcomes under DC-OPF with reserves
- report LMPs by bus, reserve clearing price, and binding lines in both cases

## Core Workflow

1. Inspect input data
   - Load the MATPOWER-format JSON network (e.g., keys: baseMVA, bus, gen, branch, gencost, reserve_capacity, reserve_requirement).
   - Verify fields exist and note units. Assumed conventions:
     - Power in MW (use MW for generator limits and reserve variables)
     - Angles in radians
     - Reactance x in per-unit; flows in MW are computed using b_MW = baseMVA / x

2. Build model primitives
   - Bus index map: map external bus numbers to contiguous indices.
   - Slack/reference bus: choose the bus with type=3 if present; otherwise use the first bus.
   - Nodal B matrix (MW units): for each in-service branch with nonzero reactance x, add susceptance b = baseMVA/x to the diagonal, subtract b on off-diagonals.
   - Branch flow operator Bf: for each in-service branch with x>0, flow_k(MW) = (baseMVA/x_k) * (theta_from − theta_to).
   - Generator-to-bus incidence Cg.

3. Choose a numerically stable formulation
   - Recommended: use MW units for Pg and Rg; compute B and Bf in MW units and keep theta in radians. This avoids per-unit scaling errors.
   - If generation costs are linear (c2=0), formulate as a linear program (LP) for better robustness and faster solve; otherwise use a QP solver.

4. Define decision variables and objective
   - Variables: Pg (MW), theta (radians), Rg (MW).
   - Objective (hourly cost): sum_i c1_i · Pg_i (+ optional c0_i constants if needed) + sum_i reserve_cost_i · Rg_i. If only linear costs are present, omit quadratic terms.

5. Add constraints
   - Nodal power balance (equality for each bus): Cg·Pg − Pd = B·theta.
   - Slack angle: theta[slack] = 0 (as an extra equality).
   - Generator limits: Pmin ≤ Pg ≤ Pmax (apply only to in-service generators; set Pg=0 if out-of-service).
   - Line limits: for each in-service branch with rate>0 and x>0, enforce −rate ≤ Bf·theta ≤ rate in MW.
   - Reserve constraints:
     - Rg ≥ 0 and Rg ≤ reserve_capacity (per generator)
     - Capacity coupling: Pg + Rg ≤ Pmax (per generator)
     - System requirement: sum_i Rg_i ≥ reserve_requirement

6. Solve scenarios
   - Base: solve with original branch limits.
   - Counterfactual: apply a multiplier (e.g., 1.2) to the target branch limit(s) in both directions. If multiple parallel circuits exist between two buses, apply the change to all matching pairs.

7. Extract outputs
   - Total cost: objective value in $/hour.
   - LMPs: use duals of the nodal balance equalities (one per bus). Units notes:
     - If the model uses MW for power and $/MWh for costs, equality duals directly represent $/MWh.
     - If a per-unit formulation is used, convert duals from $/p.u.-hour to $/MWh by dividing by baseMVA.
   - Reserve MCP: dual of the system reserve requirement constraint. Ensure sign is interpreted as the marginal cost of tightening the reserve requirement by 1 MW; with A_ub x ≤ b_ub, adjust sign if needed so MCP ≥ 0 for a binding requirement.
   - Binding lines: compute flows and flag those whose loading ≥ 99% of the MW limit.

8. Compare scenarios
   - Cost reduction = base_cost − counterfactual_cost (report ≥ 0 if the relaxation reduces cost).
   - LMP deltas: join by bus id and compute cf_lmp − base_lmp. Sort ascending to find the three largest drops.
   - Congestion relief flag: true if the adjusted branch(es) are not binding in the counterfactual.

9. Report
   - Produce a JSON report with:
     - base_case: total_cost_dollars_per_hour, lmp_by_bus, reserve_mcp_dollars_per_MWh, binding_lines
     - counterfactual: same fields
     - impact_analysis: cost_reduction_dollars_per_hour, buses_with_largest_lmp_drop (3 entries), congestion_relieved

## Verification

Perform these checks before finalizing results:
- Dimensions and counts
  - LMP list length equals number of buses.
  - All reported bus IDs align with the input bus numbers.
- Unit sanity
  - LMPs typically fall within a plausible range (e.g., 5–500 $/MWh) absent extreme scarcity.
  - Total cost magnitude roughly matches total load × average marginal cost.
  - Reserve MCP is zero if requirement is slack and positive if binding.
- Dual interpretation
  - For uncongested buses, LMPs align with the marginal generator cost setting the price.
  - If using per-unit internally, verify the $/MWh conversion: LMP = dual/baseMVA.
- Counterfactual correctness
  - Target line limit actually changed (log old/new limit). If parallel circuits exist, ensure all were adjusted.
  - Congestion_relieved reflects whether the adjusted line(s) appear in the binding set.

## Common Pitfalls

- Unit/scale mistakes
  - Multiplying instead of dividing by baseMVA when converting duals to $/MWh.
  - Mixing per-unit constraints with MW limits without consistent conversions.
- Wrong LMP sign or magnitude
  - Misinterpreting solver marginal conventions (especially for inequality signs). For HiGHS in SciPy, equality marginals are d(obj)/d(b_eq); use them directly for $/MWh in an MW-based model.
- Numerical instability
  - Inverting large matrices unnecessarily (e.g., PTDF by dense inversion). Prefer direct B and Bf formulations.
  - Using QP solvers when costs are linear; switch to LP with HiGHS for robustness.
- Topology and indexing errors
  - Using bus indices in place of bus numbers when matching lines or generators.
  - Missing the reverse direction or parallel circuits when modifying line limits.
  - Enforcing limits on out-of-service branches or those with zero/negative ratings.
- Reserve coupling mistakes
  - Omitting Pg + Rg ≤ Pmax (double counting available capacity).
  - Extracting reserve MCP from the wrong inequality row; track index or store a handle.

## Success Criteria

- Both scenarios solve to optimal (or optimal-inaccurate) status.
- Report includes all required fields and consistent dimensions.
- LMPs and reserve MCP have plausible values and correct units.
- Target constraint modification reduces congestion and/or cost as expected, and the congestion_relieved flag matches whether the adjusted lines are binding in the counterfactual.

## Optional Script Usage

A helper script is provided to run the analysis end-to-end using an LP formulation with the HiGHS solver (SciPy). It expects a MATPOWER-format JSON and lets you specify one or more line limit multipliers.

Example:
- Base vs. counterfactual where a line from bus A to bus B has its limit multiplied by 1.2.
- Ensure SciPy and NumPy are available in the environment.

Command:
- python scripts/dcopf_whatif.py --network network.json --target 64,1501 --multiplier 1.2 --output report.json

You can repeat --target and --multiplier for multiple lines; the script applies each multiplier to both directions and to all parallel circuits between the same bus pair.
