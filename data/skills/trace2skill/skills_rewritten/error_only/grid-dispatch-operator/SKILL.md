---
name: grid-dispatch-operator
description: "Optimize generator dispatches for power grid with DC power balance, transmission limits, and spinning reserve requirements."
---

# Power Grid Generator Dispatch Optimization

## When to Use

- Optimize economically efficient generator dispatch
- Satisfy power market constraints (DC balance, reserves)
- Analyze transmission line loading


## When to Use

## Execution Rules

- Follow the task's required interaction/output protocol exactly. If the environment specifies an exact completion string, emit it verbatim as the final line.
- Before the first tool use, identify any task-mandated tool/action syntax and exact completion signal; use only that protocol throughout, wait for each observation/result before the next step, and emit that exact completion string only as the final line.
- Treat interaction protocol compliance as a hard requirement: do not improvise unsupported tool syntax, wrappers, or freeform substitutes when the task specifies a strict interface.
- Hard stop: if the environment specifies an exact action/tool wrapper or completion token (for example `Thought:` / `Action:` JSON blocks or a literal completion string), use that exact syntax for every step and emit the completion token verbatim as the only final line.
- Before the first action, extract and restate to yourself the required action format and exact completion string; if your planned message does not match it literally, fix the format before sending.
- Do **not** switch to alternate wrappers, XML-style tool calls, pseudo-tools, or prose summaries, and do **not** delegate the core task to a subagent when a strict interaction protocol applies unless delegation is explicitly permitted and preserves that protocol end-to-end.
- Every tool call must be a concrete executable command or exact required payload. In shell-capable environments, write the literal `bash`/`python`/`jq`/etc. command that performs the step; do **not** send placeholders like `inspect the network file` or `run the optimization`.

- Use the task/environment-specified absolute paths. Treat `/root/report.json` as an example unless the runtime explicitly requires it.
- Write outputs only to task-approved absolute path(s). If file access is restricted, verify the destination is explicitly allowed before writing; do not invent `/root/...` or other example paths unless the runtime explicitly authorizes them.

- Before sending shell or Python commands, do a quick syntax check for broken quotes, truncated text, or malformed conditionals.
- After writing any Python/script or data file that you will execute or depend on, immediately read it back or run a lightweight validation (`python -m py_compile`, parse as JSON, etc.) to confirm the saved file contains complete executable content rather than placeholders, summaries, truncation, or a partial draft.
- Do not execute a newly written script blindly; first verify that the file content is present, syntactically valid, and matches what you intended to write.
- If a script run fails, inspect the relevant saved file lines and diagnose the specific failure before patching or rewriting. Do **not** make speculative edits without first checking the current implementation.
- Do not treat partial, truncated, or cut-off command/solver logs as success. Require explicit completion evidence such as solver success status, zero exit code, or a verified output file with expected contents.
- Do not mark parsing, modeling, solving, or reporting steps complete immediately after writing code. Treat file creation as incomplete until you have executed the script, handled runtime/import errors, and re-opened the required output artifact to verify it was actually produced.
- If command output appears cut off or incomplete, run an explicit follow-up check before proceeding, such as inspecting the exit status, rerunning with output redirected to a log, or validating that the expected report file was freshly written and parses correctly.

- Prefer the simplest constraints-compliant workflow first. Do not assume extra packages are installed; probe the runtime and prefer a verified available solver or pure-stdlib approach over assuming `numpy` or `scipy` exist.
- Before writing solver code, explicitly test the exact interpreter/environment you will use for required imports (for example `python3 -c "import scipy"`). Do not assume package availability from prior tasks or from a different interpreter.
- If needed packages are missing, do **not** attempt system-wide installation first. Prefer a compliant built-in path; if installation is truly required and permitted, use a project-local virtual environment and verify imports there before proceeding.
- Probe the runtime before committing to a solver stack: verify Python version, importable libraries, and available solver backends; prefer one stable implementation path and a single reproducible solve script when possible.
- Do not install packages or create a virtual environment unless a compliant built-in approach has been ruled out; if required packages are unavailable and system installation is blocked, use a project-local virtual environment and verify the selected interpreter can import the needed packages before solving.
- If structured inputs are large, inspect a small initial slice or targeted keys first to confirm schema, then parse the needed sections programmatically rather than repeatedly dumping the full file.
- If a file-read tool says the file is too large and recommends `offset`/`limit` reads or targeted search/grep, follow that recovery path directly on the next step instead of switching to a vague alternate approach.
- When recovering from large-file limits, use concrete partial-read or targeted-query commands/tools to inspect schema and representative rows; do not claim to have inspected or processed the file without an auditable command.
- If the first model is infeasible or unstable, debug formulation, indexing, units, and data mapping first; do not delete mandatory constraints or present a relaxed model as the final answer.
- For large networks, prefer sparse matrix assembly/formulations and solvers that exploit sparse structure; avoid unnecessary dense DC network matrices.

