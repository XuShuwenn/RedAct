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

- When a baseline schedule is provided together with freeze/change-budget rules, treat it as the default schedule and prefer minimal repairs over full rescheduling unless the task explicitly calls for a rebuild.

10. Separate objectives explicitly: first satisfy the task's hard deliverable requirement (feasible repair or explicit infeasibility/failure output), then pursue makespan improvement only if the task explicitly requires or rewards it.
11. Choose the primary optimization/acceptance target from the task statement and input artifacts, not from inference. Do not promote a baseline metric into a hard success criterion unless the task explicitly says so.


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
- Run a quick validation pass on any provided baseline schedule before repairing or optimizing it; identify concrete violations (for example downtime, capacity, precedence, or budget conflicts) so changes target actual infeasibilities rather than guessed ones.
- If policy freeze/lock rules depend on a baseline cutoff time, explicitly enumerate the affected baseline operations before solving and record the exact locked fields (`machine`, `start`, `end`, or others). Remove those operations from the movable set unless the artifacts explicitly allow changes.
- Treat baseline-derived freezes as exact equality constraints on the listed fields, not as preferences or earliest-start hints.
- For custom `instance.txt` formats, inspect the raw line structure and token stream first; map each token position, repeated count line, and per-operation option-count field from the file itself rather than assuming a standard FJSP layout.
- If parsing yields suspicious results such as empty jobs, missing operations, zero durations, impossible machine IDs, or any operation with zero machine options, stop and reinspect the raw source files before changing the solver.
- If a parser fails or parsed counts/records look inconsistent with the instance, baseline, or policy data, reopen the raw source files and infer the exact grammar and record counts from the file contents before patching the parser.
- Map freeze/lock rules to the baseline schedule exactly as supported by the artifacts. Do not treat fields like `freeze_until` as per-job operation-index cutoffs, convert stated machine/start/end locks into weaker rules, or otherwise switch semantics mid-repair unless the files explicitly define that alternative.
- When baseline or policy data marks operations as frozen/locked, validate each preserved assignment against allowed-machine rules, downtime, machine occupancy/capacity, precedence, and duration consistency before locking it into the model; if the artifacts explicitly require a lock that conflicts with other hard constraints, report infeasibility rather than relaxing the lock.
- Before modifying scheduling logic, map which baseline operations conflict with downtime or other hard constraints and record why; reserve enforceable frozen baseline intervals before scheduling unfrozen work.
- Derive change-budget metrics directly from the fully loaded baseline and candidate schedule data, and compute those metrics inside the solver or repair workflow so each candidate can be checked against the stated budget before output.
- When rebuilding or repairing a schedule, treat each operation's predecessor in the repaired schedule as the precedence anchor: compute feasible start times from the repaired predecessor end time, not from inconsistent baseline timestamps alone.
- Implement parsing, solving/repair, validation, metric computation, and artifact writing in a dedicated script (for example `/app/solve.py`) instead of piecemeal shell edits when the task has multiple interacting constraints.

## Hard Acceptance Rules

- Protocol compliance is part of correctness, not a formatting nicety: a valid schedule can still fail the task if any action used the wrong schema or the final response omitted the exact required completion token.
- If the environment requires an `Action:` line with JSON for a specific tool, use that exact structure for **every** tool interaction; do not substitute direct tool calls or other labels.
- Treat any task-specific execution protocol (required action syntax, tool-call format, or exact completion string) as a hard constraint and follow it exactly.
- Apply this final gate before writing feasible output: full baseline read confirmed, freeze/lock semantics enforced literally from the provided artifacts, any required baseline-derived anchors enforced, budget/change metrics recomputed from the final saved schedule, and `final_makespan < baseline_makespan` whenever strict improvement is required.
- Do **not** accept a candidate based only on summary metrics or solver intent. Feasibility requires a direct rule-by-rule audit on the final saved artifacts.
- Perform the final audit on `/app/output/solution.json` and `/app/output/schedule.csv` themselves, not just on solver logs or in-memory intent.
- Mandatory final audit on the saved artifacts: compare the final schedule against the baseline row-by-row for every frozen/locked operation; any mismatch in a locked field is an immediate rejection.
- Recompute change-budget metrics directly from the saved final schedule and the fully read baseline/policy files. Do not trust solver console summaries or internal counters unless they are independently checked against the written outputs.
- Check every scheduled operation against every stated downtime window using interval-overlap logic on the saved schedule before claiming feasibility.
- Do not state "all constraints are satisfied" until this explicit saved-artifact validation has passed.
- If validation or solver diagnostics identify any freeze/lock mismatch, precedence, downtime, capacity, machine-legality, duration, or budget violation, reject that candidate; do not ship it as feasible and do not switch to a relaxed model for final output.
- If freeze/lock semantics remain ambiguous after inspecting the artifacts, do **not** declare the schedule definitively feasible under an assumed interpretation. State the assumption explicitly and report unresolved validation or infeasibility unless the governing interpretation is supported by the inputs.
- Do not use an invalid baseline schedule as proof that violating downtime, precedence, or capacity is acceptable. Hard feasibility constraints still govern the final output unless the task explicitly states otherwise.
- A task is not complete until both `/app/output/solution.json` and `/app/output/schedule.csv` are written from a validated final schedule or validated infeasibility/failure-to-improve result, then read back and checked for non-emptiness and consistency.
- Make output generation and validation auditable in the run log: show the concrete write commands or script execution that produced the files, then inspect the saved files directly to confirm key fields and row counts.
- Do not rely on abstract statements such as "written", "validated", or "ok" as evidence. Final feasibility claims must be backed by observable checks of the saved artifacts.
- If no candidate satisfies all hard constraints and explicit acceptance conditions, write an explicit infeasible or failure-to-improve result instead of a same-makespan, reinterpreted, partially validated, or otherwise noncompliant schedule.
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


