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


## Runtime Protocol Is Mandatory

- Start by inspecting the workspace and referenced files to infer input paths, output path, solver options, and runtime constraints; ask clarifying questions only after confirming the needed information is genuinely unavailable.
- Before the first tool use or file operation, identify any task-specific requirements for tool-call syntax, allowed directories, file-access limits, message schema, per-turn waiting rules, and exact completion token.
- If the runtime specifies an exact `Thought`/`Action` format, JSON action payload, one-tool-per-turn rule, or single allowed tool interface, use that literal format on every step; do not substitute default tool wrappers, prose-only substitutes, or habitual syntax.
- If the runtime exposes only one tool/interface, use only that interface for reads, writes, and execution; do not invent alternate tool names or wrappers.
- Before the first action, extract the runtime interaction contract into a mini-checklist: exact wrapper/tags if any, required field names and JSON shape, allowed tool/interface names, one-action-per-turn waiting behavior, allowed paths, and exact completion token.
- If the runtime mandates a literal action format, use that exact wrapper on every tool step; do not switch to XML-style tags, markdown/code-fence wrappers, prose-plus-tool hybrids, placeholder pseudo-commands, or default tool-call syntax.
- Treat action payloads as executable artifacts, not summaries of intent: shell actions must contain the exact command text to run, and file-write/edit actions must contain exact paths and literal old/new text or full file contents.
- Do not use underspecified actions like `list directory contents`, `install dependencies`, `validate report`, or `fix the script`; issue the concrete command, path, pattern, replacement, or full content instead.
- Treat protocol compliance as a hard gate: an otherwise correct OPF result is still incomplete if tool calls, path usage, or the final completion signal violate the runtime instructions.
- Treat any plan mode as temporary at most: inspect inputs, run or patch the solve, generate the report, and exit only after the required artifact exists and has been validated.
- If a mode switch, tool call, or protocol step fails, correct the invocation immediately and continue execution; do not end with a request for permission to proceed.
- If the task requires an exact final completion string, end with exactly that string and no extra prose.
- Do not ask for file names, file locations, output path, solver choice, or format details until you have first inspected the workspace and task files using the permitted interface and confirmed the information is genuinely unavailable there.
- Treat protocol mismatch as task failure even if the OPF work itself is correct.
- Before the final response, compare your intended closing message against the runtime's exact completion instruction. If a literal token is required, output exactly that token and nothing else.
- Treat the exact completion signal as exclusive and non-substitutable: do not replace it with marker files, a prose summary, explanatory wrap-up text, or a near-match.


## Input Files

- `network.json`: MATPOWER format power system snapshot
- `math-model.md`: Mathematical model description

- Derive the solver equations from `math-model.md` before coding; do not substitute an ad hoc AC-OPF formulation without checking each objective and constraint against the provided model.

- Do not proceed from a skimmed or truncated model read when implementing equations. Confirm the exact objective, sign conventions, indexing, bounds, and branch-flow expressions from `math-model.md` before trusting solver results.


## Execution Checklist