- When a solver or formulation fails twice with the same pattern (for example `primal infeasible`, repeated iteration-limit hits, or no usable output), stop patching the same path incrementally. Re-establish a minimal validated model or switch to another available compatible solver/formulation.
- After any nontrivial model edit, run a quick structural sanity check before a full solve: confirm array/matrix shapes, variable and constraint counts, bound vector lengths, and that the script parses cleanly.
- Do not spend long periods polling a solver that has already shown the same stall or non-convergence pattern. If a run is still spinning after prior similar failures, terminate it promptly and debug or change strategy instead.


## Input

- `network.json`: MATPOWER format power network snapshot


- Inspect `network.json` and task data for explicit reserve requirements, reserve semantics, generator statuses, branch limits, and MATPOWER generator cost data before choosing modeling assumptions.
- If a reserve target, market rule, or cost treatment is not specified, state any assumption explicitly and do not present it as given input.

- Before building the model, inspect the actual `network.json` structure programmatically, especially when it is large or unfamiliar: confirm top-level keys, `baseMVA`, bus/generator/branch counts, optional reserve-related fields, status columns, branch on/off flags, branch ratings, and 1 to 3 representative `bus`/`gen`/`branch`/`gencost` rows rather than guessing from memory or pasting the whole file.
- Do **not** start coding the solver after inspecting only buses, only top-level keys, or one table preview. Before coding, confirm at minimum the `bus`, `gen`, `branch`, and `gencost` sections, generator/branch status and limit fields, any reserve-related fields, and the task's required output schema/path.
- If the file is too large to print fully, inspect it in targeted slices/searches until those modeling-critical sections are verified; treat uninspected schema details as unknown rather than safe defaults.
- Determine the reserve requirement and reserve semantics from explicit task instructions or input data only. Do not silently invent default reserve rules such as percentages of load or largest-unit heuristics; if no rule is provided, state the assumption or ambiguity explicitly.
- Verify whether `gencost` is piecewise-linear or polynomial/quadratic before choosing the objective, and map indices from the provided table shapes/column counts instead of assuming a fixed schema.
- Translate MATPOWER tables into explicit indexed structures before building constraints: create a bus-number-to-contiguous-index map, generator-to-bus map, online generator and in-service branch filters, generator/gencost alignment checks, and identify the reference/slack bus from the case data.
- Treat external MATPOWER bus numbers as labels, not array indices, and keep power, flow, limits, and cost calculations on a consistent base-MVA convention throughout the model and reporting.
- Preserve dataset semantics when reading raw limits and operating ranges; do not "clean up" values such as negative `PMIN` unless the task explicitly instructs you to do so.



## Constraints

1. DC power balance at each bus
2. Generator and transmission limits
3. Spinning reserve requirements (standard capacity coupling)


4. Final dispatch must be network-feasible: enforce nodal DC power balance, generator bounds, transmission limits, and reserve-capacity coupling in the optimization model itself, not only as a post hoc check.
5. If transmission compliance is required, use bus-angle variables and DC flow relations or an equivalent PTDF/shift-factor formulation.
6. Restrict dispatch and reserve decisions to online generators only (`GEN_STATUS > 0`); exclude offline units from feasible capacity, reserve totals, and operating margin.
7. Preserve MATPOWER `gencost` semantics in the objective; if costs are quadratic/polynomial, optimize that objective or clearly state any unavoidable approximation.

