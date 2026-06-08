---
name: manufacturing-fjsp-optimization
description: "Optimize flexible job shop scheduling with machine downtime windows and policy budget constraints to minimize makespan."
---

# Flexible Job Shop Scheduling Optimization

## When to Use

- Optimize manufacturing job shop schedules
- Handle machine downtime windows
- Minimize makespan with budget constraints

## Input Files

- `/app/data/instance.txt`: Job and operation data
- `/app/data/downtime.csv`: Machine downtime windows
- `/app/data/policy.json`: Policy budget data
- `/app/data/current baseline`: Current schedule

- Before coding any parser or solver, inspect the raw contents of each required input file and confirm the actual structure and field meanings from the source files themselves.
- Read every required input file completely before deriving constraints from it; if any view or output is truncated, continue reading until the relevant records are fully visible.
- Treat the baseline schedule as authoritative for freeze/change-budget checks; do not infer locked operations from a partial read.


- `/app/data/baseline_solution.json`: Baseline schedule/policy reference if present; read the full file before using it for locks, budgets, or comparisons

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


## Required Validation Before Modeling

- Read any baseline or policy file completely before deriving constraints from it; if prior output is truncated, rerun a command that shows the full contents.
- Do not infer freeze or lock semantics from field names alone; encode a hard constraint only when its meaning is directly supported by the task artifacts.
- If a policy interpretation appears ambiguous or inconsistent, verify the inputs and state the assumption clearly rather than hard-coding an unverified rule.

## Hard Acceptance Rules

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
- Treat policy rules as hard constraints, not heuristic penalties. Use the literal meaning from `policy.json`, baseline data, and task instructions; do not reinterpret them to rescue feasibility.
- Ground `freeze` or similar policy fields in the baseline schedule/order before using them in scheduling logic; do not assume they refer to per-job operation indices unless the data explicitly says so.
- Before solving, extract any locked fields from `policy.json` (for example frozen `machine`, `start`, `end` up to a cutoff time) and enforce them unchanged.
- Do not turn a baseline comparison or policy bound into a stricter requirement unless the inputs explicitly say so.
- Move from planning to execution quickly: run a concrete bounded solver or constructive heuristic early, and wrap expensive searches with a timeout.
- Prefer a simple feasible schedule generator over extended method discussion; iterate after you have a candidate schedule.
- If using a heuristic or local search, describe the result as a feasible or improved schedule; do not call it optimal or minimal unless you have explicit proof, a certificate, or a verified bound.
- After any solver edit, inspect the changed code and rerun with enough diagnostics to confirm behavior actually changed before trusting the new result.
- Treat written artifacts as the source of truth: after generating `/app/output/solution.json` and `/app/output/schedule.csv`, read them back and validate them before claiming success.
- Before finalizing, explicitly verify: job precedence, operation durations, one-machine-at-a-time capacity, downtime avoidance, policy-budget comparison against the complete baseline, that makespan equals the max end time in the saved schedule, and that `schedule.csv` matches `solution.json`.
- Recompute any policy/budget claims from the final saved schedule and compare against the provided baseline/policy files; do not report exact counts/totals unless they were derived from the final artifacts.
- If literal policy constraints make improvement infeasible, report that conflict clearly instead of claiming success with a modified or non-improving schedule.
- Do not rely on truncated solver console output as evidence. If logs are partial, inspect the full output files or rerun validation scripts on those files before concluding.
- Always write both required artifacts: `/app/output/solution.json` and `/app/output/schedule.csv`.
