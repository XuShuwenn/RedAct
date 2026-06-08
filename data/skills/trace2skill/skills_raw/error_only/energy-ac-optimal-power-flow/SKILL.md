---
name: energy-ac-optimal-power-flow
description: "Run AC optimal power flow analysis to find least-cost AC-feasible operating points and produce voltage profile reports."
---

# AC Optimal Power Flow Analysis

## When to Use

- Find least-cost AC-feasible operating point for power systems
- Analyze voltage profiles and power flows
- Verify day-ahead market schedule feasibility
- Generate power system reports in JSON format

- Do not use this skill for heuristic or approximate dispatch-only outputs when the task requires AC-feasible results

## Execution Focus

- Treat the task as an instance-solving job, not a software development project.
- Produce the required report for the provided inputs in the current session.
- Do not stop at a plan, architecture proposal, or request to "proceed"; complete the computation and write the report.


## Input Files

- `network.json`: MATPOWER format power system snapshot
- `math-model.md`: Mathematical model description

- Derive the solver equations from `math-model.md` before coding; do not substitute an ad hoc AC-OPF formulation without checking each objective and constraint against the provided model.


## Execution Checklist

## Execution Checklist

- Read `math-model.md` and inspect `network.json` far enough to identify the exact objective, constraints, variable definitions, limits, required report fields, and relevant MATPOWER tables (`bus`, `gen`, `branch`, `gencost`) before implementing or solving; if any read is truncated, continue reading until the needed details are confirmed.
- Follow any task- or runtime-specific interaction rules exactly; use the required tool/action syntax, path conventions, and exact completion signal verbatim when provided.
- If the environment requires waiting for an observation after each action, issue exactly one tool call per turn and wait before continuing.
- Use absolute file paths whenever the task or environment provides or requires them.
- Check available tools, Python version, and required libraries before choosing an implementation; do not assume OPF frameworks or numerical packages are installed.
- Choose a solver approach that matches the confirmed environment, and prefer established OPF tooling over a from-scratch nonlinear program when available.
- Do not commit immediately to `scipy.optimize.minimize`/SLSQP for large AC-OPF instances; if no dedicated OPF solver is available, first do a small diagnostic/prototype run to verify the formulation and method are numerically viable.
- Implement with minimal edits. If a script or report is already working, patch the specific issue instead of deleting and recreating the artifact.
- After any code change, rerun the full flow and re-check that the final report is still produced and remains valid.
- Do not delete helper scripts, temporary files, environments, or dependencies before final handoff unless cleanup is explicitly requested.

## Key Outputs