- Do **not** replace the requested constrained optimization with merit-order, proportional, copper-plate, or other heuristic dispatch.
- Do **not** optimize on system-wide balance alone and then merely check flows afterward.
- If the first transmission-constrained model is infeasible, stop and debug the formulation/data mapping. Do **not** remove branch constraints, PTDF/DC flow constraints, or nodal balance constraints just to obtain a dispatch to report.
- If you temporarily run a relaxed model for debugging, label it diagnostic-only and do not write the final report or declare task completion until a dispatch satisfying the required network constraints has been obtained.
- Couple reserves with headroom explicitly (for example, `dispatch + reserve <= pmax`).
- If post-checks show any overload or violated required constraint, the dispatch is invalid and must be re-solved so the reported dispatch itself satisfies the limits.

8. If the task requires DC bus-level feasibility, include nodal balance and branch-limit constraints directly in the solved model; a system-wide `sum(generation)=sum(load)` constraint alone is not sufficient.
9. If MATPOWER `gencost` is polynomial/quadratic, preserve those terms in the optimization and reported cost evaluation whenever the available solver supports it; do not silently replace the objective with a linear or ad hoc approximation.
10. If a `gencost` approximation is truly unavoidable, disclose it clearly and report that the optimized objective differs from the original MATPOWER cost model.

- Do **not** invent fallback reserve rules such as `10% of load`, `largest unit`, or similar formulas unless the task/input explicitly specifies them.
- Do **not** replace DC line-flow calculations or transmission-constrained optimization with heuristic flow estimates, placeholder loadings, simplified congestion scores, or post-hoc retrofit feasibility checks.
- Treat post-solution overloads or balance errors as evidence the optimization model is incomplete or mis-specified; fix the constraints/formulation and re-solve instead of accepting the dispatch.
- If any reported line loading exceeds 100% of the enforced limit beyond tolerance, do not describe the solution as transmission-constrained or network-feasible; the model/report is inconsistent and must be debugged and re-solved.
- Do not state that transmission constraints were included if your own post-solve report shows overloads or if branch limits were only analyzed after the solve.
- A solution from a model that omits required transmission constraints is not a valid final dispatch, even if the solver reports success.
- Treat signed zero values such as `-0.0` as formatting noise unless the underlying value is materially negative; do not alter the optimization result merely to remove negative zero.



## Output Format

JSON at the task-specified absolute output path (use `/root/report.json` only if the runtime instructions explicitly direct that path), for example:
```json
{
  "generator_dispatch": [
    {"id": 1, "bus": 1, "output_MW": 100.0, "reserve_MW": 30.0, "pmax_MW": 150.0}
  ],
  "totals": {
    "cost_dollars_per_hour": 8000.0,
    "load_MW": 259.0,
    "generation_MW": 259.0,
    "reserve_MW": 500.0
  },
  "most_loaded_lines": [{"from": 1, "to": 2, "loading_pct": 85.0}, ...],
  "operating_margin_MW": 50.0
}
```


Use the exact top-level keys shown above: `generator_dispatch`, `totals`, `most_loaded_lines`, `operating_margin_MW`.
Do not rename keys. After writing the report, re-open and parse the JSON to confirm it is readable, complete, and contains the required nested fields such as `output_MW`, `reserve_MW`, and `loading_pct`; do not rely on `head`/`tail` or partial text inspection as a validity check.
- Treat partial inspections as non-validation: `head`, `tail`, clipped console output, or a truncated read is not enough to prove the report is complete.
- When validating the written report, inspect the actual saved values needed to support your claims; do not infer reserve satisfaction, totals, or feasibility from solver status or partial/truncated output alone.
- If the parsed report shows any obvious contradiction with your claims or internally inconsistent values (for example overloads while claiming all transmission limits were enforced, or generator-level reserves that do not support the reported total), stop and debug the model/output rather than declaring success.
Before finalizing, compare the written JSON keys against the requested schema verbatim. Do not accept aliases or self-invented names such as `generators` for `generator_dispatch` or `top_3_loaded_lines` for `most_loaded_lines`.
Validate the actual file you wrote against the task-required schema, and inspect the exact fields you plan to mention, especially `generator_dispatch`, `totals`, `most_loaded_lines`, and `operating_margin_MW`.
Also verify the artifact exists at the required absolute path and has plausible populated content before declaring success.
If any requirement is ambiguous, especially reserve obligation or reserve-capability semantics, report the assumption explicitly instead of presenting it as given input.


