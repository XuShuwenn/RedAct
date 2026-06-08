---
name: ac-opf-casadi
description: "Formulate and solve AC Optimal Power Flow from MATPOWER-like data using CasADi/IPOPT and produce a verifiable feasibility report."
---

# AC Optimal Power Flow with CasADi/IPOPT

Reusable workflow to build, solve, and verify an AC Optimal Power Flow (ACOPF) using CasADi + IPOPT from MATPOWER-style network data. Produces a structured report with dispatch, voltages, branch loadings, and feasibility checks.

## When to Use

- You have a MATPOWER-like case (bus, gen, branch, gencost) in JSON/array form.
- You must compute a least-cost AC-feasible operating point and output a report with MW/MVAr/deg/pu units.
- You need a robust, verifiable ACOPF workflow with clear feasibility checks.

## Core Workflow

1. Inspect data
   - Load network data and confirm keys, shapes, and column layout:
     - bus: [BUS_I, TYPE, PD, QD, GS, BS, AREA, VM, VA, BASEKV, ZONE, VMAX, VMIN]
     - gen: [GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, STATUS, PMAX, PMIN]
     - branch: [F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS, ANGMIN, ANGMAX]
     - gencost: [MODEL, STARTUP, SHUTDOWN, NCOST, c2, c1, c0] for polynomial model
   - Build integer bus-id → row-index map; do not assume contiguous or 1-based indexing.

2. Normalize units (per-unit) and identify active elements
   - baseMVA = data.baseMVA
   - Pd_pu = PD/baseMVA; Qd_pu = QD/baseMVA
   - Gs_pu = GS/baseMVA; Bs_pu = BS/baseMVA
   - Active generators: STATUS == 1; Active branches: BR_STATUS == 1
   - Voltage bounds: Vmin = VMIN; Vmax = VMAX

3. Decision variables (CasADi)
   - Vm (n_bus) in pu
   - Va (n_bus) in radians
   - Pg (n_active_gen) in pu
   - Qg (n_active_gen) in pu
   - Fix reference bus angle(s): Va[slack] = 0 (equality or bounds)

4. Objective (generation cost)
   - Cost uses MW: Pg_MW = Pg_pu × baseMVA
   - For each active gen k: f += c2[k]*Pg_MW^2 + c1[k]*Pg_MW + c0[k]

5. AC network equations (pi-model with taps/shift)
   - For each active branch l (i → j):
     - If TAP ≈ 0, use tap = 1.0 (MATPOWER convention)
     - shift_rad = deg2rad(SHIFT)
     - Series admittance: g = R/(R^2+X^2), b = -X/(R^2+X^2); handle zero-impedance safely
     - Half-line charging: BR_B/2 at each side
     - Angle differences for flows: Δij = Va[i] − Va[j] − shift_rad
     - Power flow formulas (per-unit):
       - P_ij = g Vi^2/tap^2 − Vi Vj/tap (g cos Δij + b sin Δij)
       - Q_ij = −(b + Bc/2) Vi^2/tap^2 − Vi Vj/tap (g sin Δij − b cos Δij)
       - P_ji = g Vj^2 − Vi Vj/tap (g cos(−Δij) + b sin(−Δij))
       - Q_ji = −(b + Bc/2) Vj^2 − Vi Vj/tap (g sin(−Δij) − b cos(−Δij))
     - Aggregate P_out[i]+=P_ij, Q_out[i]+=Q_ij and P_out[j]+=P_ji, Q_out[j]+=Q_ji

6. Constraints
   - Nodal balances (per bus i):
     - Real: sum_k Pg_bus[i] − Pd_pu[i] − Gs_pu[i] Vi^2 − P_out[i] = 0
     - Reactive: sum_k Qg_bus[i] − Qd_pu[i] + Bs_pu[i] Vi^2 − Q_out[i] = 0
   - Thermal limits (if RATE_A > 0):
     - |S_ij|^2 = P_ij^2 + Q_ij^2 ≤ (RATE_A/baseMVA)^2 for both ends
     - Use squared form to avoid sqrt in constraints
   - Angle difference bounds per branch:
     - angmin_rad ≤ Va[i] − Va[j] ≤ angmax_rad
     - Optionally skip if (angmax − angmin) is effectively unconstrained (e.g., > ~350°)
   - Bounds:
     - Vmin ≤ Vm ≤ Vmax
     - −π ≤ Va ≤ π, with slack bus Va fixed to 0
     - Pg_min ≤ Pg ≤ Pg_max; Qg_min ≤ Qg ≤ Qg_max (per active gen)