Report at the task-required absolute output path (often `/root/report.json`, but follow the task's path constraints if they differ) with structure:
```json
{
  "summary": {
    "total_cost_per_hour": 1234567.89,
    "total_load_MW": 144839.06,
    "total_generation_MW": 145200.00,
    "solver_status": "optimal"
  },
  "generators": [{"id": 1, "bus": 316, "pg_MW": 245.5, ...}],
  "buses": [{"id": 1, "vm_pu": 1.02, "va_deg": -5.3, ...}],
  "most_loaded_branches": [{"from_bus": 123, "to_bus": 456, "loading_pct": 95.2, ...}],
  "feasibility_check": {"max_p_mismatch_MW": 0.001, ...}
}
```


Validation requirements for the final report:
- Match the requested report schema exactly and confirm the file parses as complete, valid JSON.
- Confirm the required top-level keys are present: `summary`, `generators`, `buses`, `most_loaded_branches`, and `feasibility_check`.
- Populate every numeric report field from the computed solution; do not use placeholder or hard-coded feasibility values.
- Normalize solver/library-specific termination strings to the report vocabulary before writing JSON (for example, map a successful raw status such as `Solve_Succeeded` to `"optimal"`).
- Populate `summary.solver_status` and `feasibility_check` values from actual solver results or explicit post-solve validation; do not hard-code placeholders or infer success from partial logs.
- Set `solver_status` to `optimal` only if an actual AC-OPF or AC power-flow-consistent solve succeeded under the provided model.
- Treat the output as complete only if it reflects an AC-feasible operating point, not merely the correct JSON shape.
- Verify power mismatch, voltage-limit violations, generator-limit violations, branch overloads, and consistency of generation, load, and losses before declaring success.
- If major violations, impossible balances, missing final solver status, or solver failure remain, do not report success; continue remediation or report the failure clearly.


## Units

- Power: MW (real), MVAr (reactive)
- Angles: degrees
- Voltages: per-unit


## Required Validation Before Declaring Success

## Required Validation Before Declaring Success

- Compute feasibility metrics from the final solved state; never leave placeholder values in `feasibility_check`.
- Verify system accounting is physically consistent: `total_generation_MW >= total_load_MW` and implied losses `total_generation_MW - total_load_MW` are nonnegative within a small numerical tolerance.
- Compute and report actual `max_p_mismatch_MW` and `max_q_mismatch_MVAr` from the network equations at the solution.
- Compute actual branch loading percentages and any overload amount from the solved flows and limits.
- If summary values show contradictions, such as negative losses, suspicious angles, or violated voltage/flow limits, do not state AC-feasible; flag the result as invalid and investigate.
## Tips

- Use an optimization solver suited to AC-OPF scale and numerics; prefer established OPF tooling when available.
- Check power balance by computing residuals from the solved state.
- Verify voltage limits [vmin, vmax] from reported bus voltages before concluding success.
- Monitor branch loading percentages and compute overloads from solved flows and ratings.
- Treat solver convergence as insufficient until the above validation checks pass.


- Start from the required deliverable: solve the provided network instance, then populate the final report at the required path.
- Prefer direct execution with available tools/libraries over designing new modules or reusable frameworks unless explicitly requested.
- Do not ask for input paths, output paths, or solver choice before checking the workspace and task files.
- Enforce the mathematical model in `math-model.md`; do not replace AC network equations, voltages, angles, or reactive power with ad hoc heuristics and still claim AC feasibility.
- Ground decisions in observed command/program output; do not infer file discovery, solver state, or saved-file completion without evidence.
- Verify solve completion from explicit termination evidence before writing `solver_status` in the report.
- Do not claim `optimal` based on solver startup banners, iteration headers, Jacobian counts, or truncated console output.
- If solver metadata is ambiguous, compute feasibility metrics directly from the solved point and report the true status.
- If optimization fails or is too slow, prefer an explicit failure or unsupported result over a simplified method mislabeled as AC-feasible.
- If OPF appears infeasible, first audit formulation details: bus/generator/branch indexing, per-unit vs MW/MVAr conversions, sign conventions, bounds, and power-balance/flow constraints.
- Treat physical sanity checks as completion gates: if generation/load totals are inconsistent, losses have impossible signs or magnitudes, or branch loading/voltages are clearly nonphysical, do not finalize the report as successful.
- Do not claim adherence to `math-model.md` from a partial read; finish reading truncated model text first.
- Do not assume the beginning of `network.json` shows all relevant structures; continue reading truncated input as needed.
- Do not declare completion from a partial read of the final report; confirm the full JSON structure and feasibility details.
- If you launch a solver asynchronously or in the background, wait for completion, inspect stdout/stderr, and verify the final report exists before finishing.
- Confirm available tools/commands before depending on them; if a utility is missing, switch to a supported fallback such as the Python standard library.
- Prefer robust parsing and report generation with Python over optional shell tools that may not be installed.
- If an attempted workflow step fails, correct the concrete issue, verify the changed lines are present, rerun the full OPF pipeline, and revalidate the regenerated report.
- Do not assume a rerun changed the report; reopen the final JSON and verify the specific fields you intended to change.
- Do not stop when a report-shaped JSON exists; stop only after the solved point passes feasibility checks and the final artifact has been fully inspected.



## Tips

## Execution Protocol and Final Checks

- Follow the task/runtime interface exactly as given in the prompt or system instructions. If the environment specifies a strict action/tool syntax, JSON schema, message format, file-access restriction, or exact completion token, use that literal format with no substitutions.
- Use only explicitly permitted paths and interfaces for the current run.
- Maintain an auditable sequence: inspect -> edit -> rerun -> verify.
- Do not claim a script, fix, or report exists unless it was explicitly created or updated and then checked.
- Validate the final report directly before claiming success; do not rely on a truncated preview, header-only check, or file existence alone.
- Inspect enough of the artifact to confirm the reported claims, including `solver_status`, total cost, total load/generation, and feasibility metrics.
- Do not claim solver success or report correctness from partial or truncated logs. Confirm completion from explicit final status, exit code, completion log, or by directly inspecting the final report artifact.
- If output or file reads are truncated, incomplete, or ambiguous, fetch the needed remainder, rerun with full capture, or inspect the produced artifact before making claims.
- Before finishing, verify that the final report exists at the required path, is valid JSON, and contains the required top-level keys: `summary`, `generators`, `buses`, `most_loaded_branches`, and `feasibility_check`.
- If you changed code or model inputs and reran the OPF, treat earlier outputs as stale until the new run clearly finishes and the report is confirmed to be from that latest run.
- Before declaring success, do a quick consistency pass: `total_generation_MW` should approximately equal `total_load_MW` plus losses, branch `loading_pct` should match the reported flow/limit ratio, and the report's `solver_status` should match the solver's actual termination result.
- If the task requires an exact final completion token or closing action, perform it only after the report has been verified.
- Keep the runtime environment and dependencies intact until final validation is complete.