- Before coding or patching the solver, finish reading any truncated `math-model.md`, `network.json`, or task instructions until the needed objective terms, constraints, indexing, limits, report schema, and input structure are explicitly confirmed.
- On any interpreter, virtualenv, or dependency repair step, immediately run a proof command that shows the intended Python executable works and that required imports succeed before relying on that environment.
- If a dependency is missing or installation is blocked, switch to an available interpreter/toolchain or an allowed isolated environment rather than repeating the failing approach.
- When a run fails, diagnose the first concrete blocker from the latest traceback or error line before changing solver formulation, tolerances, initialization, or model logic.
- If a solver build/run fails and the traceback or log is truncated, stop speculative editing and first rerun with full stdout/stderr capture or otherwise extract the complete error from the same failing step before making additional changes.
- When a nonlinear solver fails, stalls, or returns an infeasible/suboptimal point, debug the formulation before solver tuning: re-check bus/gen/branch indexing, sign conventions, per-unit-to-MW/MVAr conversions, admittance/flow equations, objective terms, and limit mapping against `math-model.md` and `network.json`.
- Use small targeted checks before a full rerun: verify network assembly on a few buses/branches, confirm that computed balances/flows have the expected sign and units, and only then adjust tolerances, initialization, or solver options.
- In symbolic or optimization code, reserve distinct names for core decision variables and never reuse them for local parameters from buses, generators, or branches.
- After assembling the optimization model but before solver creation, print or inspect quick sanity checks for decision-vector type/shape and bounds/constraint dimensions so name collisions, scalar-overwrite bugs, or malformed formulations are caught immediately.
- If the requested `math-model.md` formulation is not fully implemented or verified, do not present a heuristic, DC-style, sequential, or otherwise simplified fallback as task completion.
- After any code or model edit, treat prior solve conclusions as stale until the updated run completes and you inspect outputs from that new run.
- After any solver run that exits successfully, inspect the expected output artifact immediately before concluding the solve failed or switching approaches.
- After you obtain a run that produces a valid report and passes feasibility checks, freeze the working path unless a task requirement or a verified report defect still requires a change.
- Keep debugging experiments isolated from the main deliverable: use separate scratch/test scripts instead of overwriting the primary solver file with reduced repro code, then intentionally copy validated fixes back and rerun the full solve -> report pipeline end to end.
- Preserve created scripts, reports, and intermediate artifacts until final validation and handoff are complete; do not delete generated files unless cleanup is explicitly requested.

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
- Map raw solver termination text to report status only after capturing explicit final solver evidence programmatically or from complete logs; never infer `optimal` from startup banners, iteration headers, or partial console output.
- Never copy raw solver return strings directly into user-facing schema fields when the report defines its own vocabulary; translate them first, then reopen the written JSON to confirm the normalized value is what was saved.
- If solver metadata is missing, malformed, or raises an exception, keep `solver_status` aligned to the verified outcome from explicit post-solve checks; do not default it to `optimal`.
- After solving, reopen the generated report and verify that derived summary semantics are correct, especially that losses are computed as `total_generation_MW - total_load_MW` and that normalized status labels still match the actual solve outcome.
- Populate `summary.solver_status` and `feasibility_check` values from actual solver results or explicit post-solve validation; do not hard-code placeholders or infer success from partial logs.
- Gate report writing and presentation on explicit solver success plus basic feasibility checks. If the solver reports infeasible, failed convergence, invalid numbers, or the solved point has impossible balances or large violations, do not write or present it as a valid solved report.
- Treat statuses such as `Invalid_Number_Detected`, NaN residuals/Jacobians, `infeasible`, failed convergence, or missing final termination evidence as hard blocks on final report generation.
- Do not let a script write the required report path directly from intermediate iterate data. First verify explicit successful termination and basic physical consistency, then serialize the final report from that validated solved state.
- Treat any preexisting report at the target path as stale by default. Trust it only after a later run clearly finishes successfully and you confirm the artifact was regenerated from that run.
- Set `solver_status` to `optimal` only if an actual AC-OPF or AC power-flow-consistent solve succeeded under the provided model.
- Treat the output as complete only if it reflects an AC-feasible operating point, not merely the correct JSON shape.
- Verify power mismatch, voltage-limit violations, generator-limit violations, branch overloads, and consistency of generation, load, and losses before declaring success.

- Treat any positive reported overload or other explicit feasibility violation from your own checks as unfinished work, even if numerically small; do not declare success while a nonzero violation remains unless the task explicitly provides a tolerance that deems it acceptable.
- Do not use `debug`, failed-solve, infeasible, `acceptable`, or `suboptimal` iterates as final AC-OPF results unless you separately compute and confirm all required feasibility checks from that point; otherwise report failure rather than labeling it solved.- If major violations, impossible balances, missing final solver status, or solver failure remain, do not report success; continue remediation or report the failure clearly.


