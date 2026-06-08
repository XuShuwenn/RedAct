---
name: manufacturing-fjsp-optimization
description: "Optimize flexible job shop scheduling with machine downtime windows and policy budget constraints to minimize makespan."
---

# Flexible Job Shop Scheduling Optimization

## When to Use

- Optimize manufacturing job shop schedules
- Handle machine downtime windows
- Minimize makespan with budget constraints


## Execution Protocol

- Default workflow unless the task explicitly requires another order: (1) inspect and fully read all governing inputs (`instance.txt`, `downtime.csv`, `policy.json`, and any baseline file), (2) summarize the actual schema and constraint set before coding, (3) implement parsing/repair/export/validation in a dedicated script such as `/app/solve.py`, (4) execute it to write both required output artifacts, and (5) read the saved artifacts back and validate them before the final response.
- For repair tasks, use the baseline artifacts as the default scaffold when present, but do not start coding from only one file; collect instance, downtime, policy, and baseline data first so repair decisions reflect the full constraint set.
- If parsing fails or parsed counts look suspicious, immediately reopen the raw source files and recover the true schema before patching the solver against unverified format assumptions.
- Do not stop after planning, parser edits, or solver construction; complete the run by actually generating the required artifacts or an explicit infeasible/failure output.

## Execution Protocol

- If the task specifies a required action/tool-call format, follow that protocol exactly from the first action through the final completion signal.
- Do not substitute another tool syntax or omit a required completion marker.
- Before solving, confirm you can comply with the task's execution interface as written.

## Input Files

- `/app/data/instance.txt`: Job and operation data
- `/app/data/downtime.csv`: Machine downtime windows
- `/app/data/policy.json`: Policy budget data
- `/app/data/current baseline`: Current schedule

- Before coding any parser or solver, inspect the raw contents of each required input file and confirm the actual structure and field meanings from the source files themselves.
- Read every required input file completely before deriving constraints from it; if any view or output is truncated, continue reading until the relevant records are fully visible.
- Treat the baseline schedule as authoritative for freeze/change-budget checks; do not infer locked operations from a partial read.


- `/app/data/baseline_solution.json`: Baseline schedule/policy reference if present; read the full file before using it for locks, budgets, or comparisons

- If any expected file is missing or naming is uncertain, list `/app/data` first and use the discovered filenames/paths rather than assuming the names in this guide.
- Confirm the raw schema of each source file before coding parsing logic (for example line-based text vs JSON/CSV fields); match the parser to the observed structure, not to prior assumptions.
- If any required file read is visibly truncated, cut off mid-record, or otherwise incomplete, do not model against it yet. Re-read the file with a method that returns the full contents, or avoid baseline-dependent claims until the missing data is resolved.
- Do not compute machine-change budgets, start-shift budgets, freeze boundaries, or baseline comparisons from a partial baseline file.
- If a baseline artifact is truncated mid-record, malformed, or incomplete, stop baseline-dependent modeling immediately. Re-read it with a full-content method before coding repair logic, machine-change counting, start-shift calculations, or baseline-comparison checks.

## Output

### solution.json
```json
{
  "status": "",
  "makespan": ,
  "schedule": [
    {"job": , "op": , "machine": , "start": , "end": , "dur": }
  ]
}
```

### schedule.csv
Same data as solution.json in CSV format (job, op, machine, start, end, dur)


If no schedule satisfies all stated hard constraints, still write the deliverables and mark infeasibility explicitly.

Use `solution.json` like:
```json
{
  "status": "INFEASIBLE",
  "makespan": null,
  "schedule": []
}
```
Do not output `FEASIBLE` for a schedule that required relaxing freeze, budget, downtime, or precedence constraints.
- Write the actual computed schedule data to both deliverables; never write placeholders, ellipses, templates, or summary text in place of schedule rows.
- Generate `solution.json` and `schedule.csv` from the same final in-memory schedule object or dedicated export path so they cannot drift apart.
- After writing, read both files back and validate them rather than hand-editing outputs at the end.


## Goals

1. Generate feasible schedule
2. Minimize makespan
3. No worse policy budgets than baseline
4. Respect machine downtime windows


5. Preserve stated policy, baseline, freeze, and lock semantics exactly as defined by the task and input files; do not relax, strengthen, or rewrite them without explicit support
6. If the task explicitly requires a schedule with lower makespan than baseline, do not present a same-makespan solution as successful
7. Write `/app/output/solution.json` and `/app/output/schedule.csv`
8. Report results conservatively unless optimality is actually proven
9. Preserve reproducibility until outputs are finalized