## Key Metrics

- Generator dispatch MW and reserve MW
- Total cost, load, generation
- Top 3 most loaded transmission lines
- Operating margin (uncommitted capacity)

## Tips

- Use optimization (scipy.optimize or linear programming)
- Check transmission line loading percentages
- Verify spinning reserve requirements


- Build a DC network-constrained dispatch/OPF, not a single-bus economic dispatch: include generator outputs, reserve variables, bus angles, nodal DC balance, branch thermal limits, and one fixed reference bus in one model.
- Before coding, translate each task requirement into a specific model component (decision variable, objective term, or constraint) and use that checklist to verify nothing was omitted.
- Build and verify the indexed network data layer first (buses, generators, branches, reactances, limits, costs, slack/reference bus), then formulate the optimization from those structures.
- Keep status filters in every mapping step: exclude offline generators from dispatch/reserve variables and out-of-service branches from the network model.

- Use the same optimized dispatch for any post-solution flow/loading report; do not invent heuristic, capped, or placeholder `most_loaded_lines` values.
- Use the exact accepted solver dispatch and reserve values for every downstream calculation, validation, and reported metric. Do not swap in placeholder injections, proportional redispatch, or any alternate dispatch while debugging or preparing outputs.
- After solving, derive `generator_dispatch`, totals, `most_loaded_lines`, and `operating_margin_MW` in one pass from the same accepted solved variables and network data; do not use separate heuristics, capped placeholders, or a reporting workflow that could drift from the accepted dispatch.

- Check transmission line loading percentages after solving, but only as validation of constraints already enforced in the model.
- Treat implausible outputs as model bugs, not success. If line loadings or angles look nonphysical, re-check units, PTDF/DC flow calculations, sign conventions, and whether line constraints were actually enforced.
- Use validation as a gate: if loadings or angles are implausible, if reported flows came from an estimate rather than the solved DC model, or if results are only approximate, do not finalize as success.
- If flow magnitudes are implausible, stop and debug before reporting: verify base-MVA conversion, branch susceptance/reactance interpretation, sign conventions in nodal balance, reference-bus handling, and that branch limits are enforced in the model. If still unvalidated, report the limitation clearly instead of fabricating line-loading results.

- Do **not** clamp, rescale, or otherwise manually edit dispatch/reserve outputs after solving to "fix" balance or limit issues; fix the formulation and re-solve.
- If a solve fails, debug the current formulation first: check array shapes, index alignment, bounds, online/offline filtering, and solver status before changing solvers or algorithms.
- If generator-side tables do not align cleanly (`gen`, `gencost`, reserve-related inputs, status filtering), stop and fix the indexing/mapping before solving; do not rely on implicit row alignment.
- Treat MATPOWER `gencost` as authoritative input data, not a placeholder. Do not replace piecewise-linear costs with default constants or drop quadratic terms unless you clearly label that approximation.
- Build bus injections from an explicit generator-to-bus mapping/incidence matrix (for example, `Cg @ Pg`) after consistent online/offline filtering; use the same mapping in nodal balance constraints and reporting.
- For large networks, prefer sparse/incidence-based DC-OPF assembly over unnecessary dense matrix expansion when the runtime supports it.
- If using a slack-bus-eliminated formulation or PTDFs, keep it mathematically equivalent to the stated DC balance and branch-limit requirements.
- When building models with symbolic libraries, do not use Python truth-value tests on symbolic expressions or constraints; track unset state with `None` or separate bookkeeping, then build the final constraints explicitly.
- When using MATPOWER-style data, verify every matrix and vector uses the same internal bus ordering before debugging physics or solver behavior.