## Units

- Power: MW (real), MVAr (reactive)
- Angles: degrees
- Voltages: per-unit


## Required Validation Before Declaring Success

- Treat feasibility as a hard completion gate: a valid JSON file or correct schema is not completion by itself.
- Use validation checks as hard completion gates. If any required feasibility quantity cannot be computed from the current solution, or if mismatches, limit violations, negative-loss contradictions, or clearly nonphysical branch loadings remain beyond tolerance, do not mark the case `optimal` or AC-feasible.
- Do not infer success from a cost-minimizing dispatch alone. Accept the result only if bus-level AC balance, voltage variables, reactive power behavior, and branch/network constraints have been solved or explicitly validated against the required model.
- Cross-check reported aggregates and percentages against their underlying numbers before finalizing, especially branch `loading_pct = flow / limit * 100` and summary totals versus the generated report contents.
- If validation finds a nonzero branch overload, mismatch, or limit violation, continue remediation: tighten solver tolerances, rerun from the latest model, or refine post-processing/limit handling, then recompute feasibility metrics before finalizing.
- Do not let a "diagnosed but tiny" violation bypass the completion gate; either eliminate it, show that it is within an explicitly stated task tolerance, or report that strict AC-feasible completion was not achieved.
- Treat any of the following as a hard stop against success: negative implied losses beyond tolerance, total generation materially below total load, large mismatch residuals, or major voltage/branch/generator limit violations.
- If the solver says infeasible but simple adequacy checks such as total `Pmax` versus load suggest the case should be solvable, assume formulation risk first and continue debugging rather than concluding the dataset is bad.
- Do not replace missing validation with placeholders or "best found" values. Compute `feasibility_check` fields from the final solved state, or clearly report failure/unsupported status instead of claiming success.
- Validate that all table-indexing, sign conventions, and unit conversions used in the solve and post-processing match the inspected input schema; if balances or flows look wrong, audit schema mapping and per-unit conversion before concluding the model is infeasible.
- After every root-cause fix, rerun the full solve -> report pipeline and re-open the regenerated report; treat pre-fix outputs as stale.
- Do not write or preserve `summary.solver_status: "optimal"` unless explicit solver evidence and post-solve feasibility checks both support that label.

