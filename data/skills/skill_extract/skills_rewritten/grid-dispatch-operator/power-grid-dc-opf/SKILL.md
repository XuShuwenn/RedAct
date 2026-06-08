---
name: power-grid-dc-opf
description: "Formulate, solve, and verify DC optimal power flow with spinning reserves from MATPOWER-format snapshots, and produce a structured dispatch report."
---

# DC Optimal Power Flow with Spinning Reserves

Reusable workflow to parse a MATPOWER-style network snapshot, set up a DC OPF with spinning reserve capacity coupling, enforce generator and transmission limits, and produce a robust dispatch report with verification.

## When to Use

Use this skill when asked to:
- Produce generator dispatch and spinning reserve allocations from a MATPOWER-format network snapshot
- Enforce DC power balance at each bus, generator limits, and transmission limits
- Co-optimize energy and spinning reserves with capacity coupling (output + reserve ≤ Pmax)
- Summarize total cost, totals (load/generation/reserves), most loaded lines, and operating margin in a structured JSON report

## Core Workflow

1. Input inspection and parsing
   - Parse MATPOWER-format JSON fields: baseMVA, bus, gen, branch, and (if present) reserve data.
   - Respect equipment statuses:
     - Generators: only include units with GEN_STATUS > 0 in capacity and dispatch.
     - Branches: only include lines with BR_STATUS > 0 in flows and limits.
   - Map bus IDs to 0-based indices for matrix operations; preserve original IDs for reporting.

2. Data interpretation and units
   - MW/MVA quantities in MATPOWER are on the given baseMVA. DC flow equations are typically in per-unit; convert to MW/MVA as needed by multiplying by baseMVA.
   - Use branch reactance (BR_X), tap ratio (TAP, default 1 if 0), and phase shift (SHIFT in degrees) in DC equations.
   - Generator limits: use PMIN and PMAX as provided. Some datasets permit negative PMIN; do not clamp unless clearly erroneous. Apply GEN_STATUS.
   - Transmission limits: use RATE_A when > 0 as the thermal limit. If RATE_A ≤ 0 or missing, treat as unconstrained for line-limit enforcement (but exclude from “most loaded” ranking).

3. Reserve requirement handling
   - If a reserve structure exists, use its requirement(s): e.g., sum of reserves.req or a field explicitly providing MW requirement(s).
   - If zonal reserves are specified, enforce each zone’s requirement with the standard capacity coupling at unit level.
   - If no requirement exists in the data, do not assume an arbitrary percentage. Instead, set requirement to 0 MW (or request specification) and clearly document this in the report metadata or logs.

4. Model formulation (DC OPF with reserves)
   - Decision variables per online generator i:
     - Pg_i (MW): active power output
     - R_i (MW): spinning reserve
   - Decision variables per bus j: voltage angle θ_j (radians). Fix a reference angle at one slack bus (BUS_TYPE = 3). If multiple islands exist, treat each island with its own reference.
   - Objective:
     - Minimize total operating cost = sum of generation costs C_i(Pg_i) plus reserve costs, if provided.
     - Cost handling:
       - Quadratic costs: use MATPOWER gencost data when available.
       - Piecewise-linear costs: implement as linear segments or use a modeling tool’s PWL function.
   - Constraints:
     - Generator limits: PMIN_i ≤ Pg_i ≤ PMAX_i; R_i ≥ 0; Pg_i + R_i ≤ PMAX_i.
     - Reserves: sum_i R_i ≥ total reserve requirement (and zonal constraints if specified).
     - DC power balance at each bus j: sum(Pg at bus j) − Pd_j = net injection_j = (Bbus θ)_j + injection_from_phase_shifts_j.
       - Build Bbus from active branches using susceptances adjusted by tap ratios; include phase-shift injections on the right-hand side.
     - Line limits: For each active branch k from bus f to t,
       - Flow f_k = baseMVA · (θ_f − θ_t − shift_k) / (x_k · tap_k)
       - Enforce −RATE_A_k ≤ f_k ≤ RATE_A_k for lines with RATE_A_k > 0.

5. Solve and validate
   - Use a reliable convex/LP/QP solver appropriate for your cost structure.
   - Set solver tolerances (e.g., feasibility and optimality) and record status.
   - If the model is infeasible, check islands, slack selection, incorrect limit values, or missing reserve data.