- When a baseline schedule is provided together with freeze/change-budget rules, treat it as the default schedule: load it first, identify actual violations, and prefer minimal repairs over full rescheduling unless the task explicitly calls for a rebuild.
- Default repair workflow when a baseline is present: (1) read `instance.txt`, downtime, policy, and the full baseline first, (2) identify concrete baseline violations and locked/frozen fields, (3) reserve validated frozen/locked baseline intervals, (4) repair only the operations that must change for feasibility or explicit improvement, and (5) validate the resulting schedule inside the same script/run before writing outputs.
- For repair tasks, use a canonical construction order: preserve validated frozen/locked baseline assignments first, then schedule movable operations in precedence order at the earliest feasible time that respects predecessor completion, machine capacity, downtime windows, reserved protected intervals, and explicit policy locks.
- Keep construction and validation coupled in one script/run so every candidate is checked for precedence, machine legality/non-overlap, downtime, locked fields, and budget usage before it can become final output.

10. Separate objectives explicitly: first satisfy the task's hard deliverable requirement (feasible repair or explicit infeasibility/failure output), then pursue makespan improvement only if the task explicitly requires or rewards it.
11. Choose the primary optimization/acceptance target from the task statement and input artifacts, not from inference. Do not promote a baseline metric into a hard success criterion unless the task explicitly says so.
12. When artifacts provide explicit acceptance metrics such as repair feasibility, zero hard-constraint violations, or budget compliance, satisfy those first and report success against them; do not redirect the search toward beating baseline makespan unless strict makespan improvement is explicitly required.
13. Use a two-stage workflow by default: first produce one fully validated schedule that satisfies all hard constraints and required budgets, then attempt bounded makespan improvement from that validated baseline.
14. During repair or improvement, treat policy budgets (for example machine-change and start-shift limits) as candidate-level acceptance checks, not end-of-run afterthoughts; reject over-budget moves before promoting a candidate.


## Required Validation Before Modeling

- Read any baseline or policy file completely before deriving constraints from it; if prior output is truncated, rerun a command that shows the full contents.
- Do not infer freeze or lock semantics from field names alone; encode a hard constraint only when its meaning is directly supported by the task artifacts.
- For fields like `freeze`, `freeze_until`, or similar policy controls, determine from the baseline artifacts and task wording whether they refer to baseline sequence position, elapsed time, operation indices, or exact locked fields; do not assume `op < N` semantics unless the inputs explicitly support that interpretation.
- When freeze behavior depends on a baseline schedule, map the freeze boundary to the baseline schedule's actual stored order/records unless the inputs explicitly define a different indexing rule.
- If a policy interpretation appears ambiguous or inconsistent, verify the inputs and state the assumption clearly rather than hard-coding an unverified rule.
- Do not choose among multiple plausible freeze/lock interpretations because one produces a feasible schedule. Select an interpretation only when it is directly supported by the task text or input artifacts; otherwise report the ambiguity and avoid claiming definitive feasibility under the unsupported reading.
- Do not test several policy semantics and silently keep the one that works best. Solver success is not evidence that the interpretation is authorized.
- If multiple artifacts mention different metrics or acceptance signals, resolve the objective from the task wording and explicit file fields before modeling; do not assume baseline makespan must be beaten unless the task explicitly states strict improvement.

