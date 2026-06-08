---
name: fjsp-baseline-repair
description: "Repair flexible job shop baseline schedules under machine downtimes and policy budgets to produce a feasible, lower-makespan plan with verifiable constraints."
---

# Flexible Job Shop Baseline Repair with Downtime and Policy Budgets

This skill repairs a provided flexible job shop (FJSP) baseline schedule into a feasible plan that respects machine downtimes, operation precedence, and policy budgets (e.g., machine-change limit and total start-shift budget), while seeking to reduce makespan.

## When to Use

Activate this skill when you have:
- A flexible job shop instance where each operation can run on different machines with different durations.
- Known machine downtime windows.
- A baseline schedule and policy budgets (e.g., max machine changes, max total start-shift L1, optional makespan ratio guard, freeze policy).
- A requirement to produce a feasible schedule and minimize makespan without exceeding budgets.

## Inputs (conceptual)

- Instance (operations and machine alternatives):
  - First line: number_of_jobs number_of_machines
  - For each job: one line with number_of_operations
  - For each operation: first token = number_of_machine_options, followed by (machine_id duration) pairs
- Downtime: per-machine closed intervals [start, end) when the machine is unavailable
- Baseline schedule: list of records with job, op, machine, start, end, dur
- Policy:
  - change_budget: { max_machine_changes, max_total_start_shift_L1 }
  - guards: { max_makespan_ratio }
  - freeze: { enabled, freeze_until, lock_fields }

## Core Workflow

1. Parse and Inspect Inputs
   - Confirm instance format and build `allowed[(job, op)] = {machine: duration, ...}`.
   - Build `baseline_map[(job, op)] = record` and remember the baseline order as stored.
   - Normalize and sort downtime windows per machine.
   - Read budgets: max machine changes, max L1 start shift, and any makespan guard.
   - Interpret freeze policy: build the frozen set as the first `freeze_until` operations by baseline array order.
     - Freeze is a locking preference for fields in `lock_fields`; however, frozen operations that violate downtime or create machine overlaps must be repaired minimally to achieve feasibility. Count resulting changes against budgets.

2. Define Precedence-Aware Order
   - Sort (job, op) keys by:
     - op index ascending, then
     - baseline start time ascending, then
     - baseline array index ascending.
   - This order maintains within-job precedence and favors earlier baseline starts.

3. Anchoring and Candidate Generation
   - Maintain `end_time[(job, op)]` for the newly built schedule and `machine_intervals[machine] = [(start, end), ...]`.
   - For each (job, op) in precedence-aware order:
     - Compute anchor time:
       - Baseline-anchored: `anchor = max(baseline_start, end_time[(job, op-1)])`
       - Precedence-only for non-frozen (optional optimization): `anchor = end_time[(job, op-1)]` for non-frozen ops if policy allows earlier starts and budgets permit.
     - If operation is in the frozen set:
       - Attempt to keep baseline machine/start (and end if locked) only if that placement has no downtime or previously scheduled machine conflicts.
       - If it conflicts, treat it as non-frozen and repair (counting budget effects).
     - Generate candidates by iterating allowed machines; for each, find `start = earliest_feasible_time(machine, anchor, duration, machine_intervals, downtime)`.

4. Budget-Aware Selection
   - For each candidate, compute:
     - machine_change = 1 if candidate machine != baseline machine else 0
     - start_shift = abs(candidate_start - baseline_start)
   - Filter out candidates that would exceed remaining budgets if chosen.
   - Score remaining candidates prioritizing makespan reduction first:
     - Primary: earliest candidate start (or earliest end)
     - Secondary: smaller start_shift
     - Tertiary: fewer machine changes
   - Choose the best candidate, update counters (machine-change and shift), record the operation, and append interval to the machine’s timeline.

5. Completion and Output
   - After all operations are placed, makespan = max(end).
   - If a makespan guard is specified and exceeded, optionally retry with:
     - Alternate anchor policy for non-frozen ops (precedence-only)
     - More aggressive use of machine changes within budget
     - Optional limited enumeration of machine choices if the total combination count is tractable (e.g., ≤ a few thousand combos)
   - Write results in a consistent schema; produce both JSON and CSV as needed.

## Verification

Run the following checks before finalizing:
- Operation validity:
  - Assigned machine is in allowed set for (job, op) and `end = start + duration` equals the allowed duration.
- Precedence:
  - For each job, `end(job, op) ≤ start(job, op+1)` for all valid ops.
- Machine non-overlap:
  - For each machine, sort scheduled intervals by start; ensure no adjacent intervals overlap (`prev_end ≤ next_start`).
- Downtime:
  - For each machine, ensure no scheduled interval overlaps any downtime window; use half-open intervals [start, end) consistently.
- Policy budgets:
  - Machine changes (relative to baseline) ≤ max_machine_changes.
  - Total L1 start shift (sum of |start_new − start_base|) ≤ max_total_start_shift_L1.
- Makespan guard (if present):
  - makespan ≤ baseline_makespan × guard_ratio.

A solution is successful when all constraints above pass.

## Common Pitfalls and How to Avoid Them

- Mis-parsing instance format
  - Confirm the format: line 1 is jobs and machines; then each job’s number of operations; then each operation line starts with the count of alternatives followed by (machine, duration) pairs.
- Misinterpreting freeze policies
  - Freeze applies to the first N operations by baseline array order, not by operation index across jobs.
  - Even frozen ops must not violate downtime or create overlaps. If a frozen placement is infeasible, repair it and account for budget.
- Locking frozen operations without checking machine timelines
  - Always check both downtime and already-placed intervals before honoring frozen fields.
- Over-penalizing machine changes in scoring
  - If you prioritize “no machine change” before “earliest start,” you can inflate makespan. Use earliest start or earliest end as the primary criterion, then shift, then machine changes.
- Anchoring too strictly to baseline start times
  - For non-frozen ops, consider precedence-only anchors if earlier starts fit within budgets and reduce makespan, provided the policy allows earlier starts.
- Skipping validation or incomplete checks
  - Implement all verification checks (precedence, non-overlap, downtime, budgets, makespan) before finalizing outputs.

## Optional Strategy: Small-Instance Enumeration

For small instances (e.g., the product of alternatives across all operations ≤ a few thousand), enumerate all machine assignment combinations:
- For each combination, place operations greedily at earliest feasible times (respecting precedence and downtime), compute budgets and makespan, and keep the best valid schedule.
- This can outperform purely greedy selection when the search space is modest.

## Optional Script Usage

This skill ships reusable helpers in `scripts/fjsp_helpers.py`:
- earliest_feasible_time to find the first non-conflicting start.
- precedence_aware_order for the scheduling sweep.
- schedule_greedy for a budget-aware baseline repair.
- validate_schedule to verify constraints.
- enumerate_assignments to optionally explore machine combinations on small instances.

Example (conceptual):
- Build `allowed`, `baseline_schedule`, `downtime`, and `policy` structures in memory.
- Call `schedule_greedy(allowed, baseline_schedule, downtime, policy)`.
- Verify with `validate_schedule(...)` and emit JSON/CSV.

This modular approach enables iterative improvement and straightforward validation without overfitting to a single instance.
