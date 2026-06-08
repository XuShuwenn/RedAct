---
name: fjsp-repair-and-validate
description: "Repair and optimize flexible job shop schedules under downtime and policy budgets, producing validated JSON/CSV outputs."
---

# Flexible Job Shop Repair and Validation

This skill provides a reusable workflow to repair an existing (baseline) schedule for a flexible job shop with machine downtime and policy budgets, and to produce validated outputs. It is intended for tasks where a baseline plan may be infeasible or suboptimal due to machine unavailability and budget rules limiting deviation from baseline decisions.

## When to Use

Activate this skill when you must:
- read a job-shop instance, downtime windows, a policy/budget file, and a baseline schedule
- generate a feasible schedule that respects precedence, machine capacity, and downtime
- improve makespan while not exceeding policy budgets (e.g., machine-change count, start-time shift, makespan guard)
- write both solution.json and schedule.csv with identical schedule data

## Core Workflow

Follow these phases. Each phase ends with concrete checks to catch errors early.

Phase 0: Input ingestion and normalization
- Read the following resources:
  - instance: jobs and operations with allowed machines and processing times
  - downtime: per-machine blocked time windows
  - policy: budgets (e.g., max machine changes, total L1 start shift, optional makespan guard) and any freeze/lock rules
  - baseline schedule: job/op assignments, start times, durations, machines
- Normalize formats:
  - Ensure numeric types for times, durations, and machine IDs
  - Convert downtime rows to half-open intervals [start, end)
  - Build a baseline lookup keyed by (job, op): {machine, start, end, dur}
- Quick checks:
  - Every (job, op) present in baseline
  - Durations > 0 for all operations
  - Downtime windows have start < end

Phase 1: Precedence and resource context
- Construct precedence from operation indices within each job: op k must start after op k-1 finishes
- Build a precedence-aware scheduling order (e.g., increasing op index within each job; break ties by baseline start)
- Initialize machine timelines and mark downtime windows for each machine
- Quick checks:
  - Predecessor end times recognized for all ops with op > 0
  - Machine timeline structures in place (scheduled segments empty initially)

Phase 2: Feasibility-first repair
- Goal: produce a schedule that violates no precedence, capacity, or downtime rules, while respecting policy budgets.
- For each operation in precedence-consistent order:
  1) Freeze logic (if applicable):
     - Consider preserving the baseline choice only if fully feasible:
       - No overlap with any downtime window on the baseline machine
       - No overlap with already-placed operations on that machine
       - Precedence respected (start ≥ predecessor end)
     - If any check fails, do not preserve; repair like any other operation.
  2) Candidate generation:
     - Always include the baseline machine, plus all allowed alternate machines
     - For each machine, compute earliest feasible start t ≥ max(predecessor end, policy-imposed earliest start)
       - Find the earliest t such that [t, t+dur) does not intersect downtime or scheduled segments on that machine
     - Derive candidate attributes: end time, machine-change indicator, L1 start shift vs baseline
  3) Budget-aware pruning and scoring:
     - Discard candidates that would push cumulative budgets (machine changes, total L1 shift) beyond allowed maxima
     - Score candidates by:
       - primary: earliest end (or earliest start)
       - secondary: lower penalty for machine change and shift
       - tie-breakers: prefer baseline machine; then smaller shift
  4) Commit the best candidate:
     - Place interval on the machine timeline
     - Update cumulative budgets and record scheduled op
- Quick checks per operation:
  - If no candidate survives pruning, either (a) relax non-hard preferences (if policy allows) or (b) backtrack/try alternates; otherwise flag infeasible

Phase 3: Makespan-focused refinement (optional)
- If initial greedy repair is feasible but the makespan is unsatisfactory under policy guard:
  - Broaden candidate consideration for selected bottleneck operations (evaluate alternates wherever budgets still allow)
  - Explore small neighborhood changes (e.g., re-evaluating machine for a few critical ops in the critical path)
  - Keep feasibility-first: never accept a change that violates downtime, precedence, or capacity
- Stop when no improvement within budgets is found or time budget is exhausted

Phase 4: Output generation and consistency
- Build the schedule array of entries: {job, op, machine, start, end, dur}
- Compute makespan = max(end) across all entries
- Set status to a concise descriptor (e.g., FEASIBLE or OPTIMIZED)
- Write:
  - solution.json: {"status": str, "makespan": number, "schedule": [ ... ]}
  - schedule.csv: columns job,op,machine,start,end,dur in the same rows as solution.json
- Quick checks:
  - CSV rows count equals JSON schedule length
  - Row-wise equality between JSON and CSV fields

## Verification

Perform these verifications before finalizing outputs:
- Precedence: for every job, op k start ≥ end of op k-1
- Machine capacity: for each machine, no pair of operations overlaps (use [start, end) convention)
- Downtime: each operation interval does not intersect any downtime window on its machine
- Policy budgets:
  - Machine changes = count of (scheduled machine ≠ baseline machine) across all operations ≤ limit
  - L1 start shift = sum over ops of |scheduled start − baseline start| ≤ limit
  - Makespan guard (if defined) respected relative to baseline or absolute cap
  - Any “not earlier than baseline start” rule enforced if present
- Output consistency:
  - Fields are numeric where required
  - Makespan equals max end across schedule
  - JSON and CSV schedules are identical

Success criteria:
- All feasibility checks pass (precedence, capacity, downtime)
- Policy budgets not exceeded
- Outputs exist and are consistent
- Makespan is improved or within required guard, as specified by policy

## Common Pitfalls and Concrete Fixes

Pitfall: Preserving a frozen baseline operation that is actually infeasible
- Fix: Only preserve when both downtime and machine-occupancy checks pass and precedence holds; otherwise repair it like any other operation

Pitfall: Parser mismatches with the instance format
- Fix: Inspect the raw file and adapt the parser; do not assume column order or delimiters; validate counts and required fields after parsing

Pitfall: Overweighting baseline machine in scoring, missing earlier feasible alternates
- Fix: Prioritize earlier feasible completion in scoring; treat machine change and shift as penalties but not absolute blockers when budgets allow

Pitfall: Not evaluating alternates unless a strict condition triggers
- Fix: Consider all allowed machines whenever budget headroom exists; prune only by hard feasibility and budget overrun

Pitfall: Incorrect downtime intersection logic
- Fix: Use half-open intervals [start, end); declare conflict if start < downtime_end and end > downtime_start

Pitfall: Output inconsistency between JSON and CSV
- Fix: Generate both from the same in-memory schedule; run a row-wise equality check before finalizing

Pitfall: Misreported makespan
- Fix: Always recompute makespan as max end over the final schedule; do not reuse stale metrics

## Optional Script Usage

This repository includes a generic validator script to confirm feasibility and budget compliance of generated schedules and the equality of JSON/CSV outputs.

Example:
- Validate a schedule against downtime and policy budgets, and compare against a baseline for budget usage.

Command:
- python scripts/schedule_validator.py --schedule-json path/to/solution.json --schedule-csv path/to/schedule.csv --baseline-json path/to/baseline.json --downtime-csv path/to/downtime.csv --policy-json path/to/policy.json

What it checks:
- Precedence, machine capacity, downtime compliance
- Budgets: machine changes and total L1 shift vs. baseline
- Makespan recomputation and optional guard
- Equality between JSON and CSV schedules