- Before modeling or repairing, extract a complete constraint inventory from the input artifacts: true `instance.txt` structure and machine options, downtime windows from `downtime.csv`, and freeze/lock/change-budget semantics from the full baseline and policy files.
- For schedule-repair tasks, inspect `instance.txt`, `downtime.csv`, `policy.json`, and the available baseline file together before deciding what can change; derive repair logic from the combined constraints, not from any single file in isolation.
- When file contents are shown through a rendered interface or preview, inspect the raw text/bytes view and read the full file before writing a parser or deriving constraints; if output is truncated, rerun with a command that shows the complete contents.
- Before using `/app/data/baseline_solution.json` or any baseline schedule for locks, freeze checks, machine-change counts, start-shift budgets, or baseline makespan comparison, confirm you have read the entire schedule; do not derive constraints from truncated output.
- If a baseline read ends mid-record or mid-array, stop immediately and reread the file with a method that returns the complete contents before computing any baseline-derived freeze set, lock set, or change-budget metric.
- Run a quick validation pass on any provided baseline schedule before repairing or optimizing it; identify concrete violations (for example downtime, capacity, precedence, or budget conflicts) so changes target actual infeasibilities rather than guessed ones.
- Turn that validation pass into a short baseline violation report before any repair: list the specific operations and rules currently violated, and for each violated operation enumerate its allowed machine alternatives from `instance.txt`.
- Use this report to choose repair moves and repair scope instead of changing heuristics blindly.
- Restrict changes to operations implicated by those violations or by explicit task requirements such as strict-improvement targets.
- If policy freeze/lock rules depend on a baseline cutoff time, explicitly enumerate the affected baseline operations before solving and record the exact locked fields (`machine`, `start`, `end`, or others). Remove those operations from the movable set unless the artifacts explicitly allow changes.
- When a policy freezes the first `N` operations/items of a baseline plan, derive that locked set from the baseline schedule's actual stored order/sequence, not from job IDs, operation numbers, or other semantic labels unless the inputs explicitly define that mapping.
- Distinguish between freezes that lock exact timestamps and freezes that preserve baseline choices/order only. If the artifacts do not explicitly lock `start`/`end`, do not make timing immovable by assumption.
- Treat baseline-derived freezes as exact equality constraints on the listed fields only after confirming those preserved assignments are compatible with the task's hard feasibility rules; do not weaken them into preferences or earliest-start hints.
- For custom `instance.txt` formats, inspect the raw line structure and token stream first; map each token position, repeated count line, and per-operation option-count field from the file itself rather than assuming a standard FJSP layout.
- If parsing yields suspicious results such as empty jobs, missing operations, zero durations, impossible machine IDs, or any operation with zero machine options, stop and reinspect the raw source files before changing the solver.
- If a parser fails or parsed counts/records look inconsistent with the instance, baseline, or policy data, reopen the raw source files and infer the exact grammar and record counts from the file contents before patching the parser.
- Map freeze/lock rules to the baseline schedule exactly as supported by the artifacts. Do not treat fields like `freeze_until` as per-job operation-index cutoffs, convert stated machine/start/end locks into weaker rules, or otherwise switch semantics mid-repair unless the files explicitly define that alternative.
- For repair tasks, distinguish explicitly hard-locked fields from baseline values you are merely trying to preserve.
- When baseline or policy data marks operations as frozen/locked, first validate each preserved assignment against allowed-machine rules, downtime, machine occupancy/capacity, precedence, and duration consistency.
- Keep and reserve only the validated protected assignments first on the machine timelines; treat conflicting or explicitly movable operations as the repair set.
- Preserve frozen baseline fields by default only when that preserved assignment is itself hard-feasible.
- If a baseline operation inside the freeze horizon is infeasible under the task's hard constraints, follow the artifact-defined lock semantics exactly: repair it only if the rules allow that field to change, otherwise report infeasibility rather than silently keeping an invalid lock or relaxing other hard constraints.
- Before modifying scheduling logic, map which baseline operations conflict with downtime or other hard constraints and record why; reserve enforceable frozen baseline intervals before scheduling unfrozen work.
- Derive change-budget metrics directly from the fully loaded baseline and candidate schedule data, and compute those metrics inside the solver or repair workflow so each candidate can be checked against the stated budget before output.
- When rebuilding or repairing a schedule, treat each operation's predecessor in the repaired schedule as the precedence anchor: compute feasible start times from the repaired predecessor end time, not from inconsistent baseline timestamps alone.
- Implement parsing, solving/repair, validation, metric computation, and artifact writing in a dedicated script (for example `/app/solve.py`) instead of piecemeal shell edits when the task has multiple interacting constraints.
- Preferred startup/workflow for multi-constraint repair tasks: (1) inspect the raw structure of `instance.txt`, `downtime.csv`, `policy.json`, and any baseline file completely, (2) use the baseline schedule to confirm job/operation indexing and output schema when helpful, (3) implement parsing, repair, validation, metric computation, and artifact writing in one dedicated script, and (4) execute that script to write both required artifacts, then read them back to confirm the expected status, fields, and row content were actually written.
- Preserve a tight parse-debug loop for custom formats: if the first parser run throws an indexing/count/shape error, crashes with errors like `IndexError`, or produces empty/suspicious counts, treat that as evidence your file-structure assumption is wrong; reopen the raw file end-to-end, remap token/count semantics from the source, cross-check against the baseline structure when available, and only then revise the parser.
- For nonstandard `instance.txt` encodings, map the actual sequence of header/count/operation tokens from the raw file first, then build the parser to that observed structure instead of forcing a standard FJSP schema.