## Final Pre-Response Checklist

- Confirm the final saved schedule, not an exploratory candidate, is the one written to both output files.
- Recompute and verify all hard constraints on the written artifacts, including freeze/lock semantics and any strict-improvement requirement.
- If validation fails under the literal rules, write infeasible/failure-to-improve output instead of keeping the invalid schedule.
- Then emit the exact required completion marker/token with no extra trailing text.
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

- Prefer parser logic that follows the actual encoding seen in the file (for example token-based parsing for dense instance text) over fixed line-count or column-position assumptions.
- When parser output looks empty, inconsistent, or error-prone, stop and inspect the raw source files again before changing solver logic; fix the parser from the observed format first.
- Treat policy rules as hard constraints, not heuristic penalties. Use the literal meaning from `policy.json`, baseline data, and task instructions; do not reinterpret them to rescue feasibility.
- Ground `freeze` or similar policy fields in the baseline schedule/order before using them in scheduling logic; do not assume they refer to per-job operation indices unless the data explicitly says so.
- In repair tasks, a good default is: keep frozen operations on their required baseline machine/order when mandated, but shift their timing to the earliest slot that satisfies downtime, precedence, and capacity unless exact start/end locking is explicitly required.
- Before solving, extract any locked fields from `policy.json` (for example frozen `machine`, `start`, `end` up to a cutoff time) and enforce them unchanged.
- Practical freeze check: build the set of baseline operations covered by the freeze horizon, then after writing outputs assert for each such operation that final `machine`, `start`, and `end` exactly equal baseline values whenever those fields are locked.
- Practical budget check: compute policy metrics from `solution.json`/`schedule.csv` versus the baseline after writing the files; if the recomputed values differ from what the solver reported, trust the recomputed audit and reject the candidate.
- Do not turn a baseline comparison or policy bound into a stricter requirement unless the inputs explicitly say so.
- Move from planning to execution quickly: run a concrete bounded solver or constructive heuristic early, and wrap expensive searches with a timeout.
- Prefer a simple feasible schedule generator over extended method discussion; iterate after you have a candidate schedule.

- For repair or baseline-guided tasks, prefer repairing the provided baseline schedule over rebuilding from scratch when freeze/change-budget constraints are present: keep baseline assignments and timings unless a change is required for feasibility or explicit improvement.
- Use a precedence-aware constructive scheduler for movable operations: process operations in precedence-safe order, track predecessor completion times, maintain per-machine occupied intervals, and place each operation at the earliest feasible time on an allowed machine that respects capacity, downtime, and any explicit locked fields.
- If using a heuristic or local search, describe the result as a feasible or improved schedule; do not call it optimal or minimal unless you have explicit proof, a certificate, or a verified bound.
- After any solver edit, inspect the changed code and rerun with enough diagnostics to confirm behavior actually changed before trusting the new result.
- Treat written artifacts as the source of truth: after generating `/app/output/solution.json` and `/app/output/schedule.csv`, read them back and validate them before claiming success.
- Use a dedicated validator script or equivalent explicit checks on the saved artifacts; do not rely on visual inspection alone to confirm downtime, precedence, machine non-overlap, locked fields, freeze compliance, and policy-budget compliance.
- Before finalizing, explicitly verify: job precedence, operation durations, one-machine-at-a-time capacity, downtime avoidance, policy-budget comparison against the complete baseline, that makespan equals the max end time in the saved schedule, and that `schedule.csv` matches `solution.json`.
- Recompute any policy/budget claims from the final saved schedule and compare against the provided baseline/policy files; do not report exact counts/totals unless they were derived from the final artifacts.
- If literal policy constraints make improvement infeasible, report that conflict clearly instead of claiming success with a modified or non-improving schedule.
- Do not rely on truncated solver console output as evidence. If logs are partial, inspect the full output files or rerun validation scripts on those files before concluding.
- Always write both required artifacts: `/app/output/solution.json` and `/app/output/schedule.csv`.

- Read `instance.txt`, `downtime.csv`, `policy.json`, and any baseline file together before designing repair logic so machine alternatives, downtime, freeze rules, and change budgets are modeled consistently.
- Prefer baseline-guided repair when a baseline schedule is provided: load the baseline first, preserve unchanged assignments and times by default where allowed, and modify only the operations needed for feasibility or required improvement within the stated limits.
- If starting from a baseline schedule, generate a violation report first, then repair only from validated facts in the inputs and baseline.
- A reliable repair pattern is precedence-aware earliest-feasible replay: after choosing candidate machine assignments, place each operation at the earliest start that satisfies predecessor completion, machine capacity, downtime windows, reserved frozen intervals, durations, and any baseline-derived lower bounds or explicit locks.
- Reserve machine-time slots for frozen assignments that are already feasible before scheduling repaired or flexible operations; do not let later repairs displace valid frozen operations.
- Repair only frozen operations that are inherently invalid or explicitly allowed to change; if preserved locked/frozen assignments still conflict with other hard constraints, report infeasibility rather than relaxing those constraints.
- During constructive repair or local search, track policy-budget usage incrementally and reject over-budget candidates early rather than relying only on an end-of-run check.
- For each operation, evaluate all allowed machine alternatives with feasible start/end times under downtime and policy constraints; do not default to the baseline machine when other permitted machines may yield a better valid schedule.
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