- Do not claim the optimizer succeeded unless you observed explicit completion evidence, such as a success status, exit code, or verified output file with expected contents.
- Read [references/dc-opf-pattern.md](references/dc-opf-pattern.md) when implementing transmission-constrained dispatch or debugging suspicious flow magnitudes.
- Read [references/large-network-sparse-modeling.md](references/large-network-sparse-modeling.md) when `network.json` is large, you need sparse/incidence-based assembly, or the model is slow to inspect or build.


- Before solving, explicitly confirm the model contains: online-unit filtering, one `Pg` per online generator, one `R` per online generator if reserves are required, one `theta` per bus, nodal DC balance constraints, branch-flow equations, branch limits, reserve-capacity coupling, and one reference angle.
- If your model has only `sum(generation) = sum(load)`, stop and fix it before solving; that is not a valid network-constrained dispatch.
- Encapsulate parsing, optimization, validation, and JSON writing in one reproducible script so the reported dispatch and diagnostics come from the same run.
- Read [references/large-network-sparse-modeling.md](references/large-network-sparse-modeling.md) when `network.json` is large, you need sparse/incidence-based assembly, or the model is slow to inspect or build.
- Read [references/dc-opf-pattern.md](references/dc-opf-pattern.md) for consistent online-generator filtering, aggregate-balance backstops, and same-dispatch reporting requirements in transmission-constrained dispatch.

- Do not switch to a simplified, fallback, copper-plate, or diagnostic script unless you have verified it still implements the full required constrained formulation. If it omits or fails to enforce nodal DC balance, branch-flow equations, or branch limits, do not use its output as the final report.
- Use a staged solve workflow: first validate parsing/index maps and model dimensions, then solve a minimal structural version, then run the full formulation.
- Treat obviously extreme or self-contradictory post-solution transmission results as evidence the model/reporting path is wrong or unconstrained. Stop, debug the formulation or reporting pipeline, and re-solve; do not finalize those results as success.
- Read [references/solver-triage-and-sanity-checks.md](references/solver-triage-and-sanity-checks.md) when a formulation edit introduced script errors, a solver repeats non-convergence, or a solve appears stalled.




## Tips

## Final Validation

Before concluding success:

- Confirm the accepted dispatch is the direct solver result, not post-processed by ad hoc clamping or proportional rescaling.
- Do not clamp, rescale, rebalance, or otherwise patch solver outputs after optimization to force feasibility or nicer formatting. If dispatch, reserves, or totals are inconsistent, fix bounds, constraints, or indexing in the model and re-solve.
- Confirm every bus satisfies DC nodal balance in the solved model.
- Confirm no transmission line exceeds its limit.
- If your own validation shows any unresolved overload, any loading above 100% within tolerance, nodal-balance failure, or omitted required constraint, do **not** describe the result as a successful network-constrained dispatch and do not emit the task-complete signal yet. Re-solve or clearly report that a valid feasible dispatch was not obtained.
- Cross-check claimed model properties against the saved JSON itself. If `most_loaded_lines` or other reported diagnostics contradict the claim of transmission-feasible dispatch, the run is not ready for completion.
- If any post-solution check reveals overloads, nodal-balance violations, or other required-constraint failures, do not write the final report as a successful completion; fix the model/formulation and re-solve, or clearly report that a valid feasible dispatch was not obtained.

- Confirm no offline generator has nonzero dispatch or reserve.
- Confirm any reported reserve requirement and reserve totals come from task/input data or from an explicitly stated assumption that matches the implemented model.
- Confirm the objective and `cost_dollars_per_hour` match the parsed MATPOWER `gencost` representation, or explicitly disclose any approximation before claiming an economically efficient optimum.

- Confirm totals are internally consistent (`generation_MW == load_MW` within tolerance) and reserve coupling holds.
- Confirm the reserve requirement itself is satisfied, reserve totals equal the sum of generator-level `reserve_MW` values, and each reported generator obeys `output_MW + reserve_MW <= pmax_MW`.
- Confirm generator-indexed outputs still align with the intended MATPOWER generator entries after any online/offline filtering or masking.
- Scan generator rows for bound/status issues such as `output_MW < pmin`, `output_MW > pmax`, or nonzero output/reserve on offline units; if `Pmin < 0`, negative dispatch can be valid and should not be "corrected" unless it violates the input constraints.