- Before changing the baseline schedule, produce a short conflict inventory from the inputs and baseline: list the specific operations that violate downtime, capacity, precedence, machine legality, or explicit policy locks, and use that inventory to define the movable bottlenecks.
- For baseline-guided repair, classify operations into: (a) explicitly locked/frozen and still feasible as-is, (b) baseline operations that are movable, and (c) baseline operations whose stored placement is infeasible under current hard constraints.
- Before modifying a baseline-guided schedule, enumerate every baseline operation covered by any freeze horizon or explicit lock rule and record the exact locked fields for each (`machine`, `start`, `end`, or others). Exclude those fields from the movable search space.
- Use a simple startup pattern that has worked well in repair tasks: inspect `instance.txt`, `downtime.csv`, `policy.json`, and the baseline file together first, then summarize machine options, downtime windows, freeze/lock scope, and budget metrics before coding the repair or solver.
- If change budgets or guardrails matter, compute those metrics inside the solver/repair script for every candidate (for example machine-change count and total start-shift distance versus baseline) instead of treating them as a manual afterthought.
- For repair tasks, target changes at the concrete violating operations and their immediate precedence/resource neighbors first; do not start with broad rescheduling if a localized repair can satisfy the hard constraints and budgets.
- Do not choose among multiple plausible freeze/lock interpretations because one produces a feasible schedule. Select an interpretation only when it is directly supported by the task text or input artifacts; otherwise report the ambiguity and avoid claiming definitive feasibility under the unsupported reading.

## Hard Acceptance Rules

- Protocol compliance is part of correctness, not a formatting nicety: a valid schedule can still fail the task if any action used the wrong schema or the final response omitted the exact required completion token.
- If the environment requires an `Action:` line with JSON for a specific tool, use that exact structure for **every** tool interaction; do not substitute direct tool calls or other labels.
- Treat any task-specific execution protocol (required action syntax, tool-call format, or exact completion string) as a hard constraint and follow it exactly.
- Protocol violations are unrecoverable task failures even if the schedule itself is correct: one unsupported action format or a wrong completion line invalidates the run.
- Apply this final gate before writing feasible output: full baseline read confirmed, freeze/lock semantics enforced literally from the provided artifacts, any required baseline-derived anchors enforced, budget/change metrics recomputed from the final saved schedule, and `final_makespan < baseline_makespan` whenever strict improvement is required.
- Do **not** accept a candidate based only on summary metrics or solver intent. Feasibility requires a direct rule-by-rule audit on the final saved artifacts.
- Perform the final audit on `/app/output/solution.json` and `/app/output/schedule.csv` themselves, not just on solver logs or in-memory intent.
- Mandatory final audit on the saved artifacts: compare the final schedule against the baseline row-by-row for every frozen/locked operation; any mismatch in a locked field is an immediate rejection.
- Recompute change-budget metrics directly from the saved final schedule and the fully read baseline/policy files. Do not trust solver console summaries or internal counters unless they are independently checked against the written outputs.
- When policy budgets are part of acceptance, make the generation script emit the recomputed budget metrics used for acceptance so the final audit can compare those values directly against the saved artifacts.
- Check every scheduled operation against every stated downtime window using interval-overlap logic on the saved schedule before claiming feasibility.
- Make the saved-artifact audit explicit: read the saved output files, iterate every scheduled operation against every downtime window, and reject any overlap instead of relying on solver status or narrative assertions.
- Boundary-touching intervals are acceptable only when they do not overlap (for example `end == downtime_start` or `start == downtime_end`); use the same interval rule consistently in both solving and final validation.
- Do not state "all constraints are satisfied" until this explicit saved-artifact validation has passed.
- If any earlier run, note, or diagnostic flagged a candidate as relaxed, exploratory, ambiguous, or policy-violating, that candidate is permanently disqualified from final output unless it is rerun and passes the full literal-rule validation on the saved artifacts.
- In the final audit, explicitly recheck every previously problematic rule on the written files, especially freeze horizons and locked `machine`/`start`/`end` fields from the baseline/policy data.
- Do not claim exact machine-change counts, start-time-shift totals, makespan improvement amounts, or other policy metrics unless you explicitly recomputed them from the saved final artifacts or showed validator output for them.
- If validation or solver diagnostics identify any freeze/lock mismatch, precedence, downtime, capacity, machine-legality, duration, or budget violation, reject that candidate; do not ship it as feasible and do not switch to a relaxed model for final output.
- If freeze/lock semantics remain ambiguous after inspecting the artifacts, do **not** declare the schedule definitively feasible under an assumed interpretation. State the assumption explicitly and report unresolved validation or infeasibility unless the governing interpretation is supported by the inputs.
- Do not use an invalid baseline schedule as proof that violating downtime, precedence, or capacity is acceptable. Hard feasibility constraints still govern the final output unless the task explicitly states otherwise.
- A frozen or baseline-carried assignment is acceptable only if it independently passes the same hard-constraint checks as the rest of the final schedule. Baseline presence alone does not authorize downtime overlap, machine conflict, precedence violation, illegal machine use, or duration mismatch.
- Use an explicit independent validator pass on the final saved candidate, separate from the constructive scheduler or solver logic, before accepting the schedule as feasible.
- If the independent validator finds any machine overlap, downtime conflict, precedence error, illegal machine assignment, duration mismatch, budget violation, or frozen-field mismatch, reject the candidate and fix the producing logic before writing feasible output.
- A task is not complete until both `/app/output/solution.json` and `/app/output/schedule.csv` are written from a validated final schedule or validated infeasibility/failure-to-improve result, then read back and checked for non-emptiness and consistency.
- Write both output files from the same final in-memory schedule object, then read both back immediately and confirm row counts/key fields match before declaring success.
- Make output generation and validation auditable in the run log: show the concrete write commands or script execution that produced the files, then inspect the saved files directly to confirm key fields and row counts.
- Do not rely on abstract statements such as "written", "validated", or "ok" as evidence. Final feasibility claims must be backed by observable checks of the saved artifacts.
- Make output generation auditable: show the concrete command or script invocation that wrote `/app/output/solution.json` and `/app/output/schedule.csv`, then inspect the saved files directly for key fields, row counts, and parseability before claiming success.
- Do not rely on opaque tool summaries such as "wrote files" or "validated ok" when the underlying file contents were not read back or shown.
- Validate deliverables as artifacts, not just schedules: inspect both `/app/output/solution.json` and `/app/output/schedule.csv`, confirm they represent the same final schedule, and ensure any reported makespan or budget numbers are recomputed from those saved files.
- Validate constraint classes separately on the saved final artifacts: downtime overlap, precedence, machine non-overlap/capacity, allowed-machine legality, durations, freeze/lock equality checks, and policy-budget limits. Do not treat passing one category as evidence that the others also pass.
- If no candidate satisfies all hard constraints and explicit acceptance conditions, write an explicit infeasible or failure-to-improve result instead of a same-makespan, reinterpreted, partially validated, or otherwise noncompliant schedule.
- Never justify a final schedule by saying a freeze, lock, budget, downtime, or precedence rule was ignored "to maintain feasibility." If the literal constraints cannot all be met, the only acceptable final artifacts are constraint-consistent infeasible/failure-to-improve outputs.
- Do not describe a result as optimal, minimal, or best-possible unless you have explicit proof, an exhaustive method, or a validated bound that supports that claim.

