---
name: dc-opf-reserve-dispatch
description: "Solve DC optimal power flow with spinning reserve co-optimization on MATPOWER-style networks and produce a consistent dispatch report."
---

# DC-OPF with Co-Optimized Spinning Reserves

Reusable workflow to compute economically efficient generator setpoints and reserve allocations that satisfy:
- DC nodal power balance at each bus
- Generator limits and line thermal limits
- System spinning reserve requirement with capacity coupling

Outputs are structured for downstream use: per-generator dispatch and reserves, system totals, most-loaded lines, and remaining operating margin.

## When to Use

Activate this skill when you have:
- A power network snapshot in MATPOWER-style JSON (keys: baseMVA, bus, gen, branch, gencost; optional reserve_capacity and reserve_requirement)
- A need to co-optimize energy and spinning reserves under DC power flow constraints and export a standardized JSON report

## Core Workflow

1. Parse inputs
   - Read baseMVA, bus, gen, branch, gencost arrays (float-compatible).
   - Optional: reserve_capacity (per generator), reserve_requirement (scalar). If missing, treat reserve_capacity as zeros and reserve_requirement as 0.
   - Map bus numbers (bus[i][0]) to contiguous indices; bus numbers may be non-contiguous.

2. Choose units and stick to them
   - Use MW for generator outputs and reserves.
   - Use radians for voltage angles.
   - DC nodal balance in MW: S·Pg − Pd = baseMVA · (B · θ).

3. Build DC network model
   - Identify slack/reference bus: first bus with type=3, else default to index 0.
   - Build the sparse susceptance matrix B (n_bus×n_bus) from in-service branches (status==1) with nonzero reactance x:
     - b = 1/x; B[f,f]+=b; B[t,t]+=b; B[f,t]−=b; B[t,f]−=b.
   - Keep a list of in-service branches with positive flow limits for line constraints and reporting.

4. Define variables and constraints
   - Decision variables: Pg (MW per generator), Rg (MW per generator), θ (bus angles in radians).
   - Generator status: if status==0, enforce Pg=0 and Rg=0; do not contribute to cost or balance.
   - Generator bounds: Pmin ≤ Pg ≤ Pmax for online units.
   - Reserve bounds: 0 ≤ Rg ≤ reserve_capacity[i]. If reserve_capacity missing, use 0.
   - Capacity coupling: Pg + Rg ≤ Pmax (per online generator).
   - Reserve requirement: sum_i Rg[i] ≥ reserve_requirement.
   - DC nodal balance: S·Pg − Pd = baseMVA · (B · θ) at every bus.
   - Slack: θ[slack_bus] = 0.
   - Line flow limits for in-service branches with positive ratings: |b · (θ_f − θ_t) · baseMVA| ≤ Rate_A.

5. Objective (generation cost)
   - Use gencost per generator (standard polynomial model type):
     - If quadratic (ncost≥3): c2·Pg² + c1·Pg + c0.
     - If linear (ncost==2): c1·Pg + c0.
     - If constant (ncost==1): c0.
   - Include only online generators in the cost; offline units are fixed at zero.

6. Solve
   - Use a convex QP solver (e.g., CVXPY with CLARABEL/OSQP/ECOS). Try multiple solvers if necessary.
   - Maintain sparse matrices for scalability.

7. Post-solution computations and report
   - Generator dispatch list: for each generator, include id (1-based), bus number, output_MW, reserve_MW, pmax_MW.
   - Totals: cost_dollars_per_hour (objective value), load_MW (sum Pd), generation_MW (sum Pg), reserve_MW (sum Rg).
   - Line loadings: compute flow per monitored line as b · (θ_f − θ_t) · baseMVA, loading_pct = |flow|/Rate_A × 100; report top three by loading.
   - Operating margin (MW): sum over online units of max(Pmax − Pg − Rg, 0).
   - Round user-facing values to sensible precision (e.g., 2 decimals) for readability.

## Verification Checklist

Before finalizing the report:
- Power balance: |sum(Pg) − sum(Pd)| ≤ small tolerance (e.g., 1e−3 MW per bus or an aggregate tolerance consistent with solver).
- Reserve requirement: sum(Rg) ≥ reserve_requirement within tolerance.
- Generator limits: For every online generator, Pmin − tol ≤ Pg ≤ Pmax + tol; Pg + Rg ≤ Pmax + tol.
- Line limits: For each monitored line, |flow| ≤ Rate_A + tol.
- Offline units: Pg=0 and Rg=0.
- Output format matches the required JSON schema.

## Common Pitfalls and How to Avoid Them

- Mixed units (MW vs p.u.):
  - Choose a single scheme. If Pg is in MW, keep nodal balance as S·Pg − Pd = baseMVA·(B·θ) and line flows as b·(θ_f − θ_t)·baseMVA.
- Ignoring generator status:
  - Enforce Pg=Rg=0 for status==0; exclude from cost and capacity.
- Misinterpreting reserve data:
  - Do not invent default reserve requirements if one is provided. If reserve_capacity is missing, set to zeros; if reserve_requirement is missing, set to 0.
- Line limit handling:
  - Skip constraints for lines with non-positive ratings; only enforce for in-service lines with Rate_A>0 and x≠0.
- Slack and singularity:
  - Always fix one angle (slack) to avoid singular B; otherwise the problem is ill-posed.
- Dense matrices and memory:
  - Build B and incidence matrices as sparse to scale to large systems.
- Indexing errors:
  - Carefully map bus numbers to indices and reuse those indices consistently for generators and branches.
- Premature finalization:
  - Validate feasibility and constraints post-solve; if any constraint is violated beyond tolerance, adjust solver or formulation and re-run.

## Success Criteria

A solution is acceptable when all of the following hold:
- Objective solved to optimal or acceptable accuracy (solver reports optimal/optimal_inaccurate or equivalent).
- Power balance, generator, reserve, and line constraints satisfied within numerical tolerance.
- Report contains the required sections: generator_dispatch, totals, most_loaded_lines (up to three entries), operating_margin_MW.
- No use of fabricated reserve requirements or ignored statuses.

## Optional Script Usage

A helper script is provided to implement this workflow on a MATPOWER-style JSON file.

Example usage:
- python scripts/dc_opf_reserve.py --input network.json --output report.json

Script behavior:
- Parses the network file, builds a sparse DC model, solves the convex QP with generator and reserve constraints, and writes a standards-compliant report JSON.
- Requires Python 3, numpy, scipy, and cvxpy with at least one installed solver (e.g., CLARABEL/ECOS/OSQP/SCS). If cvxpy is unavailable, the script will exit with a clear message.