- Confirm reported line loadings come from the same DC-constrained dispatch being reported.
- If computed flows/loadings look implausible, unstable, or self-contradictory, stop and debug the physical calculation; do **not** replace them with a heuristic, capped, or hand-picked summary just to complete the report.
- Do not treat JSON existence, schema validation, or populated fields as sufficient when derived transmission metrics are still analytically unvalidated.
- Confirm no reported transmission metric (`most_loaded_lines`, loading percentages, flows) comes from a heuristic, fallback estimator, or different model than the accepted solver result.
- If validation reveals extreme/nonphysical loadings or self-identified approximation, treat the run as not ready for completion rather than merely noting the issue in commentary.

- If any required constraint is violated or results cannot be physically validated, do not present the run as completed successfully; revise the model or report the limitation clearly.
- End with the exact required completion string when one is specified by the environment.

- Confirm every tool interaction followed any task-mandated wrapper/serialization format exactly.
- Confirm the required output file exists at the required absolute path, parses successfully, and its schema matches the requested keys exactly.
- Confirm aggregate balance explicitly: total online generation equals total load within tolerance, including any slack/reference-bus treatment.
- Confirm apparent negatives are real violations, not display artifacts such as `-0.0`, before revising the model or output.
- Confirm reported totals come from the raw accepted solver solution; if something looks inconsistent, inspect assumptions, bounds, index mappings, and post-processing before changing signs, clipping negatives, or otherwise altering dispatch values.
- If generators legitimately allow unusual operating ranges in the input data, preserve that semantics in the report instead of forcing conventional values.
- Confirm any solver or script step you relied on showed explicit completion evidence; if output was truncated, rerun checks or inspect produced files before claiming success.
- Confirm the written report is the artifact produced by the same script/model run used for optimization and post-processing, not manually assembled from separate intermediate steps.
- Confirm operating margin matches the generator-level arithmetic implied by online capacity minus dispatched output under the task's stated semantics.
- After rounding values for the JSON report, recompute reported totals from the rounded entries or otherwise ensure the saved JSON remains internally consistent within stated tolerance.
- Perform a final protocol check immediately before the last response: verify the output file exists at the required path, verify the report contents you plan to mention by re-reading the JSON, and make the final response exactly match the environment's required completion protocol with no trailing extra text after any exact completion string.

- Before claiming any numeric result or satisfied constraint, re-open the written report and the supporting solver outputs/diagnostics, then verify the exact values you plan to mention. Do **not** infer totals, operating margin, loaded lines, or feasibility from a partial preview.
- Confirm any script you relied on was read back or otherwise validated after writing, and that it contained executable code rather than descriptive placeholder text.
- Perform a protocol-only final check separate from model validation: confirm every prior tool call used the task-mandated wrapper/schema, confirm every shell/tool action was a real executable command or exact required payload rather than a natural-language placeholder, and if the environment specifies an exact completion string, emit that exact string verbatim as the final line with no extra text after it.
- Perform an evidence check before the last response: for each claim you plan to make, confirm there is a corresponding explicit check in the current run or remove the claim.
- Cross-check aggregate generation and reserve totals against the detailed `generator_dispatch` rows before finalizing; summed `output_MW` and `reserve_MW` should agree with reported totals within tolerance.
- If report contents, parsed JSON, and runtime logs disagree, or if the report is truncated, unreadable, analytically unvalidated, or contradicts claimed feasibility, treat that as a stop signal and resolve the discrepancy before completion.
- If the only solvable model you have is a relaxed, fallback, simplified, or post-hoc-checked version that allows required network violations, do not present it as completed successfully; continue debugging or clearly report that a valid feasible dispatch was not obtained.
- Before claiming a fix worked, rerun enough of the pipeline to verify the specific problem is gone: at minimum confirm the script parses, the model builds with expected dimensions, and the solver returns a new explicit status rather than the same prior failure mode.