- Once you have a fully validated feasible schedule that satisfies the task's hard constraints, serialize it immediately to `/app/output/solution.json` and `/app/output/schedule.csv` before attempting additional improvement searches.
- If later optimization fails, times out, or introduces code errors, fall back to the best already validated saved schedule rather than leaving the task unfinished.
- If no improving schedule is found, still complete the task with the correct validated deliverable for the actual requirement: feasible repair, explicit failure-to-improve result, or explicit infeasibility, as appropriate.
- Do not stop at exploration or environment probing. A task is incomplete until you have either written the required output artifacts or written the explicit infeasible/failure-to-improve artifacts required by the task.
- Never promote a schedule found under relaxed, exploratory, or ambiguously interpreted constraints to final output. Final artifacts must come from a candidate that satisfies the literal task and policy rules, or else be marked infeasible/failure-to-improve.
- Do **not** use truncated baseline or policy data for freeze, lock, or budget enforcement. If any baseline-dependent file was only partially viewed, reread it fully before modeling, validating, or making feasibility claims.
- Do **not** return a schedule that you know violates a stated freeze/lock/policy constraint in order to "maintain feasibility." If the literal constraints appear incompatible, write the required output artifacts as explicit infeasible/failure output instead of relaxing the rule.
- Do **not** write placeholder, template, ellipsis, or summary text to `/app/output/solution.json` or `/app/output/schedule.csv`; serialize the actual final computed schedule data.
- Validate the **saved** `/app/output/solution.json` and `/app/output/schedule.csv` against every hard constraint before declaring success; do not rely on an earlier solver status, intermediate run, or diagnostic schedule.
- After writing the outputs, read both files back and confirm they are non-empty, parse correctly, and match the final in-memory/computed schedule before declaring success.
- Do **not** claim exact policy metrics, feasibility, or improvement amounts unless those values were explicitly computed from the final saved artifacts or shown by a validator.
- Base the final response on observable evidence from the saved files or validation output, not on solver intent or earlier intermediate candidates.