- Treat solver outcomes such as `acceptable`, high residuals, nontrivial constraint violation, or failed convergence as unfinished work, not successful completion, unless the task explicitly allows that status and your post-solve checks confirm all required feasibility conditions.
- If the latest visible problem is a runtime, type, formatting, or reporting exception, fix that exception first; do not pivot to model retuning until a rerun shows a genuine solver-stage issue.
- Do not accept a report as successful merely because the JSON exists or the pipeline ran end-to-end; a structurally correct artifact with impossible balances, negative losses beyond tolerance, explicit overloads, voltage violations, or contradictory status evidence is a failed result, not a completed solve.
- If the report or logs contain contradictory evidence such as `optimal` status plus infeasibility metrics, large residuals, overloads, or nonphysical totals, fix the formulation, post-processing, or status mapping before finalizing.
- After editing code late in the task, never stop at the patch itself: verify there is a subsequent completed run, a regenerated report from that run, and final inspection of the saved artifact before handoff.

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
- Do not invent convergence details such as iteration counts, final objective values, or solver-success messages unless they are explicitly visible in the current run's output or confirmed by directly inspecting the produced report/log artifact.
- If solver stdout is truncated, rerun with capturable logging or inspect the solver-produced files/report before stating that the solve succeeded.
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
- Make the first substantive move quickly: after reading the instructions, use the allowed interface to inspect the workspace or open the relevant files rather than replying with a plan or clarification request.
- Keep planning private and brief; visible progress should be an allowed action that advances the deliverable.
- Never finish without the runtime's exact completion mechanism.
- Treat protocol compliance as a completion requirement, not a formatting preference: use the exact required per-turn action syntax and finish only with the mandated completion signal.
- If the runtime is turn-based, never send multiple actions in one assistant turn even if they seem independent.
- Use only explicitly permitted paths and interfaces for the current run.
- Maintain an auditable sequence: inspect -> edit -> rerun -> verify.
- Keep the execution trail causal and observable: if you claim a script was fixed, there must be a visible edit step before the rerun that produced the new result.
- Keep artifact provenance observable: do not state that `run_opf.py`, `report.json`, or any other file was created/updated unless the session shows the concrete write action that produced it.
- Treat file-write integrity as a validation step: after creating or overwriting a `.py` file, inspect enough of the saved file to verify it contains Python source code rather than a natural-language placeholder or summary.
- Do not claim a solver script exists just because a write command succeeded; confirm the on-disk contents are executable-looking code and, when feasible, run it.
- If you wrote or patched a file in this session, name that same file explicitly in the execution command used for validation; avoid switching to a different similarly named script without first inspecting and justifying it.
- Do not claim a script, fix, or report exists unless it was explicitly created or updated and then checked.
- Validate the final report from the regenerated artifact itself, not from truncated logs, a header-only preview, or file existence.
- Treat any report/output file found before the current run as stale by default. Use it as evidence only after confirming the latest completed command regenerated or updated that exact file in this session.
- After creating or patching a critical code file, reopen it and inspect enough of the saved contents to confirm the actual code was written, not a placeholder summary or truncated fragment, before running it.
- If solver stdout/stderr or the report read is truncated before the needed fields are visible, continue reading or rerun with capturable output before making any claim about status, feasibility, totals, violations, or branch details.
- Keep all final statements evidence-bound. Only report solver status text, feasibility metrics, overload counts, limiting branches, or other numeric findings that you directly confirmed from the regenerated final JSON or explicit verification output of the latest completed run.
- Do not summarize unseen portions of the report; if a preview omitted `feasibility_check` fields, branch details, or claimed sections, open those sections before citing them.
- For JSON deliverables, verify the whole artifact: open the final report from the required path, parse it as complete JSON, confirm the required top-level keys are present, and inspect enough of each section to ensure the report is complete rather than header-correct.
- Treat any truncation notice as incomplete verification. If a file view says it was truncated, continue reading the remainder or use another method to inspect the full artifact before declaring success.
- Do not rely on `head`, `tail`, or small `grep` snippets as sole evidence for report correctness when the file is larger than those views; use targeted parsing/reads to inspect the exact required fields.
- For large JSON reports, prefer a parser-based check that prints the required fields and selected counts/entries from the saved file, then base final claims only on that observed output.
- After each fix and rerun, re-open the regenerated artifact and directly inspect the specific affected fields before claiming the issue is resolved.
- If the report is large or a read is truncated, use targeted reads/queries to inspect the exact sections you changed or rely on for final claims; do not treat a file head/tail preview as full verification.
- Inspect enough of the saved JSON to confirm the reported claims, including `solver_status`, total cost, total load/generation, `generators`, `buses`, `most_loaded_branches`, and `feasibility_check`; if the read is truncated, continue reading the remainder before declaring success.
- Sample multiple required sections of the written report before finishing: inspect `summary`, at least one populated entry from `buses` or `generators`, `most_loaded_branches`, and the full `feasibility_check` block.
- Keep final statements evidence-bound: report only values, counts, statuses, and branch/bus findings that were directly read from the final JSON or explicit verification output from the latest completed run.
- Do not claim solver success or report correctness from startup banners, Jacobian/nonzero counts, early iteration logs, dependency-install logs, partial progress text, or other incomplete fragments. Confirm completion from explicit final status, exit code, completion log, or by directly inspecting the final report artifact.
- Before opening or summarizing the report file, first verify that the producing command finished and that the report was written or updated by that completed run; treat any pre-existing report at the target path as stale until then.
- If you start a solve asynchronously or in the background, you must fetch its final status/output, inspect stdout/stderr, confirm the required report file was regenerated, and only then proceed to completion.
- Before finishing, verify that the final report exists at the required path, parses as complete valid JSON, and contains the required top-level keys: `summary`, `generators`, `buses`, `most_loaded_branches`, and `feasibility_check`.
- Do not treat structure-only checks as final validation. Cross-check that `total_generation_MW` approximately equals `total_load_MW` plus losses, branch `loading_pct` matches the reported flow/limit ratio, and the report's `solver_status` matches the solver's actual termination result.
- Separate artifact validation from solution validation before handoff: a complete schema-correct JSON file does not imply AC feasibility.
- Do not accept `solver_status: "optimal"` plus correct top-level keys as sufficient evidence of success; explicit numerical consistency checks for balances, losses, residuals, and limits must also pass.
- After each fix, verify the specific defect that motivated the change is gone in the new run. For example, if branch-flow logic was repaired, re-check branch loading and overload metrics from the regenerated report rather than only confirming that the file exists or parses.
- If output or file reads are truncated, incomplete, or ambiguous, fetch the needed remainder, rerun with full capture, or inspect the produced artifact before making claims.
- If you changed code or model inputs and reran the OPF, treat earlier outputs as stale until the new run clearly finishes and the report is confirmed to be from that latest run.
- If the latest run is infeasible or physically inconsistent, do not switch to a handoff that says the infrastructure works or the file is ready; continue remediation or explicitly report failure to obtain an AC-feasible solution.
- Separate artifact readiness from task completion: after all validations pass, perform the exact required closing action/token and nothing else when the runtime requires exclusivity.
- Keep the runtime environment and dependencies intact until final validation is complete.

