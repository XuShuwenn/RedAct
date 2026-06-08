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


## Required Validation Before Modeling

- Read any baseline or policy file completely before deriving constraints from it; if prior output is truncated, rerun a command that shows the full contents.
- Do not infer freeze or lock semantics from field names alone; encode a hard constraint only when its meaning is directly supported by the task artifacts.
- For fields like `freeze`, `freeze_until`, or similar policy controls, determine from the baseline artifacts and task wording whether they refer to baseline sequence position, elapsed time, operation indices, or exact locked fields; do not assume `op < N` semantics unless the inputs explicitly support that interpretation.
- When freeze behavior depends on a baseline schedule, map the freeze boundary to the baseline schedule's actual stored order/records unless the inputs explicitly define a different indexing rule.
- If a policy interpretation appears ambiguous or inconsistent, verify the inputs and state the assumption clearly rather than hard-coding an unverified rule.

- Before modeling or repairing, extract a complete constraint inventory from the input artifacts: true `instance.txt` structure and machine options, downtime windows from `downtime.csv`, and freeze/lock/change-budget semantics from the full baseline and policy files.
- For schedule-repair tasks, inspect `instance.txt`, `downtime.csv`, `policy.json`, and the available baseline file together before deciding what can change; derive repair logic from the combined constraints, not from any single file in isolation.
- When file contents are shown through a rendered interface or preview, inspect the raw text/bytes view and read the full file before writing a parser or deriving constraints; if output is truncated, rerun with a command that shows the complete contents.
- Before using `/app/data/baseline_solution.json` or any baseline schedule for locks, freeze checks, machine-change counts, start-shift budgets, or baseline makespan comparison, confirm you have read the entire schedule; do not derive constraints from truncated output.
- Run a quick validation pass on any provided baseline schedule before repairing or optimizing it; identify concrete violations (for example downtime, capacity, precedence, or budget conflicts) so changes target actual infeasibilities rather than guessed ones.
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

- Treat any task-specific execution protocol (required action syntax, tool-call format, or exact completion string) as a hard constraint and follow it exactly.
- Apply this final gate before writing feasible output: full baseline read confirmed, freeze/lock semantics enforced literally from the provided artifacts, any required baseline-derived anchors enforced, budget/change metrics recomputed from the final saved schedule, and `final_makespan < baseline_makespan` whenever strict improvement is required.
- Do **not** accept a candidate based only on summary metrics or solver intent. Feasibility requires a direct rule-by-rule audit on the final saved artifacts.
- If validation or solver diagnostics identify any freeze/lock mismatch, precedence, downtime, capacity, machine-legality, duration, or budget violation, reject that candidate; do not ship it as feasible and do not switch to a relaxed model for final output.
- If freeze/lock semantics remain ambiguous after inspecting the artifacts, do **not** declare the schedule definitively feasible under an assumed interpretation. State the assumption explicitly and report unresolved validation or infeasibility unless the governing interpretation is supported by the inputs.
- Do not use an invalid baseline schedule as proof that violating downtime, precedence, or capacity is acceptable. Hard feasibility constraints still govern the final output unless the task explicitly states otherwise.
- A task is not complete until both `/app/output/solution.json` and `/app/output/schedule.csv` are written from a validated final schedule or validated infeasibility/failure-to-improve result, then read back and checked for non-emptiness and consistency.
- If no candidate satisfies all hard constraints and explicit acceptance conditions, write an explicit infeasible or failure-to-improve result instead of a same-makespan, reinterpreted, partially validated, or otherwise noncompliant schedule.
- Do not describe a result as optimal, minimal, or best-possible unless you have explicit proof, an exhaustive method, or a validated bound that supports that claim.

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