- Independently recompute freeze compliance from the saved artifacts against the fully read baseline: for every frozen/locked operation, compare final `machine`, `start`, and `end` row-by-row to the baseline and reject the schedule on any mismatch in a locked field.
- Independently recompute policy change-budget metrics from the saved final schedule versus the baseline; do not accept solver-reported counts without this artifact-based comparison.
- Prefer an auditable script-based workflow over ad hoc shell edits when multiple interacting constraints are present: one script should load inputs, build/repair the schedule, write `/app/output/solution.json` and `/app/output/schedule.csv`, and run the final validation checks.
- After the script writes the outputs, open the saved files themselves and confirm they exist, are non-empty, and contain the expected schedule or explicit infeasible/failure status before declaring completion.
- Do not spend the whole run on environment probing. After confirming inputs and constraints, move to a concrete solver or repair script, execute it, and write the required artifacts.


## Final Pre-Response Checklist

- Confirm the final saved schedule, not an exploratory candidate, is the one written to both output files.
- Recompute and verify all hard constraints on the written artifacts, including freeze/lock semantics and any strict-improvement requirement.
- If validation fails under the literal rules, write infeasible/failure-to-improve output instead of keeping the invalid schedule.
- Before finalizing, scan your own prior run notes/logs for any candidate marked relaxed, exploratory, ambiguous, or violating freeze/lock/budget rules; if the written output matches such a candidate, reject it and replace it with a literally validated schedule or explicit infeasible/failure output.
- Then emit the exact required completion marker/token with no extra trailing text.

- If you have a validated feasible repair candidate, write `/app/output/solution.json` and `/app/output/schedule.csv` immediately before any further improvement search; do not risk ending with no deliverable.
- If the task's primary requirement is feasibility or repair and strict improvement is not explicitly required, stop after writing the validated feasible result instead of continuing an open-ended search for a better makespan.
- If strict improvement is explicitly required and you cannot prove an improving valid schedule, still finish by writing the required explicit failure-to-improve or infeasible artifacts.
- Before the final marker, confirm the saved files were read back, parsed or inspected for structure, and shown to contain the concrete computed schedule rather than placeholder content.
- Verify the saved output status matches the literal result: feasible only if every hard constraint passed on the saved artifacts; otherwise write explicit infeasible/failure output.
- Base the final response only on observable evidence from those read-back checks or validator output.
- Final protocol check: confirm that every prior tool interaction used the mandated schema and that the final response is exactly the required completion token/string, with no explanation before or after it.
## Hard Acceptance Rules

- Treat task requirements and policy files as hard constraints unless the task explicitly says they are optional.
- If the task requires a schedule with **less** makespan than baseline, enforce **strict improvement**: `final_makespan < baseline_makespan`. Equal makespan is a failure, not a success.
- Do **not** relax or reinterpret freeze/lock rules, downtime windows, or budget constraints just because a stricter model is harder or infeasible.
- If baseline freeze/locked operations conflict with downtime or other hard constraints, return an infeasible result instead of a schedule for a relaxed problem.
- If your validation flags any violation (freeze, locked machine/start/end, downtime, capacity, precedence, budget), do **not** write that schedule as feasible output.
- If no candidate satisfies all stated constraints and acceptance criteria, report infeasibility or failure to improve rather than emitting a known-invalid or non-improving schedule.
## Tips

- Use OR-tools or similar for scheduling
- Consider job shop scheduling constraints
- Handle machine availability windows
- Verify schedule feasibility


- Build parsers only after checking raw file format; preview formatting may be misleading.
- If parsing or early solver output looks wrong, re-open the raw `instance.txt` and map the actual token/count structure before debugging scheduling logic; fix parser assumptions first.

- Prefer parser logic that follows the actual encoding seen in the file (for example token-based parsing for dense instance text) over fixed line-count or column-position assumptions.
- When parser output looks empty, inconsistent, or error-prone, stop and inspect the raw source files again before changing solver logic; fix the parser from the observed format first.
- Treat policy rules as hard constraints, not heuristic penalties. Use the literal meaning from `policy.json`, baseline data, and task instructions; do not reinterpret them to rescue feasibility.
- Ground `freeze` or similar policy fields in the baseline schedule/order before using them in scheduling logic; do not assume they refer to per-job operation indices unless the data explicitly says so.
- In repair tasks, a good default is: keep explicitly frozen/locked operations on their required baseline machine/order when mandated, but for non-locked operations use the baseline as a starting reference and shift timing or machine assignment to the earliest feasible supported choice that satisfies downtime, precedence, capacity, and any stated budget limits.
- Before solving, extract any locked fields from `policy.json` (for example frozen `machine`, `start`, `end` up to a cutoff time) and enforce them unchanged.
- Practical freeze check: build the set of baseline operations covered by the freeze horizon, then after writing outputs assert for each such operation that final `machine`, `start`, and `end` exactly equal baseline values whenever those fields are locked.
- Practical budget check: compute policy metrics from `solution.json`/`schedule.csv` versus the baseline after writing the files; if the recomputed values differ from what the solver reported, trust the recomputed audit and reject the candidate.
- Do not turn a baseline comparison or policy bound into a stricter requirement unless the inputs explicitly say so.
- Move from planning to execution quickly: run a concrete bounded solver or constructive heuristic early, and wrap expensive searches with a timeout.
- Prefer a simple feasible schedule generator over extended method discussion; iterate after you have a candidate schedule.
- Use a staged workflow that has worked well in practice: inspect raw files first, build one fully validated feasible repair/schedule with correct policy accounting, save both artifacts, then attempt bounded improvement only if the task requires or rewards it.
- Use a staged search pattern when global guards exist: first construct and validate one literal-constraint-compliant repair, then if a required makespan/ratio/improvement guard is still unmet, run a bounded search over machine assignments or repair choices under the same hard constraints.
- Do not abandon a validated feasible repair just because improvement search is harder; save it first, then refine or return the required failure-to-improve output if strict improvement is mandatory and no improving candidate is found.