- When editing solver code that uses symbolic math libraries (for example CasADi), do not introduce Python boolean tests on symbolic expressions inside `if` statements; avoid patterns like `if mx_expr == 0` unless the library explicitly returns a real boolean there.
- If a run succeeds and the report passes feasibility checks, prefer final report verification and handoff over additional code churn.

- Do not claim solver success or report correctness from startup banners, dependency-install logs, early iteration text, partial progress output, or truncated stdout/stderr; require explicit final termination evidence, process exit evidence, or a regenerated artifact whose contents show the completed run's result.
- If output capture is incomplete or a chained command may still be running, fetch the remainder, rerun with capturable logging, or inspect the produced artifact before making any success claim.
- Treat exit code 0 or other process-success signals as a cue to check artifacts first: verify whether the required report was regenerated, parse it, and inspect solver/feasibility fields before rewriting the workflow.
- Do not replace a solver or start a new approach until you have checked whether the previous completed run already produced a valid deliverable.
- Ground the final handoff in the last completed observable run only: if the latest rerun output is truncated, interrupted, missing the expected report readback, or otherwise ambiguous, do not claim success yet.
- Do not end while a background or asynchronous solve is still running. Wait for final completion, inspect its outputs, verify the report, then emit the exact required completion token.
- Before final handoff, explicitly verify the target artifact from the filesystem produced by the latest completed run: confirm the file exists at the required path, parse it successfully, and inspect the saved contents rather than inferring success from startup text or a presumed chained command.
- If you used a scratch reproduction or temporary simplified script during debugging, confirm the final reported result came from the intended main solver/report path, not from an isolated test file unless the task explicitly allows that replacement.
- Keep final claims strictly evidence-bound: report only values, counts, statuses, and branch/bus findings that were directly read from the latest regenerated artifact or explicit verification output.
- Do not place explanatory prose where an action object or exact completion token is required.
- Once deliverables and validations are complete, stop acting immediately unless the task explicitly requests cleanup, teardown, or extra post-processing.
- Do not run cleanup commands such as deleting virtual environments, temporary folders, or helper artifacts after reporting readiness unless cleanup was explicitly requested.
- Finalization is a separate mandatory step: after the report is validated, emit the exact required completion signal and nothing else when the runtime requires exclusivity.
