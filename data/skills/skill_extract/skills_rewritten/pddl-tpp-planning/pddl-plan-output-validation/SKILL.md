---
name: pddl-plan-output-validation
description: "Use this skill to reliably generate, format, and verify PDDL plans for tasks defined by a domain/problem pair and a plan_output path in a JSON task list."
---

# PDDL Plan Generation and Output Validation

This skill helps you avoid common failure modes when solving PDDL planning tasks defined via a JSON task list that provides domain, problem, and plan_output paths. It focuses on correct file handling, plan formatting, action/object consistency, and verifiable validation.

## When to Use

Activate this skill when you need to:
- read a task list (JSON) with PDDL domain and problem file paths and write plans to specified outputs
- generate and save syntactically correct PDDL-style plans (one action per line)
- ensure action names and object names match the domain and problem
- validate plans before claiming success

## Core Workflow

1. Load task list
   - Parse the provided JSON task list.
   - For each task entry, assert the presence of keys: `id` (optional), `domain`, `problem`, and `plan_output`.
   - Do not hardcode output paths; use each task's `plan_output` exactly.

2. File existence checks
   - Confirm the domain and problem files exist and are readable before planning.
   - If a path is relative, resolve it relative to the current workspace; do not guess alternate locations.

3. Plan generation
   - Prefer using a planning library/engine available in the environment (e.g., a oneshot planner via a standard API).
   - Select a planner backend known to handle the domain; if multiple are available, try them in order.
   - Check the solver status strictly; only accept results with a solved status (e.g., satisficing or optimal as defined by the planner API). Do not infer success from a non-error run.

4. Plan formatting
   - Extract action instances from the returned plan in the given order.
   - Format each as a single line: `action_name(arg1, arg2, ..., argN)`.
   - Use the action and object names exactly as returned by the planner/domain (case and spelling must match). Do not insert numbering or extra annotations.
   - Ensure one action per line and no empty lines.

5. Static validation (pre-checks)
   - Confirm that each action name exists in the domain and that the number of arguments matches the action's parameter count.
   - Confirm that every argument object name exists in the problem's object set or in the domain's constants.
   - Use the provided optional script to perform these checks deterministically before claiming success.

6. Semantic validation (if available)
   - If a plan validator is available, run it against the domain, problem, and generated plan. Only claim the plan is valid if the validator confirms success.
   - If no validator is available, be explicit about using static checks only and avoid overclaiming.

7. Write output
   - Create parent directories of `plan_output` if they do not exist.
   - Write the plan to the exact `plan_output` path.
   - Reopen and re-check the written file: non-empty, correctly formatted lines.

8. Final confirmation
   - Confirm a 1:1 correspondence between tasks in the JSON and written plan files.
   - Summarize results without inventing additional validation claims.

## Verification

Use both static and, when possible, semantic validation:
- Static checks (always perform):
  - Domain and problem files exist.
  - For each plan line, action exists in domain and argument count matches domain parameters.
  - All argument objects exist in the problem or are declared as domain constants.
  - Plan file formatting matches `name(arg1, arg2, ...)` per line.
- Semantic checks (when validator is available):
  - The plan validator reports the plan solves the problem with no errors.

Success criteria:
- A valid plan file has been written to each task's `plan_output` path.
- The plan file is non-empty and passes static checks.
- If a validator is available, it reports success for each plan.

## Common Pitfalls and How to Avoid Them

- Hardcoding output filenames
  - Pitfall: Writing plans to fixed names instead of the `plan_output` path.
  - Avoidance: Always read and use the `plan_output` field per task.

- Skipping file existence checks
  - Pitfall: Assuming domain/problem paths and proceeding with missing files.
  - Avoidance: Fail fast with a clear error if domain/problem is missing.

- Handcrafting plans without validation
  - Pitfall: Guessing action arguments or order (e.g., repeating parameters) and claiming correctness.
  - Avoidance: Use a planner or, at minimum, cross-check action names and arity against the domain and object names against the problem.

- Misreporting planner status
  - Pitfall: Treating any planner output as success without checking solver status.
  - Avoidance: Accept only explicit solved statuses defined by the planner API.

- Incorrect plan formatting
  - Pitfall: Numbered lines, extra annotations, or wrong punctuation.
  - Avoidance: Format strictly as `action(arg1, ..., argN)` with one action per line.

- Not covering all tasks
  - Pitfall: Generating a plan for only a subset of tasks and claiming all are solved.
  - Avoidance: Iterate over the full task list and verify that an output file is written for each.

- Fictitious validation
  - Pitfall: Claiming plans are validated without running a validator or without evidence.
  - Avoidance: Run a validator when available and log the result; otherwise, explicitly state which checks were performed.

## Optional Script Usage

Use the helper script to perform deterministic static checks on a generated plan:
- Checks action existence and parameter counts using the domain file
- Verifies all plan objects exist in the problem or domain constants
- Validates per-line plan formatting

Example usage:
- python scripts/pddl_plan_check.py --domain /path/to/domain.pddl --problem /path/to/problem.pddl --plan /path/to/plan.txt

Use this prior to finalizing or as a fallback when a semantic validator is unavailable.