- For repair or baseline-guided tasks, prefer repairing the provided baseline schedule over rebuilding from scratch when freeze/change-budget constraints are present: keep baseline assignments and timings unless a change is required for feasibility or explicit improvement.
- Use a precedence-aware constructive scheduler for movable operations: process operations in precedence-safe order, track predecessor completion times, maintain per-machine occupied intervals, and place each operation at the earliest feasible time on an allowed machine that respects capacity, downtime, and any explicit locked fields.
- If using a heuristic or local search, describe the result as a feasible or improved schedule; do not call it optimal or minimal unless you have explicit proof, a certificate, or a verified bound.
- After any solver edit, inspect the changed code and rerun with enough diagnostics to confirm behavior actually changed before trusting the new result.
- Treat written artifacts as the source of truth: after generating `/app/output/solution.json` and `/app/output/schedule.csv`, read them back and validate them before claiming success.
- After writing outputs, inspect at least one machine-readable artifact and one exported artifact (typically both `solution.json` and `schedule.csv`) so you verify not only the in-memory schedule but also the persisted deliverables the task will grade.
- Use a dedicated validator script or equivalent explicit checks on the saved artifacts; do not rely on visual inspection alone to confirm downtime, precedence, machine non-overlap, locked fields, freeze compliance, and policy-budget compliance.
- Before finalizing, explicitly verify: job precedence, operation durations, one-machine-at-a-time capacity, downtime avoidance, policy-budget comparison against the complete baseline, that makespan equals the max end time in the saved schedule, and that `schedule.csv` matches `solution.json`.
- Recompute any policy/budget claims from the final saved schedule and compare against the provided baseline/policy files; do not report exact counts/totals unless they were derived from the final artifacts.
- If literal policy constraints make improvement infeasible, report that conflict clearly instead of claiming success with a modified or non-improving schedule.
- Do not rely on truncated solver console output as evidence. If logs are partial, inspect the full output files or rerun validation scripts on those files before concluding.
- Always write both required artifacts: `/app/output/solution.json` and `/app/output/schedule.csv`.

