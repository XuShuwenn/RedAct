---
name: acopf-solve-report
description: "Formulate and solve an AC Optimal Power Flow, then generate and validate a structured JSON report with correct units and feasibility metrics."
---

AC Optimal Power Flow Solve and Reporting

Skill for building a least-cost, AC-feasible operating point and producing a JSON report containing system totals, generator dispatch, bus voltages, most-loaded branches, and feasibility checks.

When to Use

Activate this skill when the task requires:
- solving an AC Optimal Power Flow (OPF) for a given network
- confirming AC feasibility via mismatch, voltage, and branch limit checks
- producing a structured JSON report with specific sections and unit conventions

Core Workflow

Phase 1: Input Discovery and Parsing
- Read the model description to understand variables, objective, and constraints.
- Load the network data and identify sections for buses, generators, branches, costs, limits, and shunts.
- Confirm unit conventions and base values (e.g., base MVA). Record voltage bounds, generator P/Q bounds, branch thermal limits, and any angle-difference limits.
- Handle status flags (e.g., in service/out of service) and exclude deactivated devices from modeling and reporting.

Phase 2: Environment Setup
- Verify Python runtime and required optimization libraries (e.g., nonlinear solver and numerical stack).
- Prefer an isolated environment (virtualenv) and confirm imports work with the interpreter used to run the solver script.
- Record the run command and preserve created files.

Phase 3: Model Formulation
- Variables: voltage magnitude (pu) and angle (radians in solver; convert to degrees for reporting) at each bus; generator active power (MW) and reactive power (MVAr). Fix a single reference bus angle.
- Objective: total generation cost. Map generator cost models (e.g., quadratic or linear) from the dataset and sum across generators. Do not include infeasible penalty terms unless explicitly required.
- Constraints:
  - AC nodal power balance using nonlinear power flow equations, including loads and shunts.
  - Generator bounds: pmin/pmax and qmin/qmax.
  - Voltage bounds: vmin/vmax per bus.
  - Branch constraints: thermal MVA limits from both ends (compute S_from and S_to); enforce angle-difference limits only if present and active in the dataset.
  - Device status: apply constraints only to in-service devices.
- Scaling: maintain consistent per-unit and MW/MVAr conversions. Use base MVA when converting between per-unit and physical units.

Phase 4: Initialization and Solve
- Provide reasonable initial values (e.g., vm ≈ 1.0 pu, va ≈ 0, Pg near forecasted load distribution, Qg ≈ 0) to aid convergence.
- Choose a robust nonlinear solver with appropriate tolerances. If the solver fails, adjust initialization or tolerances and retry.

Phase 5: Post-Processing and Report Generation
- Convert angles to degrees for reporting; keep voltages in per-unit; report powers in MW/MVAr.
- Compute flows from each branch end in MVA. Derive loading_pct = 100 × max(S_from, S_to) / limit.
- Compute total_load_MW/MVAr by summing bus loads; compute total_generation_MW/MVAr from generator dispatch.
- Compute total_losses_MW = total_generation_MW − total_load_MW (non-negative). Do not double-count shunts.
- Feasibility metrics:
  - max_p_mismatch_MW: maximum absolute active power balance residual across buses.
  - max_q_mismatch_MVAr: maximum absolute reactive power balance residual across buses.
  - max_voltage_violation_pu: maximum amount by which any bus voltage exceeds its bounds (0 if none).
  - max_branch_overload_MVA: maximum amount by which any branch flow exceeds its limit (0 if none).
- Populate the report sections with arrays of generators and buses, top most-loaded branches, and summary totals. Normalize field names and ensure numeric types.
- Set solver_status to a clear canonical string. Use "optimal" when the solver proves optimality; otherwise use a descriptive non-optimal status.

Verification

Schema checks
- Ensure the JSON has sections: summary, generators, buses, most_loaded_branches, feasibility_check.
- Confirm numeric fields are present and no values are NaN or missing.

Unit and consistency checks
- Angles reported in degrees; voltages in per-unit; powers in MW/MVAr.
- Recompute sums:
  - abs((total_generation_MW − total_load_MW) − total_losses_MW) ≤ small tolerance.
  - Sum(pg_MW) ≈ total_generation_MW; sum(qg_MVAr) ≈ total_generation_MVAr.
  - Sum of bus loads ≈ total_load_MW and total_load_MVAr.
- For each bus, vm_pu must be within [vmin_pu, vmax_pu] or counted toward max_voltage_violation_pu.
- For each reported branch, loading_pct should match flows and limit within tolerance.
- Feasibility metrics near zero indicate a high-quality AC-feasible solution.

Success Criteria
- The solver finds a least-cost, AC-feasible operating point.
- Report exists and follows the required structure and units.
- Feasibility metrics are within tight tolerances.
- No voltage limit or thermal limit violations unless explicitly allowed and reported.
- Totals and losses are internally consistent.

Common Pitfalls
- Unit mix-ups: reporting radians instead of degrees, or mixing per-unit with MW/MVAr without base MVA conversion.
- Losses computed incorrectly (e.g., double-counting shunts or mis-signing loads).
- Ignoring angle-difference constraints when they are present and active.
- Building with one Python environment and running with another (imports fail). Always verify interpreter and environment alignment.
- Incorrect branch loading calculation (use max of from/to flows and divide by limit).
- Failing to filter out-of-service devices.
- Not aligning solver_status to a canonical value; normalize to "optimal" for success.
- Large input files read naively; use streaming or chunked reads for inspection.
- Deleting created scripts or outputs; preserve artifacts needed for re-runs.

Optional Script Usage
- Use scripts/validate_acopf_report.py to validate a generated report for schema and internal consistency.
- Example: python scripts/validate_acopf_report.py path/to/report.json
- The validator checks required sections, unit-compatible relationships, totals vs sums, branch loading math, and voltage bound consistency.