6. Post-processing
   - Recompute line flows from the solved angles to confirm line limits.
   - Compute loading percentage for each constrained line: 100 · |f_k| / RATE_A_k.
   - Totals:
     - load_MW = sum Pd over all buses
     - generation_MW = sum Pg over all online units
     - reserve_MW = sum R over all online units
     - cost_dollars_per_hour = model objective (ensure consistent units)
   - Operating margin (uncommitted capacity beyond energy and reserves):
     - Sum over online units: max(0, PMAX_i − Pg_i − R_i)
   - Top 3 most heavily loaded lines: select by highest loading percentage among constrained lines (RATE_A > 0), report from-bus, to-bus, and loading_pct.

7. Report generation
   - Produce a JSON report with exactly:
     - generator_dispatch: list of objects per generator with id, bus, output_MW, reserve_MW, pmax_MW
     - totals: cost_dollars_per_hour, load_MW, generation_MW, reserve_MW
     - most_loaded_lines: three entries with from, to, loading_pct
     - operating_margin_MW: system-level value

## Verification

Run these checks before finalizing the report:
- Power balance:
  - |sum(Pg) − sum(Pd)| ≤ tolerance (e.g., 1e-3 × max(1, total load))
  - Node-wise residual: ||Bbus θ − net_injection||∞ ≤ angle/flow tolerance
- Line limits:
  - For lines with RATE_A > 0: |f_k| ≤ RATE_A_k + small_tolerance
  - If any loading_pct > 100% by more than tolerance, your optimization did not enforce line limits or scaling is wrong.
- Generator constraints:
  - PMIN_i − tol ≤ Pg_i ≤ PMAX_i + tol
  - R_i ≥ −tol and Pg_i + R_i ≤ PMAX_i + tol
- Reserve adequacy:
  - sum R_i ≥ requirement − tol (and per-zone if applicable)
- Status compliance:
  - Exclude offline branches/generators from capacity/flow/dispatch; do not count their capabilities in operating margin or reserves.
- Units and scaling:
  - Confirm flows computed from angles match reported line loadings when scaled by baseMVA and RATE_A.

Suggested numeric tolerances:
- Power balance residual: ≤ 1e-3 MW per bus, and ≤ 1e-4 relative to total load for system sum
- Line limit violations: ≤ 1e-5 of RATE_A or ≤ 1e-3 MW, whichever larger
- Generator/reserve bounds: ≤ 1e-6 MW

## Common Pitfalls and Recoveries

- Missing line-limit enforcement:
  - Symptom: post-processed loading_pct far above 100%.
  - Fix: include line flow constraints in the optimization, not only in post-analysis.
- Hardcoded reserve percentage:
  - Symptom: reserves inconsistent with dataset’s requirement.
  - Fix: derive requirement from the dataset’s reserve fields; if absent, set to 0 or require explicit input.
- Slack/reference angle not fixed:
  - Symptom: singular Bbus or unstable angles.
  - Fix: pin at least one bus angle per island; prefer BUS_TYPE = 3.
- Status flags ignored:
  - Symptom: using offline lines/generators, incorrect margins and flows.
  - Fix: filter by BR_STATUS and GEN_STATUS.
- BaseMVA/scaling mistakes:
  - Symptom: flows or limits off by a factor of baseMVA.
  - Fix: compute flows in per-unit then multiply by baseMVA; compare to RATE_A in MW/MVA.
- Negative PMIN mishandled:
  - Symptom: infeasibility or artificial clamping.
  - Fix: allow negative outputs where PMIN < 0 unless clearly erroneous.
- Solver convergence issues:
  - Symptom: mismatch between totals or residuals above tolerance.
  - Fix: try an alternative solver, adjust tolerances, warm-start, or recondition matrices.
- Multiple islands:
  - Symptom: infeasible power balance for an island with net nonzero injection.
  - Fix: solve islands separately or adjust inputs so each island is balanced by local generation.

## Optional Script Usage

The included helper provides deterministic DC powerflow construction and verification utilities.

- Compute DC flows and loading percentages, and validate a produced report:
  - python scripts/dc_opf_tools.py --verify --network path/to/network.json --report path/to/report.json

- Use the functions in your optimization code to:
  - Build Bbus and line-flow mappings
  - Compute flows from solved angles
  - Verify constraints before writing the final report

Success criteria: all verification checks pass within tolerance; most_loaded_lines are within limits (≤ 100% after optimization), totals are consistent, and the report schema matches the required structure.