7. Initialization (robustness)
   - Data-derived: Vm = clip(VM, [Vmin,Vmax]), Va = deg2rad(VA) with Va[slack]=0
   - Pg/Qg = clip(initial values, [min,max])
   - Flat fallback: Vm=1, Va=0, Pg/Qg at mid-bounds
   - If first solve fails, retry with alternate initialization

8. Solve (IPOPT)
   - CasADi nlpsol("ipopt") with sane defaults:
     - ipopt.tol ~ 1e-7, acceptable_tol ~ 1e-5
     - mu_strategy = adaptive; linear_solver = mumps (if available)
   - Map return_status to human-readable (e.g., "optimal" for Solve_Succeeded)

9. Post-processing and report
   - Convert solution to engineering units:
     - Pg_MW = Pg_pu × baseMVA; Qg_MVAr = Qg_pu × baseMVA; Va_deg = rad2deg(Va)
   - Branch flows for reporting using compute_branch_flows_pu (see script):
     - Compute MVA from both ends, percent loading vs RATE_A
     - Sort by loading and include top-N
   - Totals:
     - total_load_MW/MVAr = sum over buses
     - total_generation_MW/MVAr = sum over generators
     - total_losses_MW = total_generation_MW − total_load_MW (match requested report)
   - Feasibility check (use solver-level values, not rounded):
     - Recompute P/Q mismatches from solution
     - Report max_p_mismatch_MW and max_q_mismatch_MVAr
     - max_voltage_violation_pu = max(max(0, Vm−Vmax), max(0, Vmin−Vm))
     - max_branch_overload_MVA = max(0, max(flow − limit)) over limited branches
   - Write structured JSON report with summary, generators, buses, most_loaded_branches, feasibility_check

## Verification

- Power balance residuals near zero:
  - max_p_mismatch_MW ≈ 0 and max_q_mismatch_MVAr ≈ 0 at solver precision
- Limits satisfied:
  - No Vm outside [Vmin, Vmax]
  - No branch overload beyond rated MVA
  - Angle difference within bounds for constrained branches
- Units consistent:
  - MW/MVAr for power, degrees for angles, pu for voltages
- Sanity checks:
  - total_generation_MW − total_load_MW equals reported total_losses_MW
  - Generator dispatch within pmin/pmax and qmin/qmax

## Common Pitfalls (and Fixes)

- Variable shadowing
  - Do not reuse the name x (decision vector) for branch reactance. Use br_x for reactance.
- Tap ratio of zero in data
  - MATPOWER uses 0 to mean tap=1.0. Replace near-zero taps with 1.0 before use.
- Angle units
  - Convert all angles used in constraints and flows to radians; report bus angles in degrees.
- Angle difference constraint
  - Apply bounds to Va[i] − Va[j] (bus angle difference). Do not include branch SHIFT in the constraint; SHIFT affects flows only.
- Cost scaling
  - Cost coefficients are in MW units. Convert Pg to MW inside the objective even if the optimization uses per-unit.
- Shunt modeling
  - Include Gs (draws real power) and Bs (injects reactive power) in nodal balances with correct signs and baseMVA scaling.
- Branch flow limits
  - Enforce limits on both ends and in per-unit squared form against (RATE_A/baseMVA)^2.
- Element statuses
  - Include only in-service generators/branches in variables and constraints, or fix off-service vars to zero.
- Rounding in reports
  - Compute feasibility metrics from full-precision solution; rounding Vm/Va in the report can introduce artificial mismatches.
- Bus indexing
  - Always map BUS_I to row index. Do not assume BUS_I is contiguous or zero-based.

## Optional Script Usage

- scripts/branch_flows.py
  - Compute per-unit branch flows including taps and phase shifts for reporting and feasibility checks
  - Build bus-id mapping

- scripts/opf_feasibility.py
  - Given network arrays and a solution (Vm, Va, Pg, Qg), compute mismatches, voltage violations, and branch overloads in consistent units

Example (Python):
```python
from scripts.branch_flows import compute_branch_flows_pu, build_bus_id_to_idx
from scripts.opf_feasibility import feasibility_metrics

bus_map = build_bus_id_to_idx(buses)
P_ij, Q_ij, P_ji, Q_ji = compute_branch_flows_pu(Vm_sol, Va_sol, branch_row, bus_map)
metrics = feasibility_metrics(buses, branches, Vm_sol, Va_sol, Pg_sol, Qg_sol, baseMVA)
```