- Read `instance.txt`, `downtime.csv`, `policy.json`, and any baseline file together before designing repair logic so machine alternatives, downtime, freeze rules, and change budgets are modeled consistently.
- Prefer baseline-guided repair when a baseline schedule is provided: load the baseline first, preserve unchanged assignments and times by default where allowed, and modify only the operations needed for feasibility or required improvement within the stated limits.
- If starting from a baseline schedule, generate a concrete violation report first (conflicting operations, violated rules, and eligible alternative machines), then repair only from validated facts in the inputs and baseline.
- A reliable repair pattern is precedence-aware earliest-feasible replay: after choosing candidate machine assignments, place each operation at the earliest start that satisfies predecessor completion, machine capacity, downtime windows, reserved frozen intervals, durations, and any baseline-derived lower bounds or explicit locks.
- Reserve machine-time slots for frozen assignments that are already feasible before scheduling repaired or flexible operations; do not let later repairs displace valid frozen operations.
- Reserve feasible frozen baseline intervals first, then schedule movable work around them. If a nominally frozen baseline placement itself violates a hard constraint, keep only the explicitly locked fields and repair the rest exactly as allowed by the artifacts rather than silently preserving an impossible interval.
- Repair only frozen operations that are inherently invalid or explicitly allowed to change; if preserved locked/frozen assignments still conflict with other hard constraints, report infeasibility rather than relaxing those constraints.
- During constructive repair or local search, track policy-budget usage incrementally and reject over-budget candidates early rather than relying only on an end-of-run check.
- For each operation, evaluate all allowed machine alternatives with feasible start/end times under downtime and policy constraints; do not default to the baseline machine when other permitted machines may yield a better valid schedule.
- When comparing repair candidates, use lexicographic scoring that prioritizes earliest feasible start/end or smallest makespan impact first, then uses machine-change or start-shift penalties as secondary tie-breakers within the allowed budget.
- Use a two-stage search when helpful: for small machine-choice spaces, prefer bounded exact or near-exact enumeration of machine assignments; otherwise get a feasible baseline-respecting repair quickly, then refine it with a bounded heuristic under an explicit timeout.
- When baseline operations violate downtime on their current machines, explicitly test alternate eligible machines before concluding that delaying on the same machine is sufficient or that the instance is infeasible.
- Generate `/app/output/solution.json` and `/app/output/schedule.csv` from the same final in-memory schedule object, then read them back and validate operation completeness, machine legality, durations, precedence, machine overlap, downtime avoidance, policy/budget compliance, matching schedule rows, and that makespan equals the max end time.
- Base final claims only on the saved artifacts or full validation output; if console output is truncated, rerun inspection commands or validate the files directly instead of inferring missing details.
- When a validator fails, inspect the construction logic that produced the offending start/end times before applying formatting-only fixes such as reordering output rows.
- After any meaningful solver modification, inspect the actual edited code or diff, rerun enough diagnostics to confirm the behavior changed, and only then trust the new result.
- If improvement search stalls, fall back to the best fully validated feasible schedule you have and still write the required output files; if no schedule satisfies all hard constraints, write the explicit infeasible/failure output instead of stopping at analysis.
- Before the final response, check whether the system or task requires an exact completion token or control phrase, and emit it exactly.

- When using custom recursive or stateful search code, run a small sanity test before the full search: verify the script executes without syntax/scope errors, produces at least one candidate on a tiny case or restricted subset, and preserves a recoverable best-so-far schedule object for serialization.
- Prefer a two-phase workflow for fragile optimization tasks: (1) generate and validate one compliant schedule artifact, (2) copy or refine from that saved baseline under a bounded improvement search.
- Avoid placeholder tool actions entirely; every action should either read real inputs, execute real code, validate outputs, or write the required artifacts.

- Good default workflow: inspect raw files, validate the parser against the baseline structure, classify protected baseline assignments into feasible-to-keep versus conflicting, reserve the feasible protected intervals, produce one fully feasible repaired schedule, write both artifacts, validate the saved artifacts, then attempt bounded improvement only if the task requires or rewards it.
- Separate candidate generation from verification: write or reuse a small validator script (for example `verify_solution.py`) that checks the saved artifacts for precedence, machine legality, non-overlap, downtime, durations, freeze/lock compliance, budget metrics, and makespan consistency, then use its first concrete failing constraint category to drive solver fixes.
- When an intermediate candidate fixes one issue class (for example downtime), immediately rerun the other validators as well; repaired schedules often introduce new precedence or machine-overlap errors.
- When choosing among feasible repair moves under machine-change or start-shift budgets, score candidates by both timing impact and policy-change cost; do not optimize only delay or only baseline preservation when the task requires satisfying both.
- Use a completion-first fallback order: (1) obtain one validated schedule satisfying the literal hard constraints, (2) write both required artifacts from that schedule, and (3) only then attempt bounded improvement if the task explicitly calls for it.
- Default repair pattern for baseline-guided tasks: validate frozen/locked baseline operations first, reserve only the ones that are still feasible under downtime/capacity/precedence, then schedule the remaining operations in precedence order at the earliest feasible time.
- In precedence-aware repair, anchor each movable operation at `max(predecessor_end_in_repaired_schedule, baseline_start_if_that_is_a_required_lower_bound)` and search forward on each allowed machine for the earliest interval that satisfies downtime, occupancy, duration, and explicit lock rules.
- When change budgets or baseline-comparison metrics matter, bias tie-breaking toward baseline stability: prefer the baseline machine and the smallest valid start-time shift, and switch machines only when needed for feasibility or when the task explicitly rewards the change enough to justify the budget impact.
- If baseline-guided greedy repair stalls at a feasible but weak schedule, escalate to a broader search over machine-assignment combinations for the movable operations, and rebuild each candidate schedule from scratch rather than applying only local timing tweaks.
- When the movable operations and machine-choice branching are small enough to enumerate or tightly bound, escalate early from heuristic tweaking to bounded exhaustive search over machine assignments or repair decisions.
- If a search attempt finds a seemingly feasible candidate, immediately convert it into structured outputs and run the full saved-artifact validator before launching narrower searches.
